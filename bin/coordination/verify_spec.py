#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""協調層の「仕様（roster.json）」と「実装（team_run.py）」が一致しているかを機械で検証する。

なぜ要るか（2026-08-31 有璽氏）
  > 「認識しているものと実態が全然違うってことでしょ。なんでそういう乖離が起こるの？」
  > 「わざわざ監査役とかに毎度毎度指摘されてたら意味ないやろ。監査役は必要やけど、
  >   ならないように。どうやってならないように設計・仕組みを作っていくかを考えるべき」

  同日、窓口（ビビ）の申告が実態とズレたのが3件。3周のチーム検査で全部指摘された。
  ★3件とも構造が同じで、★3件とも機械で捕まえられるものだった。

    「blind に直した」    仕様(roster.json)に書いただけで実装(team_run.py)は直していない
    「ステラを検査役に」   関数は書いたが、実際に --dry を回して確かめていない
    「5ケースで検証した」  実行はしたがテストを残さず、記憶で報告した

  共通するのは **「書いた」を「動く」と取り違えている** こと。書いた内容は自分の意図
  そのものなので、読み返しても正しく見える。だから自己点検では見つからない。
  ★検査役は「機械で捕まえられないもの」を見る役であって、これを毎回見つける役ではない。

このファイルの役割
  仕様に書いてあることを、**実装を実際に動かして**確かめる。
  静的な読み合わせではなく、可能な限り実行して結果を突き合わせる。
  ★検証できない項目は「未検証」と正直に出す（できたことにしない）。

使い方
  python3 bin/coordination/verify_spec.py     不一致があれば exit 1
  check.sh 項目9 から毎回叩かれる。
"""
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ROSTER_PATH = os.path.join(HERE, 'roster.json')

spec = importlib.util.spec_from_file_location(
    'tr', os.path.join(REPO, 'bin', 'team_run.py'))
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)

with io.open(ROSTER_PATH, encoding='utf-8') as f:
    ROSTER = json.load(f)

TEAM_RUN_SRC = io.open(os.path.join(REPO, 'bin', 'team_run.py'),
                       encoding='utf-8').read()

results = []   # (状態, 見出し, 詳細)  状態 = ok / ng / unverified


def ok(title, detail=''):
    results.append(('ok', title, detail))


def ng(title, detail):
    results.append(('ng', title, detail))


def unverified(title, why):
    results.append(('unverified', title, why))


# ─────────────────────────────────────────────────────────────
# 1. inspection.self_inspection == 禁止 ── 作る役と検査役が重ならないか
#    ★全編成を実際に classify() へ通して確かめる（表を読むだけにしない）
# ─────────────────────────────────────────────────────────────
def verify_self_inspection():
    if ROSTER.get('inspection', {}).get('self_inspection') != '禁止':
        unverified('自己検査の禁止', 'roster.json に self_inspection の指定が無い')
        return
    probes = ['台帳の重複を直す', '契約書を確認する', 'フックのコードを直す',
              'cronを追加する', 'プレスリリースを書く', '設計の方針を決める',
              'なんとなくの相談']
    bad = []
    for p in probes:
        name, makers, checker = tr.classify(p)
        if checker in [a for a, _ in makers]:
            bad.append('%s → %s が両方' % (p, checker))
    if bad:
        ng('自己検査の禁止', '／'.join(bad))
    else:
        ok('自己検査の禁止', '%d通りの依頼で実際に編成し、重なりなし' % len(probes))


# ─────────────────────────────────────────────────────────────
# 2. inspects を持つ担当が、実際に検査役として呼ばれるか
#    ★ここが 2026-08-31 の「ステラを検査役にした（実際は未達）」を捕まえる検査。
#      仕様に inspects を書いても、編成側で常に fallback へ落ちれば意味がない。
# ─────────────────────────────────────────────────────────────
DOMAIN_PROBES = {
    '自動処理': 'cronに定期実行を1本追加したい',
    'データ': '顧客台帳の重複を統合したい',
    '法務': '業務委託契約のリーガルチェック',
    '財務': '今月の請求と入金の予実を見たい',
    'コード': 'フックのコードのバグを直したい',
}


def verify_inspectors_reachable():
    declared = {aid: a['inspects'] for aid, a in ROSTER['agents'].items()
                if a.get('inspects')}
    unreachable, reached = [], []
    for aid, domain in sorted(declared.items()):
        probe = DOMAIN_PROBES.get(domain)
        if not probe:
            unverified('検査役 %s（%s）' % (aid, domain),
                       'この領域を引き当てる依頼文の見本が未登録')
            continue
        _, makers, checker = tr.classify(probe)
        if checker == aid:
            reached.append('%s→%s' % (domain, aid))
        else:
            unreachable.append(
                '%s（%s）は「%s」で呼ばれず %s になる' % (aid, domain, probe, checker))
    if unreachable:
        ng('宣言した検査役が実際に呼ばれるか', '／'.join(unreachable))
    if reached:
        ok('宣言した検査役が実際に呼ばれるか', '実測 ： ' + '、'.join(reached))


# ─────────────────────────────────────────────────────────────
# 3. inspection.pass_a_blind.withholds ── 1周目に申告を渡していないか
#    ★「blind に直した」と報告しながら所見全文を渡していた件を捕まえる検査。
# ─────────────────────────────────────────────────────────────
def verify_blind():
    wh = ROSTER.get('inspection', {}).get('pass_a_blind', {}).get('withholds')
    if not wh:
        unverified('blind 検査', 'roster.json に pass_a_blind.withholds が無い')
        return
    # Pass A のプロンプト本体を切り出して、所見（joined）を渡していないか見る
    try:
        head = TEAM_RUN_SRC.index('chk_prompt = """')
        tail = TEAM_RUN_SRC.index('run_agent(checker, chk_prompt', head)
        pass_a = TEAM_RUN_SRC[head:tail]
    except ValueError:
        unverified('blind 検査', 'Pass A のプロンプトを特定できなかった')
        return
    problems = []
    if 'joined' in pass_a:
        problems.append('Pass A のプロンプトに joined（各担当の所見全文）が入っている')
    if '所見' in pass_a and 'わざと渡していません' not in pass_a:
        problems.append('Pass A が「所見」に言及しているが、渡していない旨の断りが無い')
    if problems:
        ng('blind 検査（1周目に申告を渡さない）', '／'.join(problems))
    else:
        ok('blind 検査（1周目に申告を渡さない）',
           'Pass A に所見を渡していないことをソースで確認')


