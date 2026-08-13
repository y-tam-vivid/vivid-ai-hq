---
name: reference_dangerous_entrypoints
description: 実行の入口は名前と既定値から挙動が読めない。何もしない/壊す/順序が罠、の3型。cron・メニュー・手順書に載せる前に実測で1回確かめる
metadata:
  node_type: memory
  type: reference
---

**規則はこれ1行。**

> **cron・メニュー・手順書に載せる前に、その1行が「書くのか、書かないのか、壊すのか」を実測で1回確かめる。名前からは判断しない。**

2026-08-13 に実際にやらかしかけた: `notion_meeting_customer_link.py` を毎朝の cron に載せる行を
提示したが、**`--apply` が無いため毎朝ログを吐くだけで1件も書かない**設定だった。
作成者本人の指摘で発覚。「登録したから動く」と思い込んだまま数週間過ぎうる形だった。

## 3つの型

**A. 呼んでも何も起きない**（安全側に倒れていて、動いていないことに気づかない）

| 入口 | 挙動 | 出典 |
|---|---|---|
| `notion_meeting_customer_link.py` | 既定 dry-run。`--apply` が無いと1件も書かない | **実測済み**（作成者が2026-08-13に確認） |
| `matchKintoneDryRun()` / `matchKintoneRun()` | Dry版と本番版が**別関数名**。Dry側を回して「終わった」と誤認しうる | 手順書・メモリ由来（7月〜8月上旬）**未再検証** |

**B. 呼ぶと取り返しがつかない**（危険なのに名前が普通）

| 入口 | 挙動 | 出典 |
|---|---|---|
| `build_sales_pipeline.gs` の `buildWorkbook` | **実行禁止**。`sh.clear()` で始まりデータが消える | 二次（`apply_schema_v3.gs.txt` 冒頭に作者本人が明記）。実物は未読 |
| `apply_schema_v3.gs` の `applySchemaV3()` | **実行禁止**。下記3点 | **実測済み（2026-08-13・実ファイル読了）** |

### `applySchemaV3()` が壊すもの（実測）

1. `90_選択肢マスタ` を `clearContent()` してから、**スクリプト内のリテラル `CHOICES_V3` で敷き直す**。
   選択肢の正がシートではなく**このファイルの中**にある。
2. そのリテラルの `流入経路` は **10値**（フォーム営業/テレアポ/名刺/紹介/交流会/イベント/SNS/
   Web問い合わせ/セミナー/その他）。現行が16値なら**差分は消える**。
3. **いちばん危険なのはこれ。** `applyValidationsV3_()` が全シートに入力規則を貼り直すが、
   当て先が**列番号ハードコード**（`00_企業マスタ` の 12/13/14/17/18/22 等）。
   **列を動かしていると別の列に入力規則が当たる。**

> ⚠️ 3 は [[reference_sales_workbook_column_moves]]（「マスタ2枚は全GASが見出し名で引く」）と衝突する。
> **`apply_schema_v3.gs` は見出し名で引いていない。**「列移動してよい」はこのファイルには適用されない。

**C. 順序・選択肢の既定が罠**

| 罠 | 結果 | 出典 |
|---|---|---|
| 週次kintone同期で `matchKintoneRun()` を飛ばして `buildInsertCsvRun()` を流す | 同じ会社をもう一度作る（手順書に「実際に2回失敗」と明記） | 手順書由来 **未再検証** |
| kintone取込で「エラー行のみスキップ」を選ぶ | 一部だけ入り、次回が重複エラーになる | 手順書由来 **未再検証** |

## 出典についての注意

**`.gs` はこのMacに存在しない**（Apps Script 側にある）。ローカルから実物を確認できないため、
上表の「未再検証」はすべて**写し（メモリ・手順書）を根拠にした記載**であり、
関数名が改名されている可能性がある。[[feedback_read_the_artifact_not_the_copy]] に従い、
**これらを根拠に「安全だ／危険だ」と断定しない。** 使う前にスクリプトエディタで実物を開いて確かめる。

確定させるときは、確認した人が出典欄を「実測済み（YYYY-MM-DD）」へ書き換える。

関連: [[project_sales_pipeline_workbook]] [[reference_sales_workbook_column_moves]]
[[reference_kintone_csv_import_landmines]] [[reference_mac_mini_execution_env]]
