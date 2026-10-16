#!/usr/bin/env python3
"""こどもステーション Ad Grants の週次・月次報告（Slack へ tell）。Mac mini で動かす。

  python3 ads_grants_report.py --weekly  --dry-run   # 送らずに本文を出す
  python3 ads_grants_report.py --monthly --dry-run
  python3 ads_grants_report.py --weekly              # cron はこれ（毎週月曜）
  python3 ads_grants_report.py --monthly             # cron はこれ（毎月1日）

材料    表「AdGrants_書き出し」＝Google広告スクリプト bin/ads_grants/export_script.js が毎朝書き直す
        （npo.station のドライブ・y_tam@vivid-global.com へ閲覧共有）。ID は ~/.vivid-relay/ads_grants_sheet_id.txt、
        無ければドライブを名前で探して控える
鍵      ~/.vivid-relay/google_token.json（sheets_client と同じ・y_tam@vivid-global.com）
心拍    ⚙️自動処理レジスタ「Ad Grants 週次・月次報告（ads_grants_report.py）」
★数字は表の値だけ。推測で埋めない（無いものは「—」）。報告に判断語を入れない（判断は ask_hub）
"""
import argparse
import datetime as dt
import os
import sys
from collections import defaultdict

RELAY = os.path.expanduser('~/.vivid-relay')
sys.path.insert(0, RELAY)
JST = dt.timezone(dt.timedelta(hours=9))
SHEET_NAME = 'AdGrants_書き出し'
ID_FILE = os.path.join(RELAY, 'ads_grants_sheet_id.txt')
PROC_NAME = 'Ad Grants 週次・月次報告（ads_grants_report.py）'   # ★⚙️自動処理レジスタの「処理名」と完全一致
CTR_LINE = 0.05          # Ad Grants の決まり：アカウント全体のクリック率 5%
STALE_HOURS = 48         # 書き出しがこれより古ければ止まっている
ADS_URL = 'https://ads.google.com/aw/campaigns?ocid=8589534196'


def sheet_id():
    if os.path.exists(ID_FILE):
        v = open(ID_FILE).read().strip()
        if v:
            return v
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    c = Credentials.from_authorized_user_file(os.path.join(RELAY, 'google_token.json'))
    q = "name = '%s' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false" % SHEET_NAME
    files = build('drive', 'v3', credentials=c).files().list(
        q=q, fields='files(id,name,owners(emailAddress))', supportsAllDrives=True,
        includeItemsFromAllDrives=True).execute().get('files', [])
    if len(files) != 1:
        raise RuntimeError('表「%s」が %d 件見つかった（1件のはず）' % (SHEET_NAME, len(files)))
    with open(ID_FILE, 'w') as fp:
        fp.write(files[0]['id'])
    return files[0]['id']


def table(sh, fid, tab):
    rows = sh.read(fid, tab)
    if not rows:
        return []
    head = rows[0]
    return [dict(zip(head, r + [''] * (len(head) - len(r)))) for r in rows[1:]]


