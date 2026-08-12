#!/usr/bin/env bash
# 規範のズレ検出。commit前とセッション開始時に走らせる。
# 不一致があれば exit 1。
cd "$(dirname "$0")"
NG=0
say() { printf '%s\n' "$1"; }
fail() { printf '  ✗ %s\n' "$1"; NG=1; }
ok()   { printf '  ✓ %s\n' "$1"; }

CANON=.claude/skills/fukuchi-core/SKILL.md

say "── 1. 正本の存在"
[ -f "$CANON" ] && ok "$CANON ($(wc -l < $CANON | tr -d ' ')行)" || fail "正本が無い: $CANON"

say "── 2. 共通規範の本文が複製されていないか"
# 正本にしか存在してはいけない見出し
for h in "## 行動規範（Fable Style）" "## Notion運用ルール" "## 【必須】作業ログの自動記録" "## 情報ファイアウォール" "## モデル運用"; do
  hits=$(grep -rl "^$h" .claude/agents .claude/output-styles CLAUDE.md 2>/dev/null)
  if [ -n "$hits" ]; then
    fail "「$h」が正本の外に複製されている:"
    printf '      %s\n' $hits
  fi
done
[ $NG -eq 0 ] && ok "配布先に規範本文の複製なし"

say "── 3. 全エージェントが正本を参照しているか"
miss=0
for f in .claude/agents/*.md; do
  case "$(basename "$f")" in pr-playbook.md) continue;; esac
  grep -q "fukuchi-core" "$f" || { fail "$(basename $f): skills: fukuchi-core が無い"; miss=1; }
done
[ $miss -eq 0 ] && ok "$(ls .claude/agents/*.md | grep -vc pr-playbook) 体すべてが fukuchi-core を参照"

say "── 4. memory索引の整合"
if [ -d memory ]; then
  orph=0
  for f in memory/*.md; do
    [ -e "$f" ] || continue
    b=$(basename "$f"); [ "$b" = "MEMORY.md" ] && continue
    grep -q "($b)" memory/MEMORY.md || { fail "索引に無い: $b"; orph=1; }
  done
  grep -o '](\([^)]*\.md\))' memory/MEMORY.md 2>/dev/null | sed 's/](\(.*\))/\1/' | while read -r f; do
    [ -f "memory/$f" ] || echo "  ✗ 索引が指すファイルが無い: $f"
  done
  [ $orph -eq 0 ] && ok "memory索引に孤児なし ($(ls memory/*.md 2>/dev/null | wc -l | tr -d ' ') 本)"
else
  say "  － memory/ 未配置（A8で symlink 予定）"
fi

say "── 5. ローカル ~/.claude が本リポジトリを向いているか"
for p in agents skills output-styles; do
  t=$(readlink "$HOME/.claude/$p" 2>/dev/null)
  case "$t" in
    *vivid-ai-hq*) ok "~/.claude/$p → $t" ;;
    "") say "  － ~/.claude/$p は実体のまま（A8未実施）" ;;
    *) fail "~/.claude/$p が別の場所を指している: $t" ;;
  esac
done

say ""
[ $NG -eq 0 ] && { say "✅ ズレなし"; exit 0; } || { say "❌ ズレを検出。上記を解消してから commit すること"; exit 1; }
