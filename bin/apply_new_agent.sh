#!/bin/bash
# 営業オペレーション調整役（ジンベエ）の担当定義を .claude/agents/ へ置く
#
# なぜ人の手が要るか
#   .claude/agents/ 配下への Write は、MacBook でも mini でも拒否される（2026-09-07 実測）。
#   Bash 経由なら通ってしまう場合があるが、それは意図的なガードの迂回にあたるので使わない。
#   ★人の手のターミナル操作は、この拒否と無関係に通る。過去に
#   apply_targets_md_replacement.sh / apply_fukuchi_core_layer0.sh で同じ形を使っている。
#
# 使い方
#   cd ~/vivid-ai-hq && bash bin/apply_new_agent.sh
#
# やること
#   ① 置き先が空いていることを確かめる（既に在れば中止・上書きしない）
#   ② bin/_pending_new_agent.md を .claude/agents/sales-ops-coordinator.md へ置く
#   ③ 置けたことを実物で確かめる（行数・先頭のname行）
#   ④ 一時ファイルを消す
#   ⑤ ./check.sh を通す
#   ⑥ commit する（push は vivid-sync.sh が自動でやる）

set -eu

REPO="$HOME/vivid-ai-hq"
SRC="$REPO/bin/_pending_new_agent.md"
DST="$REPO/.claude/agents/sales-ops-coordinator.md"

cd "$REPO"

echo "── ① 前提を確かめる ──────────────────────────────"
if [ ! -f "$SRC" ]; then
  echo "★中止： $SRC がありません。ビビへ「置き直して」と伝えてください。"
  exit 1
fi
if [ -e "$DST" ]; then
  echo "★中止： $DST が既にあります。上書きしません。"
  echo "  → 中身を見比べたうえで、どうするかを決めてください。"
  exit 1
fi
BEFORE=$(ls "$REPO/.claude/agents/"*.md | wc -l | tr -d ' ')
echo "  いまの担当の数： ${BEFORE}体"
echo "  置く先        ： .claude/agents/sales-ops-coordinator.md"
echo "  元            ： bin/_pending_new_agent.md（$(wc -l < "$SRC" | tr -d ' ')行）"

echo
echo "── ② 置く ────────────────────────────────────────"
cp "$SRC" "$DST"

echo "── ③ 置けたことを実物で確かめる ──────────────────"
AFTER=$(ls "$REPO/.claude/agents/"*.md | wc -l | tr -d ' ')
echo "  担当の数： ${BEFORE}体 → ${AFTER}体"
if [ "$AFTER" != "$((BEFORE + 1))" ]; then
  echo "★おかしい： 1体だけ増えるはずが、そうなっていません。中止します。"
  exit 1
fi
echo "  先頭の name 行："
grep -m1 '^name:' "$DST" | sed 's/^/    /'
echo "  行数： $(wc -l < "$DST" | tr -d ' ')行"
if ! grep -q '^name: sales-ops-coordinator$' "$DST"; then
  echo "★おかしい： name が想定と違います。中止します。"
  exit 1
fi

echo
echo "── ④ 一時ファイルを消す ──────────────────────────"
rm -f "$SRC"
echo "  消した： bin/_pending_new_agent.md"

echo
echo "── ⑤ check.sh を通す ─────────────────────────────"
if [ -x "$REPO/check.sh" ]; then
  ./check.sh || echo "  ★check.sh が赤を出しました。中身を読んでから commit してください。"
else
  echo "  （check.sh が見つからないので飛ばします）"
fi

echo
echo "── ⑥ commit ──────────────────────────────────────"
git add .claude/agents/sales-ops-coordinator.md bin/_pending_new_agent.md 2>/dev/null || true
git commit -q -m "営業オペレーション調整役（ジンベエ）を新設

2026-09-07 有璽氏の指示「エージェントを増やした方が動きやすいのであれば増やしてね。
営業の管理みたいな人間をエージェントとして置く」を受けた新設。
★14体中 営業専任0で「毎日の運用を回す」役の持ち主が居なかった。

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>" && echo "  commit した（push は vivid-sync.sh が15分以内に自動でやります）"

echo
echo "════════════════════════════════════════════════════"
echo " 終わりました。★担当が ${AFTER}体 になりました。"
echo " 次にセッションを立て直すと、ジンベエが呼べるようになります。"
echo "════════════════════════════════════════════════════"
