#!/bin/bash
#
# cron の投函口 ── bin/cron/<機械>.cron に置かれた行のうち、
#                 crontab にまだ無いものだけを入れる（追加のみ・冪等）
#
# ─────────────────────────────────────────────────────────────
# なぜこれがあるか（2026-08-20 実地）
#
#   Claude のセッションから `crontab file` / `crontab -` を叩くと、無応答のまま返らない。
#   2経路（パイプ／ファイル）・sandbox の有無、どちらでも同じ。プロセスは S 状態で眠り続ける。
#   一方、cron から起動された処理は自分の crontab を書ける。
#
#   ＝「AIは自動実行を作れるのに、自動実行に登録できない」という詰まり方をしていた。
#     人へ1行渡す運用に戻すのは筋が悪い（有璽氏は mini の画面からコピーできない）。
#     → **cron 自身に入れさせる。**
#
# 設計
#   - **追加しかしない。** 消すのは人。ここから行を消しても crontab は変わらない
#   - 既に同じ行があれば何もしない（冪等）
#   - 書く前に crontab を退避する（~/.vivid-relay/crontab_backup_<日時>.txt）
#   - ★書き込みが返らないときのために番人をつける（20秒で諦めてログへ残す）
# ─────────────────────────────────────────────────────────────

set -u

REPO="${VIVID_REPO:-$HOME/vivid-ai-hq}"
LOG="${VIVID_CRON_LOG:-$HOME/Library/Logs/vivid-cron-apply.log}"
BACKUP_DIR="${VIVID_CRON_BACKUP_DIR:-$HOME/.vivid-relay}"
HOST=$(/usr/sbin/scutil --get ComputerName 2>/dev/null || hostname)

case "$HOST" in
  *mini*|*Mini*|*MINI*) WANTED="$REPO/bin/cron/mini.cron" ;;
  *)                    WANTED="$REPO/bin/cron/macbook.cron" ;;
esac

[ -f "$WANTED" ] || exit 0

CURRENT=$(/usr/bin/crontab -l 2>/dev/null)

# 追加すべき行を集める（コメント・空行は無視。完全一致で有無を見る）
MISSING=""
while IFS= read -r line; do
  case "$line" in
    ''|'#'*) continue ;;
  esac
  if ! printf '%s\n' "$CURRENT" | /usr/bin/grep -qxF "$line"; then
    MISSING="${MISSING}${line}
"
  fi
done < "$WANTED"

[ -z "$MISSING" ] && exit 0

# 退避してから書く
# ★2026-08-20 つる：crontab への書き込みが塞がっている間、15分ごとに再試行→毎回退避で
#   同じ内容のバックアップが1日96本たまっていた（8/20だけで24本を実測）。
#   ① 直前の退避と中身が同じなら取り直さない ② 20世代を超えた古い分は落とす
LAST=$(ls -t "$BACKUP_DIR"/crontab_backup_*.txt 2>/dev/null | head -1)
if [ -z "$LAST" ] || ! printf '%s\n' "$CURRENT" | cmp -s - "$LAST"; then
  STAMP=$(date "+%Y%m%d-%H%M%S")
  printf '%s\n' "$CURRENT" > "$BACKUP_DIR/crontab_backup_$STAMP.txt" 2>/dev/null
fi
ls -t "$BACKUP_DIR"/crontab_backup_*.txt 2>/dev/null | tail -n +21 | while read -r old; do
  rm -f "$old"
done

NEW=$(mktemp /tmp/vivid_cron.XXXXXX)
printf '%s\n' "$CURRENT" > "$NEW"
printf '%s' "$MISSING" >> "$NEW"

# ★番人つきで書く。返らないときは諦めてログへ残す（同期本体は止めない）
/usr/bin/crontab "$NEW" &
CPID=$!
i=0
while [ $i -lt 20 ]; do
  kill -0 "$CPID" 2>/dev/null || break
  sleep 1
  i=$((i + 1))
done

if kill -0 "$CPID" 2>/dev/null; then
  kill -9 "$CPID" 2>/dev/null
  echo "[$(date '+%Y-%m-%d %H:%M')] ★crontab への書き込みが20秒で返らなかった。入れられていない：
$MISSING" >> "$LOG"
  rm -f "$NEW"
  exit 1
fi

wait "$CPID" 2>/dev/null
AFTER=$(/usr/bin/crontab -l 2>/dev/null)
OK=0
FAIL=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  if printf '%s\n' "$AFTER" | /usr/bin/grep -qxF "$line"; then
    OK=$((OK + 1))
  else
    FAIL=$((FAIL + 1))
  fi
done <<EOF
$MISSING
EOF

echo "[$(date '+%Y-%m-%d %H:%M')] 追加 ${OK}行 ／ 入らなかった ${FAIL}行
$MISSING" >> "$LOG"

rm -f "$NEW"
exit 0
