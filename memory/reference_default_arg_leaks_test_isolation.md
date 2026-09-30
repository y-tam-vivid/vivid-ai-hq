---
name: reference_default_arg_leaks_test_isolation
description: Pythonのデフォルト引数はモジュール読み込み時に値が固定される。テストでグローバル変数を差し替えても効かず、本物の置き場を汚す（2026-09-29 notion_focus_sync で実害）
metadata:
  type: reference
---

**`def f(dir=BACKUP_DIR)` の `BACKUP_DIR` は、import した瞬間の値で固定される。**
テストで `mod.BACKUP_DIR = tmp` と差し替えても、`f()` は元の本物のパスへ書く。

```
悪い  def build_backup(backup_dir=BACKUP_DIR): ...     ← 読み込み時に本物のパスで固定
良い  def build_backup(backup_dir=None):
          backup_dir = backup_dir or BACKUP_DIR         ← 呼んだ時に見る
```

**実害（2026-09-29 ピタゴラス）**：`~/.vivid-relay/notion_focus_sync.py` の隔離テストのはずが、
本物の `~/.vivid-relay/_backups/focus/` に7件書き込んだ。エラーは出ない＝**テストは合格する**。
（全件テスト由来と確認のうえ削除済み。Current_Focus・state・Notionへは届いていない）

- **★「隔離した」は、差し替えた変数の数ではなく、本物の置き場が前後で不変かで確かめる。**
  テスト前後で本物のディレクトリの件数・ハッシュを取って比べる
- 同じ型：`HOME` 差し替えで守るもの（→ [[reference_bash_subshell_exit_pitfall]] の隔離テスト注記）と違い、
  **Python内の定数は `HOME` を変えても import 済みの値は戻らない**
- 経緯 → [[project_notion_focus_sync]]
