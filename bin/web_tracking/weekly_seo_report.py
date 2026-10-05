#!/usr/bin/env python3
"""SEO週次メール（Search Console 全サイト＋Clarity＋計測タグ点検）を1通にまとめて送る。Mac mini で動かす。

  python3 weekly_seo_report.py --dry-run          # 送らずに HTML を ~/.vivid-relay/weekly_seo_report.html へ
  python3 weekly_seo_report.py --to y_tam@...     # 指定先へ送る（試し送り）
  python3 weekly_seo_report.py                    # 既定の宛先へ送る（cron はこれ）

期間        Search Console は反映に2〜3日かかるため「3日前までの7日間」を今週、その前の7日間を先週とする
            Clarity は日次シートに貯まった直近7日分（貯まっていない日数は表示で断る）
材料        台帳 sites.json（gsc.property / gsc.page_contains / clarity）
            Google 鍵 ~/.vivid-relay/google_token_seo.json（webmasters.readonly＋gmail.send・シート用とは別）
            Clarity 日次シート ~/.vivid-relay/clarity_sheet_id.txt（clarity_daily.py が毎日追記）
心拍        ~/.vivid-relay/weekly_seo_report.last
★数字は API とシートの値だけ。推測で埋めない（無いものは「—」）
"""
import base64
import datetime as dt
import html
import json
import os
import sys
import warnings
from email.mime.text import MIMEText

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
RELAY = os.path.expanduser('~/.vivid-relay')
sys.path.insert(0, RELAY)
sys.path.insert(0, HERE)
JST = dt.timezone(dt.timedelta(hours=9))
TO_DEFAULT = 'y_tam@vivid-global.com'
OUT_HTML = os.path.join(RELAY, 'weekly_seo_report.html')
HEARTBEAT = os.path.join(RELAY, 'weekly_seo_report.last')


def creds():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    p = os.path.join(RELAY, 'google_token_seo.json')
    c = Credentials.from_authorized_user_file(p)
    if not c.valid:
        c.refresh(Request())          # ★無人実行で対話認証に落とさない（失敗したら例外で止まる）
        open(p, 'w').write(c.to_json())
    return c


def svc(name, ver):
    from googleapiclient.discovery import build
    return build(name, ver, credentials=creds(), cache_discovery=False)


# ── Search Console ─────────────────────────────────────────────
def gsc_query(sc, prop, start, end, dims=None, page_contains=None, limit=25):
    body = {'startDate': start, 'endDate': end, 'rowLimit': limit, 'dataState': 'all'}
    if dims:
        body['dimensions'] = dims
    if page_contains:
        body['dimensionFilterGroups'] = [{'filters': [
            {'dimension': 'page', 'operator': 'contains', 'expression': page_contains}]}]
    return sc.searchanalytics().query(siteUrl=prop, body=body).execute().get('rows', [])


def gsc_site(sc, g, cur, prev):
    prop, pc = g['property'], g.get('page_contains')
    out = {}
    for key, (s, e) in (('cur', cur), ('prev', prev)):
        rows = gsc_query(sc, prop, s, e, page_contains=pc, limit=1)
        r = rows[0] if rows else {}
        out[key] = {'clicks': r.get('clicks', 0), 'impressions': r.get('impressions', 0),
                    'ctr': r.get('ctr', 0) * 100, 'position': r.get('position', 0)}
    q = gsc_query(sc, prop, cur[0], cur[1], ['query'], pc, 50)
    # 伸びしろ＝表示はあるが順位が8位より下（1ページ目の下〜2ページ目）
    out['chance'] = sorted([r for r in q if r.get('position', 0) > 8 and r.get('impressions', 0) >= 3],
                           key=lambda r: -r['impressions'])[:5]
    out['top'] = sorted(q, key=lambda r: -r.get('clicks', 0))[:5]
    return out


# ── Clarity（日次シートから） ─────────────────────────────────
def clarity_rows():
    from sheets_client import Sheets
    sid = open(os.path.join(RELAY, 'clarity_sheet_id.txt')).read().strip()
    rows = Sheets().read(sid, 'clarity_daily')
    return rows[1:] if rows else []


