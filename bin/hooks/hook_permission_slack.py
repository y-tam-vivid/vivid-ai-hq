#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
承認ダイアログ（イエス／ノー）が出たら Slack へ知らせる

  Claude Code の PermissionRequest フックから呼ばれる。
  stdin に {"tool_name":..., "tool_input":{...}} が来る。

なぜ要るか（2026-08-20 有璽氏）
  「この合間に挟むイエスノーってやつを、Slackでも出るようにしろ」
  ── 端末を見ていないと、承認待ちで止まっていることに気づけない。
     止まっているのに本人が知らないなら、それは止まっているのではなく消えている。

★通知するだけ。承認そのものは端末で行う（フックからは代行しない）。
★通知の失敗で本体を止めない。必ず exit 0 で終わる。
★同じ内容の連投を避けるため、直前と同じなら送らない。
"""

import os
import sys
import json
import time
import hashlib
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DM = 'D0AT4NQ6X7D'
LAST = os.path.join(HERE, '.hook_last_notify.json')
COOLDOWN = 90          # 秒。同じ内容はこの間に再送しない


def tok():
    try:
        for line in open(os.path.join(HERE, 'config.env')):
            if line.startswith('SLACK_BOT_TOKEN='):
                return line.split('=', 1)[1].strip().strip('"')
    except Exception:
        pass
    return None


def post(text):
    t = tok()
    if not t:
        return
    try:
        r = urllib.request.Request(
            'https://slack.com/api/chat.postMessage',
            data=json.dumps({'channel': DM, 'text': text, 'unfurl_links': False}).encode(),
            headers={'Authorization': 'Bearer ' + t,
                     'Content-Type': 'application/json; charset=utf-8'})
        urllib.request.urlopen(r, timeout=8)
    except Exception:
        pass


def brief(tool, inp):
    """何を承認しようとしているかを1〜2行で"""
    if tool == 'Bash':
        cmd = str(inp.get('command', ''))[:300]
        desc = str(inp.get('description', ''))
        return ('```%s```' % cmd) + (('\n' + desc) if desc else '')
    if tool in ('Write', 'Edit', 'NotebookEdit'):
        return '`%s`' % inp.get('file_path', '（不明）')
    if tool.startswith('mcp__'):
        parts = tool.split('__')
        svc = parts[1] if len(parts) > 1 else '?'
        act = parts[2] if len(parts) > 2 else '?'
        return '%s の %s' % (svc, act)
    keys = [k for k in list(inp.keys())[:4]]
    return '引数 ： %s' % ' / '.join(keys) if keys else ''


def main():
    try:
        raw = sys.stdin.read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        d = {}
    tool = d.get('tool_name', '（不明）')
    inp = d.get('tool_input', {}) or {}

    body = brief(tool, inp)
    key = hashlib.md5(('%s|%s' % (tool, body)).encode()).hexdigest()

    # 同じ内容の連投を避ける
    try:
        if os.path.exists(LAST):
            prev = json.load(open(LAST))
            if prev.get('key') == key and time.time() - prev.get('at', 0) < COOLDOWN:
                print(json.dumps({'suppressOutput': True}))
                return
    except Exception:
        pass
    try:
        json.dump({'key': key, 'at': time.time()}, open(LAST, 'w'))
    except Exception:
        pass

    post('⏸ *承認待ちで止まっています*  _（端末で「はい／いいえ」を押してください）_\n'
         '*%s*\n%s' % (tool, body))
    print(json.dumps({'suppressOutput': True}))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
    sys.exit(0)      # ★何があっても本体を止めない
