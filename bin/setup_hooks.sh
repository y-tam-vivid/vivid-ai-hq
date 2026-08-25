#!/bin/bash
# フックを この機械へ入れる（★15分ごとに vivid-sync.sh から自動で呼ばれる）
#
# なぜ要るか（2026-08-20）
#   ~/.claude/settings.json は絶対パスを含むため git で配れない。
#   ~/.vivid-relay/ も git 管理外。
#   → フックが mini にしか無く、他機は同じ失敗を繰り返す状態だった。
#   このスクリプトが、その差を埋める。
#
# ★2026-08-26 有璽氏「毎回するのが手間。それぞれが自動で入るようにできないか」
#   → 「新しい機械で1回だけ実行する」を人の記憶に預けるのをやめ、
#     vivid-sync.sh（*/15・両機）から毎回呼ぶ形にした。
#     以後は bin/hooks/ に置いて下の SPEC へ1行足すだけで、15分以内に両機へ入る。
#   → memory/reference_fix_where_git_reaches.md
#
# ★機械ローカルの設定を触る＝壊れると Claude Code が起動しなくなる。だから3つ守る。
#     ① 書く前にバックアップ（1世代・.bak）
#     ② JSON として読めなければ1バイトも触らない（壊れた設定を上書きしない）
#     ③ 変更が無ければ書かない（15分ごとに mtime を動かさない）
#
# 使い方
#   bash bin/setup_hooks.sh            静かに揃える（差分があるときだけ出力）
#   bash bin/setup_hooks.sh --verbose  何をしたか全部出す

set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.vivid-relay"
SETTINGS="$HOME/.claude/settings.json"
VERBOSE=0
[ "${1:-}" = "--verbose" ] && VERBOSE=1

say() { [ "$VERBOSE" = "1" ] && echo "$1"; return 0; }

mkdir -p "$DEST" "$(dirname "$SETTINGS")" || exit 1

# ① 実体を配る（中身が同じならコピーしない＝mtime を無駄に動かさない）
copied=0
for f in "$REPO"/bin/hooks/*.py; do
  [ -e "$f" ] || continue
  b="$(basename "$f")"
  if [ ! -f "$DEST/$b" ] || ! cmp -s "$f" "$DEST/$b"; then
    cp "$f" "$DEST/$b" && copied=$((copied+1))
    echo "置いた ： $DEST/$b"
  else
    say "同じ ： $DEST/$b"
  fi
done

# ② settings.json へ登録する
/usr/bin/python3 - "$SETTINGS" "${VERBOSE}" <<'PY'
import json, os, shutil, sys

p, verbose = sys.argv[1], sys.argv[2] == '1'

# ★JSON として読めなければ触らない（壊れた設定を上書きして起動不能にしない）
if os.path.exists(p):
    try:
        raw = open(p, encoding='utf-8').read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print('★settings.json が読めないので触らない: %s' % e)
        sys.exit(0)
else:
    raw, d = '', {}

before = json.dumps(d, ensure_ascii=False, sort_keys=True)

# ここに1行足せば、15分以内に両機へ入る（イベント名, ファイル名, matcher, timeout秒）
SPEC = [
    ('PreToolUse',       'hook_inject_memory.py',      'Bash|Write|Edit|mcp__.*', 10),
    ('UserPromptSubmit', 'hook_catch_correction.py',   None,                      10),
    ('PermissionRequest','hook_permission_slack.py',   None,                      10),
    ('Stop',             'hook_session_writeback.py',  None,                      15),
]

hooks = d.setdefault('hooks', {})
added = []
for ev, f, matcher, timeout in SPEC:
    cmd = '/usr/bin/python3 $HOME/.vivid-relay/%s' % f
    arr = hooks.setdefault(ev, [])
    if any(any(h.get('command') == cmd for h in b.get('hooks', [])) for b in arr):
        continue
    blk = {'hooks': [{'type': 'command', 'command': cmd, 'timeout': timeout}]}
    if matcher:
        blk['matcher'] = matcher
    arr.append(blk)
    added.append('%s / %s' % (ev, f))

# 承認を減らす（規範「既定は自分で進める」に合わせる）
d.setdefault('permissions', {}).setdefault('defaultMode', 'dontAsk')

after = json.dumps(d, ensure_ascii=False, sort_keys=True)

# ③ 変更が無ければ書かない
if before == after:
    if verbose:
        print('settings.json は既に揃っている（%d件のフック定義）' % len(SPEC))
    sys.exit(0)

if raw:
    shutil.copy2(p, p + '.bak')
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('settings.json を更新: ' + (', '.join(added) if added else '設定値の補完のみ'))
PY

# ③ 地雷インデックスと生存点検（失敗しても止めない）
if [ "$copied" -gt 0 ] || [ "$VERBOSE" = "1" ]; then
  /usr/bin/python3 "$DEST/build_landmine_index.py" --quiet 2>/dev/null && say "地雷インデックスを作った"
fi
[ "$VERBOSE" = "1" ] && /usr/bin/python3 "$DEST/hook_selfcheck.py" 2>/dev/null
exit 0