def clarity_site(rows, site_name, days):
    tot = [r for r in rows if r[1] == site_name and r[3] == '全体' and r[0] in days]
    got_days = sorted({r[0] for r in tot})
    def val(metric, field):
        return [(r[0], float(r[7])) for r in tot if r[5] == metric and r[6] == field]
    sess_by_day = dict(val('Traffic', 'totalSessionCount'))
    sessions = sum(sess_by_day.values())
    def rate(metric):           # セッションの何%で起きたか（日ごとのセッション数で重み付け）
        num = sum(sess_by_day.get(d, 0) * p / 100 for d, p in val(metric, 'sessionsWithMetricPercentage'))
        return (num / sessions * 100) if sessions else None
    sd = val('ScrollDepth', 'averageScrollDepth')
    scroll = (sum(sess_by_day.get(d, 0) * v for d, v in sd) / sessions) if sessions and sd else None
    pages = {}
    for r in rows:
        if r[1] == site_name and r[3] == 'URL別' and r[0] in days and r[6] == 'subTotal' \
                and r[5] in ('DeadClickCount', 'RageClickCount', 'QuickbackClick'):
            pages[r[4]] = pages.get(r[4], 0) + float(r[7])
    worst = sorted([(u, n) for u, n in pages.items() if n > 0], key=lambda x: -x[1])[:3]
    return {'days': got_days, 'sessions': sessions, 'dead': rate('DeadClickCount'),
            'rage': rate('RageClickCount'), 'quickback': rate('QuickbackClick'),
            'scroll': scroll, 'worst': worst}


# ── 表示 ─────────────────────────────────────────────────────
def pct(cur, prev):
    if not prev:
        return '<span style="color:#888">（先週0）</span>' if cur else ''
    d = (cur - prev) / prev * 100
    col = '#1e7a4c' if d > 0 else ('#b3261e' if d < 0 else '#888')
    return '<span style="color:%s">%+.0f%%</span>' % (col, d)


def f(v, fmt='{:,.0f}', none='—'):
    return none if v is None else fmt.format(v)


def build(data, cur, prev, cdays, tags):
    e = html.escape
    css = ('font-family:-apple-system,Hiragino Sans,Meiryo,sans-serif;color:#2b211a;'
           'max-width:760px;margin:0 auto;padding:16px;line-height:1.6')
    th = 'style="text-align:left;border-bottom:2px solid #e8740c;padding:6px 8px;font-size:12px;color:#7a6a5c"'
    td = 'style="border-bottom:1px solid #f0e1cf;padding:6px 8px;font-size:13px;vertical-align:top"'
    h = ['<div style="%s">' % css,
         '<h2 style="margin:0 0 4px;color:#e8740c">ふくち。グループ SEO週次レポート</h2>',
         '<div style="font-size:12px;color:#7a6a5c">検索（Search Console）%s〜%s（先週 %s〜%s）／'
         'Clarity 直近%d日（%s）</div>' % (cur[0], cur[1], prev[0], prev[1], 7,
                                         '貯まっているのは %d日分' % len(cdays) if len(cdays) < 7 else '7日分そろい'),
         '<h3 style="margin:20px 0 6px">① 全サイト一覧</h3>',
         '<table style="border-collapse:collapse;width:100%%"><tr>'
         '<th %s>サイト</th><th %s>検索の表示</th><th %s>クリック</th><th %s>順位</th>'
         '<th %s>訪問（Clarity）</th><th %s>デッド／怒り／すぐ戻る</th><th %s>読了の深さ</th></tr>'
         % ((th,) * 7)]
    for d in data:
        g, c = d.get('gsc'), d.get('clarity')
        gs = ('%s %s' % (f(g['cur']['impressions']), pct(g['cur']['impressions'], g['prev']['impressions'])),
              '%s %s' % (f(g['cur']['clicks']), pct(g['cur']['clicks'], g['prev']['clicks'])),
              f(g['cur']['position'] or None, '{:.1f}')) if g and 'cur' in g else ('—', '—', '—')
        cs = (f(c['sessions']),
              '%s／%s／%s' % (f(c['dead'], '{:.0f}%'), f(c['rage'], '{:.0f}%'), f(c['quickback'], '{:.0f}%')),
              f(c['scroll'], '{:.0f}%')) if c and c['sessions'] else ('—', '—', '—')
        h.append('<tr><td %s><b>%s</b><br><span style="font-size:11px;color:#7a6a5c">%s</span></td>'
                 % (td, e(d['name']), e(d['domain'])) + ''.join('<td %s>%s</td>' % (td, x) for x in gs + cs) + '</tr>')
    h.append('</table><div style="font-size:11px;color:#7a6a5c;margin-top:4px">'
             'デッド＝押しても反応しない所を押した訪問の割合／怒り＝同じ所を連打した割合／すぐ戻る＝開いてすぐ戻った割合。'
             '読了の深さ＝ページの何%までスクロールしたか（平均）</div>')
    h.append('<h3 style="margin:24px 0 6px">② サイト別</h3>')
    for d in data:
        g, c = d.get('gsc'), d.get('clarity')
        h.append('<div style="border:1px solid #f0e1cf;border-radius:8px;padding:10px 12px;margin:10px 0">'
                 '<b>%s</b> <span style="font-size:12px;color:#7a6a5c">%s</span>' % (e(d['name']), e(d['domain'])))
        if g and g.get('error'):
            h.append('<div style="font-size:12px;color:#b3261e">検索データ取得エラー：%s</div>' % e(g['error']))
        if g and g.get('chance'):
            h.append('<div style="font-size:12px;margin-top:6px"><b>伸びしろの検索語</b>（表示はあるが9位以下）：' +
                     '、'.join('%s（表示%d・%.0f位）' % (e(r['keys'][0]), r['impressions'], r['position'])
                              for r in g['chance']) + '</div>')
        if c and c['worst']:
            h.append('<div style="font-size:12px;margin-top:4px"><b>引っかかりの多いページ</b>：' +
                     '、'.join('%s（%d回）' % (e(u.replace('https://', '')[:60]), n) for u, n in c['worst']) + '</div>')
        if d.get('clarity_id'):
            h.append('<div style="font-size:12px;margin-top:4px"><a href="https://clarity.microsoft.com/projects/view/%s/heatmaps">'
                     'ヒートマップを開く</a>　<a href="https://clarity.microsoft.com/projects/view/%s/recordings">録画を開く</a></div>'
                     % (d['clarity_id'], d['clarity_id']))
        h.append('</div>')
    h.append('<h3 style="margin:24px 0 6px">③ 計測タグの点検</h3><div style="font-size:13px">')
    for name, st in tags:
        h.append('%s　%s<br>' % (e(st), e(name)))
    h.append('</div><div style="font-size:11px;color:#7a6a5c;margin-top:20px">'
             'Mac mini の weekly_seo_report.py が自動で作成。数字は Search Console と Clarity の値のみ（推測で埋めていない）。</div></div>')
    return '\n'.join(h)


