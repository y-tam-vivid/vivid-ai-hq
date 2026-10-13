#!/usr/bin/env python3
"""SEO・MEO・AIO の打ち手を「回答 → 実施 → 効果判定」へ送る橋。Mac mini で毎朝動かす（読み書きするのは改善ログと AI_QUEUE.md だけ）。

★2026-10-13 有璽氏「こちらから働きかけないといけないのか」→ 人が押さなくても回る形にする
  10/12 に「AIに任せる（実施）」と答えた打ち手2件が、誰にも拾われず「候補」のまま止まっていた

  1 Slack の回答（ask_hub）を読み、改善ログの「状態」を動かす   AIに任せる／進める → 採用 ・ 見送り → 見送り
  2 完了して実施日が入った行に「効果を見る日」（実施日＋21日）と「結果＝判定待ち」を入れる
  3 AI がやること（採用で担当AI・効果を見る日が来たもの）を memory/AI_QUEUE.md に書き出して commit
     → CLAUDE.md が毎ターン読み込む＝どのセッションでも気づく（担当＝ウソップ search-growth）

  python3 seo_action_bridge.py --dry-run   # 何が動くかだけ出す（書かない）
  python3 seo_action_bridge.py             # 本番（cron）
正本    Notion「🔧 サイト改善ログ（SEO・MEO・AIEO）」（データソース 720d4be9-…）
心拍    ⚙️自動処理レジスタ「SEO打ち手の橋（seo_action_bridge.py）」
"""
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RELAY = os.path.expanduser('~/.vivid-relay')
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, RELAY)
sys.path.insert(0, HERE)
from weekly_seo_report import notion, plain, NOTION_DS   # noqa: E402

JST = dt.timezone(dt.timedelta(hours=9))
QUEUE_MD = os.path.join(REPO, 'memory', 'AI_QUEUE.md')
ASK_PREFIX = '【SEO週次】打ち手の採否：'
DONE = os.path.join(RELAY, 'seo_bridge_done.json')      # 反映済みの ask_id（同じ回答を二度動かさない）
PROC_NAME = 'SEO打ち手の橋（seo_action_bridge.py）'
EFFECT_DAYS = 21
DRY = '--dry-run' in sys.argv


def rows():
    out, cur = [], None
    while True:
        body = {'page_size': 100}
        if cur:
            body['start_cursor'] = cur
        res = notion('POST', '/data_sources/%s/query' % NOTION_DS, body)
        for pg in res.get('results', []):
            p = pg['properties']
            d = lambda k: ((p.get(k) or {}).get('date') or {}).get('start')
            out.append({'id': pg['id'], 'url': pg.get('url', ''), 'title': plain(p['打ち手']), 'site': plain(p['サイト']),
                        'state': plain(p['状態']), 'who': plain(p['担当']), 'done': d('実施日'), 'check': d('効果を見る日'),
                        'result': plain(p.get('結果', {})), 'area': ', '.join(x['name'] for x in p['領域'].get('multi_select', []))})
        if not res.get('has_more'):
            return out
        cur = res.get('next_cursor')


def update(pid, props):
    if DRY:
        print('  (dry-run) 書かない', pid, list(props))
        return
    notion('PATCH', '/pages/%s' % pid, {'properties': props})


def apply_answers(log):
    done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
    items = json.load(open(os.path.join(RELAY, 'ask_hub_queue.json')))['items']
    moved = []
    for k, it in items.items():
        if k in done or not it.get('subject', '').startswith(ASK_PREFIX) or it.get('status') != 'answered':
            continue
        label = ((it.get('answer') or {}).get('label') or '')
        new = '見送り' if '見送り' in label else ('採用' if ('任せる' in label or '進める' in label) else None)
        head = it['subject'][len(ASK_PREFIX):]
        hit = [r for r in log if r['title'][:60] == head[:60] and r['state'] == '候補']
        if new and hit:
            for r in hit:
                props = {'状態': {'select': {'name': new}}}
                if new == '採用' and '任せる' in label:
                    props['担当'] = {'rich_text': [{'text': {'content': 'AI（ウソップ）'}}]}
                update(r['id'], props)
                r['state'] = new
                if '担当' in props:
                    r['who'] = 'AI（ウソップ）'
                moved.append('%s → %s：%s' % (k, new, r['title'][:40]))
        if new and (hit or not [r for r in log if r['title'][:60] == head[:60]]):
            done.add(k)                      # 反映した／該当行が無い（消された等）ものは二度見ない
    if not DRY:
        json.dump(sorted(done), open(DONE, 'w'))
    return moved


