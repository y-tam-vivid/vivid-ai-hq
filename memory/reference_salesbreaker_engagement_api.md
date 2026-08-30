---
name: reference_salesbreaker_engagement_api
description: SalesBreakerのクリック回数・ホットリード・会社単位キーはengagement/searchで全部取れる。deals/searchしか見ずに「取れない」と9日止めた
metadata:
  type: reference
---

**`engagement/search` を使う。`deals/search` ではクリック回数が取れない。**
2026-08-18 実測。9日間「APIでは取れないから先方に聞くしかない」と止まっていたが、
**`deals/search` しか見ていなかっただけ**だった。

```
POST https://salesbreaker.jp/api/operator/v0/engagement/search
  Bearer 認証（キーは ScriptProperties の SB_API_KEY・値は出力しない）
  { "pagination": {"limit":100}, "filters": {...} }
        ★ limit は pagination の下。トップに置くと 400
```

## 取れるもの（すべて実測）

| 欲しいもの | どこに |
|---|---|
| クリック回数 | `data.events[].engagement.click_count`（実数） |
| ホットリード | `filters.follow_up_only:true` + `min_clicks:2` → 通知メールと同数 |
| **会社単位のキー** | `target.target_key`。`target_rollups` がこれで集約している |
| 先方のステータス | `deal_context.status`（"未設定" 等） |
| 架電ステータス | `deal_context.call_status` |
| 未対応フラグ | `deal_context.unresolved` |
| 判定理由 | `reason_codes`（`multiple_clicks` / `deal_unresolved`） |
| 母数 | `min_clicks:1` + `follow_up_only:false` |

**`target_key`＝会社単位／`deal_id`＝送信単位。** 1社に複数 deal_id がある（実測3件）。
会社単位で1行にしたいなら `target_rollups` を使う。deal_id で流すと重複する。

## 最終クリック日時は取れない（不具合ではない）

```
sources: ["click_logs","web_tracking_logs"] は正しい書き方（requested_sources に反映される）
  → 警告 engagement_sources_deferred
     "Turn 72 reads click_logs first; requested non-click sources are deferred."
     source_handling.web_tracking_logs = "deferred timeline source"
```

**時系列を持つ源を先方がまだ有効化していない。** 保持していないのでも壊れているのでもない。
`latest_clicked_at` は `{}` のまま。**検知日はこちら側で持つ。**

## この API は叩けば仕様を教えてくる

```
エラー本文     直し方まで書いてある（"pagination.limit is required for engagement.read"）
next_actions   次に叩ける口を capability 名つきで返す
source_handling 5つのデータ源の役割を英文で返す
read_only:true  db_written / send_executed / csv_generated が false と明示される
```

**ドキュメントを探すより叩くほうが速い。** 先方の人に聞く必要がない
（先方の人とはやり取りしない ── 2026-08-18 有璽氏）。

**書き込みの口も見えている**（`activity.log` / `task.create` / `deal.activity.read`）が
**未実測・未使用。触る前に承認を取る。**

## プローブの作り方（2回ログが切れた）

全キーを再帰列挙すると Apps Script のログが打ち切られる。**最初の1回だけ列挙し、
以降は1件1行に圧縮する。** 社名・URL・電話・担当者メール・target_key・client_id は
ホワイトリスト方式で伏せる。

## 教訓

**調べた範囲を、調べ尽くした範囲だと思い込んだ。** `deals/search` が返さないことは、
`deals/search` について分かったことでしかない。同じ型で4回続けて誤った
（「未接続」→毎朝同期していた／「回数は無い」→通知メールにあった／「APIでは取れない」→別の口）。
→ [[reference_ai_output_blamed_before_inputs]]
→ [[project_sales_pipeline_workbook]]

## companies/search のフィルタは効くものと効かないものがある（2026-08-23〜27 実測）

```
✓ industry_class   効く。★ただし部分一致なので誤爆する（「エステ」で建築設計がヒット）
                   マスタの正式名を使う（「カフェ・喫茶店」「学習塾・予備校」など52種類）
✓ prefecture       効く（address も同じ）
✗ keyword          ★効かない。無視されて先頭が返る
                   6社を別々の語で引いたのに、全部同じ会社（aelva-ns.com）が返った
✗ area / query     効かない
```

