#!/usr/bin/env python3
"""Clarity の数値を毎日スプレッドシートへ貯める（Looker Studio の週次メールに載せるため）。

Clarity のデータ取り出し（Data Export API）は「直近1〜3日分・1サイト1日10回まで」しか取れない。
月次・週次で後からまとめて取れないので、毎日1日分を取って貯める。

  python3 clarity_daily.py --init     # 書き込み先のスプレッドシートを作る（初回だけ・IDを控えに保存）
  python3 clarity_daily.py --dry-run  # 取るだけで書かない（何行書くかを表示）
  python3 clarity_daily.py            # 取って追記する（cron はこれ）

台帳        ~/vivid-ai-hq/bin/web_tracking/sites.json（clarity のIDがあるサイトだけ対象）
鍵          ~/.vivid-relay/clarity_tokens.json   {"<ClarityのプロジェクトID>": "<APIトークン>", ...}
            ★Clarity の各プロジェクト →「設定」→「データのエクスポート」→「新しいAPIトークン」で発行
            ★中身は決して出力しない。鍵が無いサイトは飛ばして「鍵なし」と出すだけ
書き込み先  ~/.vivid-relay/clarity_sheet_id.txt に控えたスプレッドシート（シート clarity_daily）
            1行＝日付×サイト×(全体 or URL)×指標×項目×値 の縦持ち（Looker Studio で集計しやすい形）
心拍        ~/.vivid-relay/clarity_daily.last（成功でも失敗でも最後に書く）
"""
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
RELAY = os.path.expanduser('~/.vivid-relay')
SITES_JSON = os.path.join(HERE, 'sites.json')
TOKENS = os.path.join(RELAY, 'clarity_tokens.json')
SHEET_ID_FILE = os.path.join(RELAY, 'clarity_sheet_id.txt')
HEARTBEAT = os.path.join(RELAY, 'clarity_daily.last')
PROC_NAME = 'Clarity日次の取得（clarity_daily.py）'   # ★⚙️自動処理レジスタの「処理名」と完全一致させる
API = 'https://www.clarity.ms/export-data/api/v1/project-live-insights'
TAB = 'clarity_daily'
HEADER = ['日付', 'サイト', 'ドメイン', '範囲', 'URL', '指標', '項目', '値', '取得時刻']
JST = dt.timezone(dt.timedelta(hours=9))


def heartbeat(msg):
    """本番だけ心拍を打つ（.last とレジスタ）。★--dry-run では打たない（試しの OK が本番の沈黙を隠すため）"""
    if '--dry-run' in sys.argv:
        return
    with open(HEARTBEAT, 'w') as f:
        f.write('%s %s\n' % (dt.datetime.now(JST).isoformat(timespec='seconds'), msg))
    try:
        sys.path.insert(0, RELAY)
        from heartbeat import beat
        beat(PROC_NAME, '失敗' if msg.startswith('NG') else '成功', msg)
    except Exception as ex:
        sys.stderr.write('心拍を送れず：%s\n' % ex)


def sites():
    data = json.load(open(SITES_JSON, encoding='utf-8'))
    out = []
    for s in data['sites']:
        cid = s.get('clarity', '')
        if cid and cid.isalnum() and 8 <= len(cid) <= 12:
            dom = urllib.parse.urlparse(s['url']).netloc
            out.append({'name': s['name'], 'domain': dom, 'clarity': cid})
    return out


