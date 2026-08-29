#!/bin/bash
# ★有璽氏が手で1回叩くための適用スクリプト（2026-08-29 ピタゴラス作成）
#
# 背景：有璽氏が「規範の変更実行」を承認した1経路断定禁止の追記
# （_pending_fukuchi_core_layer0.md）を .claude/skills/fukuchi-core/SKILL.md へ
# 反映する。この配下への Edit/Write はビビ・ピタゴラスどちらも「don't ask mode」
# （今日入れた ask 設定）で拒否される（実測・意図どおりの防御）。
# この1本は AI のツールを経由せず、有璽氏本人のターミナル操作として実行する前提。
#
# なぜ規範へ上げるか（検査3＝1経路断定の機械検問の実測結果）
#   実transcript 236ファイル・953ターンで計測したところ、断定語を含むターンが70%、
#   うち1経路以下が断定ターンの28%あった。hook_output_guardの「88本で誤検知0件」とは
#   桁違いに高い比率で、機械でブロックすると「うるさくて読まれなくなる」を確実に踏む。
#   ＝ 機械の検問では止められない領域が残る。だから型（規範）で守る。
#
# やること：
#   ① 現行 SKILL.md を ~/.vivid-relay/ へバックアップ
#      （★2026-08-29 17:53 にビビが既に fukuchi-core_bk_20260829-175358.md を
#      取得済みだが、このスクリプト単体でも独立して動くよう自前でも取る）
#   ② _pending_fukuchi_core_layer0.md の内容を、SKILL.md の
#      「### 3. 確実性をどう扱うか」節の末尾
#      （「事前に定義できないものを早急に言語化しようとしない。」の直後・
#        「### 4. どう進めるか」の直前）へ挿入
#      ★挿入位置のマーカーが見つからない・順序が不正なら中止し、SKILL.md は
#      一切変更しない（Pythonブロックがファイルへ書き込む前に判定する）
#   ③ 適用後、一時ファイル _pending_fukuchi_core_layer0.md を削除
#   ④ ./check.sh を実行して確認
#   ⑤ 触ったファイルを明示して commit → bash bin/vivid-sync.sh
#
# ★事前にロジックを別ファイルで実測済み（挿入成功ケース・マーカー不在での中止ケースの
#   両方を確認）。このスクリプト自体は本番の SKILL.md に対して実行されるのは初めて。
#
# 使い方：
#   cd ~/vivid-ai-hq && bash bin/apply_fukuchi_core_layer0.sh
set -euo pipefail

REPO="$HOME/vivid-ai-hq"
SRC="$REPO/_pending_fukuchi_core_layer0.md"
DST="$REPO/.claude/skills/fukuchi-core/SKILL.md"
BK="$HOME/.vivid-relay/fukuchi-core_bk_apply_$(date +%Y%m%d-%H%M%S).md"
MARKER_BEFORE="事前に定義できないものを早急に言語化しようとしない。"
MARKER_AFTER="### 4. どう進めるか"

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

python3 - "$SRC" "$DST" "$MARKER_BEFORE" "$MARKER_AFTER" << 'PYEOF'
import sys
src, dst, marker_before, marker_after = sys.argv[1:5]
content = open(dst, encoding='utf-8').read()
pending = open(src, encoding='utf-8').read()

idx_before = content.find(marker_before)
idx_after = content.find(marker_after)
if idx_before < 0 or idx_after < 0 or idx_after <= idx_before:
    print("★想定外の形式です（挿入位置が見つからない、または順序が不正）。適用を中止します。")
    print("SKILL.md は変更していません。")
    sys.exit(1)

insert_pos = content.find('\n', idx_before)
if insert_pos < 0:
    print("★想定外の形式です（marker_beforeの後に改行がありません）。適用を中止します。")
    print("SKILL.md は変更していません。")
    sys.exit(1)
insert_pos += 1

new_content = content[:insert_pos] + pending.rstrip('\n') + '\n\n' + content[insert_pos:]
open(dst, 'w', encoding='utf-8').write(new_content)
print("適用しました: 挿入位置を特定して書き込みました")
PYEOF

echo "適用しました: $DST"
rm -f "$SRC"
echo "一時ファイルを削除しました: $SRC"

echo
echo "=== ./check.sh ==="
cd "$REPO"
./check.sh

echo
echo "=== commit ==="
git add "$DST"
git add "$SRC" 2>/dev/null || true
git status --short -- "$DST" "$SRC"

git commit -m "$(cat <<'EOF'
fukuchi-core/SKILL.mdへLayer0(1経路断定禁止・型で守る規範)を追加

有璽氏承認済み。検査3(1経路断定の機械検問)を実データで計測したところ
（953ターン中70%が断定語ヒット・うち28%が1経路以下）、機械でブロックすると
誤爆で読まれなくなると判明したため、機械では止められない領域として
型（規範）で守る方針に切り替えた。
EOF
)"

echo
echo "=== vivid-sync.sh ==="
bash bin/vivid-sync.sh
