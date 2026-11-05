---
name: reference_clasp_login_expired
description: clasp の資格が両機とも invalid_rapt で切れている。GAS を clasp で触る前に確かめる。直し方と、無いときの逃げ道
metadata:
  type: reference
---

# clasp の資格は両機とも切れている（11/4 確認）

- 症状：`clasp` が `invalid_rapt` で失敗する。MacBook・Mac mini の両方で確認（11/4）。
- ★GAS を clasp で作る・push する前に、まず `clasp` の実行結果で資格の生死を確かめる（推測で進めない）。
- 直す：有璽氏の手で `! clasp login`（対話が要る）。AI は代わりにログインできない。
- 無いとき：ブラウザの GAS エディタで作る。開くときは `authuser=y_tam@…` を URL に付けて、個人アカウントを選ぶ。
- 初回の実行許可の前は、Web アプリの `/exec` が 403「アクセスが拒否されました」を返す（リール動画LPで実測・11/4）。許可の後に確かめる。

関連 → [[project_orangeworks_portfolio_site]]（リール動画LP・clasp で作った GAS） ／ [[reference_slack_tokens_and_socket_mode]]（同じ罠を別の面で踏んだ記録）
