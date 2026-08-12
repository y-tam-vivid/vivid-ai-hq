---
name: project_local_memo_cleanup
description: "ローカルのテキストエディットメモ約1,004件の棚卸し・分類プロジェクト。ナレッジ一元化フェーズ1の一部"
metadata: 
  node_type: memory
  type: project
  originSessionId: a5c258b1-21a4-4d70-8a4d-916760150ede
---

Mac「テキストエディット」で書き溜めた **.rtf/.txt メモ 約1,004件**（~/Desktop・~/Documents に散在、2007〜2026年）を棚卸し・分類したプロジェクト。ファイルは未移動（読み取りのみ）。[[reference_notion_knowledge_hub]] のフェーズ1棚卸しに抜けていた「ローカルメモ層」を埋める位置づけ。

**状態（2026-07-07時点：下ごしらえ完了）**
- 中身から自動分類し **20カテゴリ** に整理（「その他」141→35へ細分化）。一覧表Artifact（全件・非公開）https://claude.ai/code/artifact/93140771-4010-403a-bb2c-7d9f4a996445 ／ 共有安全版（ID/PW・個人除外）https://claude.ai/code/artifact/b72d521b-2374-4e41-9a9d-c55e93afd30b
- ロビン(CKO)がトリアージ完了 → **正本候補448／要判断293／アーカイブ263**。行き先: 03議事録DB 226件（🔒個人どまり12〈機微3〉/🌐全社256）・ナレッジDB 175・02部門47・09Archive263（完全重複103含む）。決定表CSV=`~/Desktop/メモ下ごしらえ_決定表_20260707.csv`（Company/Division/確信度列つき, 1004行）。
- Notion: 棚卸しページ https://app.notion.com/p/3947b1568b578119b299fddf01e0e338 ＋ 設計ページ [[reference_notion_knowledge_design]] 末尾に「議事録DB設計への入力」連携セクションを追記済み。

**確定した組織マッピング**: いきいき(旧)=20ILIFE(LSU)前身／中古アパレル・古着EC=現行(30=現リアンライフ株式会社/旧SWELLSOCIETY・OWオレンジワークス藤井寺)／ViViD韓国ジュエリー・ねこやなぎ新品EC=終了(アーカイブ)。**未確定❓**: タチバナ4・アイドル2の現行性、Zoom低確信24件の帰属、ViViD/CROSSMALL4件。

**方針**: 「メモのまま/全部移す」の二択でなく **インデックス(この一覧)＋正本(Notion)＋アーカイブ(Drive・原本残す)** の3層。最終軸は〈事業部=Company/Division〉×〈種類=20カテゴリ〉。個人・機密は全社DBに入れずID/PWはパスワード管理へ。

**次アクション**: 別タブの議事録DB/ナレッジDB設計と合流（下ごしらえCSVが投入データ）。DBはそちらで一度だけ構築。残❓の確定後にCompany付与。

**作業データ**: scratchpad に memos.json / triage_decisions.csv / triage.py / classify・build_htmlスクリプト（セッション限り）。手法=find+textutilで全文抽出→キーワード＋本文精読で分類。
