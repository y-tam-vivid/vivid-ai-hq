#!/bin/bash
#
# 稼働盤を Vercel へ出す（2026-08-25 有璽氏「①を実行して」）
#
# ★このスクリプトのいちばん大事な仕事は「出すこと」ではなく「出していいかを確かめること」。
#
#   稼働盤の中身は社内の運用実態そのもの（人名・Slackチャンネル・会社数・仕組みの穴・DBのID）。
#   2026-08-25 の実測で、Vercel の production 固定URL <project>.vercel.app は
#   **SSO保護をかけても素の GET で 200 を返す**ことが分かった。
#     vercel project protection enable --sso   → deploymentType は
#     prod_deployment_urls_and_all_previews にしかならず、固定URLは保護対象外
#   ＝ CLI だけでは塞げない。ダッシュボードで "All Deployments" にする必要がある（人の操作）。
#
#   だから ── **保護が確認できないうちは本番の中身を載せない。**
#   その場合は「準備中」のプレースホルダを出して終わる。黙って公開しない。
#
# 使い方
#   bash bin/kadoban_deploy.sh            判定して deploy
#   KADOBAN_FORCE_PLACEHOLDER=1 …        強制的にプレースホルダにする（引き上げたいとき）
#
# 前提
#   ・Vercel CLI の認証がある機械でだけ動く（2026-08-25 時点で MacBook のみ。mini は未設定）
#   ・HTML の生成は dashboard_build.py（mini）。この機械から見えない場合は scp で取りに行く

set -u

REPO="${VIVID_REPO:-$HOME/vivid-ai-hq}"
SITE="${KADOBAN_SITE:-$HOME/.vivid-relay/kadoban_site}"
SRC_LOCAL="${KADOBAN_SRC:-$HOME/.vivid-relay/dashboard.html}"
SRC_REMOTE="${KADOBAN_SRC_REMOTE:-mini:~/.vivid-relay/dashboard.html}"
PROJECT="fukuchi-kadoban"
# ★cron から呼ばれると PATH が最小になり node/npx が見つからない（mini は /usr/local/bin）
PATH="/usr/local/bin:/opt/homebrew/bin:$HOME/.npm-global/bin:$PATH"
export PATH
VERCEL="npx --yes vercel@latest"

log() { echo "[$(date '+%Y-%m-%d %H:%M')] $1"; }

mkdir -p "$SITE" || exit 1
cp "$REPO/web/kadoban/vercel.json" "$SITE/vercel.json" 2>/dev/null

# ① 中身を用意する（この機械に無ければ mini から取りに行く）
if [ ! -f "$SRC_LOCAL" ]; then
  scp -q -o ConnectTimeout=8 "$SRC_REMOTE" "$SITE/_dashboard.html" 2>/dev/null && SRC_LOCAL="$SITE/_dashboard.html"
fi
if [ ! -f "$SRC_LOCAL" ]; then
  log "NG  稼働盤のHTMLが見つからない（${SRC_LOCAL} / ${SRC_REMOTE}）"
  exit 1
fi

# ② ★出していいかを確かめる ── 固定URLが保護されているか
PROT="$(cd "$SITE" && $VERCEL project protection "$PROJECT" 2>/dev/null | tr -d ' \n')"
SAFE=0
case "$PROT" in
  *'"deploymentType":"all"'*) SAFE=1 ;;
esac
if [ "${KADOBAN_FORCE_PLACEHOLDER:-0}" = "1" ]; then
  SAFE=0
  log "指示によりプレースホルダを出す"
fi

if [ "$SAFE" = "1" ]; then
  cp "$SRC_LOCAL" "$SITE/index.html"
  log "保護OK（deploymentType=all）→ 本番の中身を載せる"
else
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
  log "★保護が確認できない → 中身は載せない（プレースホルダ）。現在の設定: ${PROT}"
  log "   直し方: https://vercel.com/fuku-chi-vivid/fukuchi-kadoban/settings/deployment-protection"
  log "           Vercel Authentication を All Deployments にして Save"
fi

# ③ 出す
cd "$SITE" || exit 1
rm -f "$SITE/_dashboard.html"
OUT="$($VERCEL deploy --prod --yes 2>&1 | grep -o 'https://[a-z0-9.-]*vercel.app' | tail -1)"
log "deploy: ${OUT:-（URLを取得できず）}"

# ④ 実測で確かめる（申告でなく実物）
CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 "https://${PROJECT}.vercel.app" 2>/dev/null)"
log "実測 https://${PROJECT}.vercel.app → HTTP ${CODE}"
if [ "$SAFE" != "1" ] && [ "$CODE" = "200" ]; then
  log "  （想定どおり：誰でも見られるが、中身はプレースホルダ）"
fi

# ⑤ 心拍
HB="$HOME/.vivid-relay/heartbeat.py"
if [ -f "$HB" ]; then
  if [ "$SAFE" = "1" ]; then R="成功"; M="本番の中身を公開（HTTP ${CODE}）";
  else R="警告"; M="保護が未設定のため中身を載せていない（プレースホルダ・HTTP ${CODE}）"; fi
  /usr/bin/python3 "$HB" "稼働盤のWeb公開（kadoban_deploy.sh）" "$R" "$M" >/dev/null 2>&1 || true
fi
