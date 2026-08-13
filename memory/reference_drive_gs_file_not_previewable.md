---
name: reference_drive_gs_file_not_previewable
description: Driveへ拡張子なし/.gsで置いたファイルはoctet-streamになりプレビュー不可。リネームでは直らないのでGoogleドキュメントとして作り直して渡す
metadata: 
  node_type: memory
  type: reference
  originSessionId: 72d12c17-4bf6-4c52-9291-4421d31f8dab
  modified: 2026-08-11T10:08:57.392Z
---

**GASを共有ドライブへ渡すときは、Googleドキュメントとして作成する。** `.gs` や拡張子なしでローカルのDriveストリーミング同期に置くと、Driveは `application/octet-stream` として保存し、ブラウザでプレビューできない（「このファイルはプレビューできません」でダウンロードしか出ない）。

**リネームでは直らない。** `xxx.gs` → `xxx.gs.txt` に変えても `mimeType` は `application/octet-stream` のまま。Driveはアップロード時に決めた型を持ち続け、名前の変更で再判定しない（2026-08-11実測、`get_file_metadata` で確認）。

有効な渡し方：

- `google_drive create_file` に `contentMimeType: 'text/plain'` ＋ `textContent` を渡す。既定でGoogleドキュメント（`application/vnd.google-apps.document`）へ変換され、ブラウザでそのまま読める・全選択してApps Scriptエディタへ貼れる
- ドキュメント化してもコード中のシングルクォートはスマートクォートに化けない（インポート済みテキストには自動置換が掛からない）
- 実行順があるスクリプトは、ファイル名の先頭に `①先に実行` `②あとに実行` を付ける。フォルダ内で名前順に並ぶ

**ローカル同期側に置いた生テキストは残してよい**が、Driveでは開けないので `【原本テキスト】` と明示して取り違えを防ぐ。

ユーザー（田村さん）はmac miniのローカルを直接触れないため、**Driveで開けない形式で置くことは「渡していない」のと同じ。**

関連: [[project_sales_pipeline_workbook]] [[reference_sales_workbook_column_moves]] [[feedback_generated_files_attach_notion]]

**AIからの読み取りは別問題（2026-08-13 追記）。** ブラウザでプレビューできないだけで、`.gs.txt`（mimeType `text/plain`）として置かれた原本は `read_file_content` で読める。営業ワークブックのGAS 6本は Drive フォルダ `1phKsApqIzTYmNTeMewUGFfkDjMz8He7V` にこの形で在り、実物検証が可能。「プレビュー不可＝AIも読めない」と早合点しない。[[reference_dangerous_entrypoints]]
