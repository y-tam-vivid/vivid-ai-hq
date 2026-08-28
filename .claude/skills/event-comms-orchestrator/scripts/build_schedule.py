#!/usr/bin/env python3
"""
build_schedule.py - イベント開催日から配信カレンダーを逆算生成する

使い方:
  python3 build_schedule.py --name "◯◯フェア" \
    --start 2026-09-12 --end 2026-09-13 \
    --open 10:00 --close 17:00 \
    --accounts "個人,主催公式" --press --media-invite \
    --out /mnt/user-data/outputs --prefix fair2609

出力:
  <prefix>_schedule.md   … 人が読む配信計画表
  <prefix>_schedule.csv  … Notion インポート用（日付/フェーズ/媒体/タスク/状態）

設計方針:
  - プレスは早く、SNSは直前。媒体ごとにリードタイムが逆なので逆算で並べる
  - プレス配信日は火・水・木の午前に寄せる（メディアの閲覧習慣に合わせる）
  - 土日は自動回避するが、祝日データは持たないので人が最終確認する
"""
import argparse, csv, os
from datetime import date, datetime, timedelta

WD = ['月', '火', '水', '木', '金', '土', '日']
PRESS_OK = (1, 2, 3)  # 火・水・木


def parse_d(s):
    return datetime.strptime(s, '%Y-%m-%d').date()


def fmt(d):
    return f'{d.strftime("%Y-%m-%d")}（{WD[d.weekday()]}）'


def shift_to_press_day(d, earliest):
    """火・水・木に寄せる。earliest より前には出さない（前倒し優先、無理なら後ろ倒し）"""
    for delta in range(0, 7):
        c = d - timedelta(days=delta)
        if c.weekday() in PRESS_OK and c >= earliest:
            return c
    for delta in range(1, 7):
        c = d + timedelta(days=delta)
        if c.weekday() in PRESS_OK:
            return c
    return d


def avoid_weekend(d):
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def day_timeline(start, open_t, close_t, accounts, label='当日'):
    """開催時間を按分して当日の配信枠を作る"""
    o = datetime.strptime(open_t, '%H:%M')
    c = datetime.strptime(close_t, '%H:%M')
    span = (c - o).total_seconds() / 3600
    acc = accounts[0] if accounts else '公式'
    slots = [
        (-1.0, 'ストーリー', '開催告知＋カウントダウンスタンプ（開場時刻にセット）'),
        (0.0, 'ストーリー', '開場の瞬間・設営完了'),
        (span * 0.25, 'ストーリー', '参加者の手元・制作中の様子'),
        (span * 0.45, 'フィード', '当日の様子（本日分の本投稿）'),
        (span * 0.55, 'ストーリー', '混雑状況の実況（来場判断に最も効く枠）'),
        (span * 0.68, 'ストーリー', '成果物・ビフォーアフター'),
        (span - 1.25, 'ストーリー', 'ラストコール'),
        (span + 0.3, 'ストーリー', '御礼＋ハイライト保存'),
    ]
    rows = []
    for off, media, task in slots:
        t = (o + timedelta(hours=off)).strftime('%H:%M')
        rows.append((start, t, label, media, task, acc))
    return rows


