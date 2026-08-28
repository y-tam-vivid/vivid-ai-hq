#!/bin/bash
# ffmpeg を bin/vendor/ffmpeg へ導入する（sudo不要・両機それぞれで1回実行する）。
#
# なぜこの形か（2026-08-29 実測して決めた）:
#   - Homebrew は MacBook に無い。新規導入は /opt/homebrew の作成でsudoを要する
#     経路になりうるため、ここでは brew を前提にしない（miniには既にbrewがあるが
#     道具は両機で同じ手順にする＝brew専用スクリプトにしない）。
#   - evermeet.cx の静的バイナリは x86_64（arm64ネイティブ版の配布は無い）。
#     両機ともRosetta 2経由で動作することを実測済み（動画エンコードまで確認）。
#   - 80MB前後あるためリポジトリにコミットしない（.gitignoreでbin/vendor/を除外）。
#     この導入スクリプトだけをgit管理し、各機で個別にダウンロードする。
#
# 使い方:
#   bash bin/setup_ffmpeg.sh
#
# 配置後は bin/vendor/ffmpeg をフルパスで呼ぶ（PATHへは追加しない＝環境を汚さない）。

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_DIR="$REPO_ROOT/bin/vendor"
DEST="$VENDOR_DIR/ffmpeg"

mkdir -p "$VENDOR_DIR"

if [ -x "$DEST" ]; then
    echo "既に導入済みです: $DEST"
    "$DEST" -version | head -1
    exit 0
fi

# arm64機はRosetta 2が無いとx86_64バイナリを実行できない（2026-08-29 miniで実測：
# "Bad CPU type in executable"）。導入はsudo不要（実測済み）なので先に済ませる。
# ★稼働プロセス(oahd)の有無ではなく実体ファイルで判定する
#   （oahdは初回のx86_64実行まで起動しておらず、稼働チェックだと誤判定する）。
if [ "$(uname -m)" = "arm64" ] && [ ! -e /Library/Apple/usr/share/rosetta/rosetta ]; then
    echo "Rosetta 2 が未導入のため導入します（sudo不要）..."
    softwareupdate --install-rosetta --agree-to-license
fi

echo "evermeet.cx から最新安定版の情報を取得します..."
INFO_JSON="$(curl -sL -m 20 "https://evermeet.cx/ffmpeg/info/ffmpeg/release")"
ZIP_URL="$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['download']['zip']['url'])" "$INFO_JSON")"
VERSION="$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['version'])" "$INFO_JSON")"

echo "ffmpeg $VERSION をダウンロードします: $ZIP_URL"
TMP_ZIP="$(mktemp -t ffmpeg_dl).zip"
curl -sL -m 120 "$ZIP_URL" -o "$TMP_ZIP"

TMP_DIR="$(mktemp -d)"
unzip -oq "$TMP_ZIP" -d "$TMP_DIR"
mv "$TMP_DIR/ffmpeg" "$DEST"
chmod +x "$DEST"
rm -rf "$TMP_ZIP" "$TMP_DIR"

echo "=== 動作確認 ==="
"$DEST" -version | head -1
file "$DEST"
echo "導入しました: $DEST"
