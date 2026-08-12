---
name: project_sales_pipeline_workbook
description: 営業案件管理の3層構造(スプレッドシート=案件層/kintone=確定層/Notion=参照)とその語彙統一プロジェクト
metadata: 
  node_type: memory
  type: project
  originSessionId: 72d12c17-4bf6-4c52-9291-4421d31f8dab
  modified: 2026-08-08T01:27:44.081Z
---

福祉施設・補助金・toCの3事業ラインを1つのスプレッドシート「営業案件管理」（`1lcSexlRLHtV2zzBm0Te_KKmR2uzCawQLzkyY50nPoNY`）で管理し、確定した顧客だけをkintoneへ流す構造。**議論の正本は⑥ディスカッションログの当スレッド** `3ab7b1568b5781dca1b3c453f27c7bd9`（2026-07-28〜継続）。

```
[案件層] スプレッドシート  上流5値(未着手〜見積提示)を含む全ステータス
   ↓ 商談成立で
[確定層] kintone          検討中以降のみ。顧客管理77件 / 案件管理15件
   ↓ ミラー
[参照層] Notion 🏢顧客DB
```

**層の役割分担は「語彙を揃える」より優先する。** 2026-07-31に「kintoneに無い値はkintone側に追加していく」と決めたが、2026-08-02に修正：**ラベルはkintoneをスプレッドシートに合わせる／選択肢の網羅は層の役割に従う**。上流5値をkintoneに持たせると同じ案件が両層に並走し、どちらが正か判定できなくなる。

3層ID＝社内顧客ID（00_企業マスタでのみ発番）／カスタマーID（kintone自動付与）／法人番号（全レイヤーの結合キー）。kintoneへの再取り込みは**手動・週次ルーティン**（2026-08-02 田村さん確定）。

**2026-08-03に台帳統合とkintone反映が完了。企業マスタ387件 ⇄ kintone384件が1対1。**突合の鍵は**社内顧客ID**（kintoneに同名フィールドを追加済み）。法人番号・会社名・電話番号は補助。手順書は `共有ドライブ/13-001_営業・顧客リスト/週次ルーティン手順書.md`。

月曜15時の6ステップ：①kintoneからエクスポート（**UTF-8・.csv のまま**）→ ②`matchKintoneRun()` → ③`buildUpdateCsvRun()` → ④`buildInsertCsvRun()` → ⑤kintoneへ取り込む → ⑥`verifyImport()`。**②を飛ばすと重複が作られる。**

**GASの原本はDriveの「スクリプト原本」フォルダ `1phKsApqIzTYmNTeMewUGFfkDjMz8He7V`（`13-001_営業・顧客リスト` 配下）。** 命名は `<関数名>.gs.txt`、改訂版は `（YYYY-MM-DD改訂・変更点）` を付す。ローカル `~/data/houjin_bangou/*.gs` は作業用で原本ではない ── **書いたら必ずここへ上げる**（2026-08-08 田村さん指示）。2026-08-08時点で25本同期済み（match_kintone / kintone_export_csv / verify_import / find_duplicates / merge_duplicates / import_kintone_orphans / fix_mislinked / weekly_backup / protect_master / freeze_ledgers / create_intake_form ほか）。**すべてドライラン→本実行の二段構えで、引数なしは必ずドライラン。**

`buildWorkbook` は `sh.clear()` で始まるため**データ投入後は絶対に実行しない**。スキーマ変更は必ず移行関数で当てる。

**誤った法人番号は空欄より有害。**kintoneの結合キーなので別法人に紐づく。採用条件は「13桁＋検査数字＋**国税庁の商号が社名と一致**」。住所が分からない会社には当てない（同名法人が複数ある）。`auditCorpNumbers()` で96_法人番号補完を全行検査できる。

関連: [[reference_kintone_customer_master]] [[project_kintone_csv_to_notion_mirror]] [[reference_kintone_subtable_rows]] [[reference_gviz_large_sheet_access]]
