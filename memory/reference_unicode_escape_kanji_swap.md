---
name: reference_unicode_escape_kanji_swap
description: 日本語を\uエスケープで書くと別の実在する漢字に静かにすり替わる。エラーが出ないので気づけない。書いたあと必ず読み返して突合する
metadata:
  node_type: memory
  type: reference
---

**日本語を `\u` エスケープで書かない。literal のまま書く。**

2026-08-13、Notion ③決定・論点ログへ3件登録した際、`\u` エスケープで書いた日本語が
**別の実在する漢字にすり替わっていた。**

```
書いたつもり      実際に入った        原因
有璽（U+74BD）  → 有璞（U+749E）     エスケープの取り違え
曜（U+66DC）    → ٣（U+0663）        アラビア数字に化けた
溜（U+6E9C）    → 溢（U+6EA2）        別字だが意味が通ってしまう
㉓（U+3252）    → ⑓（U+2453）        丸数字の別ブロック
```

**壊れ方が静か。**
- 例外は出ない。書き込みは成功する
- **化けた先が実在する文字なので、見た目が自然**。「溢れすぎる」は日本語として読める
- 人名が特に危険。`有璽` → `有璞` は一見して気づけない

## How to apply

- **日本語は literal で書く。** ツール引数でも同じ。エスケープに変換しない
- 固有名詞（人名・社名・シート名・DB名）を含む書き込みは、**書いたあと必ず fetch して読み返す**
- 突合するのは「意味が通るか」ではなく **1文字ずつ一致するか**。意味は通ってしまう
- 同じ理由で、**大容量ファイルを逐語再生成してDriveへ上げ直すのも危険**
  （→ [[project_meishi_to_kintone_pipeline]] の「法人番号/電話番号が破損する」）

**関連する既知の型** ── kintone CSV の cp932 化け、手転記の漢字化け。
いずれも「書けてしまうが中身が違う」。**作成後の突合検証を省かない。**
→ [[project_kintone_csv_to_notion_mirror]]

関連: [[project_kintone_csv_to_notion_mirror]] [[project_meishi_to_kintone_pipeline]]
[[feedback_naming_yuji]] [[reference_notion_mcp_read_limits]]
