---
name: reference_md_to_docx
description: md を日本語の .docx へ変換する道具。bin/md2docx.py。pandoc・LibreOffice はこの環境に無い
metadata:
  type: reference
---

# Markdown → Word（.docx）── bin/md2docx.py

```
python3 ~/vivid-ai-hq/bin/md2docx.py <入力.md> [出力.docx]
```

**★この環境には pandoc も LibreOffice も入っていない**（2026-08-26 実測。`which` で3つとも不在）。
Word へ渡す成果物が出たとき、**変換の手段が無いことに気づくのは渡す直前**なので、ここに書いておく。

## 何が入っているか

| | |
|---|---|
| 部品 | `python-docx 1.2.0` ＋ `lxml 6.1.2`（`pip install --user`） |
| 入っている機 | **MacBook・Mac mini の両方**（2026-08-26 に同時に入れた。実測） |
| スクリプト | `bin/md2docx.py`。git 管理下なので両機へ自動で届く |

## 扱える記法（契約書に出るものだけ。汎用コンバータではない）

`# ## ###` 見出し／`| a | b |` 表（Table Grid・1行目をヘッダ）／`- ` 箇条書き／
`1. ` 番号付き／`**強調**`（行の途中でも効く）／`---` 区切り。
フォントは游明朝（欧文は MS Mincho にフォールバック）、本文10.5pt。

## ★変換したら必ず検算する

生成した .docx を **python-docx で読み返して数える**。実例（2026-08-26 の契約書）：

```
段落253 ／ 表2 ／ 条見出し24本（第1条〜第24条）
★ 0件 ／ ** 0件 ／ | 0件   ＝ 記法の残骸と社内の印が漏れていない
```

- **★「Wordで開けた」は検算ではない。** 開けても中身が欠けていることがある。
- **★条番号の自動採番と手書き番号が二重になっていないかは、機械では見ていない。**
  ここだけは Word で目視すること。
- 社外へ出す文書なら、**社内語の混入も同時に数える**（→ [[feedback_confidential_two_layer_rule]]）。

関連 → [[project_facility_inspection_contract]]（この道具を作った案件）
