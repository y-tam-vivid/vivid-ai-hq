#!/bin/bash
#
# 日次ジョブの配布口 ── crontab に新しい行を1本も足せない状態が続いている
#                     （crontab への書き込みが4経路すべてで無応答のまま返らない・2026-08-20実測）。
#
# だから crontab を増やさず、既に crontab に入っていて確実に動いている
# vivid-sync.sh（*/15 * * * *）から、この配布口を毎回呼ぶ。定義表（bin/daily_jobs.conf）
# を読み、「今日まだ走らせていない」かつ「定刻を過ぎた」ジョブだけを起動する。
#
# ─────────────────────────────────────────────────────────────
# 満たしていること
#   1. 定義は bin/daily_jobs.conf の1か所だけ（bin/cron/mini.cron とは役割を分けた。
#      両ファイルの冒頭コメントを参照）
#   2. 1日1回だけ走る（状態ファイル ~/.vivid-relay/daily_jobs_state/<ジョブ名>.done）
#   3. ロックを取る（前回がまだ走っている間は次を起動しない。mkdir はアトミック）
#   4. 定刻を過ぎて起動できなかった日を取りこぼさない。ただし日をまたいだら諦める
#      （状態ファイルの「今日」判定が自然にそれをやる。日付が変われば前日分は追わない）
#   5. どのジョブが失敗しても呼び出し元（vivid-sync.sh）を止めない（exit 0 で必ず返す）
#   6. 心拍は各ジョブ自身が打つ（intake_register.py --beat 等）。この配布口自体の心拍は
#      vivid-sync.sh 側の心拍とは別に⚙️レジスタへ「日次ジョブのディスパッチ」として登録
#   7. 既に crontab に入っているコマンドと同じ行は実行しない（実行直前に crontab -l と突合）
# ─────────────────────────────────────────────────────────────

set -u

REPO="${VIVID_REPO:-$HOME/vivid-ai-hq}"
CONF="${VIVID_DAILY_JOBS_CONF:-$REPO/bin/daily_jobs.conf}"
STATE_DIR="${VIVID_DAILY_JOBS_STATE:-$HOME/.vivid-relay/daily_jobs_state}"
LOCK_DIR="${VIVID_DAILY_JOBS_LOCK:-$HOME/.vivid-relay/daily_jobs.lock}"
LOG="${VIVID_DAILY_JOBS_LOG:-$HOME/Library/Logs/vivid-daily-jobs.log}"
HEARTBEAT="${VIVID_HEARTBEAT:-$HOME/.vivid-relay/heartbeat.py}"

# ★テスト用に「いま」を差し替えられるようにする（実測で①②③④を確かめるため）。
#   本番では常に実システム時刻。
NOW_TS="${VIVID_DAILY_JOBS_NOW:-$(date +%s)}"
TODAY="$(date -r "$NOW_TS" +%Y-%m-%d 2>/dev/null)"

mkdir -p "$STATE_DIR" "$(dirname "$LOG")" 2>/dev/null

[ -f "$CONF" ] || exit 0

log() { echo "[$(date '+%Y-%m-%d %H:%M')] $1" >> "$LOG"; }

# ── ③ ロック（前回がまだ走っている間は次を起動しない） ──────────
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  LOCK_PID=""
  [ -f "$LOCK_DIR/pid" ] && LOCK_PID=$(cat "$LOCK_DIR/pid" 2>/dev/null)
  if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
    log "前回がまだ走っている(pid $LOCK_PID)。今回は起動しない"
    exit 0
  fi
  # プロセスが死んでいる残骸ロック（クラッシュ等）→ 掃除して取り直す
  log "★残骸ロックを検出（pid不明または死亡）。掃除して取り直す"
  rm -rf "$LOCK_DIR"
  mkdir "$LOCK_DIR" 2>/dev/null || { log "ロック取得に失敗。今回は諦める"; exit 0; }
fi
echo $$ > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR"' EXIT

# 実行中の実crontabを1回だけ読んでおく（★⑦ 既存crontabとの二重起動防止）
CRONTAB_NOW=$(/usr/bin/crontab -l 2>/dev/null)

# ── 定義表を読み、条件を満たすものだけ起動 ──────────────────
while IFS=$'\t' read -r hhmm name cmd; do
  case "$hhmm" in ''|'#'*) continue ;; esac
  [ -z "$name" ] && continue
  [ -z "$cmd" ] && continue

  # ⑦ 同じコマンドが既に本物の crontab に入っていれば、ここでは動かさない
  if [ -n "$CRONTAB_NOW" ] && printf '%s\n' "$CRONTAB_NOW" | /usr/bin/grep -qF "$cmd"; then
    log "スキップ: $name はすでに crontab 本体にある（二重起動を避けた）"
    continue
  fi

  DONE_FILE="$STATE_DIR/$name.done"
  # ② 今日すでに走っていればスキップ
  if [ -f "$DONE_FILE" ] && [ "$(cat "$DONE_FILE" 2>/dev/null)" = "$TODAY" ]; then
    continue
  fi

  # 定刻を過ぎているか（HH:MM を今日の日付に当てはめて秒へ）
  SCHED_TS=$(date -j -f "%Y-%m-%d %H:%M" "$TODAY $hhmm" "+%s" 2>/dev/null)
  if [ -z "$SCHED_TS" ]; then
    log "★定義が壊れている（時刻を解釈できない）: $hhmm $name"
    continue
  fi
  # ④ 定刻前なら待つ。定刻後なら（取りこぼしを拾って）ここで走る
  if [ "$NOW_TS" -lt "$SCHED_TS" ]; then
    continue
  fi

  # ★bash 3.2(macOS標準)は `set -u` 下で「変数名の直後に全角文字」を変数名の一部と
  #   誤認し unbound variable で落ちる実バグがある（2026-08-20実測）。${} で必ず区切る。
  log "起動: ${name}（定刻 ${hhmm}・実行時刻 $(date -r "$NOW_TS" '+%H:%M')）"
  # ⑤ このジョブが失敗しても他のジョブ・呼び出し元を止めない
  ( bash -c "$cmd" ) >> "$LOG" 2>&1
  RC=$?
  echo "$TODAY" > "$DONE_FILE"
  if [ $RC -eq 0 ]; then
    log "完了: $name (rc=0)"
  else
    log "★失敗: $name (rc=$RC)。他のジョブは続行する"
  fi
done < "$CONF"

exit 0
