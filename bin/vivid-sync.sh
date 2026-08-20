#!/bin/bash
#
# vivid-ai-hq の受信同期（両機共通・cron から15分ごとに呼ぶ）
#
# ─────────────────────────────────────────────────────────────
# なぜこれがあるか（2026-08-17 実地）
#
#   旧: cron */15  git pull --ff-only  >> ログ
#
#   作業をすればワーキングツリーは必ず汚れる。--ff-only は汚れていると必ず失敗する。
#   つまり「作業している間は受信が止まる」構造だった。しかも失敗はログにしか出ず、
#   153回連続で失敗しても誰も気づかなかった。読む側は古い WORKING.md を最新だと
#   信じて答えた。
#
# 設計の要点 ── 「取り込む」と「知る」を分ける
#
#   取り込み（merge）は失敗してよい。作業中に他機の変更が勝手に乗る方が危ない。
#   だが「遅れている」という事実は、失敗してはいけない。必ず手元に届ける。
#
#     git fetch          常に実行する（マージしないので作業中でも成功する）
#     遅れ／進みを数える  behind = 読んでいるものが古い／ahead = 他機へ届いていない
#     SYNC_STATUS.md     ~/.claude/CLAUDE.md が @import する＝毎ターン必ず読まれる
#     心拍                ⚙️自動処理レジスタへ。沈黙すれば🔴になる
#
#   ★ ログは「見に行かないと分からない場所」。届く場所ではない。
#     だからログではなく、毎ターン読まれるファイルへ書く。
# ─────────────────────────────────────────────────────────────

set -u

# 既定値は本番。テスト時だけ環境変数で差し替える（挙動を実測で確かめられるようにするため）
REPO="${VIVID_REPO:-$HOME/vivid-ai-hq}"
STATUS="${VIVID_STATUS:-$HOME/.claude/SYNC_STATUS.md}"
HEARTBEAT="${VIVID_HEARTBEAT:-$HOME/.vivid-relay/heartbeat.py}"
NOW=$(date "+%Y-%m-%d %H:%M")
HOST=$(scutil --get ComputerName 2>/dev/null || hostname)

# 心拍は処理名の完全一致で行を探す。同名が2つあると更新されないので、機械ごとに分ける
case "$HOST" in
  *mini*|*Mini*|*MINI*) NAME="vivid-ai-hq の同期（Mac mini）" ;;
  *)                    NAME="vivid-ai-hq の同期（MacBook）" ;;
esac

cd "$REPO" || exit 1

# ★ いま手がついているものを、実態（git）から書き出す
#
#   WORKING.md は「着手前に自分で1行足す」申告制だが、忘れられる。しかも
#   忘れたこと自体は検知できない（2026-08-19 に mini・MacBook の両方で実際に起きた）。
#   未コミットのファイルは、誰かが今まさに触っている実態そのもの。
#   申告を待たずに機械が書けば、書き忘れても見える。
dirty_block() {
  [ "$DIRTY" -eq 0 ] && return 0
  echo "## いま手がついているもの（機械が git から書き出した実態）"
  echo
  echo "**着手宣言の有無に関わらず出る。** \`WORKING.md\` に載っていないものがここにあれば、"
  echo "誰かが宣言せずに触っている（＝他セッションと二重に手をつける恐れ）。"
  echo
  echo '```'
  git status --porcelain | sed 's/^/  /' | head -30
  [ "$DIRTY" -gt 30 ] && echo "  …ほか $((DIRTY - 30)) 件"
  echo '```'
}

# ① 取りに行く。マージはしないので、作業中でも成功する
FETCH_ERR=$(git fetch origin 2>&1)
FETCH_RC=$?

BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
DIRTY=$(git status --porcelain | wc -l | tr -d " ")

# ② 取り込めるときだけ取り込む（汚れていたら触らない）
MERGED="no"
if [ "$FETCH_RC" -eq 0 ] && [ "$BEHIND" -gt 0 ] && [ "$DIRTY" -eq 0 ]; then
  if git merge --ff-only origin/main >/dev/null 2>&1; then
    MERGED="yes"
    BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
  fi
fi

# ②' 送信する（コミット済みのみ。書きかけ＝未コミットは git push の対象外なので飛ばない）
#     behind=0（受信済み）のときだけ送る。behind>0 のまま push すると reject されるので、
#     先に受信が要る＝次の同期で merge されてから自動的に送られる。
PUSHED="no"
if [ "$FETCH_RC" -eq 0 ] && [ "$BEHIND" -eq 0 ] && [ "$AHEAD" -gt 0 ]; then
  if git push origin main >/dev/null 2>&1; then
    PUSHED="yes"
    AHEAD=0
  fi
fi

# ③ 状態を決める
if [ "$FETCH_RC" -ne 0 ]; then
  RESULT="失敗"
  HEAD_LINE="🔴 リモートに繋がっていない（$NOW 時点）"
  DETAIL="git fetch が失敗した。ネットワークか鍵の問題。ここが直るまで受信も送信もできない。

