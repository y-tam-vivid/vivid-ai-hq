---
name: project_notion_focus_sync
description: Obsidian 02_Current_Focus ⇄ Notion ✅ビビッドタスク管理DB の同期スキル。2026-09-25 設計中・未実装
metadata:
  type: project
---

2026-09-25 有璽氏「個人の思考やAIへの指示はObsidian、公式な進捗・マニュアルはNotion」。
二重管理の手間をなくすバケツリレーとして同期を作る。

- 仕様案の正本 → `.claude/skills/notion-focus-sync/SKILL.md`（MOC の Skill_Notion_Sync）
- ★鍵は既存の `NOTION_TOKEN`（~/.vivid-relay/config.env）で足りる。データソース 62c7fadf に 200 を実測
- ★同期先DBは未確定（全社DB＋オーナー区分=有璽氏個人 を推奨。候補に 個人DB_Task もある）
- ★スクリプト未作成・cron 未登録。手動→つる/ドーベルマン検査→cron の順

**Why:** 手で2か所に書くと片方が腐る（二重管理）。
**How to apply:** Obsidian は文言が正・Notion は Status/期日が正。消す同期はしない。[[project_obsidian_core_brain]]

**★2026-09-25 決定と実測**
- 決定（有璽氏）：同期先＝✅ビビッドタスク管理DB（全社）／対象＝オーナー区分=有璽氏個人 ＆ 🔥次のアクション（または未完了）
- 読むだけスクリプト `fetch_notion_tasks.py` をピタゴラスが保存（sha256 715f89e0…）
- ★実測：対象は **0件**。DB全体が **3件のみ**（最終編集 8/18）で、**3件ともオーナー区分が空**
  2経路一致：スクリプト実行 ／ フィルタなし全件取得（ビビが別に叩いた）
- ★全社DBは実質使われていない。議事録から抜いたタスクは 個人DB_Task 側に溜まっている → 同期先の再確認が要る
