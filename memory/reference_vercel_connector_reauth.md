---
name: reference_vercel_connector_reauth
description: claude.ai の Vercel コネクタが切れたとき、つなぎ直しの途中で「Secure Your Account with 2FA」画面が出る。どう進めるか
metadata:
  type: reference
---

2026-10-08 10:46、有璽氏の画面で確認。Claude Code 側では Vercel のツール（mcp__claude_ai_Vercel__*）が全部切断扱いになっていた。

- つなぎ直しの途中で Vercel が「Secure Your Account with 2FA」を出す。中身は★二段階認証を勧める案内で、エラーではない
  - 「Set Up Authenticator App」：認証アプリ（iPhoneの「パスワード」アプリ、Google Authenticator など）でQRを読み、6桁の数字を入れる
  - 「Skip securing my account」：設定せずに先へ進む
- ★おすすめは設定する方。このアカウントは本番のドメイン（ko-station.org・kawachibanashi.osaka.jp）を持っていて、家計台帳の本番もここへ載せる予定
- ★Vercel の作業は、コネクタが切れていても CLI（vercel コマンド）で続けられる。家計台帳は顧客データを入れる段階まで Vercel を使わない
- 押した後の画面は Claude 側では見ていない。認可画面が出たら「Allow」を押し、claude.ai の設定画面でコネクタが「接続済み」になっているかを見る

関連：[[reference_vercel_free_plan_protection]] [[project_kakei_daicho]]
