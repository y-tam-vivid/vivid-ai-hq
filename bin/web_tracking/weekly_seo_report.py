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
PROC_NAME = 'SEO週次レポート（weekly_seo_report.py）'   # ★⚙️自動処理レジスタの「処理名」と完全一致
PROBLEMS = []   # 部分失敗（AI・Notion・Slack・シート）を集めて心拍のメッセージに載せる
LOG_HTML = ''
AI_HTML = ''


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
    out['queries'] = q
    return out


def brand_share(q, words):
    """指名検索（施設名・社名を含む検索語）のクリック・表示。AIEO の代わりの指標（9/20 設計書 doc21）"""
    if not words:
        return None
    hit = [r for r in q if any(w.lower() in r['keys'][0].lower() for w in words)]
    return {'clicks': sum(r.get('clicks', 0) for r in hit), 'impressions': sum(r.get('impressions', 0) for r in hit)}


AI_REFERRERS = ('chatgpt', 'openai', 'perplexity', 'copilot', 'gemini', 'claude.ai', 'bing.com/chat', 'you.com')


def ai_referrals(rows, site_name, days):
    """Clarity の参照元（ReferrerUrl の内訳）から AI 経由の訪問を数える"""
    n, srcs = 0, {}
    for r in rows:
        if r[1] == site_name and r[3] == '内訳' and r[5] == 'ReferrerUrl' and r[0] in days \
                and r[6] == 'sessionsCount' and any(a in r[4].lower() for a in AI_REFERRERS):
            n += float(r[7])
            srcs[r[4]] = srcs.get(r[4], 0) + float(r[7])
    return n, srcs


# ── 気づき（自動で拾う規則。★しきい値は仮・運用しながら直す） ─────────
def findings(d):
    out, g, c = [], d.get('gsc') or {}, d.get('clarity') or {}
    if 'cur' in g:
        for k, label in (('clicks', 'クリック'), ('impressions', '表示')):
            cu, pr = g['cur'][k], g['prev'][k]
            if pr >= 20 and cu <= pr * 0.7:
                out.append(('SEO', '検索の%sが減った（%d→%d・先週比%+.0f%%）' % (label, pr, cu, (cu - pr) / pr * 100)))
        if g.get('chance'):
            r = g['chance'][0]
            out.append(('SEO', '表示はあるが順位が低い検索語「%s」（表示%d・%.0f位）' % (r['keys'][0], r['impressions'], r['position'])))
    if c and c.get('sessions', 0) >= 5:
        for k, label in (('dead', '反応しない所を押す'), ('rage', '連打'), ('quickback', 'すぐ戻る')):
            v = c.get(k)
            if v is not None and v >= 20:
                out.append(('使いやすさ（Clarity）', '「%s」訪問が%.0f%%（訪問%d）' % (label, v, c['sessions'])))
    return out


# ── Notion「サイト改善ログ」 ─────────────────────────────────
NOTION_DS = '720d4be9-d3e3-48f9-8e0b-67c0a8aec537'


