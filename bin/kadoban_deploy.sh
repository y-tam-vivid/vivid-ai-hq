#!/bin/bash

# ★2026-09-08 ビビ: 一時停止スイッチ（Vercelの1日100デプロイ枠をサイト側へ回すため）
#   止める: touch ~/.vivid-relay/kadoban.pause   /   戻す: rm ~/.vivid-relay/kadoban.pause
if [ -f "/Users/yuji_macmini/.vivid-relay/kadoban.pause" ]; then
  echo "[$(date +%F\ %H:%M)] 一時停止中（kadoban.pause）。何もしない"
  exit 0
fi

#
# 稼働盤を Vercel へ出す（2026-08-25 有璽氏「①を実行して」）
#
# ★このスクリプトのいちばん大事な仕事は「出すこと」ではなく「中身が晒されないこと」。
#
#   稼働盤の中身は社内の運用実態そのもの（人名・Slackチャンネル・会社数・仕組みの穴・DBのID）。
#   Vercel の Deployment Protection で固定URLまで守るのは**有料プランのみ**（2026-08-25 有璽氏確認）。
#   無料プランでは <project>.vercel.app が素の GET で 200 を返す。
#   → 設定で塞げないので、**Edge Middleware の Basic 認証**で入口を止める（無料枠で動く）。
#     合言葉は Vercel の環境変数 KADOBAN_USER / KADOBAN_PASS（暗号化保存）。
#     ★ソースにも memory にも書かない。
#
#   守り方は2段。**申告ではなく実測で守る。**
#     出す前   middleware.js と環境変数が揃っているか
#     出した後 ★素の GET が 401 を返すか。返さなければ即座にプレースホルダへ差し戻す
#
# ★2026-09-07 追記（有璽氏「リアルタイムは無理なん？」→ 10分おきへ・案A）
#   10分おきに載せる前に、まず詰まりの手当てを入れた。
#   実際に今日1回、`vercel deploy` が53分応答を返さなかった（原因未特定）。
#   10分おきにすると、詰まりが重なって多重に走る危険がある。
#
#   ① タイムアウト   macOS の bash/zsh に `timeout` は無い（実測）。
#                    `bin/run_with_timeout.py` （プロセスグループごと kill）を使う。
#                    deploy が既定300秒で返らなければ1回だけやり直す。
#                    2回連続で詰まったら Slack へ通知して諦める（黙って死なない）。
#   ② 二重起動防止   mkdir 方式のロック（アトミック）。前回がまだ走っていたら今回は
#                    スキップし、スキップしたこと自体を心拍（警告）とログに残す。
#                    stale lock（プロセスが死んでいるのに残ったロック）は奪う。
#
# 使い方
#   bash bin/kadoban_deploy.sh              判定して deploy
#   KADOBAN_FORCE_PLACEHOLDER=1 …           強制的に中身を引き上げる
#   KADOBAN_DEPLOY_TIMEOUT_SEC=10 …         タイムアウト値をテスト用に短縮（既定300秒）
#
# 前提
#   ・Vercel CLI の認証が要る（両機に配布済み・2026-08-25）
#   ・HTML の生成は dashboard_build.py（mini）。この機械に無ければ scp で取りに行く
#   経緯 → memory/project_ops_dashboard_artifact.md
#          memory/reference_vercel_free_plan_protection.md

set -u

REPO="${VIVID_REPO:-$HOME/vivid-ai-hq}"
SITE="${KADOBAN_SITE:-$HOME/.vivid-relay/kadoban_site}"
SRC_LOCAL="${KADOBAN_SRC:-$HOME/.vivid-relay/dashboard.html}"
SRC_REMOTE="${KADOBAN_SRC_REMOTE:-mini:~/.vivid-relay/dashboard.html}"
PROJECT="fukuchi-kadoban"
URL="https://${PROJECT}.vercel.app"
DEPLOY_TIMEOUT_SEC="${KADOBAN_DEPLOY_TIMEOUT_SEC:-300}"
RUN_TIMEOUT_PY="$REPO/bin/run_with_timeout.py"
LOCK_DIR="${KADOBAN_LOCK_DIR:-$HOME/.vivid-relay/kadoban_deploy.lock}"

