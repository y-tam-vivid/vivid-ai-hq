---
name: reference_vercel_github_actions_secrets
description: daco-kun のデプロイを Vercel の Git 連携から GitHub Actions へ移すとき、有璽氏の手でしかできない操作が2つある（10/8）
metadata:
  type: reference
---

2026-10-08 に開発担当から届いた依頼。

- フォーク `y-tam-vivid/daco-kun` は★有璽氏の個人アカウントにある。リポジトリの Secrets を登録できるのは★持ち主だけ。個人アカウントには、他の人へ管理者権限を渡す仕組みがない
- Vercel の Git 連携を切る（Disconnect）操作は、★編集者（Member）の権限ではボタンが押せない。オーナーの有璽氏が押す
- 手順：①Vercel のプロジェクトで「Settings」→「Git」→「Disconnect」 ②Vercel のアカウント設定の「Tokens」でトークンを発行する ③GitHub のフォークで「Settings」→「Secrets and variables」→「Actions」に3つ登録する
- 3つの名前は★一般的な型からの推測：VERCEL_TOKEN／VERCEL_ORG_ID／VERCEL_PROJECT_ID。リポジトリは非公開で、ワークフローの中身は確かめていない。登録するときは★開発担当の指示文に書かれた名前を正とする
- トークンは★チャットに貼らない。発行画面から GitHub へ直接コピーする。発行時は使える範囲（Scope）をそのチームだけにし、期限を付ける

関連：[[reference_vercel_connector_reauth]] [[reference_plaintext_credentials_handling]]
