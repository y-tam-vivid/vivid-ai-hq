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
  # 索引は MEMORY.md（全体）と memory/INDEX_*.md（分野別）の複数枚に分かれている。
  # ★どれか1枚に載っていればよい。1枚も載っていないものは孤児 → memory/project_memory_layer_design.md
  idxfiles=$(ls memory/MEMORY.md memory/INDEX_*.md 2>/dev/null)
  orph=0
  for f in memory/*.md; do
    [ -e "$f" ] || continue
    b=$(basename "$f")
    case "$b" in MEMORY.md|INDEX_*.md) continue ;; esac
    grep -q "($b)" $idxfiles 2>/dev/null || { fail "どの索引にも無い: $b"; orph=1; }
  done
  cat $idxfiles 2>/dev/null | grep -o '](\([^)]*\.md\))' | sed 's/](\(.*\))/\1/' | sort -u | while read -r f; do
    case "$f" in _archive/*) [ -f "memory/$f" ] || echo "  ✗ 索引が指すファイルが無い: $f" ; continue ;; esac
    [ -f "memory/$f" ] || echo "  ✗ 索引が指すファイルが無い: $f"
  done
  # 担当別対応表が指す分野索引が実在するか
  if [ -f memory/INDEX_担当別.md ]; then
    grep -o '](INDEX_[^)]*\.md)' memory/INDEX_担当別.md | sed 's/](\(.*\))/\1/' | sort -u | while read -r f; do
      [ -f "memory/$f" ] || echo "  ✗ 担当別が指す分野索引が無い: $f"
    done
  else
    fail "memory/INDEX_担当別.md が無い（担当ごとの常設セットの正本）"
    orph=1
  fi
  # MEMORY.md は毎ターン届く。上限を超えたら末尾が黙って落ちる
  msz=$(wc -c < memory/MEMORY.md | tr -d ' ')
  if [ "$msz" -gt 24986 ]; then
    fail "MEMORY.md が上限超過: ${msz} バイト（上限 24986）→ 分野索引へ降ろす"
    orph=1
  elif [ "$msz" -gt 20000 ]; then
    say "  △ MEMORY.md ${msz} バイト（上限 24986 に接近）"
  fi
  [ $orph -eq 0 ] && ok "memory索引に孤児なし ($(ls memory/*.md 2>/dev/null | wc -l | tr -d ' ') 本 / MEMORY.md ${msz}B)"
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


say "── 6. リポジトリ外に取り残された .md が無いか（抜け漏れ検出）"
missing=0
while IFS= read -r f; do
  b=$(basename "$f")
  find . -name "$b" -not -path "./.git/*" | grep -q . || { fail "repo未収録: ${f#$HOME/.claude/}"; missing=1; }
done < <(find "$HOME/.claude" -name "*.md" \
           -not -path "*/paste-cache/*" -not -path "*/file-history/*" \
           -not -path "*/plugins/*" -not -path "*/sessions/*" -not -path "*/tasks/*" \
           -not -path "*/cache/*" -not -path "*/plans/*" \
           -not -name "SYNC_STATUS.md" 2>/dev/null)
# SYNC_STATUS.md は repo に入れない。機械ごとに中身が違い、機械が15分ごとに上書きするため
# （git に入れると毎回コンフリクトする）。実体は bin/vivid-sync.sh が書く
[ $missing -eq 0 ] && ok "~/.claude 配下の .md はすべて repo に存在する"

say "── 7. バージョン違いの散乱"
sprawl=$(find . "$HOME/bin" -maxdepth 3 \( -name "*_v[0-9]*" -o -name "*_backup*" -o -name "*_old*" -o -name "*コピー*" -o -name "*最新*" \) -not -path "./.git/*" -not -path "./_archive/*" 2>/dev/null)
if [ -n "$sprawl" ]; then
  fail "版が並んでいるファイル（_archive/ へ集約すること）:"
  printf '      %s\n' $sprawl
else
  ok "版の並存なし"
fi

say "── 8. パスの二重定義（documentation drift・穴A型）"
# ★2026-08-29 新設。self_audit.py が hook_role_guard.py の LOG 定数と別に
#   独自パスを持ち、実物ログが9,455バイトあるのに「まだ稼働していない」と
#   言い続けていた事故（穴A）を機械的に検出する。★助言のみ・exit 1 にはしない
#   （実害の有無は人が判断する必要があるため。現状2件は値としては実質同じ場所を
#   指しており、破綻ではなく書き方の不統一）。
if [ -f bin/check_path_duplication.py ]; then
  dup_out=$(python3 bin/check_path_duplication.py 2>&1)
  if echo "$dup_out" | grep -q "★重複定義の疑い"; then
    say "  △ パスが複数箇所で異なる書き方で定義されています（助言・ブロックしない）:"
    echo "$dup_out" | sed 's/^/      /'
  else
    ok "パスの二重定義なし"
  fi
else
  say "  － bin/check_path_duplication.py が無い"
fi

say ""
[ $NG -eq 0 ] && { say "✅ ズレなし"; exit 0; } || { say "❌ ズレを検出。上記を解消してから commit すること"; exit 1; }
