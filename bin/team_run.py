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

import os
import re
import sys
import json
import time
import subprocess
import datetime

REPO = os.path.expanduser('~/vivid-ai-hq')
RELAY = os.path.expanduser('~/.vivid-relay')
CLAUDE = os.path.expanduser('~/.npm-global/bin/claude')
TIMEOUT = 1500

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
     [('system-developer', 'システム設計と堅牢性の観点で'),
      ('dev-producer', '割り振りと段取り、既存資産との重複の観点で')],
     'data-auditor'),
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


def classify(task):
    for pat, name, makers, checker in TEAM:
        if re.search(pat, task, re.I):
            _assert_separated(name, makers, checker)
            return name, makers, checker
    _assert_separated(DEFAULT[0], DEFAULT[1], DEFAULT[2])
    return DEFAULT


def validate_all():
    """全編成を起動前に検査する（--dry でも本実行でも通る）"""
    for pat, name, makers, checker in TEAM:
        _assert_separated(name, makers, checker)
    _assert_separated(DEFAULT[0], DEFAULT[1], DEFAULT[2])


def run_agent(agent, task, angle, role):
    """1体を走らせる。★他の役の出力は渡さない（会話させない）"""
    prompt = """あなたは ふくち。グループの「%s」です。
`~/vivid-ai-hq/.claude/agents/%s.md` を読んで、その人物として振る舞ってください。

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
```
600文字以内。日本語。**やっていないことをやったように書かない。**
""" % (agent, agent, role, angle, task)
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

## 各担当の所見（★作った本人の申告。信用せず実物で確かめること）
%s

## やること
1. 所見のうち **実物で裏が取れないもの** を指摘する
2. **過去に踏んだ地雷を踏んでいないか**（`~/vivid-ai-hq/memory/` を見る）
3. 最後に **「この方針で進めてよいか」を一言で**。止めるべきなら止めると言う

深刻な順に最大6件。①どこ ②何が問題か ③どの規範に反するか ④起きる事故。
問題が無ければ「無い」と明言。読んでいない範囲があれば必ず書く。700文字以内。
""" % (checker, task, joined[:6000])
    _, chk, chk_ok = run_agent(checker, chk_prompt, '検査の観点で', '検査役です。直さないでください。')
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
