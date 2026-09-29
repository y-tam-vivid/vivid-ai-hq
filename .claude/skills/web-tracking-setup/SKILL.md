---
name: web-tracking-setup
description: ふくち。グループが外へ出すWebページ（LP・サービスサイト・会社サイト・キャンペーンページ・Claude Designの書き出し・WordPress）に、公開・送信の前に必ず計測セット（SalesBreaker 1行タグ／GTM・GA4／Microsoft Clarity のクリック録画・ヒートマップ／案別クリックログ）を入れ、検査を通すスキル。「LPを公開する」「サイトを出す」「デプロイして」「SalesBreakerで送る」「フォーム営業」「ABテスト」「クリックログ」「ヒートマップ」「アクセス解析」「計測タグ」等で必ず使う。★ページを外へ出す作業に着手したら、依頼に計測の言及が無くても読む。
---

# Webページの計測セット ── 公開・送信の前に必ず入れる

**2026-09-29 有璽氏「LPにログを取れる形（クリックログやヒートマップ）を構築して。普通のWebでも同じように使えるように。絶対に構築するスキルにして」。**
LPに限らない。**外へ出すページは全部これを通す。** 送ってから・公開してからでは、その間の記録は永久に取り返せない（2026-08 ゲームブル第1波の18社で実証）。

```
部品    ~/vivid-ai-hq/bin/web_tracking/snippet.html   <head> 直後に貼る。{{…}} 4か所を差し替える
検査    ~/vivid-ai-hq/bin/web_tracking_check.py        ✗が1つでもあれば終了コード1 ＝ 公開・送信しない
```

## 何が取れるか（4つは役割が重ならない。全部要る）

| 部品 | 分かること | 見る場所 |
|---|---|---|
| SalesBreaker 1行タグ | **どの会社が来たか**（会社名が出るのはこれだけ） | SalesBreaker のトラッキング画面／API `tracking/*` |
| Microsoft Clarity | **クリックの位置・ヒートマップ・画面録画・どこで離脱したか** | clarity.microsoft.com（フィルタ：`lp_variant` `lp_source` `cta_click`） |
| GTM → GA4 | 流入元・経路別・案別の比較 | GA4（イベント `cta_click`・`page_meta`） |
| クリックログ（snippet 内） | **どのボタンが・どの案で・どの経路から押されたか** | 上の Clarity と GA4 の両方へ同時に送る |

クリックログが自動で付けるもの：
```
lp_variant   URLのパスから作る   /kids/a → kids-a ／ / → root
lp_source    ?utm_source= の値   無ければ referral / direct
cta          押した要素の data-cta（無ければリンク先）
```

## 手順（ページの作り方を問わず同じ）

1. **ID を揃える**
   - SalesBreaker：`id` と `token` は画面の「1行タグ」から写す（既存例：id=17e298ff-5e02-4630-a16d-0f4f25ede23a）
   - GTM：既定は会社共有コンテナ `GTM-PQX3L4TQ`（GA4 `G-4D1C77WR0P` 入り）。共有して実害ゼロを実測済み
   - **Clarity：サイトごとに新しいプロジェクトを作る**（無料・数分・有璽氏の操作）。別サイトと混ぜるとヒートマップが混ざる
2. **snippet.html を `<head>` の直後に貼る**。{{SB_TRACK_ID}} {{SB_TRACK_TOKEN}} {{GTM_ID}} {{CLARITY_ID}} を差し替える
3. **押してほしいボタンに `data-cta="<置き場所>"` を付ける**（例 `hero` `header` `bottom` `form-submit`）
4. **経路と案はパスで分ける**（クエリだけに頼らない。SalesBreaker はリンクを書き換えてクエリが落ちうる）
   - 経路：`/ig` `/line` `/mail` `/sign` ＋ UTM の二重
   - 案（ABテスト）：`/a` `/b` `/c` または `/<対象>/<案>`
   - Vercel は `vercel.json` の rewrites。★`destination` は `"/"`（`/index.html` は 404）
5. **社内向けファイルを塞ぐ**：`.vercelignore` に `*.md` と `*.bak*`
6. **検査を通す**（✗ が0になるまで公開・送信しない）
   ```bash
   python3 ~/vivid-ai-hq/bin/web_tracking_check.py <公開前のファイル or URL> --paths /a /b /c /ig
   ```
7. **発火を実物で確かめる**（検査は「書かれているか」まで。送っているかは別）
   ブラウザで開き、`performance.getEntriesByType('resource')` に `clarity` `collect` `sb-track` の通信があること、
   ボタンを押して `dataLayer` に `cta_click` が入ること。手順の詳細 → memory `reference_lp_tracking_tags`

## 人の手が要るもの（押す場所まで）
- **Clarity のプロジェクト作成**：clarity.microsoft.com →「新しいプロジェクト」→ サイト名とURL → 表示されるID（10文字前後）を渡す
- **GA4 で `cta_click` を数える**（初回1回だけ）：GTM → トリガー「カスタムイベント」名 `cta_click` → タグ「GA4 イベント」イベント名 `cta_click`、パラメータ `lp_variant` `lp_source` `cta` をデータレイヤー変数で渡す → 公開
  ★これが無くても Clarity 側には案別クリックが残る

## やってはいけない
- 計測が ✗ のまま「とりあえず公開」「先に送って後で入れる」
- Clarity の ID を別サイトと共有する
- `?v=` などクエリだけで案を切り替える（送信ツールのリダイレクトで落ちると全員が既定の案になる）

## 関連
memory：`reference_salesbreaker_campaign_setup`（送信前の3点）／`reference_lp_tracking_tags`（発火を確かめる3手）
