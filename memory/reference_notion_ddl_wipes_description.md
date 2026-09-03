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

## ★列の説明は、APIからは書けない（2026-09-03 実測で確定）

上の「DDLに説明を書く構文が無い」を、**2経路で確かめて確定させた。**

```
経路1  ADD COLUMN "..." RICH_TEXT DESCRIPTION '...'
       → validation_error「Expected ADD, DROP, RENAME, or ALTER keyword, got "DESCRIPTION"」
       ＝ 型の後ろに説明を書く構文が存在しない
経路2  ADD COLUMN "..." RICH_TEXT（説明なしで作成）→ 作成後のスキーマを実測
       → その列の description は "" のまま。後から入れる構文も無い   → 一致
```

**★「消えたら手で戻すしかない」だけでなく、「そもそも一度も書けない」。**
説明を入れるのは**必ず人の手（Notionの画面）**。AIは押す場所まで特定して渡す。
```
① 台帳を開く → ② 列の見出しをクリック → ③「プロパティを編集」→ ④「説明」欄に貼る
```

### ★試し方が正しかった（型として残す）

**本番の列で試さなかった。**
```
やったこと   使い捨てのテスト列（_tmp説明テスト）を作り、そこで2経路を試して DROP した
             ★DROP後にスキーマを実測し、テスト列が消え他の列が無傷なことを確認
やらなかったこと  本番の「公開レベル」列へ ALTER COLUMN ... SET を撃つこと
理由         ★SETは置換なので、既存の選択肢を書き戻し損ねると12行の値を壊す。
             **説明を1行足すために、台帳の実データを賭ける取引にはしない**
```
**★「できるか試す」と「本番で試す」は違う。** 壊れても困らない対象を1つ作ってから試す。
→ [[feedback_verify_before_declining]]（できないと言う前に試す）の**安全な実行の仕方**。
