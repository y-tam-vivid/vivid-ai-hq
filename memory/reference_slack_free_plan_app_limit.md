---
name: reference_slack_free_plan_app_limit
description: ふくち。の Slack は無料プラン＝アプリは10個まで（既製もカスタムも数える）。新しい App を作る案を出す前に、既存の bot で済ませる
metadata:
  type: reference
---

**ふくち。の Slack は無料プラン（2026-11-04 有璽氏「以前にもあった」）。無料プランでは、入れられるアプリが10個までになる。**
- 公式のヘルプと料金のページでは10個。既製のアプリもカスタムアプリも数える。一部の地域版のページには3個と書かれているが、古い記載とみてよい。
- いま何個入っているかは、このセッションでは数えていない（管理画面「アプリを管理する」で見られる）。

**何をしたか（2026-11-04 リール動画LP）**
- Incoming Webhook が1本も無かったので、「通知だけの App を新しく作る」手順を有璽氏に渡した。
- 有璽氏から「無料なので複数のアプリは作れないのでは」と戻ってきた。前にも同じことがあったのに、記録が無かった。

**How to apply**
- Slack へ通知を足すときは、新しい App を作る案を最初に出さない。
- 次の順に、使える道を探す。
  1. 既存の bot（mini の `notify.py`／`ask_hub.py` が使う bot token）から chat.postMessage で送る
  2. 既存の App に Incoming Webhook を足す（scope が増えるので、入れ直しが1回要る）
  3. メールで送る
- 新しい App を作る案を出すときは、「10個の枠のうち1つを使う」と添える。

関連 [[reference_slack_tokens_and_socket_mode]] [[project_orangeworks_portfolio_site]]
