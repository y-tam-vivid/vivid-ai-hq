#!/usr/bin/env python3
"""
build_runsheet.py - イベント当日の香盤表（進行表）と役割分担表を生成する

主催イベントでは「誰が・いつ・何をするか」が決まっていないと当日が破綻する。
開催時間とプログラムから、設営・リハ・開場・進行・撤収までを分単位で並べる。

使い方:
  python3 build_runsheet.py --config runsheet.json --out /mnt/user-data/outputs --prefix fair

設定JSONの例:
{
  "イベント名": "◯◯フェア2026",
  "開催日": "2026-09-12",
  "開場": "10:00",
  "終了": "17:00",
  "設営所要分": 90,
  "撤収所要分": 60,
  "リハ所要分": 30,
  "プログラム": [
    {"名称": "オープニング挨拶", "所要分": 10, "担当": "田村", "備考": "音響確認済のこと"},
    {"名称": "ワークショップ第1部", "所要分": 90, "担当": "松本", "備考": "定員20名"},
    {"名称": "休憩", "所要分": 30, "担当": "-", "備考": ""},
    {"名称": "ワークショップ第2部", "所要分": 90, "担当": "松本", "備考": ""}
  ],
  "体制": [
    {"役割": "総括", "担当": "田村", "連絡先": "090-xxxx-xxxx", "業務": "全体判断・来賓対応"},
    {"役割": "受付", "担当": "柴田", "連絡先": "", "業務": "受付・配布物・人数カウント"},
    {"役割": "記録", "担当": "鈴木", "連絡先": "", "業務": "写真動画撮影・SNS素材"},
    {"役割": "安全", "担当": "吉川", "連絡先": "", "業務": "導線管理・救護連絡"}
  ]
}
"""
import argparse, csv, json, os
from datetime import datetime, timedelta

REQUIRED_ROLES = {
    '総括': '当日の最終判断を下す人。不在だと判断が止まる',
    '受付': '来場者数の実測はここでしか取れない。報告書のKPIに直結',
    '記録': '写真・動画がないと広報も報告書も作れない',
    '安全': '導線・救護・緊急連絡。主催なら必須',
}


def t(s):
    return datetime.strptime(s, '%H:%M')


def build(cfg):
    open_t, close_t = t(cfg['開場']), t(cfg['終了'])
    rows = []  # (開始, 終了, 区分, 内容, 担当, 備考)

    setup = int(cfg.get('設営所要分', 90))
    reh = int(cfg.get('リハ所要分', 30))
    BRIEF = 10
    start_setup = open_t - timedelta(minutes=setup + reh + BRIEF)
    rows.append((start_setup, start_setup + timedelta(minutes=setup), '準備', '設営・什器搬入・配線',
                 cfg.get('設営担当', '全員'), '完了時に写真を1枚記録'))
    r0 = start_setup + timedelta(minutes=setup)
    rows.append((r0, r0 + timedelta(minutes=reh), '準備', 'リハーサル・動作確認・役割最終確認',
                 '全員', '音響・映像・ネットワークを実機で確認'))
    rows.append((open_t - timedelta(minutes=BRIEF), open_t, '準備', '開場前ブリーフィング',
                 cfg.get('体制', [{}])[0].get('担当', '総括'), '当日の変更点を共有'))

    cur = open_t
    rows.append((cur, cur, '進行', '開場', '受付', '来場カウント開始'))
    for p in cfg.get('プログラム', []):
        dur = int(p.get('所要分', 0))
        end = cur + timedelta(minutes=dur)
        rows.append((cur, end, '進行', p['名称'], p.get('担当', '-'), p.get('備考', '')))
        cur = end

    if cur < close_t:
        rows.append((cur, close_t, '進行', '自由観覧・個別対応', '全員', ''))
    elif cur > close_t:
        rows.append((close_t, cur, '進行', '⚠ プログラムが終了時刻を超過しています', '-',
                     f'{int((cur - close_t).total_seconds() // 60)}分オーバー。要調整'))

    rows.append((close_t, close_t, '進行', '閉場', '受付', '最終来場数を確定して記録'))
    tear = int(cfg.get('撤収所要分', 60))
    rows.append((close_t, close_t + timedelta(minutes=tear), '撤収', '撤収・原状回復・忘れ物確認',
                 '全員', '会場担当へ引き渡し'))
    rows.append((close_t + timedelta(minutes=tear), close_t + timedelta(minutes=tear + 15),
                 '撤収', '簡易振り返り（その場で3点）', '全員', '記憶が新しいうちに課題を口頭共有'))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--out', default='/mnt/user-data/outputs')
    ap.add_argument('--prefix', default='event')
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding='utf-8'))
    os.makedirs(a.out, exist_ok=True)
    rows = build(cfg)

    md = [f'# {cfg.get("イベント名", "")} 香盤表',
          f'\n開催日: {cfg.get("開催日", "")}　開場 {cfg["開場"]} / 終了 {cfg["終了"]}\n',
          '| 時刻 | 区分 | 内容 | 担当 | 備考 |', '|---|---|---|---|---|']
    for s, e, kind, name, who, note in rows:
        tm = s.strftime('%H:%M') if s == e else f'{s.strftime("%H:%M")}-{e.strftime("%H:%M")}'
        md.append(f'| {tm} | {kind} | {name} | {who} | {note} |')

    taitai = cfg.get('体制', [])
    md += ['', '## 役割分担', '', '| 役割 | 担当 | 連絡先 | 業務内容 |', '|---|---|---|---|']
    for r in taitai:
        md.append(f'| {r.get("役割","")} | {r.get("担当","")} | {r.get("連絡先","")} | {r.get("業務","")} |')

    assigned = {r.get('役割', '') for r in taitai}
    missing = [f'{k}（{v}）' for k, v in REQUIRED_ROLES.items() if k not in assigned]
    no_contact = [r.get('担当', '') for r in taitai if not str(r.get('連絡先', '')).strip()]
    md += ['', '## 確認事項', '']
    if missing:
        md.append('**未設定の必須役割**')
        md += [f'- {m}' for m in missing]
    else:
        md.append('- 必須役割はすべて割り当て済み')
    if no_contact:
        md.append(f'- 連絡先が未記入: {", ".join(x for x in no_contact if x)}。当日連絡が取れないと判断が止まる')
    md += ['- 緊急時の一次連絡先（会場管理・救急）を別途明記すること',
           '- 雨天・機材障害時の代替案を決裁者と共有済みか確認すること']

    mp = f'{a.out}/{a.prefix}_runsheet.md'
    open(mp, 'w', encoding='utf-8').write('\n'.join(md))
    cp = f'{a.out}/{a.prefix}_runsheet.csv'
    with open(cp, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['開始', '終了', '区分', '内容', '担当', '備考'])
        for s, e, kind, name, who, note in rows:
            w.writerow([s.strftime('%H:%M'), e.strftime('%H:%M'), kind, name, who, note])
    print(f'{len(rows)}行の香盤表を生成')
    if missing:
        print('未設定の必須役割:', ', '.join(m.split('（')[0] for m in missing))
    print(f'  {mp}\n  {cp}')


if __name__ == '__main__':
    main()
