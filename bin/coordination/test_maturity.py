#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成熟度モード（実測 full ⇄ 仕様 spec）の実測テスト。

なぜファイルとして残すか
  「4通りとも実測した」と報告しても、テストが残っていなければ裏が取れない
  （2026-08-31 チーム検査2周目の指摘で学んだ）。他人が同じ手順で再現できる形で置く。

★本物の実績台帳（maturity.json）は汚さない。一時ディレクトリへ差し替えて実行する。

使い方
  python3 bin/coordination/test_maturity.py     不一致があれば exit 1
  check.sh 項目9 から毎回叩かれる。
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

spec = importlib.util.spec_from_file_location(
    'tr', os.path.join(REPO, 'bin', 'team_run.py'))
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)

ng = []


def check(label, got, expect):
    hit = (got == expect)
    if not hit:
        ng.append('%s ： %s（期待 %s）' % (label, got, expect))
    print('%s %-44s %-6s 期待=%s' % ('✓' if hit else '✗', label, got, expect))


def with_temp_ledger(fn):
    """本物の台帳を触らずに実行する"""
    real = tr.MATURITY_PATH
    tmp = tempfile.mkdtemp(prefix='test_maturity_')
    tr.MATURITY_PATH = os.path.join(tmp, 'maturity.json')
    with io.open(tr.MATURITY_PATH, 'w', encoding='utf-8') as f:
        json.dump({'_spec_fingerprint': tr._spec_fingerprint(), 'kinds': {}}, f)
    try:
        fn()
    finally:
        tr.MATURITY_PATH = real
        shutil.rmtree(tmp, ignore_errors=True)


def test_promote_demote():
    need = int(tr.ROSTER['inspection']['maturity']['promote_after_clean_runs'])
    k = '__test__'
    check('初回は実測（full）', tr.mode_for(k)[0], 'full')
    for i in range(need - 1):
        tr.record_run(k, sent_back=False)
        check('%d回通過ではまだ full' % (i + 1), tr.mode_for(k)[0], 'full')
    tr.record_run(k, sent_back=False)
    check('%d回連続通過で spec へ降ろす' % need, tr.mode_for(k)[0], 'spec')
    tr.record_run(k, sent_back=True)
    check('差し戻し1回で full へ戻る', tr.mode_for(k)[0], 'full')


def test_verdict():
    """★検査役が落ちた回を『通過』として実績に積まない（5周目の指摘②）"""
    cases = [
        ('検査役の実行が失敗（空）', '', False, True),
        ('検査役の実行が失敗（文章あり）',
         '載せてよい。問題ない内容です。実物を確認しました。', False, True),
        ('正常に通過', '実物を確認しました。問題ない。この方針で進めてよい。', True, False),
        ('正常に差し戻し', '差し戻し。必須条件が3点あります。実物で確認しました。', True, True),
        ('中身の無い返答', 'OK', True, True),
        ('肯定も否定も無い',
         'roster.json を読みました。team_run.py も読みました。以上です。', True, True),
    ]
    for label, text, ok_flag, expect in cases:
        check('判定 ： ' + label, tr.looks_sent_back(text, checker_ok=ok_flag), expect)


def test_fingerprint():
    """★仕様だけでなく実装が変わっても降格する（5周目の指摘③）"""
    covered = [os.path.basename(p) for p in tr.FINGERPRINT_FILES]
    check('指紋に roster.json を含む', 'roster.json' in covered, True)
    check('指紋に team_run.py を含む', 'team_run.py' in covered, True)
    check('指紋に verify_spec.py を含む', 'verify_spec.py' in covered, True)


def test_ledger_guarded():
    """★実績台帳を直接書き換えて昇格できないこと（5周目の指摘①）"""
    hspec = importlib.util.spec_from_file_location(
        'hsw', os.path.join(REPO, 'bin', 'hooks', 'hook_session_writeback.py'))
    hsw = importlib.util.module_from_spec(hspec)
    hspec.loader.exec_module(hsw)
    check('実績台帳が書込ガードの対象',
          hsw._is_guarded('bin/coordination/maturity.json'), True)
    check('仕様も書込ガードの対象',
          hsw._is_guarded('bin/coordination/roster.json'), True)



def test_risk_floor():
    """★危険度の下限は実績を上書きする（2026-08-31 有璽氏の承認で追加）。
    kind は7分類で粗く、軽い依頼の実績が重い依頼へ流用されうる。
    取り返しのつかない領域だけ、何回通っても実測に固定する。"""
    need = int(tr.ROSTER['inspection']['maturity']['promote_after_clean_runs'])
    k = '実装'
    for _ in range(need):
        tr.record_run(k, sent_back=False)
    check('危険語なしなら spec のまま', tr.mode_for(k, 'ログ表示を整える')[0], 'spec')
    danger = [
        ('台帳へ書く', '顧客台帳へ新規行を登録する'),
        ('外へ出る', 'プレスリリースをPR TIMESへ配信する'),
        ('規範の変更', 'fukuchi-core の規範を改訂する'),
        ('自動処理', 'cronへ定期実行を1本追加する'),
        ('削除', '古いNotionページを削除する'),
        ('お金', '見積を出して発注する'),
    ]
    for label, task in danger:
        check('危険度の下限 ： %s → 実測固定' % label, tr.mode_for(k, task)[0], 'full')


def main():
    with_temp_ledger(test_promote_demote)
    with_temp_ledger(test_risk_floor)
    test_verdict()
    test_fingerprint()
    test_ledger_guarded()
    print('')
    if ng:
        print('★不一致 %d件' % len(ng))
        for n in ng:
            print('   ' + n)
        return 1
    print('全件一致。★危険度の下限（A案）は実装済み ── 台帳・外へ出る・規範・自動処理・'
          '削除・お金 は実績に関係なく実測。担当/ファイル単位の実績（B案）は未実装で、'
          '同じ危険度の中では kind（7分類）の粗さが残る。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
