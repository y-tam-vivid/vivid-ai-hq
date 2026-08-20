#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保護の範囲を器の行数まで伸ばす ── 足りていれば何もしない（自己修復）

  python3 ledger_guard_extend.py            読むだけ（足りていない本数を出す）
  python3 ledger_guard_extend.py --run      伸ばす
  python3 ledger_guard_extend.py --run --beat

なぜ要るか（2026-08-20 実測）
  00_企業マスタ は器807行でデータが満杯だった。新規行のため add_rows で1行足したが、
  ★範囲保護4本は endRowIndex:807 のままで、808行目に及ばなかった。

    行を足す作業は「値を書く」と「守りを伸ばす」の2つ。
    片方だけやると、**新しい行にだけ穴が開く**。既存行を見ている限り気づけない。

  08_関係フォロー には保護の自動延長を組み込んであるが、00_企業マスタ には無かった。
  ここで両方を面倒みる。

★条件付き書式は add_rows に自動追随することを実測（行2〜808へ伸びていた）。
  追随しないのは範囲保護だけ。
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets_client import Sheets, WORKBOOK_ID          # noqa: E402

PROC_NAME = '台帳の保護を器の行数まで伸ばす'
SHEETS = ('00_企業マスタ', '01_顧客詳細', '02_個人マスタ', '08_関係フォロー', '40_活動ログ')


def scan(sh):
    r = sh.svc.spreadsheets().get(
        spreadsheetId=WORKBOOK_ID,
        fields='sheets(properties(title,gridProperties),protectedRanges)').execute()
    out = []
    for s in r.get('sheets', []):
        name = s['properties']['title']
        if name not in SHEETS:
            continue
        rows = s['properties']['gridProperties']['rowCount']
        short = []
        for x in s.get('protectedRanges', []):
            end = x['range'].get('endRowIndex')
            # ★endRowIndex が無い＝シート全体の保護。伸ばす必要が無い
            if end is not None and end < rows:
                short.append(x)
        out.append((name, rows, s.get('protectedRanges', []), short))
    return out


def main(dry=True, beat=False):
    sh = Sheets()
    found = scan(sh)
    total_short = 0
    reqs = []
    for name, rows, all_pr, short in found:
        print('%-14s 器%4d行 ／ 保護%2d本 ／ ★届いていない %d本'
              % (name, rows, len(all_pr), len(short)))
        for x in short:
            total_short += 1
            rg = dict(x['range'])
            old = rg.get('endRowIndex')
            rg['endRowIndex'] = rows
            print('     id=%-12s %s行 → %d行  %s'
                  % (x['protectedRangeId'], old, rows, (x.get('description') or '')[:34]))
            reqs.append({'updateProtectedRange': {
                'protectedRange': {'protectedRangeId': x['protectedRangeId'], 'range': rg},
                'fields': 'range'}})

    if total_short == 0:
        print('\n足りている。何もしない。')
    elif dry:
        print('\n---- 読むだけ。伸ばすには --run ----')
    else:
        sh.svc.spreadsheets().batchUpdate(
            spreadsheetId=WORKBOOK_ID, body={'requests': reqs}).execute()
        # ★実行したら必ず読み返して突合する
        again = sum(len(s) for _, _, _, s in scan(sh))
        print('\n★%d本を伸ばした。読み返し ： まだ届いていない %d本' % (len(reqs), again))
        if again:
            print('★伸ばしきれていない。人が見ること')
            total_short = again

    if beat and not dry:
        try:
            from heartbeat import beat as hb
            hb(PROC_NAME, '警告' if total_short else '成功',
               '伸ばした%d本' % len(reqs) if reqs else '足りている')
        except Exception as e:
            sys.stderr.write('[心拍] 打てず ： %s\n' % e)
    return 0


if __name__ == '__main__':
    sys.exit(main(dry=('--run' not in sys.argv), beat=('--beat' in sys.argv)))
