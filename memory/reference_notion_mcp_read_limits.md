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
- 内部インテグレーションは**DBごとに「⋯→接続」で共有しないと `object_not_found`**。ページを共有しても配下DBに自動継承されない（2026-08-13 実測：親ページ `ビビッド業務管理` 未共有のまま、明示接続した3DBだけが通った）。

## ★ relation は「相手側DBも共有されていないと空で返る」（2026-08-13 実測）

**これは D型の事故＝エラーも出さず完走して、件数だけ静かに違う。** 同一レコードを2経路で読んで確定させた。

```
株式会社Kinection の 自社取引担当者
  MCP（OAuth・ユーザー権限）        → 担当者ページ1件が入っている
  内部インテグレーション（API）      → "relation": []   ← 空に見える
                                      （相手＝👤担当者マスターDBが未共有のため）

🔒個人議事録DB 先頭100件（API経由）
  部門 rel = 0 / プロジェクト rel = 0   ← 相手DBが未共有
  顧客 rel = 12                        ← 🏢顧客DBは共有済みなので見える
```

**帰結**：
- **APIでNotionのrelationを読む処理は、相手側DBを共有するまで書かない。**「空だから埋める」と判断すると既存の紐付けを壊す。
- upsert等を書くときは **relation列に一切触れない**のが安全（埋めるべきは事実列と鍵）。
- **MCPで見えたからAPIでも見える、は成り立たない。** 経路が違えば見える範囲が違う。片方の観測で他方を検証しない（実際、別セッションがMCPで数えた値を根拠に「APIでも見えている」と誤結論を出しかけた）。

関連 [[project_meeting_customer_relation_linker]] [[project_notion_operating_rules]]
