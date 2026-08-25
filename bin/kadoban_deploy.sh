#!/bin/bash
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
# 使い方
#   bash bin/kadoban_deploy.sh              判定して deploy
#   KADOBAN_FORCE_PLACEHOLDER=1 …           強制的に中身を引き上げる
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

# ★cron から呼ばれると PATH が最小になり node/npx が見つからない（mini は /usr/local/bin）
PATH="/usr/local/bin:/opt/homebrew/bin:$HOME/.npm-global/bin:$PATH"
export PATH
VERCEL="npx --yes vercel@latest"

log() { echo "[$(date '+%Y-%m-%d %H:%M')] $1"; }

RESULT="成功"
MSG="開始しただけで終わった"

beat() {
  HB="$HOME/.vivid-relay/heartbeat.py"
  [ -f "$HB" ] || return 0
  /usr/bin/python3 "$HB" "稼働盤のWeb公開（kadoban_deploy.sh）" "${RESULT}" "${MSG}" >/dev/null 2>&1 || true
}
trap beat EXIT

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

deploy() { (cd "$SITE" && $VERCEL deploy --prod --yes 2>&1 | grep -o 'https://[a-z0-9.-]*vercel.app' | tail -1); }

probe() { curl -s -o /dev/null -w '%{http_code}' --max-time 25 "$URL" 2>/dev/null; }

mkdir -p "$SITE" || exit 1
cp "$REPO/web/kadoban/vercel.json"   "$SITE/vercel.json"   2>/dev/null
cp "$REPO/web/kadoban/middleware.js" "$SITE/middleware.js" 2>/dev/null

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
ENVS="$( (cd "$SITE" && $VERCEL env ls 2>&1) | grep -c 'KADOBAN_USER\|KADOBAN_PASS' )"
if [ "${ENVS:-0}" -lt 2 ]; then
  GUARD_OK=0
  log "NG  環境変数 KADOBAN_USER / KADOBAN_PASS が揃っていない（${ENVS:-0}件）"
fi
if [ "${KADOBAN_FORCE_PLACEHOLDER:-0}" = "1" ]; then
  GUARD_OK=0
  log "指示により中身を引き上げる"
fi

if [ "$GUARD_OK" = "1" ]; then
  cp "$SRC_LOCAL" "$SITE/index.html"
else
  placeholder
fi
rm -f "$SITE/_dashboard.html"

OUT="$(deploy)"
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
    OUT2="$(deploy)"
    CODE2="$(probe)"
    log "    差し戻し: ${OUT2:-（URLを取得できず）} → HTTP ${CODE2}"
    RESULT="失敗"
    MSG="認証が効かず中身を引き上げた（元 ${CODE} → 差し戻し後 ${CODE2}）"
  fi
else
  RESULT="警告"
  MSG="鍵か門番が無いため中身を載せていない（プレースホルダ・HTTP ${CODE}）"
  log "★中身は載せていない（プレースホルダ）"
fi
