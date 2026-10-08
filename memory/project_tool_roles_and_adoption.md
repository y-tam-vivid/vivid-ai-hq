---
name: project_tool_roles_and_adoption
description: ツールの使い分け（Obsidian=机の上／Notion=本棚／git=完成品）と社内の導入状況（2026-09-23 有璽氏）
metadata:
  type: project
---

**社内の導入状況（2026-09-23 有璽氏・外部AIとの対話で共有）**
- Notion：有璽氏が個人で使い、一部メンバーにアカウント付与。★全社の情報ハブ（マニュアル・議事録・タスク）は構想のみで未運用
- Claude：多くのメンバーが使用。★経営する施設側は未導入
- Google Workspace・Slack：使用中だが一部未導入者あり
- 方針：まず有璽氏個人で型を作り、有意義なら全社へ広げる

**使い分け（確定分）**
```
Obsidian 00_System   机の上＝有璽氏とAIの動的な作業場。Obsidian Sync（スマホ・両Mac）
Notion               本棚＝確定したマニュアル・議事録・共有タスク（人が見る場所）
vivid-ai-hq（git）   完成したコード・規範・スキル（保管庫へはリンクで見せる・Sync対象外）
Drive                一般ファイル
```
- タスクは1件1か所。Obsidian→Notion は `notion_focus_sync.py`（mini）→ [[project_notion_focus_sync]]
- ★外部AI（Chrome上の対話）の提案のうち「保管庫へ git clone」「Notion Syncプラグイン」は採らなかった
  （前者は git と Sync の取り合い、後者は1件1か所・双方向完了の要件を満たせない）→ [[project_obsidian_core_brain]]

**Why:** ツールが増えるほど「どれが正本か」が曖昧になり管理が崩れる（有璽氏の課題感）。
**How to apply:** 新しい情報の置き場を決めるときは上の4行のどれかに必ず当てる。施設側へ広げる話は Claude 未導入を前提にする。

**★日々のメモの現状（2026-09-27 有璽氏）**：MacBookのメモ帳・Chatwork・iPhone標準メモの3か所に分散。
Obsidianへ寄せるかを検討中（提案＝書き留める場所は Obsidian の 01_Inbox 1か所、振り分けはAI。パスワード類は入れない）
- ✅2026-09-27 デイリーノートの受け皿を作成（MacBook）：`.obsidian/daily-notes.json`＝保存先 01_Inbox・名前 YYYY-MM-DD・型 `90_Templates/デイリーノート`（見出し：メモ／やること／決まったこと／人への連絡）。`templates.json`＝90_Templates。MOC §1 に1行。控え `~/.vivid-relay/_backups/obsidian_config_20260927/`
  ★設定ファイルは Obsidian 起動中に外から書いた＝反映は再起動後。スマホへ設定が届くかは Sync の「設定を同期」次第（ディスクから読めない・未確認）
  ★01_Inbox の「やること」は Notion へ自動では行かない（同期対象は Current_Focus だけ）。AIの振り分けで移す


## MEMORY.md の索引から戻した記述（2026-10-08 棚卸し・索引には現在地だけを残した）

- Obsidian=机・Notion=本棚・git=完成品。★施設側はClaude未導入・Notionは有璽氏個人＋一部／日々のメモは3か所に分散(Macメモ帳・Chatwork・iPhoneメモ)→Obsidian 01_Inbox のデイリーノートへ集約開始(9/27・振り分けは未)
