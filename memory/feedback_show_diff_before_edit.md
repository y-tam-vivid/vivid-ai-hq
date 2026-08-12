---
name: feedback-show-diff-before-edit
description: "Before creating or editing any file, present the planned change as a diff/preview and list every file that will be touched in the same operation. Wait for approval before writing."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 592209ce-4f2a-490a-940d-506c96fe4a57
---

ファイルを作成・編集する前に、まず変更内容を差分（diff）形式や具体的な対比表で提示し、同時に修正される他のファイルも一覧化してユーザーの承認を待つ。承認後に実際の書き込みを行う。

**Why:** ユーザーが Write/Edit ツール呼び出しをキャンセルし「具体的にどの行のどの部分を、何から何に書き換えようとしていますか。先に変更内容のdiff（差分）を見せてください。また、同時に修正すべき他のファイルがあれば一覧で示してください。」と明示的に要求した。レビュー前の改変を嫌うため、サプライズ書き込みは禁忌。

**How to apply:**
- 新規ファイル作成: ファイル全文（または共通部＋差分プレースホルダ表）を提示してから Write
- 既存ファイル編集: before/after の対比を提示してから Edit
- 複数ファイルにまたがる場合は「変更対象ファイル一覧」テーブルを必ず先出し（パス／操作／種別の3列）
- 既存ファイルを編集しない場合は「他ファイルへの影響なし」を明記
- 承認の言葉（「進めて」「OK」等）を確認してから書き込み実行
- 軽微な差分（typo修正など）でも省略しない
