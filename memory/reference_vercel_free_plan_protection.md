---
name: reference_vercel_free_plan_protection
description: Vercel無料プランでは固定URLを保護できない。塞ぐならMiddlewareのBasic認証（無料枠で動く）
metadata:
  type: reference
---

**Vercel の無料プラン（Hobby）では、`<project>.vercel.app` の固定URLを塞げない。**
2026-08-25 実測＋有璽氏の確認。

```
vercel project protection enable --sso
  → deploymentType は "prod_deployment_urls_and_all_previews" にしかならない
  → deployment固有URL（…-5n22jywnn-…）と preview は SSO で塞がる（302を実測）
  → ★固定URL <project>.vercel.app は塞がらない（素のGETで HTTP 200 を実測）

ダッシュボードで "All Deployments" にすれば塞がる
  → ★有璽氏の確認: **その設定は有料プランのみ**（Hobby では選べない）
```

**Why:** Vercel の Deployment Protection は「本番の固定URLまで守る」部分が有料機能。
CLI にも deploymentType を `all` にする口が無い。**プランの壁で、設定では解けない。**

**How to apply:**

```
塞ぎたいのが「社内向けの画面」なら ── ★Middleware の Basic認証を使う（無料枠で動く）
  middleware.js をプロジェクト直下に置くだけ。ビルド設定は要らない
  合言葉は Vercel の環境変数（暗号化保存）。★ソースにも memory にも書かない
  ブラウザが標準のログインダイアログを出すので、スマホでも見られる
```

- **★「保護がかかっているつもり」を作らない。**設定画面の表示ではなく、
  **素の `curl` で HTTP 401 が返ることを実測してから**中身を載せる。
- 公開してよい内容なら Basic認証は要らない。**判断の分かれ目は中身**
  （稼働盤は人名・Slackチャンネル名・会社数・仕組みの穴・DBのIDを含む＝社内限定）。
- 他の道と、選ばなかった理由
  | 案 | なぜ採らなかったか |
  |---|---|
  | 推測されにくいURLにする | 塞いだことにならない。漏れたら終わり |
  | Cloudflare Access | 無料枠はあるが独自ドメインが要る。DNSはさくらで当方に権限が無い → [[reference_vivid_dns_sakura]] |
  | GitHub Pages | private リポジトリの Pages は有料 |
  | 有料プランへ上げる | お金＝要承認。まず無料で解けるかを先に試す |

関連: [[project_ops_dashboard_artifact]] [[reference_plaintext_credentials_handling]]
[[feedback_verify_before_declining]]（できないと言う前に、別の道を数える）
