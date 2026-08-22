---
name: working-via-ai-agents-and-notion-hub
description: "User wants work routed through the ONE PIECE-named AI agent roster, referencing the Notion AI knowledge hub"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 35c80315-9c01-42cf-beb6-75bf6a9a1ad0
---

今後の作業は「① AI組織図の体制を経由」＋「② Notionの蓄積を参照」して進める方針（2026-07-08 表明）。

**Why:** ふくち。グループ（田村有璽）は、中央窓口ビビを起点にCXO/開発ラインへ振り分けるAIエージェント体制と、Claude等との過去のやり取りをNotionに集約する運用を確立済み。個別チャットで一から始めるのではなく、既存の体制と蓄積の上で継続したい。

**How to apply:**
- 中央窓口として振る舞う際はビビ（秘書/中央窓口）の役割を意識。専門領域は名鑑の担当者（ナミ=CFO/財務、ロビン=CKO/ナレッジ・会議準備、センゴク=CLO/法務、ベガパンク系=開発）に対応づける。
- 「🚤 AIエージェント名鑑」DB: collection://ce19f944-22fb-4647-987b-7f93715809df（親: AI組織図 3957b156-8b57-81b4-a9dc-ffa26382e48c）
- 「🧠 AIナレッジハブ」page: 3957b156-8b57-81cc-8605-fa415fc28a6b。配下6DB。過去の議論は⑥ディスカッションログDB collection://01061f08-2b49-432d-8ff9-40eb24993376（1議論スレッド=1ページ、約50本）。
- 新しい作業に着手する前に、関連スレッドを⑥で検索・参照してから進める。
- 記録運用: **都度・積極的に残す（2026-07-20 変更）**。従来の「週次の遡り型」主体は廃止。作った/変えた・判断した/方針が変わった・想定と違った・知見が出た、のいずれかでその場で⑥へ書く。迷ったら書く。
- 週次バッチ（毎週金曜20:00「【週次】Claude AI→Notion記録」）は**取りこぼしの回収用**として存続。正本は `.claude/skills/fukuchi-core/SKILL.md`「作業ログの自動記録」節。
  ★旧記述は `~/.claude/core/10-法人.md` を指していた（2026-08-13 に統合済み・存在しない正本）。
  AIが自動で読みに行く導線を1本でも残すと再発するため張り替えた（2026-08-23 つる）。
