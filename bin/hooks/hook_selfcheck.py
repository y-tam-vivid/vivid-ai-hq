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
 # ★2026-08-29 追加（穴B・ビビ指摘）。役割違反の検問2本がPreToolUseに登録されているのに
 #   生存点検の対象外だった＝唯一の強い機械ゲートの生死を点検の外に置いていた。
 #   Bashのリダイレクト書込み疑いは exit0+JSON なのでCASES向き。
 ('hook_role_guard.py','{"tool_name":"Bash","tool_input":{"command":"cat > /tmp/selfcheck_probe.py <<EOF"},"session_id":"selfcheck"}','additionalContext'),
 ('hook_output_guard.py','{"tool_name":"Write","tool_input":{"file_path":"/tmp/selfcheck_probe.py","content":"for x in [1]:\\n    if x:\\n        print(\\\"OK\\\")\\nprint(\\\"すべて正常\\\")\\n"}}','additionalContext'),
]
# ★JSONではなく素のテキストを返すフック（Stop フックはこの形）。
#   2026-08-29 つる追加。それまで CASES は3本しか無く、settings.json に登録されている
#   4本目（hook_session_writeback.py / Stop）を一度も点検していなかった。
#   ＝規範を機械で止める唯一のゲートが、壊れても毎朝「3本とも正常」と出る状態だった。
PLAIN_CASES=[
 ('hook_session_writeback.py','{"session_id":"selfcheck-probe","transcript_path":"/nonexistent","stop_hook_active":false}','書き戻し'),
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
for f,inp,expect in PLAIN_CASES:
    try:
        r=subprocess.run(['/usr/bin/python3',os.path.join(HERE,f)],input=inp,
                         capture_output=True,text=True,timeout=30)
        if expect not in (r.stdout or '')+(r.stderr or ''):
            ng.append('%s ： 反応しない' % f)
    except Exception as e:
        ng.append('%s ： %s' % (f,str(e)[:80]))
# settings.json に登録されているか
# ★Stop を 2026-08-29 に追加。settings.json は機械ローカル（git外）で手で編集されるため、
#   Stop の行が消えても誰も気づけなかった（それが唯一の機械ゲート）。
try:
    s=json.load(open(os.path.expanduser('~/.claude/settings.json')))
    for ev in ('PreToolUse','UserPromptSubmit','PermissionRequest','Stop'):
        if ev not in s.get('hooks',{}): ng.append('settings.json に %s が無い' % ev)
except Exception as e:
    ng.append('settings.json を読めない ： %s' % e)
# ★本数はベタ書きしない（数えた結果を出す）。bin/hooks/hook_output_guard.py の型
_n=len(CASES)+len(PLAIN_CASES)
print('★フック点検 ： %s' % ('異常 %d件' % len(ng) if ng else '%d本とも正常' % _n))
for x in ng: print('   '+x)
try:
    from heartbeat import beat
    beat('フックの生存点検','失敗' if ng else '成功', '／'.join(ng)[:180] or '%d本とも正常' % _n)
except Exception as e: sys.stderr.write('[心拍] %s\n'%e)
sys.exit(1 if ng else 0)
