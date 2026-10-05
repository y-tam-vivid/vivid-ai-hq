#!/usr/bin/env python3
"""SEO月次レポート（振り返り）。前の暦月を、全サイトの実測で集計し、AIが深掘りと考察・アクション案を書く。
有璽氏がそれを読んで、Slack のボタンで「どう動くか」を指示する。Mac mini で毎月1日に動かす。

  python3 monthly_seo_report.py --dry-run           # 送らず HTML を ~/.vivid-relay/monthly_seo_report.html へ
  python3 monthly_seo_report.py --to y_tam@...      # 試し送り（Notion・Slack には出さない）
  python3 monthly_seo_report.py [--month 2026-09]   # 本番：メール＋Notionに保存＋アクションごとにSlackで指示を聞く

週次との違い
  週次＝AIが回す（打ち手は最大3件・採否だけ聞く）
  月次＝有璽氏が舵を切る（先月の実測・先々月比・週ごとの推移・打ち手の効果 → AIの考察とアクション案 → 有璽氏が指示）
★数字は Search Console／Clarity 日次シート／週次サマリー／改善ログ の値だけ。推測で埋めない
"""
import calendar
import datetime as dt
import html
import json
import os
import sys
import warnings

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import weekly_seo_report as w          # 取得・集計の部品を共有する（同じ数え方にするため）
from ai_analysis import analyze

JST, RELAY = w.JST, w.RELAY
OUT_HTML = os.path.join(RELAY, 'monthly_seo_report.html')
HEARTBEAT = os.path.join(RELAY, 'monthly_seo_report.last')
PROC_NAME = 'SEO月次レポート（monthly_seo_report.py）'   # ★⚙️自動処理レジスタの「処理名」と完全一致
DONE_FILE = os.path.join(RELAY, 'monthly_seo_report.done')   # 本番を出した月（再実行で Notion・Slack を二重に出さない）
PARENT_PAGE = '2e77b1568b57809db199f2061d17de79'      # Notion「[12-100]広報部_PR・プレスリリース」


def month_range(y, m):
    return dt.date(y, m, 1).isoformat(), dt.date(y, m, calendar.monthrange(y, m)[1]).isoformat()


def target_month():
    if '--month' in sys.argv:
        y, m = map(int, sys.argv[sys.argv.index('--month') + 1].split('-'))
    else:
        p = dt.datetime.now(JST).date().replace(day=1) - dt.timedelta(days=1)
        y, m = p.year, p.month
    cur = month_range(y, m)
    py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
    return (y, m), cur, month_range(py, pm)


def weekly_rows(start, end):
    try:
        from sheets_client import Sheets
        sid = open(os.path.join(RELAY, 'clarity_sheet_id.txt')).read().strip()
        rows = Sheets().read(sid, w.SUMMARY_TAB) or []
        return [dict(zip(rows[0], r)) for r in rows[1:] if start <= r[0] <= end]
    except Exception:
        return []