# ★cron から呼ばれると PATH が最小になり node/npx が見つからない（mini は /usr/local/bin）
PATH="/usr/local/bin:/opt/homebrew/bin:$HOME/.npm-global/bin:$PATH"
export PATH
# ★テスト容易性のため環境変数で上書き可能にする（既定は従来どおり）。
#   本物のnpxは PATH の並び順(/usr/local/bin が $HOME/.npm-global/bin より前)のため
#   隔離テストでダミーnpxに差し替えられなかった（2026-09-07 実測）。VERCEL自体を
#   差し替えられるようにして、テストがPATH解決の癖に左右されないようにした。
VERCEL="${KADOBAN_VERCEL_CMD:-npx --yes vercel@latest}"

log() { echo "[$(date '+%Y-%m-%d %H:%M')] $1"; }

RESULT="成功"
MSG="開始しただけで終わった"

beat() {
  HB="$HOME/.vivid-relay/heartbeat.py"
  [ -f "$HB" ] || return 0
  /usr/bin/python3 "$HB" "稼働盤のWeb公開（kadoban_deploy.sh）" "${RESULT}" "${MSG}" >/dev/null 2>&1 || true
}

# ── ★二重起動の防止（mkdir はアトミック） ─────────────────────
acquire_lock() {
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    echo $$ > "$LOCK_DIR/pid"
    return 0
  fi
  local old_pid
  old_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null)"
  if [ -n "${old_pid:-}" ] && kill -0 "$old_pid" 2>/dev/null; then
    return 1  # まだ生きている＝本当に前回が走行中
  fi
  # stale lock（プロセスは死んでいるのに残ったロック）。奪う
  log "★stale lock を奪う（pid=${old_pid:-不明} は既に死んでいる）"
  rm -rf "$LOCK_DIR"
  mkdir "$LOCK_DIR" 2>/dev/null || return 1
  echo $$ > "$LOCK_DIR/pid"
  return 0
}

release_lock() {
  # ★自分が取ったロックだけ消す（他プロセスのロックを誤って消さない）
  if [ -f "$LOCK_DIR/pid" ] && [ "$(cat "$LOCK_DIR/pid" 2>/dev/null)" = "$$" ]; then
    rm -rf "$LOCK_DIR"
  fi
}

on_exit() {
  release_lock
  beat
}
trap on_exit EXIT

if ! acquire_lock; then
  RESULT="警告"
  MSG="前回の公開処理がまだ走っている（二重起動を回避してスキップ・pid=$(cat "$LOCK_DIR/pid" 2>/dev/null)）"
  log "★スキップ：前回がまだ走っている（ロック: $LOCK_DIR ／ pid=$(cat "$LOCK_DIR/pid" 2>/dev/null)）"
  exit 0
fi

