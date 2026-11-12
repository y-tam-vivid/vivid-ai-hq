---
name: feedback_read_the_card_thread_before_acting
description: 判断カードの答えを受けて動く前に、そのカードのSlackスレッドを読む（有璽氏が置き場などの条件を後から足す）。2026-11-12 行政ニュースDBを二重に作った
metadata:
  type: feedback
---

判断カード（ask_hub）の答えが届いたら、★動く前にそのカードのSlackスレッドを読む。答えのボタンの後に、有璽氏がスレッドへ条件を足すことがある。

**Why:** 2026-11-12 #6ab3bb（DB=Notionに新しいDB）の答えを受けて、Claude Code のビビが「ビビッド業務管理」の下に 📰行政ニュースDB を作った。
同じ時刻に有璽氏はスレッド（受付 #s5dd414）へ「Notionのデータベースはこちらの場所に」と置き場（情報発信 コンテンツ管理DB）を指定しており、
Slackの窓口がフランキーへ回して 🏛️行政ニュース集約DB をそこに作っていた。二重に作り、DMへ4投稿を廃止側から出した。
窓口は「担当のセッションはいま閉じています」と判断していた（Claude Code 側は開いていた）＝窓口と対話セッションの間に橋が無い。

**How to apply:**
- ask_wait.py の「回答あり」を受けたら、作業前に Slack 検索でそのカードのスレッド（受付番号・件名）を読む。`slack_search_public_and_private` で件名語＋当日。
- 同じ件に受付番号（#s…）が振られていたら、窓口経由で別の担当が動いている前提で、その結果を先に確かめる。
- 重複に気づいたら、有璽氏が指定した側を正にし、自分の側は⛔降格（削除しない）→ スレッドへ報告。
関連：[[project_slack_command_center]] [[reference_two_sessions_built_the_same_thing]] [[project_gov_news_feed]]
