#!/bin/bash
# cron / launchd から claude を呼ぶ入口（2026-10-14・#c31c98 有璽氏承認）
#
# なぜ要るか：長期トークン CLAUDE_CODE_OAUTH_TOKEN は ~/.zshenv にしか無く、ssh のシェルだけが読む。
#   cron は読まない → .credentials.json に落ち、その更新鍵が 10/5 08:56 に切れて以降、
#   claude を呼ぶ自動処理（self_audit / memory_sweep / slack_inbox / inbox_runner / team_run / run_agent）が全部落ちていた。
# やること：環境に無ければ ~/.vivid-relay/config.env から読んで渡し、本体を exec する。★値は表示しない。
# 確かめ方：env -i HOME=$HOME PATH=/usr/bin:/bin ~/.vivid-relay/claude_cron.sh -p "OKとだけ返して"

CFG="$HOME/.vivid-relay/config.env"
if [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] && [ -r "$CFG" ]; then
  v=$(grep -m1 '^CLAUDE_CODE_OAUTH_TOKEN=' "$CFG" | cut -d= -f2- | sed -e 's/^["'\'']//' -e 's/["'\'']$//')
  if [ -n "$v" ]; then
    export CLAUDE_CODE_OAUTH_TOKEN="$v"
  fi
fi
export PATH="$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"
exec "$HOME/.npm-global/bin/claude" "$@"