\`\`\`
$FETCH_ERR
\`\`\`"
elif [ "$BEHIND" -gt 0 ]; then
  RESULT="警告"
  HEAD_LINE="🔴 いま読んでいる WORKING.md / MEMORY.md は古い（$NOW 時点・未取込 ${BEHIND}件）"
  DETAIL="**この機は他機の変更を取り込めていない。過去の状態を最新だと思って答えないこと。**
原因はほぼ常に「ローカルに未コミットの変更があり、ff-only マージができない」。

未取込の内容:

\`\`\`
$(git log --oneline HEAD..origin/main --pretty='%h %ad %s' --date=short 2>/dev/null | head -10)
\`\`\`

取り込み方（作業中の変更を捨てずに）:

\`\`\`
cd ~/vivid-ai-hq && git status        # 何を書きかけているか見る
git add -A && git commit              # 自分の変更を確定させる
git merge origin/main                 # 両方のブロックを残してマージ
\`\`\`

$(dirty_block)"
elif [ "$AHEAD" -gt 0 ] || [ "$DIRTY" -gt 0 ]; then
  RESULT="警告"
  HEAD_LINE="🟡 まだ確定していない変更がある（$NOW 時点・未push ${AHEAD}件／未コミット ${DIRTY}件）"
  DETAIL="**コミット済みの変更は vivid-sync.sh が自動で push する（次の同期で全機へ配送）。**
残っているのは、まだ commit していない変更か、他機が先に進んでいて保留された push。
区切りがついたら commit すれば、あとは自動で届く。

\`\`\`
cd ~/vivid-ai-hq && git add -A && git commit    # push は自動
\`\`\`

$(dirty_block)"
else
  RESULT="成功"
  HEAD_LINE="🟢 最新（$NOW 時点・未取込 0件）"
  DETAIL="規範・記憶・WORKING.md は他の面と一致している。"
fi

# ④ 毎ターン届く場所へ書く（ログではなく）
mkdir -p "$HOME/.claude"
cat > "$STATUS" <<EOF
# 同期の鮮度（${HOST}）

> **機械が書く。手で編集しない。** \`bin/vivid-sync.sh\` が15分ごとに上書きする。
> このファイルは \`~/.claude/CLAUDE.md\` が @import しているので毎ターン読まれる。
> 目的は1つ ── **古いものを最新だと思って答えるのを防ぐこと。**

$HEAD_LINE

$DETAIL
EOF

# ④' フックの自動導入（★人に1行貼らせない）
#    2026-08-20 有璽氏「Mac miniはコピペできない。ここにコード貼っても俺は触れない」
#    → 「この1行を貼ってください」という渡し方そのものをやめる。
#      同期のたびに、入っていなければ入れる。入っていれば何もしない（冪等）。
SETUP="$HOME/vivid-ai-hq/bin/setup_hooks.sh"
SELFCHECK="$HOME/.vivid-relay/hook_selfcheck.py"
if [ -x "$SETUP" ]; then
  NEED=0
  # 実体が無い / settings.json に登録が無い / 索引が無い のどれかなら入れ直す
  [ -f "$HOME/.vivid-relay/hook_inject_memory.py" ] || NEED=1
  [ -f "$HOME/.vivid-relay/landmines.json" ] || NEED=1
  if [ -f "$HOME/.claude/settings.json" ]; then
    /usr/bin/grep -q "hook_inject_memory.py" "$HOME/.claude/settings.json" || NEED=1
  else
    NEED=1
  fi
  # 実体が repo より古ければ入れ直す（フックを更新したら全機へ広がる）
  if [ -f "$HOME/.vivid-relay/hook_inject_memory.py" ] &&
     [ "$HOME/vivid-ai-hq/bin/hooks/hook_inject_memory.py" -nt "$HOME/.vivid-relay/hook_inject_memory.py" ]; then
    NEED=1
  fi
  if [ "$NEED" = "1" ]; then
    bash "$SETUP" >> "$HOME/Library/Logs/vivid-hooks-setup.log" 2>&1 || true
    echo "[$(date '+%Y-%m-%d %H:%M')] フックを導入/更新した" >> "$HOME/Library/Logs/vivid-hooks-setup.log"
  fi
fi

# ④'' cron の投函口（★AIが自分で crontab を書けないときの経路）
#     2026-08-20 実測: Claude のセッションから crontab を書くと無応答のまま返らない。
#     cron から起動されたこの処理なら書ける。bin/cron/<機械>.cron に置かれた行のうち
#     まだ入っていないものだけを入れる（追加のみ・冪等・番人つき）。
CRON_APPLY="$HOME/vivid-ai-hq/bin/cron_apply.sh"
[ -f "$CRON_APPLY" ] && bash "$CRON_APPLY" >/dev/null 2>&1 || true

# ④''' 日次ジョブの配布口（★crontab 書き込みが直る見込みが立たない間の代替経路）
#      2026-08-20: crontab への書き込みが4経路すべてで無応答のまま返らない状態が続いている。
#      crontab を増やさず、この vivid-sync.sh（*/15・既に稼働中）から日次ジョブを配る。
#      定義は bin/daily_jobs.conf（正本）。1日1回・定刻管理・ロック付き。
#      失敗しても本体（この後の心拍）を止めない。
DAILY_JOBS="$HOME/vivid-ai-hq/bin/daily_jobs.sh"
[ -x "$DAILY_JOBS" ] && "$DAILY_JOBS" >/dev/null 2>&1 || true

# ⑤ 心拍（失敗しても本体は落とさない）
if [ -f "$HEARTBEAT" ]; then
  MSG="未取込${BEHIND}件 / 未push${AHEAD}件 / 未コミット${DIRTY}件 / 取込=${MERGED} / 送信=${PUSHED}"
  /usr/bin/python3 "$HEARTBEAT" "$NAME" "$RESULT" "$MSG" >/dev/null 2>&1 || true
fi

exit 0