**「フィルタを付けたら結果が変わった」だけでは効いた証拠にならない。**
存在しない値を入れて0件になるか、返り値の中身が条件と一致するかで確かめる。

## activity.log の書き方（2026-08-27 実測・18件成功）

```json
{"target": {"deal_id": 65489925},
 "summary": "LPクリック3回／要フォロー",
 "details": "…"}
```

- `target.deal_id` と、`summary` または `details` が必須
- ★**deals/upsert/preview は 403「Production route closed in this pilot phase」**
  ＝ **案件のステータス変更はできない。** 書けるのは活動ログだけ
- deal_id は `engagement/search` の `deal_context.deal_id` から取れる

## ★接続の経路（2026-08-27 有璽氏の問いで実測）

有璽氏「SalesBreaker側とは **GitHubを経由して**既に繋がっていると思うけど」

```
★GitHub ではない
実体      Google Apps Script の ScriptProperties に SB_API_KEY
          → **GAS側から叩いている**
mini側    config.env に鍵は無し（0件）／叩く実装も無し
          ＝ このマシンからは直接叩けない
vivid-ai-hq  設定を配るためのリポジトリ。★SalesBreakerとの接続経路ではない
```

**★「繋がっている」と「どこから繋がっているか」は別。**
鍵の在り処を確かめないと、どのマシンで作業すればよいか分からない。
→ [[reference_tool_access_map]]（道具ごとの鍵の在り処）

## ★住所を先方へ聞く前に、自分で叩いて確かめる（2026-08-27）

```
有璽氏の見立て  「こちらで提供した住所録なので渡してはいる。
                 そもそも多分絶対ある。**だって絞れるもん**」
当方の実測      05_問い合わせ営業リスト（受け取り口）に住所の列は無い
★結論の出し方   「受け取り口に無い」は「先方が持っていない」ではない
                 ★エラー本文が直し方を教えてくれる ＝ **叩けば分かる**
```

**★メールを書く前に、APIを1回叩く。** 聞かずに済むなら、そのほうが速い。
（★ただし先方の人とはやり取りしない ── 2026-08-18 有璽氏。
　どうしても必要なら、送るのは有璽氏）

## ★契約が turn82 になり、読み取り経路の多くが閉じた（2026-08-28 実測）

`bin/capability_check.sh` の contract が **`operator-turn75-…` → `operator-turn82-tracking-read`**
に変わっていた。**capability一覧には35本すべて enabled と出るが、実際に叩くと403が返るものがある。**

```
★capability に載っていること ≠ 叩けること。一覧だけで判断しない
  403 operator_production_route_closed
     templates/list  templates/get  saved-lists/list  campaigns/preview
     history/list    engagement/summary
  200 生きている
     templates/preview        ★テンプレの中身（件名・本文・URL）を読む唯一の経路
     saved-lists/preview      ★リストの名前と件数を読む唯一の経路
     tracking/summary         ページ別・参照元別のアクセス
     companies/search         企業の抽出
     activities/log           dealへの活動記録
```

**確かめ方**

```python
# テンプレ  {'template_id': 1609} → data.rendered に件名・本文、data.url_present
call('/api/operator/v0/templates/preview', {'template_id': 1609})
# リスト    {'saved_list_id': 735} → saved_list_name / target_count
call('/api/operator/v0/saved-lists/preview', {'saved_list_id': 735})
```

- **★件数の大きいリストは 504 になる**（7,735件のリスト728で実測）。失敗＝不在ではない
- **`templates/save` は 2026-08-27 に実際に通った実績がある**（本文が書き換わったことを
  preview で確認済み）。ただし turn82 以降に通るかは未検証。**送信直前にテンプレを触らない**
  ── save が壊れても読み取りが403だと気づけない時期があった

## ★送信直前にテンプレを触らない（2026-08-28 判断）

第2波3,121件の送信前、URLを `/form?utm_source=…` へ更新するか検討して**やめた**。

```
利得   GA4の集客レポートで「salesbreaker / form」と明示的に見える
リスク save が本文を壊すと、3,121件が壊れた文面で送られる
       経路の識別は「/ (フォーム営業) と /ig (IG DM)」で既に足りている
判断   触らない。利得よりリスクが大きい
```
