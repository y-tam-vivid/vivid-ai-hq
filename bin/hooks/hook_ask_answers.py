#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack のボタンで押された回答を、毎ターン会話へ差し込む ── UserPromptSubmit フック

なぜ要るか（2026-10-14 有璽氏）
  「Slackでボタンを押したのに確認が遅れているケースが多い。どうやって判断してるのか」
  ask_hub は回答を mini の ask_hub_queue.json に書くだけで、セッションへ届く経路が無かった。
  10/7 に「ターン末に answered を数える」と規則にしたが守られず、10/14 に再発（1分で押された3件を見落とし）。
  ★規則ではなく必ず届く経路へ置く。

やること
  ① 台帳を読む（mini は手元・それ以外は ssh mini。届かなければ黙って抜ける）
  ② このセッションでまだ見せていない回答（直近12時間）を additionalContext へ出す
  ③ 見せたものを ~/.vivid-relay/ask_answers_seen/<session_id>.json に覚える

★止めない。ブロックしない。何も無ければ何も出さない。
"""

import os
import sys
import json
import datetime
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(HERE, 'ask_hub_queue.json')
SEEN_DIR = os.path.join(HERE, 'ask_answers_seen')
WINDOW_H = 12

# mini 側で回答済みだけを小さく返す（台帳全体を運ばない）
REMOTE = r'''python3 - <<"PY"
import json,os
q=json.load(open(os.path.expanduser("~/.vivid-relay/ask_hub_queue.json")))
out=[]
for k,v in q.get("items",{}).items():
    a=v.get("answer") or {}
    if v.get("status")=="answered" and a.get("at"):
        out.append({"id":k,"subject":v.get("subject",""),"asked_by":v.get("asked_by",""),
                    "label":a.get("label",""),"free_text":a.get("free_text"),"at":a.get("at")})
print(json.dumps(out,ensure_ascii=False))
PY'''


def load_answers():
    if os.path.exists(QUEUE):
        q = json.load(open(QUEUE))
        out = []
        for k, v in q.get('items', {}).items():
            a = v.get('answer') or {}
            if v.get('status') == 'answered' and a.get('at'):
                out.append({'id': k, 'subject': v.get('subject', ''), 'asked_by': v.get('asked_by', ''),
                            'label': a.get('label', ''), 'free_text': a.get('free_text'), 'at': a.get('at')})
        return out
    r = subprocess.run(['ssh', '-o', 'ConnectTimeout=2', '-o', 'BatchMode=yes', 'mini', REMOTE],
                       capture_output=True, text=True, timeout=6)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout or '[]')


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    sid = (data.get('session_id') or 'nosession').replace('/', '_')
    try:
        answers = load_answers()
    except Exception:
        return
    if not answers:
        return

    os.makedirs(SEEN_DIR, exist_ok=True)
    seen_path = os.path.join(SEEN_DIR, sid + '.json')
    try:
        seen = set(json.load(open(seen_path)))
    except Exception:
        seen = set()

    since = (datetime.datetime.now() - datetime.timedelta(hours=WINDOW_H)).strftime('%Y-%m-%d %H:%M')
    new = [a for a in answers if a['at'] >= since and a['id'] not in seen]
    if not new:
        return
    new.sort(key=lambda a: a['at'])

    lines = ['★Slackのボタンで有璽氏が回答した判断があります（このセッションでは初めて見せるもの）。',
             '自分（または自分の担当）が出した問いなら、★この回答を前提に動くこと。「回答待ち」と書かないこと。']
    for a in new:
        ft = f' ／記述:「{a["free_text"]}」' if a.get('free_text') else ''
        lines.append(f'- #{a["id"]} {a["at"]} 【{a["asked_by"]}】{a["subject"]} → {a["label"]}{ft}')

    seen.update(a['id'] for a in new)
    tmp = seen_path + '.tmp'
    json.dump(sorted(seen), open(tmp, 'w'))
    os.replace(tmp, seen_path)

    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit',
                                             'additionalContext': '\n'.join(lines)}}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
