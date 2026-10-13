#!/usr/bin/env python3
"""MEO（Googleビジネスプロフィール）の週次の数字。weekly_seo_report.py から呼ぶ。Mac mini で動かす。

★2026-10-13 有璽氏「MEOの数字を毎週のSEOレポートに入れて」
鍵      ~/.vivid-relay/google_token_gbp.json（business.manage だけ・シート用/SEO用とは別。許可の道具 oauth_gbp.py）
読むだけ 店舗情報は書き換えない（住所などの修正は有璽氏の承認を取ってから別に行う）
期間    Search Console と同じ「今週／先週」の7日間（実績の反映に数日かかるため）
★数字は API の値だけ。取れなかったものは None（表示は「—」）

  python3 gbp_weekly.py      # 単体で今週の数字を出して確かめる
"""
import datetime as dt
import os
import warnings

warnings.filterwarnings('ignore')
RELAY = os.path.expanduser('~/.vivid-relay')
TOKEN = os.path.join(RELAY, 'google_token_gbp.json')
ACCOUNT = 'accounts/100503061612855623838'      # 田村有璽（yuji）の個人アカウント＝3法人のプロフィールが入っている
# sites.json の name → プロフィールの店舗ID（★三ツ星咖哩は対象外）
LOCATIONS = {
    '株式会社ILIFE / LIFE STAND UP': '13251415499376587425',
    'オレンジワークス藤井寺': '6456992888466241688',
    'NPO法人 南河内こどもステーション': '3337679468125437882',
}
IMPRESSIONS = ('BUSINESS_IMPRESSIONS_DESKTOP_MAPS', 'BUSINESS_IMPRESSIONS_MOBILE_MAPS',
               'BUSINESS_IMPRESSIONS_DESKTOP_SEARCH', 'BUSINESS_IMPRESSIONS_MOBILE_SEARCH')
ACTIONS = ('BUSINESS_DIRECTION_REQUESTS', 'WEBSITE_CLICKS', 'CALL_CLICKS')
SHEET_TAB = 'meo_weekly'
SHEET_HEADER = ['週の初日', '週の末日', 'サイト', 'マップでの表示', '検索での表示', '経路検索', 'サイトへのクリック',
                '電話のクリック', '先週の表示合計', 'クチコミ総数', '平均評価', '今週の新しいクチコミ', '未返信のクチコミ', '記録時刻']


def session():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request, AuthorizedSession
    c = Credentials.from_authorized_user_file(TOKEN)
    if not c.valid:
        c.refresh(Request())          # ★無人実行で対話認証に落とさない（失敗したら例外）
        open(TOKEN, 'w').write(c.to_json())
    return AuthorizedSession(c)


def _ymd(prefix, iso):
    y, m, d = (int(x) for x in iso.split('-'))
    return [('%s.year' % prefix, y), ('%s.month' % prefix, m), ('%s.day' % prefix, d)]


def metrics(s, lid, start, end):
    params = [('dailyMetrics', m) for m in IMPRESSIONS + ACTIONS]
    params += _ymd('dailyRange.startDate', start) + _ymd('dailyRange.endDate', end)
    r = s.get('https://businessprofileperformance.googleapis.com/v1/locations/%s:fetchMultiDailyMetricsTimeSeries' % lid,
              params=params, timeout=60)
    r.raise_for_status()
    tot = {}
    for m in r.json().get('multiDailyMetricTimeSeries', []):
        for t in m.get('dailyMetricTimeSeries', []):
            tot[t['dailyMetric']] = sum(int(v.get('value', 0)) for v in t.get('timeSeries', {}).get('datedValues', []))
    return {'maps': tot.get('BUSINESS_IMPRESSIONS_DESKTOP_MAPS', 0) + tot.get('BUSINESS_IMPRESSIONS_MOBILE_MAPS', 0),
            'search': tot.get('BUSINESS_IMPRESSIONS_DESKTOP_SEARCH', 0) + tot.get('BUSINESS_IMPRESSIONS_MOBILE_SEARCH', 0),
            'directions': tot.get('BUSINESS_DIRECTION_REQUESTS', 0), 'website': tot.get('WEBSITE_CLICKS', 0),
            'calls': tot.get('CALL_CLICKS', 0)}


def reviews(s, lid, start, end):
    """クチコミの総数・平均・期間中の新着・未返信（★返信は人がする。ここは数えるだけ）"""
    out, items, token = {}, [], None
    for _ in range(10):
        p = {'pageSize': 50}
        if token:
            p['pageToken'] = token
        r = s.get('https://mybusiness.googleapis.com/v4/%s/locations/%s/reviews' % (ACCOUNT, lid), params=p, timeout=60)
        r.raise_for_status()
        j = r.json()
        out.setdefault('total', j.get('totalReviewCount', 0))
        out.setdefault('avg', j.get('averageRating'))
        items += j.get('reviews', [])
        token = j.get('nextPageToken')
        if not token:
            break
    out['new'] = sum(1 for v in items if start <= v.get('createTime', '')[:10] <= end)
    out['unreplied'] = sum(1 for v in items if not v.get('reviewReply'))
    return out


