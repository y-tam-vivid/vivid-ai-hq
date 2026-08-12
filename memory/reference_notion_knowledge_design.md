---
name: reference_notion_knowledge_design
description: Notion「ナレッジホーム設計」ページ=社内ナレッジ一元化・Drive/命名・議事録自動化の協議ハブ
metadata: 
  node_type: memory
  type: reference
  originSessionId: 96262bc3-3622-4f19-ac63-b79921ce8d3f
---

社内ナレッジ整理・一元化の**協議用マスタードキュメント**（叩き台、随時追記）。田村さんとの設計議論はここに集約する。

- **ページ**: 🗂️【設計】社内ナレッジ整理・一元化／ナレッジホーム設計 → https://app.notion.com/p/3927b1568b5781e19b57d7da9bd0617c （親=「ビビッド業務管理」ハブ https://app.notion.com/p/35e7b1568b5781c391dbcc87f0ee6b1f ）
- **既存の全社分類体系**（ここに整合させること）: Company/法人＝10ビビッド・20ILIFE(株式会社ILIFE)・30SWELL(現 リアンライフ株式会社／旧SWELLSOCIETY。select実値は`30SWELL`のまま)・グループ横断／Department＝5桁コード(10経営企画・11事業開発・12マーケ・13営業・14管理・15施設運営…)／Project＝FUKU-CHI・Senet・HERITAGE 等。法人はタグ扱い、部門コードが構造の背骨。
- **セクション構成**: 1背景 / 2進め方4フェーズ / 3現状マップ / 4 Notion正本アーキテクチャ / 5 議事録システム(4DB:個人議事録・全社議事録・タスク・担当者マスター) / 6 AIエージェント体制(ロビン=CKO/ジンベエ=CSO案) / 7-8 未決・次アクション / **9 Google Drive住み分け・命名(事業×法人モデル)** ←2026-07-05に本セッションで追記。
- **Drive設計の要点(§9)**: 事業を源の主軸・法人はショートカットのビュー／3層住み分け(A共有ドライブ=正/B会社マイドライブ=作業机/C個人アカウント)／命名 `NN_`『部門』`【タグ】``[V]``[Y]``_wip_`。ビジュアル版設計書Artifact: https://claude.ai/code/artifact/6b2f5641-c444-41c5-8356-c522463f8486
- **Drive §9の未決**: 会社/個人の線引き(iLife=法人か事業か)・17分類アーカイブの役割・独立共有ドライブにする事業・進め方。関連: [[project_downloads_archive_system]]
