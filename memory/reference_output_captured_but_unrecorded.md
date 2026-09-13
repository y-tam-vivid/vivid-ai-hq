---
name: reference_output_captured_but_unrecorded
description: 自動処理が正しくprintしていても標準出力を捨てていると台帳が残らない／git管理下を書き換える自動処理はcommitまでしないと他機へ届かない
metadata:
  type: reference
---

★C（lsu-editor・ブラウザ編集ツール）の適用処理 `~/.vivid-relay/editor_apply.py` は
「いつ・どのページの・何を直したか」を最初から正しく print していた。しかし crontab 側が
`> /dev/null` で標準出力を丸ごと捨てており、**中身は正しいのにどこにも残っていなかった**。

有璽氏の指摘（2026-09-13）：「保存したものは反映されるんだっけ？ログとしては残らない
みたいなこと言ってなかった？」で発覚。

**Why**: 「print しているから記録されている」は誤り。標準出力の行き先（cronのリダイレクト）
まで見ないと、実際に残るかは分からない。もう1つ、`editor_apply.py` は git 管理下の
`theme/lifestandup/` 配下を書き換えるのに、一度も `git commit` していなかった＝
**書いた内容は正しくファイルへ反映されるが、未コミットのまま積み上がり他機（MacBook）へ
届かない**（`bin/vivid-sync.sh` はコミット済みしか push しないため）。

**How to apply**:
- 自動処理を作る／レビューするとき、print/logの中身だけでなく**行き先**（`> /dev/null` に
  なっていないか）を必ず見る。
- git管理下のファイルを書き換える自動処理は、書くだけでなく **commit まで** をワンセットで
  実装する（push は既存の同期スクリプトに任せてよい。commitだけは自分でやる）。
- commitメッセージには「いつ・何を・前の値→後の値」を人が読める形で残す（機械が直したものを
  後から人が追えるように）。
- 修正は crontab 1行の変更（出力先を `.log` ファイルへ）＋ `editor_apply.py` への
  `git_commit_applied()` 新設（適用0件のときはcommitしない＝空コミット防止）。
  詳細 → `~/.vivid-relay/chopper_ledger_result.md`（2026-09-13）。

関連: [[project_lifestandup_website_wordpress]] [[reference_autocommit_pattern]]
