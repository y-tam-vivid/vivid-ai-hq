#!/bin/bash
# bin/launchd/*.plist を、この機械の $HOME を埋めて設置する。★冪等（何度走らせても同じ）
#
# なぜ要るか ── 2026-09-13 有璽氏「自動で更新が継続的にかかる形でないと、この設計そのものが
#   意味ない。なんで止まってんのって話やし、止まらんように設計して」
#   ★cron は予定時刻に機械が寝ていると、その回を捨てる。MacBook は持ち運ぶので夜は必ず閉じている。
#   実測：2026-09-12 22:30 の使用量集計が飛んだ／Downloads整理は7回中2回（29%）飛んでいた。
#   ★launchd の StartCalendarInterval は、寝ていた場合は復帰後に実行する。
#
# 使い方
#   bash bin/install_launchd.sh            ★何が起きるかを出すだけ（既定はドライラン）
#   bash bin/install_launchd.sh --run      実際に設置する
#   bash bin/install_launchd.sh --list     いま載っているものを見る
#
# ★USER を決め打ちしない：機械ごとにユーザー名が違う（yujimac / yuji_macmini）。
#   plist の __HOME__ をこの機械の $HOME へ置き換えてから配置する。
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/launchd"
DST="$HOME/Library/LaunchAgents"
MODE="${1:-dry}"

if [ "$MODE" = "--list" ]; then
  echo "=== いま載っている vivid の launchd ==="
  launchctl list 2>/dev/null | grep -i vivid || echo "（1件も無い）"
  exit 0
fi

[ -d "$SRC" ] || { echo "★$SRC が無い"; exit 1; }
mkdir -p "$DST"
n=0
for f in "$SRC"/*.plist; do
  [ -e "$f" ] || continue
  base="$(basename "$f")"
  label="${base%.plist}"
  out="$DST/$base"
  n=$((n+1))
  if [ "$MODE" != "--run" ]; then
    echo "[ドライラン] $label → $out"
    grep -q "__HOME__" "$f" && echo "            __HOME__ を $HOME へ置換する"
    continue
  fi
  # ★控えを取ってから置く（既にあるものを黙って上書きしない）
  if [ -f "$out" ] && ! diff -q <(sed "s|__HOME__|$HOME|g" "$f") "$out" >/dev/null 2>&1; then
    cp "$out" "$HOME/.vivid-relay/_backups/${base}.bak_$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
  fi
  sed "s|__HOME__|$HOME|g" "$f" > "$out"
  # 載せ直す（既に載っていれば外してから）
  launchctl bootout "gui/$UID/$label" 2>/dev/null || true
  if launchctl bootstrap "gui/$UID" "$out" 2>/dev/null; then
    echo "✅ 設置: $label"
  else
    echo "★設置できなかった: $label（$out は置いた）"
  fi
done

echo
if [ "$MODE" = "--run" ]; then
  echo "=== 実測：載っているか ==="
  launchctl list 2>/dev/null | grep -i vivid || echo "★1件も載っていない"
else
  echo "★ドライラン。$n 件が対象。実際に設置するには --run を付ける。"
fi
