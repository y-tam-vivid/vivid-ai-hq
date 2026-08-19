#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フックが生きているかを毎朝みる（⑥の穴：フックが壊れても気づかない）"""
import os,sys,json,subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
CASES=[
 ('hook_inject_memory.py','{"tool_name":"Bash","tool_input":{"command":"sheets_client"}}','additionalContext'),
 ('hook_catch_correction.py','{"prompt":"何回も言ってるやろ"}','additionalContext'),
 ('hook_permission_slack.py','{"tool_name":"Bash","tool_input":{"command":"ls"}}','suppressOutput'),
]
ng=[]
for f,inp,expect in CASES:
    try:
        r=subprocess.run(['/usr/bin/python3',os.path.join(HERE,f)],input=inp,
                         capture_output=True,text=True,timeout=20)
        d=json.loads(r.stdout or '{}')
        ok = expect in json.dumps(d) or expect in json.dumps(d.get('hookSpecificOutput',{}))
        if not ok: ng.append('%s ： 反応しない' % f)
    except Exception as e:
        ng.append('%s ： %s' % (f,str(e)[:80]))
# settings.json に登録されているか
try:
    s=json.load(open(os.path.expanduser('~/.claude/settings.json')))
    for ev in ('PreToolUse','UserPromptSubmit','PermissionRequest'):
        if ev not in s.get('hooks',{}): ng.append('settings.json に %s が無い' % ev)
except Exception as e:
    ng.append('settings.json を読めない ： %s' % e)
print('★フック点検 ： %s' % ('異常 %d件' % len(ng) if ng else '3本とも正常'))
for x in ng: print('   '+x)
try:
    from heartbeat import beat
    beat('フックの生存点検','失敗' if ng else '成功', '／'.join(ng)[:180] or '3本とも正常')
except Exception as e: sys.stderr.write('[心拍] %s\n'%e)
sys.exit(1 if ng else 0)
