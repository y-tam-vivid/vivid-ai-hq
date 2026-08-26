#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GAS の稼働を「成果物の実体」から判定する ── 外形監視

  python3 gas_outside_watch.py            読むだけ
  python3 gas_outside_watch.py --run      ⚙️レジスタの最終実行を実体に合わせて書き戻す
  python3 gas_outside_watch.py --run --beat

なぜ要るか（2026-08-20 実測）
  ⚙️レジスタが「営業ワークブックの週次バックアップ ＝ 256時間前」と申告していた。
  ★だが Drive を見ると 8/16(日) 19:54 にバックアップが実在した。**動いている。**

    真因 ── weekly_backup.gs は心拍を打たない。
             レジスタの 8/9 は人が手で書いた値だった。
             ＝ **心拍を打たないものをレジスタに載せると、永久に🔴になる。**

  「動いていないものを見逃す」のと「動いているものを止まっていると誤判定する」のは
  同じ欠落の裏表 → memory/reference_monitor_must_exclude_parked.md

★記憶に「外形監視は使えない（証拠がSheets側・miniにGoogle認証なし）」とあったが、
  2026-08-19 に OAuth が通って以降、**mini から Drive を読める**。前提が変わった。

見方
  成果物（バックアップのコピー）の作成日時 ＝ その GAS が最後に動いた時刻
  GAS 本体には一切触らない。承認も要らない。
"""

import os
import re
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets_client import Sheets                      # noqa: E402

# ★2026-08-27 つる ── ここは watch_external.py と同じ名前を打っていた（相乗り）。
#   結果、専用行「GASの稼働を成果物から判定する（外形監視）」へは心拍が届かず、
#   毎朝08:45に rc=0 で完走しているのに永久に🟡遅延を出していた（8/25・8/26 実測）。
#   ★レジスタの行名と1文字ずつ一致させること。
PROC_NAME = 'GASの稼働を成果物から判定する（外形監視）'
JST = datetime.timezone(datetime.timedelta(hours=9))

# レジスタの処理名 → 成果物の名前に含まれる語
# ★AIが手で取ったバックアップと混ざらないよう、名前の形を正規表現で厳密に指定する。
#   2026-08-20 実測 ── 最初は「'バックアップ' を含む最新」で拾ったため、
#   その日の朝に当方が取った `営業案件管理（福祉施設／…）_バックアップ_20260820-0126` を
#   「週次バックアップが動いた証拠」と誤認した。
#   **自分の書き込みを、自動処理が動いた証拠にしてはいけない。**
WATCH = [
    # (レジスタの処理名, 成果物の名前にかかる正規表現, 期待間隔[時間])
    ('営業ワークブックの週次バックアップ',
     r'^営業案件管理_バックアップ_(\d{8})-(\d{4})$', 168),
]


def latest(sh, pattern):
    """★共有ドライブも見る（既定ではマイドライブしか見えない）
    ★名前が pattern に**完全一致**するものだけを数える。
      部分一致で拾うと、AIが手で取ったバックアップを自動処理の証拠と誤認する。
    """
    rx = re.compile(pattern)
    r = sh.drive.files().list(
        q="trashed=false and name contains 'バックアップ'",
        orderBy='createdTime desc', pageSize=100,
        supportsAllDrives=True, includeItemsFromAllDrives=True,
        fields='files(id,name,createdTime)').execute()
    best = None
    for f in r.get('files', []):
        m = rx.match(f['name'])
        if not m:
            continue
        # ★名前の日時を使う。createdTime は Drive 側のタイムゾーンで揺れる
        d, t = m.group(1), m.group(2)
        try:
            when = datetime.datetime(int(d[:4]), int(d[4:6]), int(d[6:8]),
                                     int(t[:2]), int(t[2:]), tzinfo=JST)
        except ValueError:
            continue
        if best is None or when > best[0]:
            best = (when, f['name'])
    return best if best else (None, None)


def main(dry=True, beat=False):
    sh = Sheets()
    now = datetime.datetime.now(JST)
    bad = 0
    rows = []
    for name, kw, interval in WATCH:
        when, fname = latest(sh, kw)
        if not when:
            print('%-34s ★成果物が見つからない' % name[:32])
            bad += 1
            continue
        h = (now - when).total_seconds() / 3600
        mark = '★遅れ' if h > interval else '正常'
        print('%-34s %s  %s（%.0f時間前 / 期待%d時間）'
              % (name[:32], mark, when.strftime('%m-%d %H:%M'), h, interval))
        print('     実体 ： %s' % fname[:66])
        if h > interval:
            bad += 1
        rows.append((name, when, h > interval, fname))

    if dry:
        print('\n---- 読むだけ。レジスタへ書き戻すには --run ----')
        return 0

    # ★レジスタの「最終実行」を実体に合わせる（心拍を打たないGASの代わり）
    sys.path.insert(0, HERE)
    from heartbeat import _token, _api, REGISTER_DB
    tok = _token()
    q = _api(tok, 'POST', '/databases/%s/query' % REGISTER_DB, {'page_size': 100})
    by_name = {}
    for p in q.get('results', []):
        t = ''.join(x['plain_text'] for x in p['properties']['処理名']['title'])
        by_name[t] = p['id']
    for name, when, late, fname in rows:
        pid = by_name.get(name)
        if not pid:
            print('★レジスタに「%s」の行が無い' % name)
            continue
        _api(tok, 'PATCH', '/pages/%s' % pid, {'properties': {
            '最終実行': {'date': {'start': when.isoformat()}},
            '最終結果': {'select': {'name': '警告' if late else '成功'}},
            'メッセージ': {'rich_text': [{'text': {'content':
                '外形監視（成果物から判定）： %s' % fname[:80]}}]},
        }})
        print('レジスタへ書き戻した ： %s → %s' % (name[:26], when.strftime('%m-%d %H:%M')))

    if beat:
        try:
            from heartbeat import beat as hb
            hb(PROC_NAME, '警告' if bad else '成功',
               '%d本を見て、遅れ %d本' % (len(WATCH), bad))
        except Exception as e:
            sys.stderr.write('[心拍] 打てず ： %s\n' % e)
    return 0


if __name__ == '__main__':
    sys.exit(main(dry=('--run' not in sys.argv), beat=('--beat' in sys.argv)))
