---
name: reference_workspace_agentic_oauth
description: Google Workspace の「agentic」OAuth クライアント設定（2026-11-11 期限）は、いまの仕組み（REST API だけ）には影響しない。対象に名指しされた2プロジェクトと判断
metadata:
  type: reference
---

2026-10-13 4:13 着信「[Action Required] Mark AI agent OAuth clients as agentic for Google Workspace MCP by Nov 11, 2026」（workspace-noreply@google.com）。

- 中身：Google が Workspace の MCP サーバー（Gmail・Drive・カレンダー等をAIエージェントから使う公式の口）を出す。★そこを呼べるのは「agentic」に印を付けた OAuth クライアントだけ。印は 10/12〜11/11 に付けられ、★11/12 以降は既存クライアントでは変えられない（新しいクライアントを作れば選べる）。
- ★Gmail API・Sheets API など REST API だけを使うアプリは「対応不要」とメール本文に明記。
- 名指しされたプロジェクト：`vivid-sheets`（番号 472246617753＝シート読み書き・Search Console・GBP API の申請先）と `orange-seo-agent`（★2026-10-13 時点で MacBook と mini のファイルを grep して記録なし＝claude.ai 側で作った可能性。中身は未確認）。
- **判断（ビビの推奨）**：既存の2つには印を付けない。こちらのスクリプトは REST API だけ＝影響なし。agentic には「エージェント用の別の制御」がかかると書かれており、印を付けると今動いている処理に効く恐れがある。Workspace の MCP を使いたくなったら、そのとき★新しい agentic クライアントを別に作る（メールも「混ぜずに分けろ」と推奨）。
- ✅**2026-10-13 有璽氏決定「印を付けないでOK」**＝vivid-sheets・orange-seo-agent とも agentic にしない。★11/11 を過ぎても対応不要。MCP を使うときは新しいクライアントを作る。→ [[feedback_seo_standard_kit]]
