---
name: notion-focus-sync
description: Obsidian の 02_Current_Focus.md に書いた「- [ ] タスク」と、Notion ✅ビビッドタスク管理DB（全社）を同期する。★設計中（2026-09-25）・スクリプト未実装。「フォーカスをNotionへ」「Current_Focusを同期」「Notionのタスクを取り込んで」等で読む。
---

# notion-focus-sync（旧称 Skill_Notion_Sync）── ★設計中・未実装

> 状態：2026-09-25 仕様案のみ。**スクリプトは未作成・自動実行は未登録。**
> MOC の `[[Skill_Notion_Sync]]` の実体はこのファイル。

## 役割の分担（バケツリレー）

```
Obsidian 02_Current_Focus.md        Notion ✅ビビッドタスク管理DB（全社）
  有璽氏の思考・AIへの指示     ⇄      公式な進捗・担当・期日
  ★正：タスクの文言・並び             ★正：Status・Due Date・担当・関連
```

## 接続先（2026-09-25 実測）

| 項目 | 値 |
|---|---|
| 鍵 | `~/.vivid-relay/config.env` の `NOTION_TOKEN`（既存・★新しい鍵は要らない） |
| データソースID | `62c7fadf-3fb1-409d-bc90-238fdce29b0f`（★DBのIDとは別物。API は `/v1/data_sources/{id}`） |
| API版 | `Notion-Version: 2025-09-03` |
| 使う列 | `Name`(title)／`Status`(select)／`オーナー区分`=`有璽氏個人`／`Due Date`／`備考` |
| Status の選択肢 | 📥 未着手／🔥 次のアクション／🚀 進行中／⏸ 待機中／✅ 完了／🗄 アーカイブ |

## 同期の決まり（仕様案）

1. **1行＝1レコード。行末の目印で結ぶ。**
   `- [ ] 見積を送る <!-- n:1a2b3c4d -->`（HTMLコメント＝Obsidianの表示では見えない）
   目印が無い行＝新規 → Notion に作り、目印を書き戻す
2. **完了はどちらからでも完了。** `[x]` ⇄ `✅ 完了`。戻す（未完了化）は Obsidian の操作だけを採る
3. **文言は Obsidian が正**。Notion で名前を変えても Obsidian は上書きしない
4. **Notion 側で増えたタスク**（オーナー区分=有璽氏個人・Status=🔥 次のアクション）は
   ファイル末尾の `## Notionから` 見出しの下へ足す
5. **消さない。** Obsidian で行を消しても Notion は消さない（`備考` に「Focusから外れた」と書くだけ）
6. **書き戻しは目印と `[x]` だけ。** 文章は1文字も変えない。書く直前にファイルの更新時刻を見て、
   読んだ後に人が触っていたらその回は書かない（Obsidian Sync との衝突を避ける）
7. 既定は**読むだけ（dry-run）**。`--run` のときだけ書く。毎回の差分をログへ残す

## 実行（予定）

- 置き場：`~/.vivid-relay/notion_focus_sync.py`（mini）
- まず手動で数回 → つる（データ）・ドーベルマン（自動処理）の検査 → mini の cron（15分ごと）
- ⚙️自動処理レジスタへ行を作り、成功でも失敗でも心拍を打つ
