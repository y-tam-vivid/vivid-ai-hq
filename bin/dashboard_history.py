#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""稼働盤の数字を日ごとに残す（★過去を消さないための器）

なぜ要るか（2026-08-25 有璽氏）
  > 「過去のやつは消えますか？ 今のものも、今後含めて遡れますか？」

  実測すると dashboard_data.json も dashboard.html も**毎回まるごと上書き**で、
  履歴を残す処理が1行も無かった。定期実行に載せるほど失う過去が増える構造だった。
  → memory/reference_overwriting_containers_have_no_past.md

設計
  残す単位   ★日ごと最新1本。回数では残さない
             （2時間おき＝1日12版。全部残すと「その日の姿」が分からなくなる）
             → memory/reference_retention_by_count_deletes_the_wrong_ones.md
  残すもの   ★画面(HTML)ではなく数字(JSON)。見た目が変わっても比較できる
  置き場     git 配下 data/dashboard_history/YYYY-MM-DD.json.gz
             ★~/.vivid-relay/ に置くと もう一方のマシンから見えず、消えても気づかない
  消さない   過去の日は上書きも削除もしない。同じ日だけ最新で置き換える

使い方
  python3 bin/dashboard_history.py            保存（既定）
  python3 bin/dashboard_history.py --list     残っている日を一覧する
  python3 bin/dashboard_history.py --diff     前回保存分との差分を出す（読むだけ）
"""
import gzip, json, os, sys, datetime

REPO = os.environ.get('VIVID_REPO', os.path.expanduser('~/vivid-ai-hq'))
SRC  = os.environ.get('DASHBOARD_JSON', os.path.expanduser('~/.vivid-relay/dashboard_data.json'))
DEST = os.path.join(REPO, 'data', 'dashboard_history')


def days():
    if not os.path.isdir(DEST):
        return []
    return sorted(f[:-8] for f in os.listdir(DEST) if f.endswith('.json.gz'))


def load(day):
    with gzip.open(os.path.join(DEST, day + '.json.gz'), 'rt', encoding='utf-8') as f:
        return json.load(f)


def flat(d, prefix=''):
    """{"value":…} の3点セットだけを拾って平らにする"""
    out = {}
    if isinstance(d, dict):
        if 'value' in d and 'how' in d:
            out[prefix.rstrip('.')] = d['value']
            return out
        for k, v in d.items():
            out.update(flat(v, prefix + k + '.'))
    return out


def save():
    if not os.path.exists(SRC):
        print('NG  元データが無い: ' + SRC)
        return 1
    data = json.load(open(SRC, encoding='utf-8'))
    gen = data.get('generated_at', '')
    day = (gen[:10] if len(gen) >= 10 else datetime.date.today().isoformat())
    os.makedirs(DEST, exist_ok=True)
    path = os.path.join(DEST, day + '.json.gz')
    existed = os.path.exists(path)
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    size = os.path.getsize(path)
    print('%s  %s (%d バイト) ／ 残っている日 %d 日ぶん'
          % ('上書き（その日の最新）' if existed else '新規保存', path, size, len(days())))
    return 0


def show_list():
    d = days()
    if not d:
        print('まだ1日も残っていない')
        return 0
    print('残っている日 %d 日ぶん（%s 〜 %s）' % (len(d), d[0], d[-1]))
    for x in d:
        print('    ' + x)
    return 0


def show_diff():
    d = days()
    if len(d) < 2:
        print('比較できる日が2日ぶん無い（いま %d 日）' % len(d))
        return 0
    a, b = flat(load(d[-2])), flat(load(d[-1]))
    keys = sorted(set(a) | set(b))
    changed = [(k, a.get(k), b.get(k)) for k in keys if a.get(k) != b.get(k)]
    print('%s → %s ／ 変わった項目 %d 件' % (d[-2], d[-1], len(changed)))
    for k, x, y in changed:
        print('    %-46s %s → %s' % (k, x, y))
    return 0


if __name__ == '__main__':
    if '--list' in sys.argv:
        sys.exit(show_list())
    if '--diff' in sys.argv:
        sys.exit(show_diff())
    sys.exit(save())
