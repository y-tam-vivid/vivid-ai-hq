---
name: project_obsidian_core_brain
description: Obsidian保管庫 Core_Brain を「動的な正本」にする方針（2026-09-24 有璽氏）。vivid-ai-hq はコード・スキルの置き場へ
metadata:
  type: project
---

2026-09-24 有璽氏が方針を示した。

```
動的な正本     ~/Documents/Core_Brain/00_System/（MOC・Secretary_Core・Current_Focus）
               人の思考とリアルタイムに繋がる。Obsidian Sync でスマホ・MacBookと同期
リポジトリ     ~/vivid-ai-hq ＝ 完成したコード・スキル
将来           vivid-ai-hq を Core_Brain/10_Skills_Repository/ へ clone（または移動）して内包
入口           Core_Brain/CLAUDE.md（2026-09-24 作成）
```

**★いまの状態（2026-09-24 実測）**
- 00_System の3ファイルは名前が `.md.md`（二重拡張子）。CLAUDE.md が指す `.md` と一致しない
- 02_Current_Focus は 0バイト。10_Skills_Repository は空
- 毎ターン届く経路（~/.claude/CLAUDE.md の @import）は **まだ vivid-ai-hq 側しか指していない**
  ＝Core_Brain はそこで作業するセッションにしか届かない

**Why:** 規範の正本を2か所に置くと二重管理になる（fukuchi-core「どれが正本か先に決める」）。
**How to apply:** fukuchi-core 本文の改訂・@import の差し替えは「規範の変更」＝要承認。
移行が済むまでは、どちらの記述を正とするか都度確かめる。[[project_memory_layer_design]]