def build(a):
    start, end = parse_d(a.start), parse_d(a.end or a.start)
    today = date.today()
    accounts = [s.strip() for s in a.accounts.split(',') if s.strip()]
    acc_all = ' / '.join(accounts) if accounts else '公式'
    rows = []  # (日付, 時刻, フェーズ, 媒体, タスク, 担当アカウント)

    def add(d, t, phase, media, task, acc=''):
        rows.append((d, t, phase, media, task, acc or acc_all))

    # ---- 事前フェーズ ----
    if a.media_invite:
        d = shift_to_press_day(start - timedelta(days=30), today)
        add(d, '10:00', '事前', 'メディア', 'メディア招致案内を記者へ送付（取材枠の確保には1か月前が目安）')
    d = avoid_weekend(start - timedelta(days=21))
    add(d, '', '事前', '準備', 'プレス用素材を準備：メイン画像候補3案以上、登壇者・実施概要の確定')
    if a.press:
        d = shift_to_press_day(start - timedelta(days=14), today)
        add(d, '10:00', '事前', 'プレスリリース', 'PR TIMES配信（一般告知。イベントは2週間以上前が目安）')
    d = avoid_weekend(start - timedelta(days=10))
    add(d, '', '事前', 'フィード', '告知投稿1本目：開催概要・参加方法')
    d = avoid_weekend(start - timedelta(days=7))
    add(d, '', '事前', 'フィード＋ストーリー', '告知投稿2本目：見どころ・前回実績。ストーリーで補足')
    if a.media_invite:
        d = avoid_weekend(start - timedelta(days=3))
        add(d, '', '事前', 'メディア', '記者へリマインド連絡（取材予定の最終確認）')
    add(start - timedelta(days=1), '', '事前', 'ストーリー', '前日告知＋当日の運用素材・機材の最終確認')

    # ---- 当日フェーズ（会期分ループ）----
    cur, n_days, i = start, (end - start).days + 1, 1
    while cur <= end:
        label = '当日' if n_days == 1 else f'当日{i}日目'
        for r in day_timeline(cur, a.open, a.close, accounts, label):
            rows.append(r)
        cur += timedelta(days=1); i += 1

    # ---- 事後フェーズ ----
    add(end + timedelta(days=1), '', '事後', 'フィード', '実施報告投稿：来場実績・印象的だった場面')
    add(end + timedelta(days=3), '', '事後', 'リール', '会期総集編リールを投稿。ハイライトへ保存')
    if a.press:
        d = shift_to_press_day(end + timedelta(days=7), end + timedelta(days=1))
        add(d, '10:00', '事後', 'プレスリリース', 'PR TIMES配信（実施報告。来場数など数値が固まってから）')
    add(end + timedelta(days=7), '', '事後', '振り返り', '各投稿のリーチ・保存数を記録し、次回の配信設計に反映')

    rows.sort(key=lambda r: (r[0], r[1] or '00:00'))
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--name', required=True)
    p.add_argument('--start', required=True, help='開催初日 YYYY-MM-DD')
    p.add_argument('--end', default=None, help='最終日。単日なら省略可')
    p.add_argument('--open', default='10:00')
    p.add_argument('--close', default='17:00')
    p.add_argument('--accounts', default='公式', help='カンマ区切り')
    p.add_argument('--press', action='store_true', help='プレスリリースを配信する')
    p.add_argument('--media-invite', action='store_true', help='メディア招致を行う')
    p.add_argument('--out', default='/mnt/user-data/outputs')
    p.add_argument('--prefix', default='event')
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = build(a)
    start = parse_d(a.start)

    md = [f'# {a.name} 配信カレンダー', '',
          f'会期: {fmt(start)}' + (f' 〜 {fmt(parse_d(a.end))}' if a.end and a.end != a.start else ''),
          f'開催時間: {a.open} - {a.close}', '',
          '| 日付 | 時刻 | フェーズ | 媒体 | タスク | 担当 |',
          '|---|---|---|---|---|---|']
    end_d = parse_d(a.end) if a.end else start
    for d, t, ph, me, ta, ac in rows:
        if d < start:
            rel_s = f'D{(d - start).days}'
        elif d <= end_d:
            rel_s = 'D-Day' if d == start else f'D-Day+{(d - start).days}'
        else:
            rel_s = f'終了+{(d - end_d).days}日'
        md.append(f'| {fmt(d)} {rel_s} | {t or "-"} | {ph} | {me} | {ta} | {ac} |')
    md += ['', '> D表記は開催初日基準。祝日は判定していない。プレス配信日が祝日に当たらないか目視で確認すること。',
           '> 各タスクの実制作は event-social-kit / event-press-kit / event-report-kit に委譲する。']

    mp = f'{a.out}/{a.prefix}_schedule.md'
    open(mp, 'w').write('\n'.join(md))
    cp = f'{a.out}/{a.prefix}_schedule.csv'
    with open(cp, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['日付', '時刻', 'フェーズ', '媒体', 'タスク', '担当アカウント', '状態'])
        for d, t, ph, me, ta, ac in rows:
            w.writerow([d.isoformat(), t, ph, me, ta, ac, '未着手'])
    print(f'{len(rows)}件のタスクを生成')
    print(f'  {mp}\n  {cp}')


if __name__ == '__main__':
    main()
