#!/bin/bash
# HUG 本日の様子：受け取り → 利用者別・月別に分ける → 共有ドライブへ → 月別にドライブのショートカット（★恒久ルール・有璽氏 2026-10-20）
#
#   有璽氏：HUG「本日の様子一括印刷」→ すべてチェック →「印刷」→「PDFを出力する」で
#           ~/Documents/_機微_HUG本日の様子/受け取り（HUGから保存）/ に保存（期間は何か月でもよい）
#   AI    ：「保存した」と言われたら MacBook でこれを1回流す
#
#   bin/hug_yosu_run.sh            全部
#   bin/hug_yosu_run.sh --dry-run  数えるだけ（何も書かない）
# → memory/reference_hug_record_output.md
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/Documents/_機微_HUG本日の様子"
DRIVE="$HOME/Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com/共有ドライブ/15-000_施設運営部門/LIFE STAND UP/本日の様子（HUG）"
WORK="$(mktemp -d)"   # python は空のフォルダから起動する（置かれたPDFの横で起動しない）
trap 'rm -rf "${WORK}"' EXIT

if [ "${1:-}" = "--dry-run" ]; then
  (cd "${WORK}" && python3 "${HERE}/hug_split_yosu.py" --dry-run)
  exit 0
fi

# ① 分ける（受け取りが空なら飛ばして ② 以降だけ流す＝取りこぼしの追い付け）
if ls "${BASE}/受け取り（HUGから保存）"/*.pdf >/dev/null 2>&1; then
  (cd "${WORK}" && python3 "${HERE}/hug_split_yosu.py")
fi

# ② 共有ドライブへ（同じ名前は上書きしない）
[ -d "${DRIVE}" ] || { echo "共有ドライブのフォルダが見えません：${DRIVE}"; exit 1; }
mkdir -p "${DRIVE}/利用者別" "${DRIVE}/元PDF"
rsync -a --ignore-existing "${BASE}/利用者別/" "${DRIVE}/利用者別/"
rsync -a --ignore-existing "${BASE}/元PDF/" "${DRIVE}/元PDF/"
want=$(find "${BASE}/利用者別" -name '*.pdf' | wc -l | tr -d ' ')
echo "手元の原本 ${want}本 → 同期フォルダへコピー済み"

# ③ ドライブ側にそろうのを待ってから、mini でショートカットを作る（最長20分）
scp -q "${HERE}/hug_drive_shortcuts.py" mini:/tmp/hug_drive_shortcuts.py
for _ in $(seq 1 40); do
  n=$(ssh mini 'python3 /tmp/hug_drive_shortcuts.py --dry-run 2>/dev/null' | sed -n 's/^原本 \([0-9]*\)本.*/\1/p')
  echo "$(date +%H:%M:%S) ドライブ側の原本 ${n:-?}/${want}"
  [ "${n:-0}" -ge "${want}" ] && break
  sleep 30
done
[ "${n:-0}" -ge "${want}" ] || { echo "★ドライブ側がそろわないまま打ち切り。あとでもう一度流す"; exit 1; }
# ★ssh が切れても止まらないよう nohup で流し、終わるのを待って結果だけ読む（10/20 Broken pipe で途中終了した）
ssh mini 'nohup python3 /tmp/hug_drive_shortcuts.py > /tmp/hug_shortcuts.log 2>&1 &'
for _ in $(seq 1 80); do
  sleep 15
  ssh mini 'pgrep -f hug_drive_shortcuts >/dev/null' || break
done
ssh mini 'grep -E "^(原本|ショートカット)|Error" /tmp/hug_shortcuts.log'