def build(ym, cur, prev, data, ai, log, cdays):
    e = html.escape
    css = ('font-family:-apple-system,Hiragino Sans,Meiryo,sans-serif;color:#2b211a;'
           'max-width:820px;margin:0 auto;padding:16px;line-height:1.7')
    th = 'style="text-align:left;border-bottom:2px solid #e8740c;padding:6px 8px;font-size:12px;color:#7a6a5c"'
    td = 'style="border-bottom:1px solid #f0e1cf;padding:6px 8px;font-size:13px;vertical-align:top"'
    h = ['<div style="%s">' % css,
         '<h2 style="margin:0;color:#e8740c">ふくち。グループ SEO月次レポート %d年%d月</h2>' % ym,
         '<div style="font-size:12px;color:#7a6a5c">検索（Search Console）%s〜%s（先月 %s〜%s）／Clarity %d日分</div>'
         % (cur[0], cur[1], prev[0], prev[1], len(cdays)),
         '<h3 style="margin:22px 0 6px">1. AIの総括</h3>']
    if ai.get('error'):
        h.append('<div style="color:#b3261e;font-size:13px">AIの分析を作れませんでした（%s）</div>' % e(ai['error'][:160]))
    else:
        h.append('<div style="font-size:14px;background:#fffaf3;border-left:4px solid #e8740c;padding:10px 14px">%s</div>'
                 % e(ai.get('summary', '')).replace('\n', '<br>'))
    h.append('<h3 style="margin:22px 0 6px">2. 実測（月の合計・先月比）</h3>'
             '<table style="border-collapse:collapse;width:100%%"><tr><th %s>サイト</th><th %s>検索の表示</th>'
             '<th %s>クリック</th><th %s>CTR</th><th %s>順位</th><th %s>訪問（Clarity）</th>'
             '<th %s>デッド／怒り／すぐ戻る</th><th %s>指名検索クリック</th><th %s>AI経由</th></tr>' % ((th,) * 9))
    for d in data:
        g, c, b, a = d.get('gsc') or {}, d.get('clarity') or {}, d.get('brand'), d.get('ai')
        if 'cur' in g:
            gc, gp = g['cur'], g['prev']
            gs = ('%s %s' % (w.f(gc['impressions']), w.pct(gc['impressions'], gp['impressions'], '先月')),
                  '%s %s' % (w.f(gc['clicks']), w.pct(gc['clicks'], gp['clicks'], '先月')),
                  w.f(gc['ctr'], '{:.1f}%'), w.f(gc['position'] or None, '{:.1f}'))
        else:
            gs = ('—',) * 4
        cs = (w.f(c.get('sessions')) if c.get('sessions') else '—',
              '%s／%s／%s' % (w.f(c.get('dead'), '{:.0f}%'), w.f(c.get('rage'), '{:.0f}%'), w.f(c.get('quickback'), '{:.0f}%'))
              if c.get('sessions') else '—', w.f(b['clicks']) if b else '—', w.f(a[0]) if a else '—')
        h.append('<tr><td %s><b>%s</b><br><span style="font-size:11px;color:#7a6a5c">%s</span></td>' % (td, e(d['name']), e(d['domain']))
                 + ''.join('<td %s>%s</td>' % (td, x) for x in gs + cs) + '</tr>')
    h.append('</table>')
    h.append('<h3 style="margin:22px 0 6px">3. サイト別の深掘り</h3>')
    for x in ai.get('sites', []):
        h.append('<div style="border:1px solid #f0e1cf;border-radius:8px;padding:10px 14px;margin:10px 0;font-size:13px">'
                 '<b style="font-size:14px">%s</b><br><b>何が起きた</b>　%s<br><b>なぜ</b>　%s<br><b>次の1か月</b>　%s</div>'
                 % tuple(e(x.get(k, '')) for k in ('site', 'what', 'why', 'next')))
    h.append('<h3 style="margin:22px 0 6px">4. 打ち手の効果（改善ログ）</h3><div style="font-size:13px">')
    done = [r for r in log if r['state'] in ('完了', '実施中')]
    for r in done:
        h.append('・［%s］%s（%s）%s<br>' % (e(r['site']), e(r['title']), e(r['state']),
                 ('<br>　→ ' + e(r['effect'])) if r['effect'] else '<br>　→ 効果の記録なし'))
    if not done:
        h.append('実施中・完了の打ち手はまだありません')
    h.append('</div><h3 style="margin:22px 0 6px">5. AIの考察と、次の1か月のアクション案</h3>'
             '<div style="font-size:12px;color:#7a6a5c">★1件ずつSlackでお聞きします。「進める／保留／見送り」か、ボタンの「その他」で指示を書いてください</div>')
    for i, a in enumerate(ai.get('actions', []), 1):
        h.append('<div style="font-size:13px;margin:8px 0;padding:8px 12px;background:#fdfaf6;border-radius:6px">'
                 '<b>%d. ［%s／%s］%s</b>（担当：%s・手間：%s）<br>なぜ：%s<br>やり方：%s</div>'
                 % ((i,) + tuple(e(a.get(k, '')) for k in ('site', 'area', 'title', 'who', 'effort', 'why', 'how'))))
    h.append('<div style="font-size:11px;color:#7a6a5c;margin-top:20px">Mac mini の monthly_seo_report.py が作成。'
             '数字は Search Console・Clarity・週次サマリー・改善ログの値のみ。</div></div>')
    return '\n'.join(h)


