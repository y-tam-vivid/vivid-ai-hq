---
name: feedback_sales_workbook_hands_off
description: 営業案件管理スプレッドシートは勝手に触らない。GASは読む場合も含め着手前に確認を取る。実行は禁止扱い
metadata:
  node_type: memory
  type: feedback
---

**営業案件管理スプレッドシートを勝手に触らない。GAS を触るときは先に確認を取る。**
（2026-08-13 本人指示。理由＝「今作ったものが壊れるから」）

**Why:** ワークブックは現在も構築・調整の途中で、外から書き込むと進行中の作業が壊れる。
加えて `buildWorkbook` / `applySchemaV3` は**実行すれば壊れることが実測で確定している**
（→ [[reference_dangerous_entrypoints]]）。「検証のため」も実行の理由にならない。

**How to apply:**

| 操作 | 扱い |
|---|---|
| シートへの書き込み・列や選択肢の変更 | **禁止。** 依頼されても着手前に内容を提示して承認を得る |
| `buildWorkbook()` / `applySchemaV3()` の実行 | **禁止。** 検証目的でも走らせない |
| `matchKintoneRun()` の実行 | 書き込み側なので**確認なしで回さない** |
| `matchKintoneDryRun` / `Report` / `Orphans` | 書かないが、実行前に一声かける |
| `.gs.txt` / シートの**読み取り** | 無害だが、**読んだことを本人に言える状態にしておく** |

※ この指示は別セッション経由で伝わったもの（2026-08-13）。本人の言葉は
「営業案件管理スプレッドシートは勝手に触らない。GASを触るときは先に確認を取る」。
意図と食い違っていた場合はこのファイルを直す。

関連: [[project_sales_pipeline_workbook]] [[project_sales_workbook_read_first]]
[[reference_sales_workbook_column_moves]] [[feedback_show_diff_before_edit]]
