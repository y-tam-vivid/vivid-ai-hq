#!/bin/bash
# ★有璽氏が手で1回叩くための適用スクリプト（2026-08-29 ピタゴラス作成）
#
# 背景：.claude/skills/customer-db-sync/references/targets.md への Edit/Write は
# ビビ・ピタゴラスどちらも「don't ask mode」で拒否される（実測・構造的な制約）。
# この1本は AI のツールを経由せず、有璽氏本人のターミナル操作として実行する前提。
#
# やること：
#   ① 現行 targets.md を ~/.vivid-relay/ へバックアップ
#   ② _pending_targets_md_replacement.md の本体（先頭のHTMLコメントを除く）を
#      targets.md へ上書き
#   ③ 適用後、一時ファイルを削除
#   ④ ./check.sh を実行して確認
#
# 使い方：
#   cd ~/vivid-ai-hq && bash bin/apply_targets_md_replacement.sh
set -euo pipefail

REPO="$HOME/vivid-ai-hq"
SRC="$REPO/_pending_targets_md_replacement.md"
DST="$REPO/.claude/skills/customer-db-sync/references/targets.md"
BK="$HOME/.vivid-relay/targets_bk_apply_$(date +%Y%m%d-%H%M%S).md"

if [ ! -f "$SRC" ]; then
  echo "★適用元が見つかりません: $SRC"
  echo "  既に適用済み、または削除済みの可能性があります。"
  exit 1
fi

if [ ! -f "$DST" ]; then
  echo "★適用先が見つかりません: $DST"
  exit 1
fi

mkdir -p "$HOME/.vivid-relay"
cp "$DST" "$BK"
echo "バックアップ: $BK"

# 先頭のHTMLコメント（<!-- ... -->）を除いた本体だけを書く
LINE=$(grep -n '^-->$' "$SRC" | head -1 | cut -d: -f1)
if [ -z "$LINE" ]; then
  echo "★想定外の形式です（終端の --> が見つかりません）。適用を中止します。"
  exit 1
fi
tail -n +$((LINE + 1)) "$SRC" > "$DST"

echo "適用しました: $DST"
rm -f "$SRC"
echo "一時ファイルを削除しました: $SRC"

# 副産物：cross-check/SKILL.md:138「フック3本の生存点検」が実物（4本）と食い違っている件
# （2026-08-29 stale_copy_finder.py が検出・実物で裏取り済み。ビビ依頼で同梱）
CC="$REPO/.claude/skills/cross-check/SKILL.md"
if grep -q 'フック3本の生存点検' "$CC" 2>/dev/null; then
  CC_BK="$HOME/.vivid-relay/cross_check_skill_bk_$(date +%Y%m%d-%H%M%S).md"
  cp "$CC" "$CC_BK"
  echo "バックアップ: $CC_BK"
  sed -i '' 's/フック3本の生存点検/フック4本の生存点検/' "$CC"
  echo "適用しました: $CC （フック3本→4本）"
else
  echo "cross-check/SKILL.md は既に修正済み、または該当箇所が見つかりません（スキップ）"
fi

echo
echo "=== ./check.sh ==="
cd "$REPO"
./check.sh