def save_notion(ym, body_text):
    """月次レポートを Notion の広報部ページの下に1ページ保存する（記録層・あとから読み返す用）"""
    blocks = [{'object': 'block', 'type': 'paragraph',
               'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': chunk}}]}}
              for chunk in [body_text[i:i + 1900] for i in range(0, min(len(body_text), 1900 * 90), 1900)]]
    r = w.notion('POST', '/pages', {'parent': {'page_id': PARENT_PAGE}, 'icon': {'type': 'emoji', 'emoji': '📊'},
                                    'properties': {'title': {'title': [{'text': {'content': 'SEO月次レポート %d年%d月' % ym}}]}},
                                    'children': blocks})
    return r.get('url', '')


def main():
    ym, cur, prev = target_month()
    sites = json.load(open(os.path.join(HERE, 'sites.json'), encoding='utf-8'))['sites']
    sc = w.svc('webmasters', 'v3')
    try:
        crows = w.clarity_rows()
    except Exception:
        crows = []
    d0, d1 = dt.date.fromisoformat(cur[0]), dt.date.fromisoformat(cur[1])
    mdays = {(d0 + dt.timedelta(days=i)).isoformat() for i in range((d1 - d0).days + 1)}
    cdays = sorted({r[0] for r in crows if r[0] in mdays})
    data = []
    for s in sites:
        if s.get('noindex_expected') or (not s.get('gsc') and not s.get('clarity')):
            continue
        d = {'name': s['name'], 'domain': s['url'].split('/')[2], 'log_label': s.get('log_label', '全サイト')}
        if s.get('gsc') and s['gsc'].get('property', '').startswith(('sc-domain:', 'http')):
            try:
                d['gsc'] = w.gsc_site(sc, s['gsc'], cur, prev)
                d['brand'] = w.brand_share(d['gsc']['queries'], s.get('brand'))
                pages = w.gsc_query(sc, s['gsc']['property'], cur[0], cur[1], ['page'], s['gsc'].get('page_contains'), 10)
                d['top_pages'] = [{'page': r['keys'][0], 'clicks': r.get('clicks'), 'impr': r.get('impressions'),
                                   'pos': round(r.get('position', 0), 1)} for r in pages]
                # ★先月分の検索語・ページも渡す（原因を「どのページ・どの検索語で失ったか」まで追えるように）
                pq = w.gsc_query(sc, s['gsc']['property'], prev[0], prev[1], ['query'], s['gsc'].get('page_contains'), 25)
                pp = w.gsc_query(sc, s['gsc']['property'], prev[0], prev[1], ['page'], s['gsc'].get('page_contains'), 10)
                cut = lambda rows: [{'key': r['keys'][0], 'clicks': r.get('clicks'), 'impr': r.get('impressions'),
                                     'pos': round(r.get('position', 0), 1)} for r in rows]
                d['prev_month'] = {'top_queries': cut(pq), 'top_pages': cut(pp)}
            except Exception as ex:
                d['gsc'] = {'error': str(ex)[:160]}
        if (s.get('clarity') or '').isalnum():
            d['clarity'] = w.clarity_site(crows, s['name'], mdays)
            d['ai'] = w.ai_referrals(crows, s['name'], mdays)
        data.append(d)
    try:
        log = w.improvement_log()
    except Exception:
        log = []
    payload = {'month': cur, 'previous_month': prev, 'clarity_days': len(cdays),
               'weekly_trend': weekly_rows(prev[0], cur[1]),
               'improvement_log': [{'site': r['site'], 'title': r['title'], 'state': r['state'], 'effect': r['effect']} for r in log],
               'sites': [{'site': d['name'], 'domain': d['domain'],
                          'search': ({k: d['gsc'].get(k) for k in ('cur', 'prev')} if d.get('gsc') and 'cur' in d['gsc'] else None),
                          'top_queries': ([{'q': r['keys'][0], 'clicks': r.get('clicks'), 'impr': r.get('impressions'),
                                            'pos': round(r.get('position', 0), 1)} for r in d['gsc'].get('queries', [])[:25]]
                                          if d.get('gsc') and 'queries' in d['gsc'] else None),
                          'top_pages': d.get('top_pages'), 'previous_month_breakdown': d.get('prev_month'),
                          'clarity': ({k: v for k, v in d['clarity'].items() if k != 'days'} if d.get('clarity') else None),
                          'brand_search': d.get('brand'), 'ai_referrals': (d['ai'][0] if d.get('ai') else None)} for d in data]}
    ai = analyze(payload, 'monthly', timeout=900)
    body = build(ym, cur, prev, data, ai, log, cdays)
    open(OUT_HTML, 'w', encoding='utf-8').write(body)
    subject = 'ふくち。グループ SEO月次レポート（%d年%d月）' % ym
    if '--dry-run' in sys.argv:
        print('dry-run：%s（%dサイト・アクション案%d件・送っていない）' % (OUT_HTML, len(data), len(ai.get('actions', []))))
        return
    test = '--to' in sys.argv
    tag = '%d-%02d' % ym
    if not test and '--force' not in sys.argv and os.path.exists(DONE_FILE) and tag in open(DONE_FILE).read().split():
        print('この月（%s）は本番を出し済み。出し直すなら --force' % tag)
        return
    to = sys.argv[sys.argv.index('--to') + 1] if test else w.TO_DEFAULT
    r = w.send(to, subject, body)
    msg = 'OK 送信 %s id=%s' % (to, r.get('id'))
    if not test:
        import re
        try:
            url = save_notion(ym, re.sub(r'<[^>]+>', '\n', body).replace('&nbsp;', ' '))
            msg += ' Notion=%s' % url
        except Exception as ex:
            msg += ' ／一部失敗：Notion保存(%s)' % str(ex)[:60]
        try:
            import ask_hub
            for i, a in enumerate(ai.get('actions', []), 1):
                ask_hub.ask('【SEO月次 %d年%d月】アクション%d：%s' % (ym + (i, a.get('title', '')[:50])),
                            '%s ── %s（担当：%s）どう動きますか？' % (a.get('site', ''), a.get('title', ''), a.get('who', '')),
                            [('進める', 'primary'), ('保留（来月また検討）', None), ('見送り', None)],
                            detail='なぜ：%s\nやり方：%s\n手間：%s' % (a.get('why', ''), a.get('how', ''), a.get('effort', '')),
                            asked_by='SEO月次レポート（AI）', kind='広報')
        except Exception as ex:
            msg += ' ／一部失敗：Slack(%s)' % str(ex)[:60]
        if ai.get('error'):
            msg += ' ／一部失敗：AI分析'
        open(DONE_FILE, 'a').write(tag + '\n')
        open(HEARTBEAT, 'w').write('%s %s\n' % (dt.datetime.now(JST).isoformat(timespec='seconds'), msg))
        try:
            from heartbeat import beat
            beat(PROC_NAME, '警告' if '一部失敗' in msg else '成功', msg)
        except Exception as ex:
            sys.stderr.write('心拍を送れず：%s\n' % ex)
    print(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        if '--dry-run' not in sys.argv and '--to' not in sys.argv:
            open(HEARTBEAT, 'w').write('%s NG %s\n' % (dt.datetime.now(JST).isoformat(timespec='seconds'), str(ex)[:200]))
            try:
                from heartbeat import beat
                beat(PROC_NAME, '失敗', 'NG %s' % str(ex)[:200])
            except Exception:
                pass
        raise
