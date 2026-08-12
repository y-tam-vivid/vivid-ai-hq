---
name: feedback_customer_files_drive_location
description: 顧客情報・kintone反映ファイルのDrive格納先は財務(03)でなく取引先・人物別(11)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 41edb8f6-2705-4dac-93d0-901e01d25136
---

顧客情報・kintone反映系のファイル（顧客マスター、kintone取込用61列xlsx、名刺反映の成果物等）のGoogle Drive格納先は、**`マイドライブ/Downloads書類アーカイブ/11_取引先・人物別/顧客情報kintone反映csv/`**。財務・経理・税務(03)フォルダではない。

**Why:** 顧客＝取引先データであり、経理書類ではない。2026-07-16にユーザーが「顧客情報関連は営業系フォルダへ」と指示し、フォルダごと03→11へ移管。「今後もそのように申し送りを徹底」と明言された恒久ルール。

**How to apply:** [[project_kintone_csv_to_notion_mirror]]／スキル`customer-db-sync`でDrive反映する際は迷わず11_取引先・人物別/顧客情報kintone反映csv/へ`cp`（md5照合）。targets.mdにも反映済み。名刺画像そのものの保管のみ02_デザイン・制作でよい。
