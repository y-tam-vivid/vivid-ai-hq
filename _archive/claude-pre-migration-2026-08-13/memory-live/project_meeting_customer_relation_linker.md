---
name: project_meeting_customer_relation_linker
description: 議事録DB→顧客DBのrelationを自動付与するローカルバッチ。詰まり①の担い手として2026-08-12に決定・実装
metadata: 
  node_type: memory
  type: project
  originSessionId: 455160de-880a-40ac-b139-3f3a16f5750c
  modified: 2026-08-12T09:49:15.504Z
---

🔒個人議事録DBの「顧客」relationを自動で張るバッチ。**「誰が張るか未決」だった詰まりの答え＝独立ローカルスクリプト（毎朝07:35 cron想定）**として2026-08-12に決定・実装した。

- 実体：`~/.vivid-relay/notion_meeting_customer_link.py`（標準ライブラリのみ／Chatworkリレーと同居）
- 既定は **dry-run**、`--apply` で書き込み。`顧客` が空の行だけが対象＝**既存relationは絶対に上書きしない**
- 候補が**一意に決まったときだけ**張る。0件/2件以上は `meeting_customer_link_report.csv` へ回して人が見る
- 正規化：法人格（株式会社/合同会社/NPO法人等）・敬称（様/さん/氏）・記号・全半角・長音を落とす。括弧内外と区切り（・/／、）でトークン分割し順に照合。検証済み例＝`North object（大城様）`→`northobject`/`大城`、`BNI天竜・吉良さん`→`bni天竜`/`吉良`
- 対象母数 **320件**（2026-08-12実測。個人議事録DB 649件から「種別=社内/私用」「相手・会社が空」を除いた数）。導線として🔒個人議事録DBにビュー **「⚠️ 顧客未紐付（要relation）」** を新設済み

**GASに入れなかった理由**：議事録の登録処理を巻き込むリスクと、バックログ＋日々の新規を1本で処理できること。

**ブロッカー（田村さん手番）**：Notionインテグレーション「Chatworkリレー」を🏢顧客DB・🔒個人議事録DBに「⋯→接続」で追加する1操作。未実施だと `object_not_found`。これが済めば**詰まり③（毎朝07:30の`00_企業マスタ`→🏢顧客DB upsert）も同じトークンで実装できる**。

正＝[🔗 議事録DB × 顧客DB 連携フロー（現況まとめ）](https://app.notion.com/p/3b27b1568b578184902ffd4324882ed5) の8章。
関連 [[project_giji_automation_gas]] [[reference_kintone_customer_master]] [[reference_notion_mcp_read_limits]]
