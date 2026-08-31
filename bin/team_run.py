#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
チームで回す ── 依頼を渡すと、編成・並列実行・検査・統合まで自動でやる

  python3 team_run.py "受付シートの残りを台帳へ入れて"
  python3 team_run.py --dry "…"          編成だけ見る（実行しない）
  python3 team_run.py --from-slack       Slack DM の最新の依頼を拾って回す

なぜ要るか（2026-08-20 有璽氏）
  > 「有機的に全然動かせてねえじゃん。チームを束ねる位置づけになるんじゃないの？
  >   ちゃんとそこ連携して、全てにおいてだよ、ミスも連携してなくすようにするとかよ。
  >   チェックもそうだし、制作もそうだし、そうやって役割分担してやれっつってんねん」

  ★これまで ── ビビが都度「この作業はピタゴラス」と判断して1体呼ぶ。
    判断を忘れれば一人でやる。忘れたことに誰も気づかない。
  ★これから ── 依頼を渡せば**必ず**編成される。ビビの判断に依存しない。

型（Skill cross-check の実装）
  ① 分類          何の仕事か（実装／調査／設計／検査／記録）
  ② 編成          作る役（複数・並列）＋ 検査役 ＋ 束ねる役
  ③ 並列実行      ★AI同士を会話させない。同じ型で並べる
  ④ 検査          ★作った本人ではない主体が「通す／止める」まで判定する
  ⑤ 統合          ロビンが 合意点／対立点／不明点 に分ける
  ⑥ 出す          人へは1本。判断が要るものだけ Slack へ

どこでも同じように動く
  このファイルは vivid-ai-hq/bin/ にあるので、git で全機へ配られる。
  claude CLI さえあれば MacBook でも mini でも同じ編成で回る。