def n(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def day(s):
    return dt.date.fromisoformat(str(s)[:10])


def sum_by_campaign(rows, start, end):
    out = defaultdict(lambda: {'impressions': 0, 'clicks': 0, 'conversions': 0})
    for r in rows:
        d = day(r['date'])
        if start <= d <= end:
            o = out[r['campaign']]
            for k in o:
                o[k] += n(r[k])
    return out


def ctr(imp, clk):
    return clk / imp if imp else None


def pct(v):
    return '—' if v is None else '%.1f%%' % (v * 100)


def build(kind, today, data):
    camp, conv, terms, kws, meta = data
    if kind == 'weekly':
        end = today - dt.timedelta(days=1)
        start = end - dt.timedelta(days=6)
        pstart, pend = start - dt.timedelta(days=7), start - dt.timedelta(days=1)
        label = '週次'
    else:
        end = today.replace(day=1) - dt.timedelta(days=1)
        start = end.replace(day=1)
        pend = start - dt.timedelta(days=1)
        pstart = pend.replace(day=1)
        label = '月次（%d月）' % start.month
    cur = sum_by_campaign(camp, start, end)
    prev = sum_by_campaign(camp, pstart, pend)
    lines = ['期間 %s〜%s（比べる相手 %s〜%s）' % (start, end, pstart, pend), '']

    # キャンペーン別
    tot = {'impressions': 0, 'clicks': 0, 'conversions': 0}
    ptot = {'impressions': 0, 'clicks': 0, 'conversions': 0}
    names = sorted(set(cur) | set(prev))
    lines.append('■ キャンペーン別（表示／クリック／クリック率／成果）')
    for c in names:
        a, b = cur.get(c, {}), prev.get(c, {})
        for k in tot:
            tot[k] += a.get(k, 0)
            ptot[k] += b.get(k, 0)
        lines.append('・%s：%s／%s／%s／%s %s' % (
            c, '{:,.0f}'.format(a.get('impressions', 0)), '{:,.0f}'.format(a.get('clicks', 0)),
            pct(ctr(a.get('impressions', 0), a.get('clicks', 0))), '{:,.0f}'.format(a.get('conversions', 0)),
            '（前の期間のクリック %s）' % '{:,.0f}'.format(b['clicks']) if b.get('clicks') else ''))
    acc = ctr(tot['impressions'], tot['clicks'])
    if not tot['impressions']:
        lines.append('・🔴 この期間、広告は1回も表示されていない')
    lines.append('・合計：表示 %s／クリック %s／クリック率 %s／成果 %s（前の期間：表示 %s・クリック %s）' % (
        '{:,.0f}'.format(tot['impressions']), '{:,.0f}'.format(tot['clicks']), pct(acc),
        '{:,.0f}'.format(tot['conversions']), '{:,.0f}'.format(ptot['impressions']), '{:,.0f}'.format(ptot['clicks'])))
    lines.append('')

    # Ad Grants の決まり（クリック率5%）＝月の初めからの累計で見る
    mstart = end.replace(day=1)
    mt = sum_by_campaign(camp, mstart, end)
    mi = sum(v['impressions'] for v in mt.values())
    mc = sum(v['clicks'] for v in mt.values())
    mctr = ctr(mi, mc)
    mark = '—' if mctr is None else ('✅' if mctr >= CTR_LINE else '🔴')
    lines.append('■ Ad Grants の決まり：アカウント全体のクリック率 5%以上')
    lines.append('・%s %d月1日〜%s の累計 %s（表示 %s・クリック %s）' % (
        mark, end.month, end, pct(mctr), '{:,.0f}'.format(mi), '{:,.0f}'.format(mc)))
    lines.append('')

    # 成果の内訳
    by_act = defaultdict(float)
    for r in conv:
        if start <= day(r['date']) <= end:
            by_act[r['action']] += n(r['conversions'])
    lines.append('■ 成果の内訳（電話・LINE・お問い合わせの押下）')
    if any(by_act.values()):
        for a, v in sorted(by_act.items(), key=lambda x: -x[1]):
            if v:
                lines.append('・%s：%s' % (a, '{:,.0f}'.format(v)))
    else:
        lines.append('・この期間は0件')
    lines.append('')

    # 検索語
    agg = defaultdict(lambda: [0, 0])
    for r in terms:
        if start <= day(r['date']) <= end:
            k = (r['campaign'], r['search_term'])
            agg[k][0] += n(r['impressions'])
            agg[k][1] += n(r['clicks'])
    top = sorted(agg.items(), key=lambda x: (-x[1][1], -x[1][0]))[:10 if kind == 'weekly' else 20]
    lines.append('■ 表示された検索語（クリックの多い順・上位%d）' % len(top))
    if top:
        for (c, t), (i, k) in top:
            lines.append('・「%s」 表示 %s・クリック %s（%s）' % (t, '{:,.0f}'.format(i), '{:,.0f}'.format(k), c))
    else:
        lines.append('・この期間は記録なし')
    lines.append('')

    # 品質スコア（Ad Grants は 1〜2 のキーワードを置かない決まり）
    low = [r for r in kws if str(r.get('quality_score', '')).strip() not in ('', '0') and n(r['quality_score']) <= 2]
    unk = [r for r in kws if str(r.get('quality_score', '')).strip() in ('', '0')]
    lines.append('■ キーワードの品質スコア（全%d語）' % len(kws))
    lines.append('・1〜2 のもの：%d語%s' % (len(low), '' if not low else '（' + '、'.join(
        '%s／%s' % (r['keyword'], r['ad_group']) for r in low) + '）'))
    lines.append('・まだ点が付いていないもの：%d語' % len(unk))
    lines.append('')
    lines.append('書き出しの最終更新 %s ／ Google広告 %s' % (meta.get('updated_at', '—'), ADS_URL))
    summary = '%s：表示 %s・クリック %s・クリック率 %s・成果 %s' % (
        label, '{:,.0f}'.format(tot['impressions']), '{:,.0f}'.format(tot['clicks']), pct(acc),
        '{:,.0f}'.format(tot['conversions']))
    return 'こどもステーション Ad Grants %s' % label, '\n'.join(lines), summary


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--weekly', action='store_true')
    g.add_argument('--monthly', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--today', help='試験用 YYYY-MM-DD')
    a = ap.parse_args()
    kind = 'weekly' if a.weekly else 'monthly'
    today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.now(JST).date()
    ok, msg = False, ''
    try:
        from sheets_client import Sheets
        sh = Sheets()
        fid = sheet_id()
        meta = {r['key']: r['value'] for r in table(sh, fid, 'meta')}
        data = (table(sh, fid, 'campaign_daily'), table(sh, fid, 'conversions'),
                table(sh, fid, 'search_terms'), table(sh, fid, 'keywords'), meta)
        title, body, summary = build(kind, today, data)
        upd = meta.get('updated_at', '')
        stale = True
        if upd:
            t = dt.datetime.fromisoformat(str(upd)).replace(tzinfo=JST)
            stale = (dt.datetime.now(JST) - t).total_seconds() > STALE_HOURS * 3600
        if stale and not a.today:
            body = '🔴 広告の書き出しが %s から更新されていない（Google広告のスクリプト「AdGrants 書き出し」）\n\n' % (upd or '—') + body
        if a.dry_run:
            print(title)
            print(summary)
            print(body)
        else:
            from notify import tell
            tell(title, body, summary='返信は要りません。' + summary)
        ok = not stale or bool(a.today)
        msg = summary if ok else '書き出しが古い（%s）' % upd
    except Exception as e:  # noqa: BLE001 ― 失敗も心拍で残す
        msg = '%s: %s' % (type(e).__name__, e)
        print(msg, file=sys.stderr)
    if not a.dry_run:
        try:
            from heartbeat import beat
            beat(PROC_NAME, '成功' if ok else '失敗', msg)
        except Exception as e:  # noqa: BLE001
            print('心拍を打てなかった: %s' % e, file=sys.stderr)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
