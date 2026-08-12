---
name: reference_notion_mcp_read_limits
description: Notion MCPのSQLクエリはワークスペース上限あり。viewモードは無制限だが表示列指定は効かず全プロパティ返る
metadata: 
  node_type: memory
  type: reference
  originSessionId: 455160de-880a-40ac-b139-3f3a16f5750c
  modified: 2026-08-12T09:48:56.341Z
---

Notion MCPで大量行を読むときの制約（2026-08-12実地）。

- **`query_data_sources` のSQLモードはワークスペース単位の利用上限がある**（Business+Notion AI以外）。上限に達すると `Your workspace has reached the usage limit for Query Data Source` で全クエリが落ちる。復旧を待つしかない。
- **viewモード（`mode:"view"` + `view_url`）は上限なし**。大量読み取りはビュー経由に寄せる。`view_url` は `https://www.notion.so/<db-id>?v=<view-id>`（ハイフンなし）で組める。
- **viewの `SHOW` は返却JSONに効かない**。表示列を絞っても全プロパティが返るため、メモ等の長文列があると1ページ100行で60k文字級になる。→ 表示列で軽くしようとしても無駄。
- 対策：①巨大な結果はツールが自動でファイル保存するので、**Bash+Pythonでファイルを処理する**（contextに載せない）②そもそも件数が多いなら MCP でなく **Notion内部インテグレーション＋ローカルスクリプト**に切り替える。1行ずつのrelation更新をMCPでやるのは非現実的。
- 内部インテグレーションは**DBごとに「⋯→接続」で共有しないと `object_not_found`**。ページを共有しても配下DBに自動継承されない。

関連 [[project_meeting_customer_relation_linker]] [[project_notion_operating_rules]]