"""

import io
import os
import re
import sys
import json
import time
import subprocess
import datetime

# ★スクリプト自身の位置から導く（2026-08-31）。~/vivid-ai-hq 固定だと、クラウド面や
#   別ユーザー名の機械で「ファイルが無い」で落ちる。実測で踏んだので直した。
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELAY = os.path.expanduser('~/.vivid-relay')
def _find_claude():
    """claude CLI の場所を実際に探す。★固定パスにしない（2026-08-31）。
    ~/.npm-global/bin/claude 固定だったため、実体が /opt/node22/bin/claude にある面で
    「claude が無い」と誤って報告した。パスは機械ごとに違う。"""
    import shutil
    found = shutil.which('claude')
    if found:
        return found
    for c in ('~/.npm-global/bin/claude', '/opt/node22/bin/claude',
              '/usr/local/bin/claude', '/opt/homebrew/bin/claude'):
        c = os.path.expanduser(c)
        if os.path.exists(c):
            return c
    return 'claude'

CLAUDE = _find_claude()
TIMEOUT = 1500

# ── 協調層の正本を読む（2026-08-31）────────────────────────────
#   役割・読むもの・封筒の型・終了条件・人が入る点は bin/coordination/roster.json が正本。
#   ★ここへ書き写さない。写した瞬間に二重管理になり、片方だけ直る事故が起きる。
ROSTER_PATH = os.path.join(REPO, 'bin', 'coordination', 'roster.json')
try:
    with io.open(ROSTER_PATH, encoding='utf-8') as _f:
        ROSTER = json.load(_f)
except Exception as _e:
    raise SystemExit('★協調層の正本が読めません ： %s\n  %s' % (ROSTER_PATH, _e))

def roster_of(agent):
    return ROSTER.get('agents', {}).get(agent, {})

_INDEX_BY_AGENT = os.path.join(REPO, 'memory', 'INDEX_担当別.md')

def reads_of(agent):
    """その担当が常設で読むもの。
    ★正本は memory/INDEX_担当別.md の表。roster.json にも agents/*.md にも写さない。
      2026-08-31、roster.json 側へ書き写したところ、書いたその日に既存の表と3件ズレた
      （ナミ・つる・モルガンズが INDEX_notion も読む点が落ちていた）。だから読みに行く。
    表の書式 ： | 担当名 | `<agent>.md` | [INDEX_xxx](INDEX_xxx.md) ／ … |"""
    try:
        with io.open(_INDEX_BY_AGENT, encoding='utf-8') as f:
            for line in f:
                if not line.startswith('|'):
                    continue
                cols = [c.strip() for c in line.strip().strip('|').split('|')]
                if len(cols) < 3 or ('`%s.md`' % agent) not in cols[1]:
                    continue
                found = re.findall(r'\((INDEX_[^)]+\.md)\)', cols[2])
                if '全部' in cols[2]:
                    found = ['INDEX_' + n for n in
                             ['営業.md', '仕組み.md', 'notion.md', '発信.md',
                              '担当と案件.md', '担当別.md']]
                return ['memory/' + x for x in dict.fromkeys(found)]
    except Exception:
        pass
    return []

def envelope_spec():
    return ROSTER.get('envelope', {})

def max_rounds():
    return ROSTER.get('termination', {}).get('max_rounds', 2)


# ── 何の仕事か → 誰を呼ぶか（★ここが編成の正本）────────────────
#   makers  : 並列で走る「作る役」。違う角度を持たせる
#   checker : ★作る役とは必ず別。「通す／止める」まで判定させる
TEAM = [
    # (判定キーワード, 仕事の名前, makers, checker)
    (r'台帳|顧客|マスタ|重複|突合|発番|kintone|スプレッドシート|シート',
     '台帳・顧客データ',
     [('system-developer', 'データの流れと実装の観点で'),
      ('cfo', '数字と与信の観点で。件数・金額の整合を疑う')],
     'data-auditor'),
    (r'notion|ナレッジ|記録|議事録|ドキュメント|まとめ',
     'ナレッジ・記録',
     [('cko', '記録の設計と過去の経緯の観点で'),
      ('design', '見せ方・情報設計の観点で')],
     'data-auditor'),
    (r'実装|コード|スクリプト|バグ|修正|cron|自動化|フック|hook',
     '実装',
     # ★dev-producer（ステラ）を作る役に入れない（2026-08-31 チーム検査の指摘②）。
     #   入れると「コード」領域の検査役が自分自身になり fallback（つる）へ落ちるため、
     #   ステラが検査役として一度も呼ばれない状態が続いていた。
     [('system-developer', 'システム設計と堅牢性の観点で'),
      ('cko', '過去に踏んだ地雷と既存資産との重複の観点で')],
     'dev-producer'),
    (r'契約|法務|規約|コンプラ|個人情報|機微',
     '法務',
     [('legal', '日本法と契約実務の観点で'),
      ('cfo', '金額・支払条件・与信の観点で')],
     'data-auditor'),      # ★legalを検査役にすると作る役と同じになる（2026-08-20 実測で発見）
    (r'発信|広報|プレス|sns|投稿|記事',
     '広報',
     [('pr', '対外発信と炎上リスクの観点で'),
      ('design', '見せ方と伝わり方の観点で')],
     'legal'),           # ★legalは作る役に入れない。検査役として通す／止めるを判定させる
    (r'設計|方針|どうする|進め方|全体像|構想',
     '設計・方針',
     [('dev-producer', '実現可能性と段取りの観点で'),
      ('cko', '過去の決定との整合の観点で'),
      ('cfo', 'コストと効果の観点で')],
     'data-auditor'),
]
DEFAULT = ('その他',
           [('cko', '過去の蓄積と整合の観点で'),
            ('system-developer', '実装と運用の観点で')],
           'data-auditor')


def _assert_separated(name, makers, checker):
    """★作る役と検査役が同じなら止める。
    この仕組みの核心（自分が作ったものを自分で検査しない）に反するため。
    2026-08-20、法務の編成で legal が両方に入っていたのを実測で発見した。
    編成表を手で書く限り再発するので、機械が弾く"""
    who = [a for a, _ in makers]
    if checker in who:
        raise SystemExit(
            '★編成が壊れています ： %s で「%s」が作る役と検査役を兼ねています。\n'
            '  自分が作ったものを自分で検査させてはいけません。TEAM を直してください。'
            % (name, checker))


def inspector_for(domain):
    """その領域の検査役を roster.json の inspects から引く。
    ★TEAM 側へ検査役を書き写さない（2026-08-31 チーム検査の指摘①）。
      roster.json は cfo/legal/dev-producer/data-auditor/automation-watchdog の5体に
      inspects を持たせているのに、TEAM の checker は data-auditor と legal の2体固定で、
      「cron・GASトリガーは必ずドーベルマンを通す」ゲートが実装に存在しなかった。"""
    for aid, a in ROSTER.get('agents', {}).items():
        if a.get('inspects') == domain:
            return aid
    return None


# 仕事の中身 → 通すべき検査役の領域（★ここは「領域名」だけを書く。担当名は書かない）
INSPECT_DOMAIN = [
    (r'cron|routine|トリガー|定期実行|自動処理|daily_jobs', '自動処理'),
    (r'台帳|顧客|マスタ|重複|突合|発番|kintone|スプレッドシート|シート', 'データ'),
    (r'契約|法務|規約|コンプラ|個人情報', '法務'),
    (r'請求|入金|予実|kpi|資金', '財務'),
    (r'実装|コード|スクリプト|バグ|フック|hook', 'コード'),
]


def classify(task):
    for pat, name, makers, checker in TEAM:
        if re.search(pat, task, re.I):
            checker = _override_checker(task, makers, checker)
            _assert_separated(name, makers, checker)
            return name, makers, checker
    checker = _override_checker(task, DEFAULT[1], DEFAULT[2])
    _assert_separated(DEFAULT[0], DEFAULT[1], checker)
    return DEFAULT[0], DEFAULT[1], checker


def _override_checker(task, makers, fallback):
    """roster.json のゲートを優先する。★作る役と重なる場合はフォールバックへ戻す
    （自分が作ったものを自分で検査させない、が上位の規範）"""
    who = [a for a, _ in makers]
    for pat, domain in INSPECT_DOMAIN:
        if re.search(pat, task, re.I):
            cand = inspector_for(domain)
            if cand and cand not in who:
                return cand
    return fallback


def validate_all():
    """全編成を起動前に検査する（--dry でも本実行でも通る）"""
    for pat, name, makers, checker in TEAM:
        _assert_separated(name, makers, checker)
    _assert_separated(DEFAULT[0], DEFAULT[1], DEFAULT[2])


def run_agent(agent, task, angle, role):
    """1体を走らせる。★他の役の出力は渡さない（会話させない）"""
    _reads = reads_of(agent)
    _reads_block = ('\n'.join('  - ~/vivid-ai-hq/%s' % x for x in _reads)
                    if _reads else '  （このagentは常設の読みものを持ちません）')
    prompt = """あなたは ふくち。グループの「%s」です。
`~/vivid-ai-hq/.claude/agents/%s.md` を読んで、その人物として振る舞ってください。

## 着手前に必ず読むもの（協調層の正本 roster.json で固定されています）
%s
★「どれを読むか」を自分で選ばないでください。上に挙がったものだけを読みます。

## 役割
%s

## 観点
**%s** 見てください。他の担当も並列で別の観点から見ています。
★合意しようとしないでください。あなたの角度から見えたものを書くのが仕事です。

## 依頼
%s

## 出し方
```
結論      … 一文で
根拠      … 実物を読んで確かめたことだけ。推測は「推測」と明記
必須条件  … あなたの領域から見て、これが無いと成立しないもの
懸念      … 見落とされそうなこと
自信度    … high / medium / low
確かめた経路 … 何経路で確かめたか。**1経路なら「1経路でしか確かめていない」と書く**
```
600文字以内。日本語。**やっていないことをやったように書かない。**
★「すべて」「0件」「無い」「変わっていない」は、2経路で確かめた時だけ書いてよい。
★他の担当へ質問を書かないでください。受け取るのは束ねる役だけで、往復はしません。
""" % (agent, agent, _reads_block, role, angle, task)
    try:
        r = subprocess.run([CLAUDE, '-p', prompt], cwd=REPO,
                           capture_output=True, text=True, timeout=TIMEOUT)
        return agent, (r.stdout or '').strip(), r.returncode == 0
    except Exception as e:
        return agent, '★失敗 ： %s' % str(e)[:200], False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    task = ' '.join(args).strip()
    if not task:
        print('依頼を渡してください ： python3 team_run.py "…"')
        return 1

    validate_all()                      # ★編成表そのものを毎回検査する
    name, makers, checker = classify(task)
    print('【%s】チームで回す' % ('編成だけ' if dry else '実行'))
    print('■ 依頼 ： %s' % task[:100])
    print('■ 仕事の種類 ： %s' % name)
    print('■ 編成')
    for a, angle in makers:
        print('   作る役   %-18s %s' % (a, angle))
    print('   検査役   %-18s ★作る役とは別。通す／止めるまで判定させる' % checker)
    print('   束ねる役 %-18s 合意点／対立点／不明点に分ける' % 'cko')
    print('')
    if dry:
        print('---- 編成だけ。実行しない ----')
        return 0

    # ── ③ 並列（会話させない）──────────────────────────
    import concurrent.futures as cf
    outs = []
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=len(makers)) as ex:
        futs = [ex.submit(run_agent, a, task, angle, '所見を書く役です。実装はしないでください。')
                for a, angle in makers]
        for f in cf.as_completed(futs):
            outs.append(f.result())
    print('■ 所見 ： %d体 ／ %.0f秒' % (len(outs), time.time() - t0))
    for a, o, ok in outs:
        print('')
        print('── %s %s' % (a, '' if ok else '★失敗'))
        print(o[:700])
    print('')

    # ── ④ 検査（★作った本人ではない）────────────────────
    joined = '\n\n'.join('【%s の所見】\n%s' % (a, o) for a, o, _ in outs)
    chk_prompt = """あなたは検査役です。`~/vivid-ai-hq/.claude/agents/%s.md` を読んで振る舞ってください。
`~/vivid-ai-hq/.claude/skills/cross-check/SKILL.md` の型に従ってください。

## 依頼（元の議題）
%s

## ★1周目は blind です（roster.json inspection.pass_a_blind）
各担当の所見は **わざと渡していません**。申告を先に読むと、報告に無いもの
（落とした指示・過剰修正）が見えなくなるためです。実物と diff だけを見てください。

  git -C %s diff HEAD~1     直近の変更
  git -C %s status --short  未コミットの変更

## やること（★roster.json の inspection.pass_a_blind に従う）
★いまは1周目です。**各担当の所見はわざと渡していません。**実物と diff だけで判断してください。
   （申告を先に読むと、報告に無いもの＝落とした指示・過剰修正が見えなくなるため）
1. **diff に出てくる数字を、あなた自身が別経路で数え直す。**
   実例 ： 「解消11件」の申告を突合したら実物は7件だった（2026-08-29）。
2. **実物で裏が取れない変更** を指摘する（コメントやdocstringの主張と実装のズレを含む）
3. **「すべて」「0件」「無い」「変わっていない」が1経路の確認で書かれていないか**を見る
4. **過去に踏んだ地雷を踏んでいないか**（`~/vivid-ai-hq/memory/` と
   `~/vivid-ai-hq/bin/hooks/adversarial_cases.md` を見る）
5. **その検問・仕組みをすり抜ける書き方が無いか**を敵対的に探す
6. 最後に **「この方針で進めてよいか」を一言で**。止めるべきなら止めると言う

深刻な順に最大6件。①どこ ②何が問題か ③どの規範に反するか ④起きる事故。
問題が無ければ「無い」と明言。読んでいない範囲があれば必ず書く。700文字以内。
""" % (checker, task, REPO, REPO)
    _, chk_a, chk_ok = run_agent(checker, chk_prompt, '検査の観点で',
                                 '検査役です（1周目・blind）。直さないでください。')
    # ── Pass B ── ここで初めて申告を見せる（roster.json inspection.pass_b_context）
    chk_b_prompt = """あなたは同じ検査役です。1周目は実物だけを見て次を書きました。

## あなたの1周目の所見（blind）
%s

## いま初めて渡す「作った本人の申告」
%s

## やること
1. **申告にあって、あなたが1周目に見つけられなかったもの** ＝ 実物で裏が取れているか
2. **あなたが1周目に見つけたのに、申告に出てこないもの** ＝ ★これが本命。
   「できません」は書けるが「忘れました」は本人にも見えない。落ちた指示は報告に出ない
3. 最後に「進めてよいか／止めるか」を一言で
400文字以内。日本語。""" % (chk_a[:2500], joined[:4000])
    _, chk_b, _ = run_agent(checker, chk_b_prompt, '申告との突合の観点で',
                            '検査役です（2周目）。直さないでください。')
    chk = '【1周目・実物だけを見た所見】\n%s\n\n【2周目・申告と突き合わせて】\n%s' % (chk_a, chk_b)
    print('── 検査役 %s' % checker)
    print(chk[:900])
    print('')

    # ── ⑤ 統合 ─────────────────────────────────────────
    sum_prompt = """あなたはロビン（CKO）。`~/vivid-ai-hq/.claude/agents/cko.md` を読んで振る舞ってください。

## 議題
%s

## 各担当の所見
%s

## 検査役の判定
%s

## やること
**束ねてください。合意させないでください。**
```
■ 合意点     … 全員が同じことを言っている部分
■ ★対立点   … 角度によって答えが違う部分（★消さない。並べる）
■ 不明点     … 誰も確かめていない部分
■ 次の一手   … 有璽氏が「承認」か「差し戻し」だけで済む形にする
■ ★人が要る … AIでは進められないもの（あれば）
```
800文字以内。日本語。
""" % (task, joined[:5000], chk[:2000])
    _, summary, _ = run_agent('cko', sum_prompt, '統合の観点で', '束ねる役です。')
    print('── 統合（ロビン）')
    print(summary[:1200])

    # ── ⑥ 人へ出す（判断が要るものだけ）──────────────────
    try:
        sys.path.insert(0, RELAY)
        from notify import tell
        need = ('人が要る' in summary and '★人が要る ： 0' not in summary)
        head = '★判断が要ります' if need else 'チームで検討しました'
        tell('%s ： %s' % (head, task[:40]),
             '編成 ： %s ／ 検査 ： %s\n\n%s'
             % ('・'.join(a for a, _ in makers), checker, summary[:2500]))
    except Exception as e:
        sys.stderr.write('[Slack] 送れず ： %s\n' % e)
    return 0


if __name__ == '__main__':
    sys.exit(main())
