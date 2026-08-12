---
name: reference_notion_relation_dual_landmine
description: NotionのRelation列をone-way→DUAL(双方向)変換すると既存値が全件消える。新規列は最初からDUALで作る
metadata: 
  node_type: memory
  type: reference
  originSessionId: c098c0e5-29ff-47a2-a799-997db13145e0
  modified: 2026-07-21T05:12:00.799Z
---

Notion の Relation 列を **one-way → DUAL（双方向）に変換すると、入っていた Relation 値が全件 null になる**。列の構造と逆方向プロパティは正しく生成されるが、値はタスクDB側・マスター側の両方から消える（マスター側へ移動するのではない）。2026-07-21 に✅タスクDBの`法人`列で実際に踏んだ。

**How to apply:**
- 新規 Relation 列は **最初から DUAL で作る**。後から双方向化すると必ず復旧作業が発生する
- 値の入った列を DUAL 化する前に、必ず全行の値をエクスポート保全し、変換後に手で再投入する前提で計画する
- 複数列を変換するときは **1列だけ試して実測検証 → ダメなら残りに進まない**。このガードが実際に被害を1列に限定した
- 検証は必ず**双方向とも**行う。片側だけ見ると「値がマスター側に移っただけ」と誤認する

関連：`update_content` による日本語長文の部分置換は API 側で文字が化けて（ページ→パージ 等）一致せず失敗することがある。日本語ページへの追記は `insert_content` を使う。

落とし穴の正本は案Bの引き継ぎページ §7/§10。詳細な経緯は⑥ディスカッションログ「Notionデザインガイドライン（UI・情報設計）の策定」2026-07-21セッション。
[[project_notion_operating_rules]] [[reference_org_master_4db]]