# ─────────────────────────────────────────────────────────────
# 4. envelope.required ── 出し方の指示に、必須項目が実際に書かれているか
# ─────────────────────────────────────────────────────────────
LABELS = {'conclusion': '結論', 'grounds': '根拠', 'must': '必須条件',
          'risk': '懸念', 'confidence': '自信度', 'routes': '確かめた経路'}


def verify_envelope():
    req = ROSTER.get('envelope', {}).get('required') or []
    missing = []
    for item in req:
        key = item.split(':')[0]
        label = LABELS.get(key)
        if not label:
            unverified('封筒の項目 %s' % key, '日本語ラベルの対応が未登録')
            continue
        if label not in TEAM_RUN_SRC:
            missing.append('%s（%s）' % (key, label))
    if missing:
        ng('封筒の必須項目が指示に入っているか', '実装に無い ： ' + '、'.join(missing))
    else:
        ok('封筒の必須項目が指示に入っているか', '%d項目すべて実装に存在' % len(req))


# ─────────────────────────────────────────────────────────────
# 5. flow.forbidden_edges ── 担当同士に互いの出力を渡していないか
# ─────────────────────────────────────────────────────────────
def verify_no_worker_crosstalk():
    forbidden = [e for e in ROSTER.get('flow', {}).get('forbidden_edges', [])
                 if e.get('from') == '*workers*' and e.get('to') == '*workers*']
    if not forbidden:
        unverified('担当同士の往復禁止', 'roster.json に該当の禁止辺が無い')
        return
    try:
        head = TEAM_RUN_SRC.index('def run_agent(')
        body = TEAM_RUN_SRC[head:TEAM_RUN_SRC.index('\ndef ', head + 10)]
    except ValueError:
        unverified('担当同士の往復禁止', 'run_agent の本体を特定できなかった')
        return
    if 'joined' in body or 'outs' in body:
        ng('担当同士の往復禁止', 'run_agent が他の担当の出力を受け取れる形になっている')
        return
    # ★呼び出し側も見る（2026-08-31 チーム検査4周目の指摘）。関数本体が綺麗でも、
    #   main() で他の担当の出力を混ぜて渡していれば往復と同じことが起きる。
    #   makers を回している箇所（並列実行）で joined/outs を渡していないか。
    import re as _re
    calls = _re.findall(r'run_agent\([^)]*\)', TEAM_RUN_SRC, _re.S)
    dirty = [c for c in calls
             if ('joined' in c or 'outs' in c) and 'chk' not in c]
    if dirty:
        ng('担当同士の往復禁止',
           '作る役の呼び出しに他の担当の出力が混ざっている ： %s' % dirty[0][:80])
    else:
        ok('担当同士の往復禁止',
           'run_agent の本体と全%d箇所の呼び出しの両方を確認' % len(calls))


