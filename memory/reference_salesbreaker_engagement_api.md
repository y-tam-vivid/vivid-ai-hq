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