def send(to, subject, body_html):
    msg = MIMEText(body_html, 'html', 'utf-8')
    msg['To'], msg['Subject'] = to, subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return svc('gmail', 'v1').users().messages().send(userId='me', body={'raw': raw}).execute()


def main():
    today = dt.datetime.now(JST).date()
    end = today - dt.timedelta(days=3)
    cur = ((end - dt.timedelta(days=6)).isoformat(), end.isoformat())
    prev = ((end - dt.timedelta(days=13)).isoformat(), (end - dt.timedelta(days=7)).isoformat())
    cdays = {(today - dt.timedelta(days=i)).isoformat() for i in range(1, 8)}
    sites = json.load(open(os.path.join(HERE, 'sites.json'), encoding='utf-8'))['sites']
    sc = svc('webmasters', 'v3')
    try:
        crows = clarity_rows()
    except Exception as ex:
        crows = []
        sys.stderr.write('Clarityシート読み取り失敗：%s\n' % ex)
    got_cdays = sorted({r[0] for r in crows if r[0] in cdays})
    import site_audit
    data, tags = [], []
    for s in sites:
        if not s.get('gsc') and not s.get('clarity'):
            continue
        d = {'name': s['name'], 'domain': s['url'].split('/')[2]}
        cid = s.get('clarity', '')
        if cid.isalnum():
            d['clarity_id'] = cid
            d['clarity'] = clarity_site(crows, s['name'], cdays)
        if s.get('gsc'):
            try:
                d['gsc'] = gsc_site(sc, s['gsc'], cur, prev)
            except Exception as ex:
                d['gsc'] = {'error': str(ex)[:160]}
        if s.get('noindex_expected'):
            continue        # 検索対象外のLPは一覧に載せない
        data.append(d)
        try:
            a = site_audit.audit(s)
            tags.append((s['name'], a.get('clarity', '—')))
        except Exception as ex:
            tags.append((s['name'], '✗ 点検失敗 %s' % str(ex)[:60]))
    body = build(data, cur, prev, got_cdays, tags)
    open(OUT_HTML, 'w', encoding='utf-8').write(body)
    subject = 'ふくち。グループ SEO週次レポート（%s〜%s）' % (cur[0][5:].replace('-', '/'), cur[1][5:].replace('-', '/'))
    if '--dry-run' in sys.argv:
        print('dry-run：%s（%dサイト・送っていない）' % (OUT_HTML, len(data)))
        return
    to = sys.argv[sys.argv.index('--to') + 1] if '--to' in sys.argv else TO_DEFAULT
    r = send(to, subject, body)
    msg = 'OK 送信 %s id=%s %dサイト' % (to, r.get('id'), len(data))
    open(HEARTBEAT, 'w').write('%s %s\n' % (dt.datetime.now(JST).isoformat(timespec='seconds'), msg))
    print(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        open(HEARTBEAT, 'w').write('%s NG %s\n' % (dt.datetime.now(JST).isoformat(timespec='seconds'), str(ex)[:200]))
        raise