# ─────────────────────────────────────────────────────────────
# 6. termination ── 終了条件が実装に反映されているか
#    ★守れていないものを「守れている」と書かない。未実装なら未実装と出す。
# ─────────────────────────────────────────────────────────────
def verify_termination():
    t = ROSTER.get('termination', {})
    if 'max_rounds' in t:
        # 実装側にラウンド制御があるか。無いなら正直に未実装と出す
        # ★「関数が存在する」を「実装されている」と読まない（2026-08-31 自戒）。
        #   max_rounds() を定義しただけでラウンド制御が無い状態を、最初の版は
        #   「実装に参照あり」＝ok と判定していた。まさに「書いた」を「動く」と
        #   取り違える型で、この検査自身が同じ誤りを犯していた。
        #   実際にラウンドを数えて止めているか（比較や繰り返し）を見る。
        import re as _re
        controls = _re.search(r'max_rounds\(\)\s*[<>=]|range\(\s*max_rounds',
                              TEAM_RUN_SRC)
        if controls:
            ok('終了条件 max_rounds', '実装がラウンド数を実際に比較している')
        else:
            unverified(
                '終了条件 max_rounds=%s' % t['max_rounds'],
                '★team_run.py は1回きりの実行でラウンド制御が無い。'
                '複数周は人が繰り返し呼んでいる（＝仕様が実装にまだ落ちていない）')
    if 'timeout_minutes' in t:
        want = int(t['timeout_minutes']) * 60
        got = getattr(tr, 'TIMEOUT', None)
        if got == want:
            ok('終了条件 timeout', '%d秒で一致' % got)
        else:
            ng('終了条件 timeout',
               'roster=%d分(%d秒) だが実装 TIMEOUT=%s' % (
                   t['timeout_minutes'], want, got))


CHECKS = (verify_self_inspection, verify_inspectors_reachable, verify_blind,
          verify_envelope, verify_no_worker_crosstalk, verify_termination)



# ─────────────────────────────────────────────────────────────
# 7. 網羅性 ── 仕様に書いてあるのに検証していない項目を列挙する
#    ★2026-08-31 チーム検査4周目の指摘。「未検証は明示する」と自分で書きながら、
#      envelope.forbidden・termination.on_unresolved/on_malformed_envelope・
#      human_gates を黙って通していた。仕様の過半が検証範囲の外にあった。
#    ★これは個別項目の検査ではなく「検査の網羅率そのもの」を測る。
#      roster.json に新しい項目を足せば、自動的に「未検証」として出てくる。
# ─────────────────────────────────────────────────────────────
# いま機械で検証できている仕様のキー（上の各 verify_* が実際に見ているもの）
COVERED = {
    'inspection.self_inspection', 'inspection.pass_a_blind',
    'envelope.required', 'flow.forbidden_edges',
    'termination.max_rounds', 'termination.timeout_minutes',
}

# 検証しないと決めたもの（理由つき）。★「できない」を隠さず、理由を書いて残す
WONT = {
    'inspection.pass_b_context': '2周目に何を渡すかは実行時にしか決まらない',
    'flow.entry': '入口が secretary であることは実行経路が1本なので自明',
}


def _spec_keys():
    """roster.json の検証対象キーを列挙する（_ で始まる注記は除く）"""
    keys = []
    for section in ('envelope', 'flow', 'inspection', 'termination', 'human_gates'):
        node = ROSTER.get(section)
        if not isinstance(node, dict):
            continue
        for k in node:
            if k.startswith('_'):
                continue
            keys.append('%s.%s' % (section, k))
    return keys


def verify_coverage():
    keys = _spec_keys()
    uncovered = [k for k in keys if k not in COVERED and k not in WONT]
    covered = [k for k in keys if k in COVERED]
    if uncovered:
        # ★不一致ではないが、黙って通してはいけない。必ず名前を出す
        unverified(
            '検証していない仕様が %d件（網羅率 %d/%d）' % (
                len(uncovered), len(covered), len(keys)),
            '、'.join(uncovered))
    else:
        ok('仕様の網羅性', '%d件すべて検証済み' % len(covered))
    for k, why in sorted(WONT.items()):
        if k in keys:
            unverified('%s は検証しない' % k, why)


def main():
    for fn in CHECKS:
        try:
            fn()
        # ★BaseException で受ける（2026-08-31 実測）。team_run.py の
        #   _assert_separated() は SystemExit を投げるが、SystemExit は Exception を
        #   継承しないため `except Exception` では捕まらない。実測すると
        #   verify_spec.py は検査結果を1行も出さずに落ち、しかも rc=0（成功）で返り、
        #   check.sh が「✓ 仕様⇄実装の一致」と表示していた。
        #   ＝ 検証が死んでいるのに緑になる、いちばん危ない壊れ方だった。
        except BaseException as e:
            ng(fn.__name__, '検証中に例外 ： %s: %s' % (type(e).__name__, str(e)[:100]))

    # ★1件も結果が無いのは「問題なし」ではなく「検証が走っていない」
    if not results:
        print('  ✗ 検証が1件も実行されていない（検証プロセス自体の異常）')
        return 1

    verify_coverage()          # ★印字より前に呼ぶ（結果に載せるため）

    mark = {'ok': '✓', 'ng': '✗', 'unverified': '△'}
    for state, title, detail in results:
        print('  %s %s%s' % (mark[state], title, ('  ── ' + detail) if detail else ''))

    bad = [r for r in results if r[0] == 'ng']
    un = [r for r in results if r[0] == 'unverified']
    print('')
    print('  仕様⇄実装 ： 一致 %d ／ 不一致 %d ／ 未検証 %d'
          % (len(results) - len(bad) - len(un), len(bad), len(un)))
    if un:
        print('  ★未検証は「守れている」ではない。機械で確かめられていないだけ。')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