placeholder() {
  cat > "$SITE/index.html" <<'HTML'
<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>準備中</title><style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f9f9f7;color:#52514e;
font:15px/1.7 -apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif}
@media (prefers-color-scheme:dark){body{background:#0d0d0d;color:#c3c2b7}}
p{margin:0}
</style></head><body><p>準備中です。</p></body></html>
HTML
}

# ── ★タイムアウト付き deploy（詰まりの手当て） ─────────────────
notify_stuck() {
  local body="$1"
  if [ ! -f "$HOME/.vivid-relay/notify.py" ]; then
    log "★notify.py が無く通知できない"
    return 0
  fi
  /usr/bin/python3 -c "
import sys
sys.path.insert(0, '$HOME/.vivid-relay')
try:
    from notify import tell
    tell('稼働盤の公開が詰まっています', '''$body''')
except Exception as e:
    sys.stderr.write('[notify] 送れず: %r\n' % e)
" >/dev/null 2>&1 || true
}

deploy_attempt() {
  # $1 = 出力先ファイル。戻り値: run_with_timeout.py の rc（124=タイムアウト）
  local out="$1"
  ( cd "$SITE" && /usr/bin/python3 "$RUN_TIMEOUT_PY" "$DEPLOY_TIMEOUT_SEC" -- $VERCEL deploy --prod --yes ) > "$out" 2>&1
  return $?
}

# ★重要：この関数は $(deploy) のようにコマンド置換で呼んではいけない。
#   コマンド置換はサブシェルなので、中の exit や DEPLOY_URL への代入が
#   親シェルへ伝わらない（2026-09-07 実測で判明。詰まり通知は出たのにスクリプト
#   全体が止まらず続行してしまうバグを1回作った。rc=0のまま最後まで完走した）。
#   ★必ず `if deploy; then ... fi` の形で呼び、URLは $DEPLOY_URL で受け取る。
DEPLOY_URL=""

deploy() {
  local out rc
  out="$(mktemp "${TMPDIR:-/tmp}/kadoban_deploy_out.XXXXXX")"
  deploy_attempt "$out"; rc=$?
  if [ "$rc" = "124" ]; then
    log "★deploy が ${DEPLOY_TIMEOUT_SEC}秒で返らなかった。1回だけやり直す"
    : > "$out"
    deploy_attempt "$out"; rc=$?
    if [ "$rc" = "124" ]; then
      log "★★2回目も ${DEPLOY_TIMEOUT_SEC}秒で詰まった。公開を諦める"
      notify_stuck "vercel deploy が ${DEPLOY_TIMEOUT_SEC}秒を2回連続で超えました。手動で cd $SITE && npx vercel@latest deploy --prod を確認してください。直近のログ: $(tail -5 "$out" 2>/dev/null | tr '\n' ' ')"
      DEPLOY_URL=""
      rm -f "$out"
      return 1
    fi
    log "★2回目は${DEPLOY_TIMEOUT_SEC}秒以内に返った"
  fi
  DEPLOY_URL="$(grep -o 'https://[a-z0-9.-]*vercel.app' "$out" | tail -1)"
  cat "$out" 1>&2
  rm -f "$out"
  return 0
}

probe() { curl -s -o /dev/null -w '%{http_code}' --max-time 25 "$URL" 2>/dev/null; }

mkdir -p "$SITE" || exit 1
cp "$REPO/web/kadoban/vercel.json"   "$SITE/vercel.json"   2>/dev/null
cp "$REPO/web/kadoban/middleware.js" "$SITE/middleware.js" 2>/dev/null
# ★2026-09-08 追加（案B）: /api/data.json（Vercel Function・Blobから軽量値を返す）を運ぶ。
#   ★このファイルが無くても本体（index.html）のデプロイ自体は壊れない
#   （画面側のJSはfetch失敗を検知して古いまま表示を続けるだけ・rt-fresh参照）。
mkdir -p "$SITE/api"
cp "$REPO/web/kadoban/api/data.js" "$SITE/api/data.js" 2>/dev/null

# ① 中身を用意する（この機械に無ければ mini から取りに行く）
if [ ! -f "$SRC_LOCAL" ]; then
  scp -q -o ConnectTimeout=8 "$SRC_REMOTE" "$SITE/_dashboard.html" 2>/dev/null && SRC_LOCAL="$SITE/_dashboard.html"
fi
if [ ! -f "$SRC_LOCAL" ]; then
  RESULT="失敗"; MSG="稼働盤のHTMLが見つからない"
  log "NG  稼働盤のHTMLが見つからない（${SRC_LOCAL} / ${SRC_REMOTE}）"
  exit 1
fi

# ② 出す前の確認 ── 鍵と門番が揃っているか
GUARD_OK=1
if [ ! -f "$SITE/middleware.js" ]; then
  GUARD_OK=0
  log "NG  middleware.js が無い"
fi
# ★2026-09-07 実測で判明：env ls も詰まりうる（テスト中に本物のnpxがハングした）。
#   deploy と同じタイムアウトで保護する。ここが詰まっても「鍵が確認できない」扱いで
#   プレースホルダへ倒すだけなので、deployのような2回リトライ＋Slack通知は不要。
ENVS_OUT="$(mktemp "${TMPDIR:-/tmp}/kadoban_envls_out.XXXXXX")"
( cd "$SITE" && /usr/bin/python3 "$RUN_TIMEOUT_PY" "$DEPLOY_TIMEOUT_SEC" -- $VERCEL env ls ) > "$ENVS_OUT" 2>&1
ENVS_RC=$?
if [ "$ENVS_RC" = "124" ]; then
  GUARD_OK=0
  log "★NG  env ls が ${DEPLOY_TIMEOUT_SEC}秒で返らなかった（詰まり扱い）"
else
  ENVS="$(grep -c 'KADOBAN_USER\|KADOBAN_PASS' "$ENVS_OUT")"
  if [ "${ENVS:-0}" -lt 2 ]; then
    GUARD_OK=0
    log "NG  環境変数 KADOBAN_USER / KADOBAN_PASS が揃っていない（${ENVS:-0}件）"
  fi
fi
rm -f "$ENVS_OUT"
if [ "${KADOBAN_FORCE_PLACEHOLDER:-0}" = "1" ]; then
  GUARD_OK=0
  log "指示により中身を引き上げる"
fi

if [ "$GUARD_OK" = "1" ]; then
  cp "$SRC_LOCAL" "$SITE/index.html"

# ★2026-09-07 担当のアイコンを一緒に運ぶ（有璽氏「アイコンは表示されていないよ」）
#   HTML は assets/agents/<担当>.png を相対で参照している。ここでコピーしないと
#   公開先に画像が無く、13体ぶん全部が壊れた画像で出る。作った側（フランキー）と
#   画面側（ピタゴラス）が別で、運ぶ人がいなかったのが原因。
#   ★10分おき運用でも毎回運ぶ（消さないこと）。
ICONS_SRC="$HOME/.vivid-relay/assets/agents"
if [ -d "$ICONS_SRC" ]; then
  mkdir -p "$SITE/assets/agents"
  cp "$ICONS_SRC"/*.png "$SITE/assets/agents/" 2>/dev/null || true
  n=$(ls "$SITE/assets/agents"/*.png 2>/dev/null | wc -l | tr -d ' ')
  echo "  アイコン ${n}枚 を公開先へ運んだ"
  # ★HTMLが参照している名前が、実際に運べたか数える（足りなければ名前を出す）
  for f in $(grep -oE 'assets/agents/[a-z0-9-]+\.png' "$SITE/index.html" | sort -u); do
    [ -f "$SITE/$f" ] || echo "  🔴 HTMLが参照しているのに無い: $f"
  done
else
  echo "  🔴 アイコンの置き場が無い: $ICONS_SRC"
fi
else
  placeholder
fi
rm -f "$SITE/_dashboard.html"

if ! deploy; then
  RESULT="失敗"
  MSG="deployが2回連続で${DEPLOY_TIMEOUT_SEC}秒を超えて詰まった"
  log "★deployが詰まったため、これ以上進めず終了する"
  exit 1
fi
OUT="$DEPLOY_URL"
log "deploy: ${OUT:-（URLを取得できず）}"
sleep 8
CODE="$(probe)"
log "実測 ${URL} → 認証なしで HTTP ${CODE}"

# ③ ★出した後の確認 ── 素の GET が 401 でなければ、中身を置いたままにしない
if [ "$GUARD_OK" = "1" ]; then
  if [ "$CODE" = "401" ]; then
    RESULT="成功"
    MSG="公開OK（認証なしは401・中身は認証の向こう側）"
    log "OK  Basic認証が効いている。中身を載せたままにする"
  else
    log "★NG  認証が効いていない（HTTP ${CODE}）。中身を引き上げる"
    placeholder
    if deploy; then
      OUT2="$DEPLOY_URL"
      CODE2="$(probe)"
      log "    差し戻し: ${OUT2:-（URLを取得できず）} → HTTP ${CODE2}"
      RESULT="失敗"
      MSG="認証が効かず中身を引き上げた（元 ${CODE} → 差し戻し後 ${CODE2}）"
    else
      # ★差し戻し用のdeployも詰まった。プレースホルダのHTMLはローカルに
      #   用意済みだが、Vercelへ出せていない＝直前の中身が公開されたままの恐れがある。
      log "★★差し戻しのdeployも詰まった。中身が公開されたままの恐れがある"
      RESULT="失敗"
      MSG="認証が効かず引き上げようとしたが、差し戻しのdeployも詰まった（要手動確認）"
    fi
  fi
else
  RESULT="警告"
  MSG="鍵か門番が無いため中身を載せていない（プレースホルダ・HTTP ${CODE}）"
  log "★中身は載せていない（プレースホルダ）"
fi
