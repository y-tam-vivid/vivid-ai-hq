---
name: feedback_generated_files_attach_notion
description: 生成・発行したファイル(MD/Skill/HTML/資料等)はNotionの該当ページに実ファイルを添付する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1d73b6d9-e954-4b58-94e8-3640388031c9
---

生成・発行したファイル（MD／Skill／HTML／資料 等）は、該当するNotionページに**実ファイルを添付（DL可）**して残す。一時領域(scratchpad等)に置いたままにしない。2026-07-16ユーザー指示・全AI標準。

**Why**: 抽出/生成物が一時領域にあるだけでは、ユーザー・他スタッフ・引き継ぎから参照できない。Notion=共有正本に着地させて初めて資産になる。

**How to apply**:
- テキスト(MD/docx等) → 全文(または本文)を子ページ化＋**原本ファイルを`<file src="file-upload://...">`で添付**(DL可)。Notionの`notion-create-attachment`は`content`インライン(≤200KiB)でMD/HTML/CSV等を直接アップロード可。
- 動くHTML/ツール → `<embed src="file-upload://...">`でNotion内にライブ描画(クリック不要でその場に見える)＋必要ならArtifactも併記。今後この見せ方を標準にする(ユーザー承認済の好例)。
- Skill/その他ファイルが発生したものも同様に添付する。
関連: [[project_claude_ai_logs_to_notion_migration]] [[project_design_agent]]