def notion(method, path, body=None):
    import urllib.request
    tok = ''
    for line in open(os.path.join(RELAY, 'config.env')):
        if line.startswith('NOTION_TOKEN='):
            tok = line.split('=', 1)[1].strip().strip('"\'')
    req = urllib.request.Request('https://api.notion.com/v1' + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + tok, 'Notion-Version': '2025-09-03',
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def plain(p):
    t = p.get('title') or p.get('rich_text') or []
    if t:
        return ''.join(x.get('plain_text', '') for x in t)
    if p.get('select'):
        return p['select']['name']
    return ''


def improvement_log():
    rows = []
    res = notion('POST', '/data_sources/%s/query' % NOTION_DS, {'page_size': 100})
    for pg in res.get('results', []):
        pr = pg['properties']
        rows.append({'title': plain(pr['打ち手']), 'site': plain(pr['サイト']), 'state': plain(pr['状態']),
                     'effect': plain(pr['効果確認']), 'url': pg.get('url', '')})
    return rows


def add_candidates(cands, week_start, existing):
    """AI の打ち手を「候補」として起票し、Slack のボタンで採否を聞く。★同じサイト×同じ打ち手が既にあれば足さない"""
    have = {(r['site'], r['title']) for r in existing}
    made = 0
    for site, area, title, a in cands:
        text = '%s／やり方：%s（担当：%s・手間：%s）' % (a.get('why', ''), a.get('how', ''), a.get('who', ''), a.get('effort', ''))
        if not title:
            continue
        if (site, title) in have:
            continue
        notion('POST', '/pages', {'parent': {'data_source_id': NOTION_DS}, 'properties': {
            '打ち手': {'title': [{'text': {'content': title[:180]}}]},
            'サイト': {'select': {'name': site}}, '領域': {'multi_select': [{'name': area}]},
            '状態': {'select': {'name': '候補'}}, '起票': {'select': {'name': '週次レポート（自動）'}},
            '気づいた週': {'date': {'start': week_start}},
            '気づき': {'rich_text': [{'text': {'content': text[:1900]}}]},
            '担当': {'rich_text': [{'text': {'content': 'AI' if a.get('who') == 'AI' else '人（有璽氏が指示）'}}]}}})
        made += 1
        try:
            import ask_hub
            ask_hub.ask('【SEO週次】打ち手の採否：%s' % title[:60], '%s ── %s' % (site, title),
                        [('AIに任せる（実施）' if a.get('who') == 'AI' else '進める', 'primary'), ('見送り', None)],
                        detail=text, asked_by='SEO週次レポート（AI）', kind='広報')
        except Exception as ex:
            sys.stderr.write('Slackへの採否依頼に失敗：%s\n' % ex)
            PROBLEMS.append('Slack採否')
    return made


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
def pct(cur, prev, unit='先週'):
    if not prev:
        return '<span style="color:#888">（%s0）</span>' % unit if cur else ''
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
         '<h3 style="margin:20px 0 6px">① 記録：全サイト一覧</h3>',
         '<table style="border-collapse:collapse;width:100%%"><tr>'
         '<th %s>サイト</th><th %s>検索の表示</th><th %s>クリック</th><th %s>順位</th>'
         '<th %s>訪問（Clarity）</th><th %s>デッド／怒り／すぐ戻る</th><th %s>読了の深さ</th>'
         '<th %s>指名検索クリック</th><th %s>AI経由の訪問</th></tr>'
         % ((th,) * 9)]
    for d in data:
        g, c = d.get('gsc'), d.get('clarity')
        gs = ('%s %s' % (f(g['cur']['impressions']), pct(g['cur']['impressions'], g['prev']['impressions'])),
              '%s %s' % (f(g['cur']['clicks']), pct(g['cur']['clicks'], g['prev']['clicks'])),
              f(g['cur']['position'] or None, '{:.1f}')) if g and 'cur' in g else ('—', '—', '—')
        cs = (f(c['sessions']),
              '%s／%s／%s' % (f(c['dead'], '{:.0f}%'), f(c['rage'], '{:.0f}%'), f(c['quickback'], '{:.0f}%')),
              f(c['scroll'], '{:.0f}%')) if c and c['sessions'] else ('—', '—', '—')
        b, ai = d.get('brand'), d.get('ai')
        cs = cs + ((f(b['clicks']) if b else '—'), (f(ai[0]) if ai else '—'))
        h.append('<tr><td %s><b>%s</b><br><span style="font-size:11px;color:#7a6a5c">%s</span></td>'
                 % (td, e(d['name']), e(d['domain'])) + ''.join('<td %s>%s</td>' % (td, x) for x in gs + cs) + '</tr>')
    h.append('</table><div style="font-size:11px;color:#7a6a5c;margin-top:4px">'
             'デッド＝押しても反応しない所を押した訪問の割合／怒り＝同じ所を連打した割合／すぐ戻る＝開いてすぐ戻った割合。'
             '読了の深さ＝ページの何%までスクロールしたか（平均）。指名検索＝施設名・社名を含む検索（AIEOの代わりの指標）。'
             'AI経由＝ChatGPT・Copilot・Perplexity等から来た訪問（Clarityの参照元）</div>')
    h.append('<h3 style="margin:24px 0 6px">② AIの深掘りと今週の打ち手</h3>')
    h.append(AI_HTML or '<div style="font-size:12px;color:#7a6a5c">（AIの分析なし）</div>')
    h.append('<h4 style="margin:16px 0 4px;font-size:13px">機械が拾った変化（参考）</h4><div style="font-size:13px">')
    anyf = False
    for d in data:
        for area, text in d.get('findings', []):
            anyf = True
            h.append('・<b>%s</b>［%s］%s<br>' % (e(d['name']), e(area), e(text)))
    if not anyf:
        h.append('大きな変化なし')
    h.append('</div>')
    h.append('<h3 style="margin:24px 0 6px">③ 改善ログ（AIの作業記録・Notion）</h3><div style="font-size:13px">')
    h.append(LOG_HTML)
    h.append('</div>')
    h.append('<h3 style="margin:24px 0 6px">④ サイト別</h3>')
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
    h.append('<h3 style="margin:24px 0 6px">⑤ 計測タグの点検</h3><div style="font-size:13px">')
    for name, st in tags:
        h.append('%s　%s<br>' % (e(st), e(name)))
    h.append('</div><div style="font-size:11px;color:#7a6a5c;margin-top:20px">'
             'Mac mini の weekly_seo_report.py が自動で作成。数字は Search Console と Clarity の値のみ（推測で埋めていない）。</div></div>')
    return '\n'.join(h)


