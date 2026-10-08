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
- ✅2026-09-25 完了：MacBook の `~/.claude/CLAUDE.md` にも 00_System 3本の @import を追加（有璽氏が手作業・申告）
- ★残：02_Current_Focus は 0バイト・10_Skills_Repository は空

**Why:** 規範の正本を2か所に置くと二重管理になる（fukuchi-core「どれが正本か先に決める」）。
**How to apply:** fukuchi-core 本文の改訂・@import の差し替えは「規範の変更」＝要承認。
移行が済むまでは、どちらの記述を正とするか都度確かめる。[[project_memory_layer_design]]

**★2026-09-25 リポジトリを保管庫へ入れる前に分かったこと（実測）**
- Core_Brain は Obsidian Sync が有効（`.obsidian/core-plugins.json` の sync=true）
  ＝保管庫の中へ入れた瞬間、vivid-ai-hq（122MB・memory 262本）がクラウドと他端末へ同期され始める
- MacBook には別の git クローンがある ＝ **git と Obsidian Sync が同じファイルを取り合う**。
  Obsidian Sync は `.git` を運ばないので、MacBook 側に「git でないコピー」がもう1つできる
- パスの依存：crontab 4行・~/.claude のリンク3本・launchd 1本・~/.vivid-relay 35本・リポジトリ内37本
- MOC の元の文面にも「GitHub管理下のソースコード（Sync対象外）」とあった
- ★決定（2026-09-25 有璽氏）：**実体は動かさない。Sync対象外にした 10_Skills_Repository へリンクで置く。**
  MOC は相対リンク化済み（../10_Skills_Repository/{vivid-ai-hq,agents,skills,output-styles}/）。
  `.claude` は Obsidian に見えないので agents/skills/output-styles は別リンクで出す。
  グローバル設定は `~/vivid-ai-hq` のまま（実体が動かないため書き換え不要）
- ✅2026-09-25 00:19 mini にリンク4本を作成。MOC の相対リンク11本が全部解決（ファイルの実在で確認）。check.sh ✅
  ★Sync除外の確認は有璽氏の申告のみ（設定はObsidian内部に保存され、ディスクから読めない）＝1経路
- ✅2026-09-25 完了：MacBook にもリンク4本を作成（有璽氏が手作業。`有璽_My_Brain/10_Skills_Repository/` に4本の実在を確認）
- 保管庫のフォルダ名は端末で異なる：mini＝`~/Documents/Core_Brain/`／MacBook＝`~/Documents/有璽_My_Brain/`（Obsidian Syncで同一内容）。MOC §0・§6 に併記済み
- notion-focus-sync は SKILL.md 登録済みだが、自動実行に載るまで MOC §7（設計中）に留め、§3 は14本のまま（2026-09-25 有璽氏決定）
- 🔴2026-09-27 発見・修正：MacBook の `~/.claude/CLAUDE.md` は `Documents/Core_Brain/…` を @import していたが、MacBook の実フォルダは `有璽_My_Brain`
  ＝**9/25〜9/27、MacBook では 00_System が1度も読み込まれていなかった**（@import は存在しないパスを黙って捨てる）。
  ★「追加した（申告）」は届いたことの証拠にならない。直し：`~/Documents/Core_Brain -> 有璽_My_Brain` のリンクを作成＝両機とも同じパスで届く


## MEMORY.md の索引から戻した記述（2026-10-08 棚卸し・索引には現在地だけを残した）

- 00_Systemを毎ターン@import／10_Skills_RepositoryはSync除外・リンク4本(両機済)／★MacBookは9/27まで@importが空振り→Core_Brainリンクで解消
