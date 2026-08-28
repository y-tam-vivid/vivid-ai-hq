#!/usr/bin/env python3
"""
validate_report.py - 実施報告書の内容を機械検証する

報告書は「記載内容を統一する」ことに価値がある。同じ器で貯めるから年次比較ができる。
本スクリプトは必須項目の充足・KPI対比の成立・収支の整合を判定する。

使い方:
  python3 validate_report.py report.json [--json]
"""
import argparse, json, sys

REQUIRED = ['イベント名', '開催日', '会場', '主催者', '開催目的', '実施内容', '総括']
KPI_KEYS = ['指標', '目標値', '実績値']


def num(v):
    try:
        return float(str(v).replace(',', '').replace('円', '').replace('人', '').strip())
    except Exception:
        return None


def validate(r):
    err, warn, note = [], [], []

    for k in REQUIRED:
        if not str(r.get(k, '')).strip():
            err.append(f'必須項目が空です: {k}')

    kpis = r.get('KPI', [])
    if not kpis:
        err.append('KPIが1件もありません。目標に対する達成度を示せないと報告書の価値が出ません')
    for i, k in enumerate(kpis, 1):
        for kk in KPI_KEYS:
            if kk not in k or str(k.get(kk, '')).strip() == '':
                warn.append(f'KPI{i}「{k.get("指標","?")}」の{kk}が空です')
        t, a = num(k.get('目標値')), num(k.get('実績値'))
        if t is not None and a is not None:
            rate = round(a / t * 100) if t else None
            note.append(f'{k.get("指標")}: 目標{k.get("目標値")} → 実績{k.get("実績値")}'
                        + (f'（達成率{rate}%）' if rate is not None else ''))
            if rate is not None and rate < 80 and not str(k.get('未達要因', '')).strip():
                warn.append(f'KPI「{k.get("指標")}」は達成率{rate}%です。未達要因の記載がありません')

    sp = r.get('収支', {})
    if sp:
        inc, exp = num(sp.get('収入')), num(sp.get('支出'))
        bal = num(sp.get('収支'))
        if inc is not None and exp is not None:
            calc = inc - exp
            if bal is not None and abs(calc - bal) > 1:
                err.append(f'収支が合いません: 収入{inc:,.0f} - 支出{exp:,.0f} = {calc:,.0f}（記載は{bal:,.0f}）')
            else:
                note.append(f'収支: 収入{inc:,.0f} - 支出{exp:,.0f} = {calc:,.0f}')
        if r.get('KPI'):
            visitors = next((num(k.get('実績値')) for k in kpis if '来場' in str(k.get('指標', ''))), None)
            if visitors and exp and visitors > 0:
                note.append(f'来場者1人あたりコスト: {exp / visitors:,.0f}円')

    if not str(r.get('課題・改善点', '')).strip():
        warn.append('課題・改善点が空です。次回に引き継ぐ資産がないと報告書が記録で終わります')
    if not r.get('参加者の反応'):
        warn.append('参加者の反応（アンケート・声）がありません。定量だけでは施策の理由が読めません')

    total = str(r.get('総括', ''))
    for w in ('成功だった', '盛況だった', 'good', '良かった'):
        if w in total and not any(c.isdigit() for c in total):
            warn.append('総括が数値を伴わない主観表現になっています。事実と数値で書き直してください')
            break
    return err, warn, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report'); ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    r = json.load(open(a.report, encoding='utf-8'))
    err, warn, note = validate(r)
    if a.json:
        print(json.dumps({'errors': err, 'warnings': warn, 'computed': note},
                         ensure_ascii=False, indent=2))
        sys.exit(1 if err else 0)
    print(f'=== 報告書検証: {r.get("イベント名", "(名称未設定)")} ===\n')
    for label, items, mark in (('エラー（提出不可）', err, '×'),
                               ('警告', warn, '!'),
                               ('自動算出', note, '·')):
        if items:
            print(f'■ {label}')
            for x in items: print(f'  {mark} {x}')
            print()
    print('判定:', '提出不可' if err else ('要確認' if warn else '提出可'))
    sys.exit(1 if err else 0)


if __name__ == '__main__':
    main()
