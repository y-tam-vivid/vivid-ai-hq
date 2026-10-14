#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hook_ask_answers.py を ~/.claude/settings.json の UserPromptSubmit へ登録する（人が1回だけ叩く）。
控えを取ってから足す。既に入っていれば何もしない。"""
import os, json, shutil, datetime

p = os.path.expanduser('~/.claude/settings.json')
cmd = '/usr/bin/python3 $HOME/.vivid-relay/hook_ask_answers.py'
s = json.load(open(p))
ups = s.setdefault('hooks', {}).setdefault('UserPromptSubmit', [])
if any(h.get('command') == cmd for g in ups for h in g.get('hooks', [])):
    print('既に登録済み。何もしていません。')
else:
    bak = os.path.expanduser('~/.vivid-relay/_backups/claude_settings.json.bak_'
                             + datetime.datetime.now().strftime('%Y%m%d-%H%M'))
    os.makedirs(os.path.dirname(bak), exist_ok=True)
    shutil.copy2(p, bak)
    ups.append({'hooks': [{'type': 'command', 'command': cmd, 'timeout': 10}]})
    tmp = p + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
        f.write('\n')
    json.load(open(tmp))
    os.replace(tmp, p)
    print('登録しました。控え:', bak)
