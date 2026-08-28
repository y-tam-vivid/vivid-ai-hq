---
name: reference_what_actually_reaches_the_next_turn
description: 次の回に確実に届くのは CLAUDE.md と MEMORY.md 先頭だけ。Skillのdescriptionは圧縮で消える。フックは25種あり我々は3つしか使っていない
metadata:
  type: reference
---

**2026-08-29、公式ドキュメントを実際に検索して確認した**（推測ではない）。
出典 ── code.claude.com/docs の memory / hooks / hooks-guide / context-window。
有璽氏「ちゃんと自分のAIの構造特性を分析、検索含めて行い、抜け漏れない回答を出せ」。

## 何が確実に届き、何が消えるか

```
毎ターン確実に届く（圧縮を越える）
  ~/.claude/CLAUDE.md（絶対パス @import）      上限 4MiB ／ @import は最大4段
  MEMORY.md の先頭                              ★200行 または 25KB（先に来た方）
  システムプロンプト・環境情報
  圧縮後に再注入される：読んだ CLAUDE.md ／ invoke した Skill 本体（最大5,000トークン/本）

★圧縮で消える
  会話の本文（要約に置き換わる。手順は残り「なぜ」が落ちる）
  Skill の description 一覧          ← 起動時には入るが、圧縮後は戻らない
  読んだファイルの中身
  分野索引の先の topic file 本文     ← 引かれなければ消える

自分から取りに行かないと来ない
  memory の各ファイル ／ Notion ／ Drive ／ path-scoped rules
```

**★MEMORY.md の上限は「24.4KB」だけではなく「200行 または 25KB」だった。**
2026-08-29 実測で MEMORY.md は 72行・12.5KB ＝ **行数にはまだ余裕がある**
（[[feedback_memory_index_hygiene]] は byte だけを見ていた。行の制約も併記すること）。

## フックは25種ある。我々は3つしか使っていない

```
使っている     PreToolUse（地雷の注入） ／ Stop（書き戻し・未検索の差し戻し）
               UserPromptSubmit（記録の督促）

★使っていない（2026-08-29 時点）
  PostCompact      圧縮直後に走り、matcher: "compact" で stdout を文脈へ再注入できる
                   ＝ 圧縮で落ちた「役割」を戻せる可能性がある唯一の口
  SubagentStop     担当の所見が返った瞬間に検査を挟める
  PostToolUseFailure / StopFailure / PermissionDenied
  SessionEnd / InstructionsLoaded / ConfigChange / FileChanged / TaskCompleted ほか
```

## ★フックで捕まえられない経路（これは仕様。回避できない）

```
モデルがツールを呼ばずテキストだけ出して終わる
   → PreToolUse は発火しない。事前に止める手段は無い
   → ★Stop フックで transcript_path を読んで**事後に**差し戻すのが唯一の手段
      （[[reference_no_gate_on_asking_the_human]] の実装はこれ。設計として正しいが「事後」）
```

**事前ゲートが作れない領域があると理解したうえで運用する。**
「次からは気をつける」で埋めようとしない。事後検知＋差し戻しで回す。

## 未確認（分かっていないと明記する）

- `PostCompact` の入出力スキーマ。公式に実装例が無い → **使う前に実測が要る**
- `transcript_path` の JSON スキーマ（実測で確かめるしかない）
- `skillListingMaxDescChars` の既定値
- 圧縮の要約ロジックそのもの

関連: [[reference_heartbeat_proves_life_not_results]] [[reference_no_gate_on_asking_the_human]]
[[project_memory_layer_design]] [[feedback_memory_index_hygiene]] [[feedback_use_the_team_not_alone]]