SUMMARY_TAB = 'weekly_summary'
SUMMARY_HEADER = ['週の初日', '週の末日', 'サイト', 'ドメイン', '検索の表示', '検索のクリック', 'CTR(%)', '平均順位',
                  '先週の表示', '先週のクリック', 'Clarity訪問', 'デッド(%)', '怒り(%)', 'すぐ戻る(%)', '読了の深さ(%)',
                  '指名検索クリック', 'AI経由の訪問', 'Clarityの日数', 'タグ点検', '記録時刻']


def record_summary(data, cur, cdays, tags):
    """①の一覧を「1週×1サイト＝1行」でシートに積む（週で見比べるための記録）。同じ週の行が既にあれば積まない"""
    from sheets_client import Sheets
    sh = Sheets()
    sid = open(os.path.join(RELAY, 'clarity_sheet_id.txt')).read().strip()
    titles = [s['properties']['title'] for s in sh.svc.spreadsheets().get(spreadsheetId=sid).execute()['sheets']]
    if SUMMARY_TAB not in titles:
        sh.svc.spreadsheets().batchUpdate(spreadsheetId=sid, body={'requests': [
            {'addSheet': {'properties': {'title': SUMMARY_TAB}}}]}).execute()
        sh.svc.spreadsheets().values().update(spreadsheetId=sid, range=SUMMARY_TAB + '!A1',
                                              valueInputOption='RAW', body={'values': [SUMMARY_HEADER]}).execute()
    have = {(r[0], r[2]) for r in (sh.read(sid, SUMMARY_TAB) or [])[1:] if len(r) > 2}
    tagd = dict(tags)
    now = dt.datetime.now(JST).isoformat(timespec='seconds')
    rows = []
    for d in data:
        if (cur[0], d['name']) in have:
            continue
        g, c, b, ai = d.get('gsc') or {}, d.get('clarity') or {}, d.get('brand'), d.get('ai')
        gc, gp = g.get('cur', {}), g.get('prev', {})
        rnd = lambda v, n=1: '' if v is None else round(v, n)
        rows.append([cur[0], cur[1], d['name'], d['domain'],
                     gc.get('impressions', ''), gc.get('clicks', ''), rnd(gc.get('ctr')), rnd(gc.get('position')),
                     gp.get('impressions', ''), gp.get('clicks', ''),
                     c.get('sessions', ''), rnd(c.get('dead')), rnd(c.get('rage')), rnd(c.get('quickback')),
                     rnd(c.get('scroll')), b['clicks'] if b else '', ai[0] if ai else '', len(cdays),
                     tagd.get(d['name'], ''), now])
    if rows:
        sh.svc.spreadsheets().values().append(spreadsheetId=sid, range=SUMMARY_TAB + '!A1', valueInputOption='RAW',
                                              insertDataOption='INSERT_ROWS', body={'values': rows}).execute()
    return len(rows)


