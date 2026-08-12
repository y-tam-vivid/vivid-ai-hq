---
name: reference_apps_script_api_verification
description: Apps Scriptを生成したら node --check だけでは不十分。使用メソッドを所属クラス(Sheet/Range/Spreadsheet)と突合する
metadata: 
  node_type: memory
  type: reference
  originSessionId: 72d12c17-4bf6-4c52-9291-4421d31f8dab
  modified: 2026-07-31T00:00:22.219Z
---

**`node --check` は「存在しないメソッド」を検出しない。** 文法が正しければSYNTAX OKを返し、実行して初めて `TypeError: ... is not a function` になる。2026-07-31、`sh.clearDataValidations()` で実際に踏んだ（正しくは Range のメソッド）。

Apps Script（特にSpreadsheetサービス）を生成したら、構文チェックに加えて**使用した全メソッドを所属クラスと突合する**。Sheet / Range / Spreadsheet に似た名前が分散していて取り違えやすい。

```
Sheet : clear() clearContents() clearFormats() clearNotes() clearConditionalFormatRules()
Range : clearDataValidations()   ← 入力規則の解除だけRange側
```

突合の実務手順：
```bash
grep -oE "\b(sh|ss)\.[a-zA-Z]+\(" x.gs | sed 's/.*\.//' | sort -u   # レシーバ別に列挙
```

もう一点、**`onOpen` のカスタムメニューはスプレッドシートにバインドされたスクリプトでしか動かない**。script.google.com から作ったstandaloneでは出ない。メニューが要るなら「対象シート > 拡張機能 > Apps Script」から作らせる。

**動作確認前の成果物をNotionの「原本」として置き換えない。** 実行が通ってから差し替え、バグ版は消さずログとして残す。

関連: [[project_sales_pipeline_workbook]] [[feedback_generated_files_attach_notion]]
