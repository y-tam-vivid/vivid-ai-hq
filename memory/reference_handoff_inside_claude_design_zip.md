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

関連：[[project_handoff_bundle]]
