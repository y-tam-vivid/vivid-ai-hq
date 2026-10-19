---
name: reference_hand_built_timestamp_zero_pad
description: 手で組んだ日時文字列は時の桁をゼロ埋めする。4:28:50 は fromisoformat が受けない（2026-10-19 ads_grants_report.log で落ちた）
metadata:
  node_type: memory
  type: reference
---

**事実**：`ads_grants_report.log` に `ValueError: Invalid isoformat string: '2026-10-19 4:28:50'` が出た（2026-10-19 実測）。
時が1桁のまま（`4:28:50`）で書かれた文字列を `datetime.fromisoformat()` に渡すと落ちる。`2026-10-19 04:28:50` なら通る。

**確かめたこと**：書いている側のスクリプトは `~/.vivid-relay/` と `~/vivid-ai-hq/bin/` を `ads_grants_report` で検索して見つからなかった（10/19 時点）。
ログ行は1本だけで、落ちた後の続きは無い。

**How to apply:**
- 日時を文字に組むときは `strftime("%Y-%m-%d %H:%M:%S")`（ゼロ埋め）か `isoformat()` を使う。手の連結（f-string で `{h}:{m}`）をしない。
- 読むときに自分の書いた形式が読めるかは、同じ関数で往復（書く→読む）させて確かめる。
- ads_grants_report の書き手を探すこと自体は未完了。見つけたら上の書式へ直す（公開を伴う変更ではない）。

関連：[[project_notion_focus_sync]]（同じ日のログ警告の経緯）