def set_check_dates(log):
    n = 0
    for r in log:
        if r['state'] == '完了' and r['done'] and not r['check']:
            c = (dt.date.fromisoformat(r['done'][:10]) + dt.timedelta(days=EFFECT_DAYS)).isoformat()
            props = {'効果を見る日': {'date': {'start': c}}}
            if not r['result']:
                props['結果'] = {'select': {'name': '判定待ち'}}
                r['result'] = '判定待ち'
            update(r['id'], props)
            r['check'] = c
            n += 1
    return n


def write_queue(log):
    today = dt.datetime.now(JST).date().isoformat()
    todo = [r for r in log if r['state'] in ('採用', '実施中') and r['who'].startswith('AI')]
    judge = [r for r in log if r['state'] == '完了' and r['check'] and r['check'] <= today and r['result'] in ('', '判定待ち')]
    L = ['# AIの作業待ち（機械が毎朝書く・手で直さない）', '',
         '> `bin/web_tracking/seo_action_bridge.py`（mini 毎朝）が改善ログから書き出す。**有璽氏が押さなくても回すための一覧。**',
         '> 1件でもあれば、いまのセッションの区切りで担当 **ウソップ（search-growth）** の手順で片づける。'
         '公開を伴う直しは★直す前／直した後を有璽氏に見せてから。正本＝Notion改善ログ。', '',
         '更新：%s　実施待ち %d件／効果判定 %d件' % (dt.datetime.now(JST).strftime('%Y-%m-%d %H:%M'), len(todo), len(judge)), '']
    if todo:
        L.append('## 実施待ち（有璽氏が「AIに任せる」と回答済み）')
        L += ['- [%s] %s（%s・%s）%s' % (r['site'], r['title'], r['area'], r['state'], r['url']) for r in todo]
        L.append('')
    if judge:
        L.append('## 効果判定の時期（実施日から%d日）' % EFFECT_DAYS)
        L += ['- [%s] %s（実施 %s）%s' % (r['site'], r['title'], r['done'], r['url']) for r in judge]
        L.append('')
    if not todo and not judge:
        L.append('なし')
    text = '\n'.join(L) + '\n'
    old = open(QUEUE_MD, encoding='utf-8').read() if os.path.exists(QUEUE_MD) else ''
    strip = lambda s: '\n'.join(x for x in s.splitlines() if not x.startswith('更新：'))
    if DRY:
        print(text)
        return len(todo), len(judge), False
    if strip(old) == strip(text):
        return len(todo), len(judge), False          # 中身が同じなら書かない（毎朝の空コミットを作らない）
    open(QUEUE_MD, 'w', encoding='utf-8').write(text)
    rel = os.path.relpath(QUEUE_MD, REPO)
    subprocess.run(['git', '-C', REPO, 'add', '--', rel], check=True)          # ★このファイルだけ（git add -A は使わない）
    subprocess.run(['git', '-C', REPO, 'commit', '-q', '-m', 'AI_QUEUE：実施待ち%d件・効果判定%d件（seo_action_bridge 自動）'
                    % (len(todo), len(judge)), '--', rel], check=True)
    return len(todo), len(judge), True


def beat(ok, msg):
    if DRY:
        return
    try:
        from heartbeat import beat as hb
        hb(PROC_NAME, '成功' if ok else '失敗', msg)
    except Exception as ex:
        sys.stderr.write('心拍を送れず：%s\n' % ex)


def main():
    log = rows()
    moved = apply_answers(log)
    n = set_check_dates(log)
    t, j, wrote = write_queue(log)
    msg = 'OK 回答の反映%d件・効果を見る日%d件・作業待ち 実施%d／判定%d%s' % (len(moved), n, t, j, '（AI_QUEUE更新）' if wrote else '')
    for m in moved:
        print(' ', m)
    print(msg)
    beat(True, msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        beat(False, 'NG %s' % str(ex)[:200])
        raise
