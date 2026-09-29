---
name: web-tracking-setup
description: ふくち。グループが外へ出すWebページ（LP・サービスサイト・会社サイト・キャンペーンページ・Claude Designの書き出し・WordPress）に、公開・送信の前に必ず計測セット（SalesBreaker 1行タグ／GTM・GA4／Microsoft Clarity のクリック録画・ヒートマップ／案別クリックログ）を入れ、検査を通すスキル。「LPを公開する」「サイトを出す」「デプロイして」「SalesBreakerで送る」「フォーム営業」「ABテスト」「クリックログ」「ヒートマップ」「アクセス解析」「計測タグ」等で必ず使う。★ページを外へ出す作業に着手したら、依頼に計測の言及が無くても読む。
---

# Webページの計測セット ── 公開・送信の前に必ず入れる

**2026-09-29 有璽氏「LPにログを取れる形（クリックログやヒートマップ）を構築して。普通のWebでも同じように使えるように。絶対に構築するスキルにして」。**
LPに限らない。**外へ出すページは全部これを通す。** 送ってから・公開してからでは、その間の記録は永久に取り返せない（2026-08 ゲームブル第1波の18社で実証）。

```
部品    ~/vivid-ai-hq/bin/web_tracking/snippet.html（v2）  <head> 直後に貼る。{{…}} 4か所を差し替える
検査    ~/vivid-ai-hq/bin/web_tracking_check.py        ✗が1つでもあれば終了コード1 ＝ 公開・送信しない
★検問  ~/vivid-ai-hq/bin/hooks/hook_web_tracking_gate.py（2026-09-29 有璽氏「即実装・一般のサイトでも標準に」）
        Webページの公開コマンド（vercel・netlify・wrangler・firebase・surge・redeploy.sh）と
        SalesBreaker の文面保存（curl で templates/save）の直前に自動で検査し、✗なら★機械が止める
        両機へは setup_hooks.sh が15分以内に自動配布。毎朝の hook_selfcheck で生死を点検
        直したら必ず bin/web_tracking/test_gate.py（160件・ネットに出ない・JS は node で実行）を全件通す
        公開の検査：<html を持つ完全なページを全部見る（archive/review/components/includes も対象・.htm も見る）。
                    除外は node_modules・.git・.vercel・.next・_backup と、<html を含まない断片だけ。★除外した枚数と理由は出力に出る。
                    300枚を超えたら黙らず「未検査N枚」を出す。タグは <script> の中に在ることが条件（コメント・本文の文字列は数えない）
        SB の検査：着地先は並列で取得・全体20秒の上限。307/308 の転送は5回まで追う。★上限切れ・403（bot 検問など）は「検査できなかった」＝止めずに警告で通す
                    （検査不能で止めると、SB 障害・ネット断のたびに全送信が止まる。計測が無いと分かったものは deny のまま）
対象外  ~/vivid-ai-hq/bin/web_tracking/exempt.json    社内画面・スタッフ確認用・解析しないと決めたサイト。★理由必須・有璽氏の了解
        paths：ディレクトリは完全一致かパス区切り単位の配下／URL は★ホスト完全一致（host.evil.example は通らない）
        own_domains：★SB の文面で着地先として検査する自社ドメイン（いまは vivid-global.com／orange-works.co／i-life-fukushi.com／fuku-chi.com）。
                     ★*.vercel.app（自社の Vercel エイリアス）は常に自社扱い。末尾一致は「.」区切り（evil-vivid-global.com は別物）
                     文面のカレンダー予約リンク等の他社URLは検査せず注記のみ。★自社で新しいドメインを持ったらここへ足す
```
**★スキルを読み忘れても、公開の瞬間に検問が止める。止められたら、この手順どおりに入れてから出し直す。**
★効かない場面（＝守れない。ここは人が手で検査を通す）：
- cron が直接走らせる公開（Claude を通らない）
- Python 等のスクリプトの中から SalesBreaker へ保存する場合（コマンドに現れない）
- 文面を変数・ファイルの中身で組み立てて送る場合のうち、コマンド文字列にも @file にも URL が現れないもの（例：`$(cat …)` や別スクリプトが作ったファイルを標準入力で渡す）
- `sudo -u root vercel` のように、包む語の値つきオプションの値が先頭語に見える形
- Next.js 等の HTML を持たないサイト（警告だけ出して通す→公開後に URL で検査する）
★拾える包み方：`url=$(…)`／timeout・nohup・nice・xargs・sudo・env の後ろ／`vc`・`vercel@版`／`source ./redeploy.sh`／`ssh host 'cmd'`（中身を読む）／`bash -c '…'`／`if …; then`／`pushd X && …`／`(cd X && …)`／`vercel <dir> --prod`。
★閲覧は止めない：`vercel --scope team ls`・`--help`・`-h`（値を取るオプションの値をサブコマンドと読み違えない）。

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
lp_source    ?utm_source= の値   無ければ referral / direct。★最初のページで決めて sessionStorage に保持し、
                                 同じサイトの2ページ目以降も同じ経路（最初が direct/referral なら後から来た utm を採る）
cta          押した要素の data-cta（無ければリンク先。★tel: と mailto: は中身を送らず "tel" "mailto" だけ）
form_submit  form の送信（data-cta の有無を問わず。Enter キー送信も。action のクエリは送らない）
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
