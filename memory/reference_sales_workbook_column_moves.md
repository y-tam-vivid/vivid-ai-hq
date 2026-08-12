---
name: reference_sales_workbook_column_moves
description: 営業案件管理ワークブックのマスタ2枚は列を移動してよい（全GASが見出し名で引く・2026-08-10に37本を実測）。受付シートは例外。apply_schema_v3.gsは実行禁止
metadata: 
  node_type: memory
  type: reference
  originSessionId: 72d12c17-4bf6-4c52-9291-4421d31f8dab
  modified: 2026-08-10T09:47:23.452Z
---

営業案件管理ワークブック（`1lcSexlRLHtV2zzBm0Te_KKmR2uzCawQLzkyY50nPoNY`）の **`00_企業マスタ` / `02_個人マスタ` は列を並べ替えてよい。** GAS 37本を実測したところ、この2枚を触るスクリプトに列を数値で指す箇所は1つも無く、全て見出し名で解決していた。

```
import_ledgers.gs   mi() = mHead.indexOf(列名)   行も mHead 長ぶんの空配列に名前で埋める
match_kintone.gs    head.forEach → idx[列名]
verify_import.gs    見出し名で15箇所
protect_master.gs   head.indexOf(colName)         保護対象も列名で決めている
```

数値で列を指しているのは `90_選択肢マスタ` のE列（流入経路の選択肢置き場）だけで、これは別シート。

**「列の追加は必ず末尾」という運用ルールは、列を位置で引いていた頃の前提。** 実装が名前引きに変わったあとも文言だけ残っていた。`protect_master.gs` のコメントが根拠にする「昇格スクリプト（受付シート→本体）」は**まだ存在しない**（移し替えは手作業）。

移動するときの条件は2つ。

- **見出し名を変えない。** 名前が鍵なので `流入経路詳細`→`流入経路_詳細` のような改名で全スクリプトが落ちる
- **切り取り＆貼り付けではなく「列の移動」を使う。** ドラッグまたは右クリック→列を左/右に移動。これなら入力規則・書式・保護が列と一緒に動く。切り取り＆貼り付けは入力規則が置き去りになる

移動後に不安なら `protectMasters()` を再実行すれば保護を貼り直せる。

**例外：受付シート（フォーム連携）は触らない。** 列を消すとフォームが管理範囲を復元しようとして空のプレースホルダ列が生える（[[reference_sheets_number_format_order]] ⑥）。移動も避ける。

**`apply_schema_v3.gs` は実行禁止。** 旧10値の流入経路（`フォーム営業/テレアポ/名刺/紹介/交流会/イベント/SNS/Web問い合わせ/セミナー/その他`）が固定で書かれており、再実行すると選択肢マスタが16値から巻き戻る。廃止した「イベント」も復活する。`buildWorkbook`（`sh.clear()` で始まる）と同じ扱いにする。

関連: [[project_sales_pipeline_workbook]] [[reference_sheets_number_format_order]] [[reference_apps_script_api_verification]]
