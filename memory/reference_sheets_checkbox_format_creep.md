---
name: reference_sheets_checkbox_format_creep
description: Sheetsのチェックボックス書式は空行に残っていると、後からその行にデータが入った瞬間にfalseが値として混入して事故になる。「空行だから実害なし」で放置しない
metadata: 
  node_type: memory
  type: reference
  originSessionId: 72d12c17-4bf6-4c52-9291-4421d31f8dab
  modified: 2026-08-12T02:26:01.102Z
---

**Sheetsでチェックボックスの入力規則が列に敷かれていると、未チェック＝`false` が値として入る。** 空行のうちは無害に見えるが、`String(false)` は `'false'` で空文字ではないため、後からその行に実データが入った瞬間に「値が入っている」と判定されて下流を壊す。

2026-08-12の実例：`00_企業マスタ` の `kintoneレコード番号` 列（3〜780行の全域にCHECKBOX）。8/8にtoC台帳から2社を778行・780行へ追加したところ、kintone更新CSVのキーが `FALSE` になった。**8/9に同じ現象を見て「空行なので実害なし・シート全体の書式であって欠陥ではない」と判断して放置していた。この判断が誤り。**

- **「今は無害な書式」は、行が増えれば有害になる。** 空行に見えていても行番号は予約されていない
- 書式の異常を見つけたら、実害が出ていなくてもその場で潰す。「空行だから」は先送りの理由にならない
- 数字が入っているセルとCHECKBOX規則は共存する（規則違反のまま値が残る）。**3行目を見ただけでは「規則なし」と誤認しない**
- 潰すときは列ごとに判定を変える。`kintoneレコード番号`＝正の整数だけ残す／`kintone突合方法`＝真偽値だけ消す（文字が入る列に数字判定をかけると全部消える）
- 直し方は `clearDataValidations()` ＋ 不正値だけ `setValues('')`。関係区分など**本来チェックボックスの列は除外**する

**CSVを出したら、キーが期待する形（数字なら数字）かを必ず検査する。** 値の検査だけでは足りない。スクリプト側に検査を内蔵し、不正なら出力せずに止めるのが確実（`~/data/houjin_bangou/channel_update_csv.gs` の `checkRecordKeys_`）。

関連: [[project_sales_pipeline_workbook]] [[reference_sheets_number_format_order]] [[reference_kintone_csv_import_landmines]]
