# notion ── 分野索引

**Notion運用・各DB・Drive・共有**

> この分野の作業に着手したら読む。正本は各ファイルの本文。ここは索引。
> **上限は無い。** 毎ターン届く `MEMORY.md` と違い、必要なときだけ読まれる。
> 呼び出しの対応は [[INDEX_担当別]] にある。

- [claude.aiログ→Notion移行](project_claude_ai_logs_to_notion_migration.md) — 約15Projectの議論ログを📚ナレッジDBへ。パイロットの空ページ作成済・流し込み待ち
- [AI活用ログDB統合(案A)](project_ai_log_db_consolidation.md) — 単一台帳化。Phase1完了／Phase2(発信ネタDB統合・投稿生成)は保留
- [締切ダッシュボード](project_deadline_dashboard.md) — タスク/法務期日DBに🚦Formula、📆で横断。ビビ朝に🔴🟡集約
- [組織マスター4DB](reference_org_master_4db.md) — 組織軸の正本(部門/法人/部署/PJ)。担当者マスターのRelation張替は未実施
- [組織マスターの所在とコード](reference_org_master_notion.md) — 4DBのdata source ID。施設運営は15-300/15-400へ再コード化済
- [Relation双方向化の地雷](reference_notion_relation_dual_landmine.md) — one-way→DUAL変換で既存値が全件消失。新規列は最初からDUALで作る
- [DDLは説明文を消す](reference_notion_ddl_wipes_description.md) — ALTER COLUMN SETで選択肢を足すと列の説明が空になる。触る前に控える／ADD COLUMNは安全
- [タスクDB Relation付替](project_task_db_relation_migration.md) — Step1-5＋双方向化まで完了。残=ビュー実在確認・Step7降格処理
- [Notionナレッジハブ](reference_notion_knowledge_hub.md) — 業務管理Notion＋組織マスターの体系。別タブの会話は読めない
- [ローカルメモ棚卸し](project_local_memo_cleanup.md) — 約1,004件を20分類(未移動)。商談約300件は議事録DBの原資
- [共有ドライブのフォーム](reference_shared_drive_form_upload.md) — ファイル添付不可。フォーム本体だけマイドライブへ移す
- [共有ドライブの権限の床](reference_shared_drive_permission_floor.md) — 配下の権限を狭められない。`_機微`は無効＝別ドライブへ出す
- [Notionは戻せる](reference_notion_restore_path.md) — GETの生プロパティをPATCHで復元。★未実行のバックアップはバックアップでない
- [Notionを消してよい線](reference_notion_archive_line.md) — 配った/リンクされた/参照された が1つでもあれば消さない。消す前に被リンク0件を確認
- [Notion運用ルール正本](project_notion_operating_rules.md) — 読み書き前に必ず参照。4層モデル＋要約は鮮度ヘッダー必須
- [【廃止】最新版を最上部](feedback_notion_latest_version_top.md) — 規律依存で破綻し廃止。後継=Notion運用ルール正本
- [ナレッジ設計ページ](reference_notion_knowledge_design.md) — Drive住み分け・命名(事業×法人)の協議ハブ
- [Notion MCPの読み取り制約](reference_notion_mcp_read_limits.md) — ★404の切り分けは/v1/search／DBテンプレはAPI経由で効かない／実データはview mode
- [リンク共有は配下に効く](reference_link_sharing_inherits_everywhere.md) — 機微の置き場は共有設定／Notion公開はpublic_urlで数えられる(現在0件)
