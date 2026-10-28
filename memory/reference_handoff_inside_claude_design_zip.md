---
name: reference_handoff_inside_claude_design_zip
description: 有璽氏が「〇〇に従って」と言うファイルは、Claude Design から落とした zip の中にあることがある。find/mdfind は zip の中を見ない。日本語名は unzip で失敗するので ditto で展開する
metadata:
  type: reference
---

**事実（2026-10-27）**：「HANDOFF_CLAUDE_CODE.md に従って GitHub に登録して」の引き継ぎ書は、
`~/Downloads/119番 Design System stage ①.zip` の中にあった（展開されていなかった）。
有璽氏の補足「このファイル名（zip）の中にあると思う」。

- `find` も `mdfind` も **zip の中は見ない**。見つからなければ、次に新しい zip を `unzip -l` で覗く
- **日本語名のファイルが入った zip は `unzip` で落ちる**（`Illegal byte sequence`）。`ditto -x -k <zip> <空の新しいフォルダ>` で展開する
- 展開先は scratchpad の空のフォルダ（ダウンロードした物は信用しない）

## Design System を GitHub＋スキルにした実例（2026-10-27 完了）

- 正本：https://github.com/y-tam-vivid/fukushi119-design（Private・main・初回 e0a5600a）
- ★gh は Homebrew 無しで入れた：公式 release の macOS_arm64 zip を checksums で照合 → `~/.local/bin/gh`（MacBookのみ。miniには無い）
  ログインは `gh auth login --web` を裏で起動 → 確認コードを有璽氏へ渡す（コードは自動でクリップボードに入る）
- ★`~/.claude/skills` の実体は vivid-ai-hq の中。別リポジトリを clone するときは vivid-ai-hq の `.gitignore` に
  `/.claude/skills/<名前>/` を足してから（足さないと15分同期が入れ子のリポジトリを抱え込む）。miniには clone していない
- 次の5本（kodomo-station／vivid／life-stand-up／meiku／fukuchi）も同じ手順。リポジトリ名は確定前に有璽氏へ確認
- ✅10/28 残り5本も登録済み（HANDOFF_CLAUDE_CODE_ALL.md）：fukuchi／vivid／life-stand-up／kodomo-station／meiku の各 -design。
  手順は1本ずつ同じ処理（.gitignore で除外＝ファイルは消さない→init→commit→gh repo create→タグ→clone→同期から外す→SHA 3か所照合）。
  ★zip ごとに形が違う：ビビッドは styles.css・tokens/・assets/logo が無く README.md 大文字・SKILL.md に設定欄が無い／
  LSU の SKILL.md の name は lifestandup-design／こどもSの uploads に文字化けした名前（zip 側で二重符号化）。どれも直さず報告
- ★まとめ方（10/27 有璽氏「今のプランの中でできるやり方」＝組織は作らない）：個人 y-tam-vivid のまま
  タグで束ねる。作ったら必ず `gh repo edit <repo> --add-topic design-system --add-topic brand-<ブランド>`。
  一覧の入口 https://github.com/y-tam-vivid?tab=repositories&q=topic%3Adesign-system
  ★`gh search repos --owner` は private を0件で返した。確かめるのは `gh api 'search/repositories?q=user:y-tam-vivid+topic:design-system'`

関連：[[project_handoff_bundle]]
