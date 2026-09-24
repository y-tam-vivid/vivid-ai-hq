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

**★いまの状態（2026-09-24 夜・切替済み）**
- 00_System の `.md.md` 二重拡張子は `.md` へ直した（有璽氏承認）
- mini の `~/.claude/CLAUDE.md` 先頭で 00_System 3本を @import ＝毎ターン届く。vivid-ai-hq の3本は当面併読
  控え `~/.vivid-relay/_backups/claude_global_CLAUDE.md.bak_20260924`
- fukuchi-core 冒頭に「正本の置き場」節を追加（控え `_backups/fukuchi-core_SKILL.md.bak_20260924`）
- MEMORY.md を 25,009B→約2.8KB へ。旧本体110行は `INDEX_全体.md`、全文は `_archive/MEMORY_full_20260924.md`
- ★残：MacBook の `~/.claude/CLAUDE.md` は機械ローカル＝未切替（git で配れない）
- ★残：02_Current_Focus は 0バイト・10_Skills_Repository は空

**Why:** 規範の正本を2か所に置くと二重管理になる（fukuchi-core「どれが正本か先に決める」）。
**How to apply:** fukuchi-core 本文の改訂・@import の差し替えは「規範の変更」＝要承認。
移行が済むまでは、どちらの記述を正とするか都度確かめる。[[project_memory_layer_design]]
