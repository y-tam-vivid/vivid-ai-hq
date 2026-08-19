#!/bin/bash
# フックを この機械へ入れる（新しい機械・新しい面で1回だけ実行する）
#
# なぜ要るか（2026-08-20）
#   ~/.claude/settings.json は絶対パスを含むため git で配れない。
#   ~/.vivid-relay/ も git 管理外。
#   → フックが mini にしか無く、他機は同じ失敗を繰り返す状態だった。
#   このスクリプトが、その差を埋める。
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.vivid-relay"
SETTINGS="$HOME/.claude/settings.json"

mkdir -p "$DEST"
for f in "$REPO"/bin/hooks/*.py; do
  cp "$f" "$DEST/"
  echo "置いた ： $DEST/$(basename "$f")"
done

/usr/bin/python3 - "$SETTINGS" <<'PY'
import json,os,sys
p=sys.argv[1]
d=json.load(open(p)) if os.path.exists(p) else {}
hooks=d.setdefault('hooks',{})
SPEC=[('PreToolUse','hook_inject_memory.py','Bash|Write|Edit|mcp__.*'),
      ('UserPromptSubmit','hook_catch_correction.py',None),
      ('PermissionRequest','hook_permission_slack.py',None)]
n=0
for ev,f,matcher in SPEC:
    cmd='/usr/bin/python3 $HOME/.vivid-relay/%s' % f
    arr=hooks.setdefault(ev,[])
    if any(any(h.get('command')==cmd for h in b.get('hooks',[])) for b in arr): continue
    blk={'hooks':[{'type':'command','command':cmd,'timeout':10}]}
    if matcher: blk['matcher']=matcher
    arr.append(blk); n+=1
# 承認を減らす（規範「既定は自分で進める」に合わせる）
perms=d.setdefault('permissions',{})
perms.setdefault('defaultMode','dontAsk')
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2)
print('settings.json へ %d件のフックを登録' % n)
PY

/usr/bin/python3 "$DEST/build_landmine_index.py" --quiet && echo "地雷インデックスを作った"
/usr/bin/python3 "$DEST/hook_selfcheck.py" || true
echo
echo "★cron へ次を足すこと（この機械で定期実行する場合）"
echo "  20 8 * * * /usr/bin/python3 \$HOME/.vivid-relay/hook_selfcheck.py"
echo "  25 8 * * * /usr/bin/python3 \$HOME/.vivid-relay/build_landmine_index.py --quiet"