def render_ai(ai):
    e = html.escape
    if not ai:
        return ''
    if ai.get('error'):
        return '<div style="font-size:12px;color:#b3261e">AIの分析を作れませんでした（%s）</div>' % e(ai['error'][:120])
    h = ['<div style="font-size:13px;background:#fffaf3;border-left:4px solid #e8740c;padding:8px 12px">%s</div>'
         % e(ai.get('summary', '')).replace('\n', '<br>')]
    for x in ai.get('sites', []):
        h.append('<div style="font-size:13px;margin:8px 0"><b>%s</b><br>何が起きた：%s<br>なぜ：%s<br>次に：%s</div>'
                 % tuple(e(x.get(k, '')) for k in ('site', 'what', 'why', 'next')))
    if ai.get('actions'):
        h.append('<div style="font-size:13px;margin-top:8px"><b>今週の打ち手（Slackで採否をお聞きします）</b></div>')
        for a in ai['actions']:
            h.append('<div style="font-size:13px;margin:4px 0 4px 8px">・［%s／%s］<b>%s</b>（担当：%s・手間：%s）<br>'
                     '<span style="color:#7a6a5c">なぜ：%s／やり方：%s</span></div>'
                     % tuple(e(a.get(k, '')) for k in ('site', 'area', 'title', 'who', 'effort', 'why', 'how')))
    return '\n'.join(h)