def fetch(token, dimension=None):
    params = {'numOfDays': '1'}
    if dimension:
        params['dimension1'] = dimension
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(params),
                                 headers={'Authorization': 'Bearer ' + token,
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def flatten(resp, site, day, now, dimension=None):
    """API の応答を縦持ちの行にする。項目名は応答に書かれたまま（仕様変更で列が増えても落ちない）"""
    rows = []
    for m in resp if isinstance(resp, list) else []:
        metric = m.get('metricName', '')
        for info in m.get('information') or []:
            # 内訳（Browser/Device/OS/Country/PageTitle/ReferrerUrl 等）やページ別のURLは、名前を URL 列に入れる。
            # ★項目名（"URL" "Url" "name"…）は応答ごとに違うので名前で引かず「数字でない値」を拾う
            #   （10/5 実測：dimension1=URL でも info['URL'] は空だった／内訳は名前が落ちていた）
            labels = [str(v) for k, v in info.items() if num(v) is None and v not in (None, '')]
            url = labels[0] if labels else ''
            for k, v in info.items():
                if dimension and k == dimension:
                    continue
                n = num(v)
                if n is None:
                    continue       # 文字列（ページ名など）は値にしない（URL 列へ入れた）
                rows.append([day, site['name'], site['domain'],
                             'URL別' if dimension else ('内訳' if url else '全体'),
                             url, metric, k, n, now])
    return rows


def sheets():
    sys.path.insert(0, RELAY)
    from sheets_client import Sheets
    return Sheets()


def init():
    if os.path.exists(SHEET_ID_FILE):
        print('既にある：', open(SHEET_ID_FILE).read().strip())
        return
    sh = sheets()
    body = {'properties': {'title': 'SEO計測_Clarity日次（自動・編集しない）'},
            'sheets': [{'properties': {'title': TAB}}, {'properties': {'title': 'README'}}]}
    ss = sh.svc.spreadsheets().create(body=body, fields='spreadsheetId').execute()
    sid = ss['spreadsheetId']
    sh.svc.spreadsheets().values().batchUpdate(spreadsheetId=sid, body={
        'valueInputOption': 'RAW',
        'data': [
            {'range': TAB + '!A1', 'values': [HEADER]},
            {'range': 'README!A1', 'values': [
                ['Mac mini の clarity_daily.py が毎日追記する（手で編集しない）'],
                ['正本のコード  ~/vivid-ai-hq/bin/web_tracking/clarity_daily.py'],
                ['日付＝取得した日の前日（JST）。Clarity は「呼んだ時点から24時間」を返すため厳密な暦日ではない'],
                ['範囲＝全体（サイト全体）／URL別（ページごと）。値は Clarity の応答の数値をそのまま'],
                ['使い道  Looker Studio「ふくち。グループSearch Console」のデータソース'],
            ]}]}).execute()
    with open(SHEET_ID_FILE, 'w') as f:
        f.write(sid + '\n')
    print('作成：https://docs.google.com/spreadsheets/d/%s' % sid)


def main():
    if '--init' in sys.argv:
        return init()
    dry = '--dry-run' in sys.argv
    tokens = json.load(open(TOKENS)) if os.path.exists(TOKENS) else {}
    now = dt.datetime.now(JST)
    day = (now - dt.timedelta(days=1)).date().isoformat()
    stamp = now.isoformat(timespec='seconds')
    all_rows, report = [], []
    for s in sites():
        tok = tokens.get(s['clarity'], '')
        if len(tok) < 40:            # 未記入（「ここに…を貼る」のまま）も鍵なし扱い
            report.append('%s  鍵なし（飛ばした）' % s['name'])
            continue
        try:
            rows = flatten(fetch(tok), s, day, stamp)
            rows += flatten(fetch(tok, 'URL'), s, day, stamp, 'URL')   # 1サイト1日2回（上限10回）
            all_rows += rows
            report.append('%s  %d行' % (s['name'], len(rows)))
        except urllib.error.HTTPError as e:
            report.append('%s  ✗ HTTP %d（401=鍵が違う/失効・429=1日10回超え）' % (s['name'], e.code))
        except Exception as e:
            report.append('%s  ✗ %s' % (s['name'], str(e)[:120]))
    print('\n'.join(report))
    if dry:
        print('dry-run：%d行（書いていない）' % len(all_rows))
        return
    if all_rows:
        sid = open(SHEET_ID_FILE).read().strip()
        # ★同じ日付×サイトが既にあれば積まない（手で再実行しても二重にならない）
        have = {(r[0], r[1]) for r in (sheets().read(sid, TAB) or [])[1:] if len(r) > 1}
        dup = {(r[0], r[1]) for r in all_rows} & have
        if dup:
            report.append('既に記録済みの日付×サイト %d組は積まなかった' % len(dup))
            all_rows = [r for r in all_rows if (r[0], r[1]) not in have]
    if all_rows:
        sheets().svc.spreadsheets().values().append(
            spreadsheetId=open(SHEET_ID_FILE).read().strip(), range=TAB + '!A1', valueInputOption='RAW',
            insertDataOption='INSERT_ROWS', body={'values': all_rows}).execute()
    bad = [r for r in report if '✗' in r]
    heartbeat(('NG ' if bad else 'OK ') + '%d行 ' % len(all_rows) + ' / '.join(report))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        heartbeat('NG 例外 %s' % str(e)[:200])
        raise
