---
name: reference_tool_results_cache_keeps_secrets
description: MCPで読んだファイルの中身が ~/.claude/projects/<session>/tool-results/ に平文で残る。機微を読んだら作業の最後に消す。サブエージェントは権限で消せない
metadata:
  node_type: memory
  type: reference
---

**MCPツールで読んだファイルの中身は、`~/.claude/projects/<session-id>/tool-results/` に平文で残る。**
自分で作った一時ファイルを消しても、**こちらは残る。**2026-09-04 実測（予実の作業中）。

```
実例   Google Drive の口座明細CSVを読んだ結果
       mcp-claude_ai_Google_Drive-download_file_content-<epoch>.txt
       ★口座番号・取引先名・金額が平文。10ファイル・計3.4MB が残っていた
```

## 何が問題か

- **★読んだ本人は「Driveの原本しか触っていない」と思っている。**キャッシュの存在が見えない。
- **★scratchpad を掃除しても残る。**掃除の対象から構造的に外れている
  → [[reference_backups_in_volatile_places]]（置き場を見落とす型）。
- 機微を読む作業（口座・給与・契約・個人情報）では、**作業のたびに溜まる。**

## How to apply

```
機微を読む作業の最後に
  ls ~/.claude/projects/<session-id>/tool-results/
  rm -f  …/tool-results/mcp-*     ★原本が残っている前提で消す（再取得できる）
2経路目
  find ~/.claude/projects -name "mcp-*" | wc -l   ★他セッションのぶんも見える
```

- **★サブエージェントは消せないことがある。**2026-09-04、ナミが `rm` を試して権限で拒否された
  （「don't ask mode」）。**親（ビビ）が実行したら通った。**
  → **サブエージェントに掃除まで任せない。最後に親が確認して消す。**
- **★他セッションのキャッシュには触らない。**同じ日の実測で、別セッション3つに計31件あった。
  中身が予実の機微とは限らず、**ファイル名からは判別できない。**報告に留めて人の判断を仰ぐ。
- 原本（Drive）は消さない。**消すのはキャッシュだけ。**必要なら読み直せる。

関連 [[feedback_confidential_two_layer_rule]]（機微は本人限定の場所にだけ置く）
／[[project_cfo_agent]]（この型を踏んだ実例）