def collect(cur, prev):
    """{サイト名: {'cur':…, 'prev':…, 'reviews':…} or {'error': …}} を返す"""
    res = {}
    try:
        s = session()
    except Exception as ex:
        return {n: {'error': '鍵を読めない：%s' % str(ex)[:120]} for n in LOCATIONS}
    for name, lid in LOCATIONS.items():
        d = {}
        try:
            d['cur'] = metrics(s, lid, *cur)
            d['prev'] = metrics(s, lid, *prev)
        except Exception as ex:
            d['error'] = '実績を取れない：%s' % str(ex)[:120]
        try:
            d['reviews'] = reviews(s, lid, *cur)
        except Exception as ex:
            d['error'] = (d.get('error', '') + '／クチコミを取れない：%s' % str(ex)[:120]).lstrip('／')
        res[name] = d
    return res


def build_html(meo, pct, f):
    """週次メールに差し込む表（pct・f は weekly_seo_report の表示関数を受け取る）"""
    import html
    th = 'style="text-align:left;border-bottom:2px solid #e8740c;padding:6px 8px;font-size:12px;color:#7a6a5c"'
    td = 'style="border-bottom:1px solid #f0e1cf;padding:6px 8px;font-size:13px;vertical-align:top"'
    h = ['<h3 style="margin:24px 0 6px">①-2 MEO：Googleマップ・検索での店舗の見え方</h3>',
         '<table style="border-collapse:collapse;width:100%%"><tr><th %s>店舗</th><th %s>マップでの表示</th>'
         '<th %s>検索での表示</th><th %s>経路検索</th><th %s>サイトへ</th><th %s>電話</th><th %s>クチコミ</th></tr>' % ((th,) * 7)]
    for name, d in meo.items():
        if d.get('error') and 'cur' not in d:
            h.append('<tr><td %s><b>%s</b></td><td %s colspan="6" style="color:#b3261e">%s</td></tr>'
                     % (td, html.escape(name), td, html.escape(d['error'])))
            continue
        c, p, r = d.get('cur', {}), d.get('prev', {}), d.get('reviews') or {}
        cell = lambda k: '%s %s' % (f(c.get(k)), pct(c.get(k, 0), p.get(k, 0))) if c else '—'
        rv = ('%s件・平均%s<br><span style="font-size:11px;color:#7a6a5c">今週の新着 %s／未返信 %s</span>'
              % (f(r.get('total')), f(r.get('avg'), '{:.1f}'), f(r.get('new')), f(r.get('unreplied')))) if r else '—'
        h.append('<tr><td %s><b>%s</b></td>' % (td, html.escape(name)) +
                 ''.join('<td %s>%s</td>' % (td, cell(k)) for k in ('maps', 'search', 'directions', 'website', 'calls')) +
                 '<td %s>%s</td></tr>' % (td, rv))
    h.append('</table><div style="font-size:11px;color:#7a6a5c;margin-top:4px">Googleビジネスプロフィールの実績（パソコン＋スマホの合計）。'
             '増減は先週比。未返信のクチコミは、返信すると評価と表示順位に効きやすい（返信は人が行う）。</div>')
    return '\n'.join(h)


def record(meo, cur):
    """1週×1店舗＝1行で Clarity と同じシートの meo_weekly タブへ積む。同じ週は積まない"""
    from sheets_client import Sheets
    sh = Sheets()
    sid = open(os.path.join(RELAY, 'clarity_sheet_id.txt')).read().strip()
    titles = [x['properties']['title'] for x in sh.svc.spreadsheets().get(spreadsheetId=sid).execute()['sheets']]
    if SHEET_TAB not in titles:
        sh.svc.spreadsheets().batchUpdate(spreadsheetId=sid, body={'requests': [
            {'addSheet': {'properties': {'title': SHEET_TAB}}}]}).execute()
        sh.svc.spreadsheets().values().update(spreadsheetId=sid, range=SHEET_TAB + '!A1',
                                              valueInputOption='RAW', body={'values': [SHEET_HEADER]}).execute()
    have = {(r[0], r[2]) for r in (sh.read(sid, SHEET_TAB) or [])[1:] if len(r) > 2}
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds')
    rows = []
    for name, d in meo.items():
        if 'cur' not in d or (cur[0], name) in have:
            continue
        c, p, r = d['cur'], d['prev'], d.get('reviews') or {}
        rows.append([cur[0], cur[1], name, c['maps'], c['search'], c['directions'], c['website'], c['calls'],
                     p['maps'] + p['search'], r.get('total', ''), r.get('avg', ''), r.get('new', ''), r.get('unreplied', ''), now])
    if rows:
        sh.svc.spreadsheets().values().append(spreadsheetId=sid, range=SHEET_TAB + '!A1', valueInputOption='RAW',
                                              insertDataOption='INSERT_ROWS', body={'values': rows}).execute()
    return len(rows)


if __name__ == '__main__':
    today = dt.date.today()
    end = today - dt.timedelta(days=3)
    cur = ((end - dt.timedelta(days=6)).isoformat(), end.isoformat())
    prev = ((end - dt.timedelta(days=13)).isoformat(), (end - dt.timedelta(days=7)).isoformat())
    import json
    print(cur, prev)
    print(json.dumps(collect(cur, prev), ensure_ascii=False, indent=1))
