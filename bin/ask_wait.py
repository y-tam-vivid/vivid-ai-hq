#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack のボタンの回答を待ち、押されたら終わる ── セッションを起こすための待ち役

なぜ要るか（2026-10-17 有璽氏「8時5分に入れてるのに、なんで今もまだ通知されてないの」）
  回答はフック（hook_ask_answers.py）で届くが、フックは★有璽氏が次に話しかけたときしか動かない。
  問いを出してターンを終えると、押されても誰も起きない（10/5・10/15・10/17 と同じ型）。
  Claude Code の「バックグラウンドで実行」は、終わったときにセッションを起こす。
  ★だから問いを出したら、この待ち役をバックグラウンドで走らせてからターンを終える。

使い方
  python3 bin/ask_wait.py 47be69 [47be69 ...]   （Bash の run_in_background で呼ぶ）
  どれか1件が押されたら、その回答を出して終わる。既定の上限は12時間（--hours で変える）。
"""

import sys
import json
import time
import argparse
import subprocess

REMOTE = r'''python3 - "$@" <<"PY"
import json,os,sys
q=json.load(open(os.path.expanduser("~/.vivid-relay/ask_hub_queue.json"))).get("items",{})
out={}
for k in sys.argv[1:]:
    v=q.get(k) or {}
    a=v.get("answer") or {}
    out[k]={"status":v.get("status"),"label":a.get("label"),"free_text":a.get("free_text"),"at":a.get("at"),"subject":v.get("subject")}
print(json.dumps(out,ensure_ascii=False))
PY'''


def check(ids):
    cmd = ['ssh', '-o', 'ConnectTimeout=5', '-o', 'BatchMode=yes', 'mini', 'bash', '-s', '--'] + ids
    r = subprocess.run(cmd, input=REMOTE, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout or '{}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ids', nargs='+')
    ap.add_argument('--hours', type=float, default=12)
    ap.add_argument('--every', type=int, default=30)
    a = ap.parse_args()
    ids = [i.lstrip('#') for i in a.ids]
    end = time.time() + a.hours * 3600
    while time.time() < end:
        try:
            st = check(ids)
        except Exception:
            st = None
        if st:
            done = {k: v for k, v in st.items() if v.get('status') == 'answered'}
            if done:
                for k, v in done.items():
                    ft = f' ／記述:「{v["free_text"]}」' if v.get('free_text') else ''
                    print(f'★回答あり #{k} {v.get("at")} {v.get("subject")} → {v.get("label")}{ft}')
                rest = [k for k in ids if k not in done]
                if rest:
                    print('まだ押されていない：' + ' '.join('#' + k for k in rest))
                return 0
        time.sleep(a.every)
    print('上限の時間まで押されなかった：' + ' '.join('#' + k for k in ids))
    return 1


if __name__ == '__main__':
    sys.exit(main())
