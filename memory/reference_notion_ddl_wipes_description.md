---
name: reference_notion_ddl_wipes_description
description: NotionのALTER COLUMN SETは選択肢を書き換えると同時に、その列の説明文を空にする
metadata:
  type: reference
---

**`notion-update-data-source` の `ALTER COLUMN "X" SET SELECT(...)` は、
その列の説明（description）を消す**（2026-08-25 実測）。

```
やったこと   📱発信アカウント台帳の「主体」列へ選択肢を4つ足すため
             ALTER COLUMN "主体" SET SELECT(既存4件 + 新規4件)
起きたこと   選択肢は正しく8件になった。★同時に説明文が "" になった
             消えた文 ── 「個人と法人は混ぜない。情報ファイアウォールの単位」
戻せるか     ★DDLに説明を書く構文が無い。Notionの画面から手で戻すしかない
```

- **選択肢を足すだけなら、既存の全オプションを書き戻す必要がある**（`SET` は置換であって
  追加ではない）。ここまでは想定どおり。**説明まで巻き込むのが想定外**。
- **触る前に説明文を控える。** `notion-fetch` の `data-source-state` に
  `"description"` として入っている。**消えてから探しても、そこにはもう無い**。
- `ADD COLUMN` は既存列に触らないので安全。危ないのは `ALTER COLUMN ... SET` だけ。
- 型としては [[reference_notion_relation_dual_landmine]] と同じ ──
  **列の設定を変える操作は、指定していない属性まで初期値に戻す**。
- 関連 → [[reference_notion_restore_path]]（Notionは戻せるが、控えを取っていた場合だけ）