def beat_once(ok, msg):
    """本番だけ心拍（.last＋レジスタ）。★--dry-run・--to（試し送り）では打たない"""
    if '--dry-run' in sys.argv or '--to' in sys.argv:
        return
    open(HEARTBEAT, 'w').write('%s %s\n' % (dt.datetime.now(JST).isoformat(timespec='seconds'), msg))
    try:
        from heartbeat import beat
        beat(PROC_NAME, '成功' if ok and not PROBLEMS else ('警告' if ok else '失敗'), msg)
    except Exception as ex:
        sys.stderr.write('心拍を送れず：%s\n' % ex)


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
        if s.get('gsc') and s['gsc'].get('property', '').startswith(('sc-domain:', 'http')):   # ★未登録（「★未登録…」等）は取りにいかない
            try:
                d['gsc'] = gsc_site(sc, s['gsc'], cur, prev)
            except Exception as ex:
                d['gsc'] = {'error': str(ex)[:160]}
        if s.get('noindex_expected'):
            continue        # 検索対象外のLPは一覧に載せない
        if d.get('gsc') and 'queries' in d['gsc']:
            d['brand'] = brand_share(d['gsc']['queries'], s.get('brand'))
        if d.get('clarity_id'):
            d['ai'] = ai_referrals(crows, s['name'], cdays)
        d['findings'] = findings(d)
        d['log_label'] = s.get('log_label', '全サイト')
        data.append(d)
        try:
            a = site_audit.audit(s)
            tags.append((s['name'], a.get('clarity', '—')))
        except Exception as ex:
            tags.append((s['name'], '✗ 点検失敗 %s' % str(ex)[:60]))
    global LOG_HTML, AI_HTML
    ai = {}
    if '--no-ai' not in sys.argv:
        from ai_analysis import analyze
        payload = {'period': {'this_week': cur, 'last_week': prev}, 'clarity_days': len(got_cdays), 'sites': [{
            'site': d['name'], 'domain': d['domain'],
            'search': ({k: d['gsc'].get(k) for k in ('cur', 'prev')} if d.get('gsc') and 'cur' in d['gsc'] else None),
            'top_queries': ([{'q': r['keys'][0], 'clicks': r.get('clicks'), 'impr': r.get('impressions'),
                              'pos': round(r.get('position', 0), 1)} for r in d['gsc'].get('queries', [])[:15]]
                            if d.get('gsc') and 'queries' in d['gsc'] else None),
            'clarity': ({k: v for k, v in d['clarity'].items() if k != 'days'} if d.get('clarity') else None),
            'brand_search': d.get('brand'), 'ai_referrals': (d['ai'][0] if d.get('ai') else None),
            'signals': [t for _, t in d.get('findings', [])], 'tag': dict(tags).get(d['name'])} for d in data]}
        try:
            payload['improvement_log'] = [{'site': r['site'], 'title': r['title'], 'state': r['state'],
                                           'effect': r['effect']} for r in improvement_log()]
        except Exception:
            pass
        ai = analyze(payload, 'weekly')
        if ai.get('error'):
            PROBLEMS.append('AI分析')
    AI_HTML = render_ai(ai)
    db_url = 'https://app.notion.com/p/afbfa222ea2848598c384e6c4d983d97'
    try:
        log = improvement_log()
        label = {d['name']: d.get('log_label', '全サイト') for d in data}
        cands = [(label.get(a.get('site'), '全サイト'), a.get('area', 'SEO'), a.get('title', ''), a) for a in ai.get('actions', [])]
        made = 0 if ('--dry-run' in sys.argv or '--to' in sys.argv) else add_candidates(cands, cur[0], log)   # ★試し送り（--to）では起票しない
        act = [r for r in log if r['state'] in ('採用', '実施中')]
        LOG_HTML = ('進行中の打ち手 %d件／候補 %d件（今回の自動起票 %d件）<br>' %
                    (len(act), len([r for r in log if r['state'] == '候補']), made) +
                    ''.join('・［%s］%s（%s）%s<br>' % (html.escape(r['site']), html.escape(r['title']), html.escape(r['state']),
                            ('<br>　→ 効果：' + html.escape(r['effect'])) if r['effect'] else '') for r in act) +
                    '<a href="%s">改善ログを開く（候補を採用・見送りに変える）</a>' % db_url)
    except Exception as ex:
        PROBLEMS.append('Notion改善ログ')
        LOG_HTML = ('<span style="color:#b3261e">改善ログを読めませんでした（%s）。'
                    'Notionの接続設定を確認してください。</span><br><a href="%s">改善ログを開く</a>' % (html.escape(str(ex)[:80]), db_url))
    body = build(data, cur, prev, got_cdays, tags)
    # ①を週次サマリーとしてシートに積む（本番送信時。--record を付ければ試し・dry-run でも積む）
    if '--record' in sys.argv or ('--dry-run' not in sys.argv and '--to' not in sys.argv):
        try:
            print('週次サマリーを記録：%d行' % record_summary(data, cur, got_cdays, tags))
        except Exception as ex:
            sys.stderr.write('週次サマリーの記録に失敗：%s\n' % ex)
            PROBLEMS.append('週次サマリー記録')
    open(OUT_HTML, 'w', encoding='utf-8').write(body)
    subject = 'ふくち。グループ SEO週次レポート（%s〜%s）' % (cur[0][5:].replace('-', '/'), cur[1][5:].replace('-', '/'))
    if '--dry-run' in sys.argv:
        print('dry-run：%s（%dサイト・送っていない）' % (OUT_HTML, len(data)))
        return
    to = sys.argv[sys.argv.index('--to') + 1] if '--to' in sys.argv else TO_DEFAULT
    r = send(to, subject, body)
    msg = 'OK 送信 %s id=%s %dサイト' % (to, r.get('id'), len(data))
    if PROBLEMS:
        msg += ' ／一部失敗：' + '・'.join(PROBLEMS)
    beat_once(True, msg)
    print(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        beat_once(False, 'NG %s' % str(ex)[:200])
        raise
