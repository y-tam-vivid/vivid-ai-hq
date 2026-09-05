# 申告が失われても、変更内容はリビジョンから読み取れる

2026-09-05、ピタゴラスがテレアポリストの指摘①〜⑤を直したが、**作業は実際に行われたのに
報告文がログに残らなかった**（`~/.vivid-relay/saleslist_fix2.log` は警告5行のみ・プロセスは終了済み）。
＝**「何をどう変えたか」の申告が存在しない状態で検査を求められた。**

**申告が無いことは、検査ができないことを意味しない。** 実物どうしを突き合わせればよい。

## Googleスプレッドシートの場合（実測で通った手順）

```
① 検査した版を固定する    drive.files().get(fields='version,modifiedTime')
② 前の版を .xlsx で落とす  ★revisions().get_media() は Google ネイティブ形式では 404 になる
                          正しい入口は revisions().get(fields='*') の exportLinks
                          https://docs.google.com/spreadsheets/export?id=<ID>&revision=<REV>&exportFormat=xlsx
                          へ Authorization: Bearer <token> を付けて GET する
③ openpyxl で読む         ★数値セルが float になる。"662998888.0" は先頭0落ちの検出を素通りする。
                          比較の前に末尾 ".0" を落として正規化する
④ 1セルずつ突合する        差分を「型」で分類する（先頭0の復元／番号の訂正／その他）。
                          ★「その他 0件」まで言えて初めて「意図した変更だけ」と断定できる
⑤ 行の増減はキーで説明する  行数の差だけ見ない。消えた行のキーを1件ずつ数え、
                          1件ずつ理由を付ける。★説明のつかない減りが0件かを言う
```

## なぜ型にするか

- **申告を読んで検査すると、申告に書かれていないことを見ない。** 今回は申告が無かったので
  全セルを突き合わせるしかなく、結果として**申告があるときより網羅的になった**
  （事業所単位が「触られていない」ではなく「188セルだけ意図どおり触られた」と分かった）。
- **リビジョンは作った側の言い分ではない。** 機械が残した事実なので、申告と食い違えばこちらが正。
- **申告が失われたら差し戻す、は誤り。** 実物が残っているなら読む。→ [[feedback_verify_before_declining]]

関連 [[feedback_one_route_is_not_verification]] ／ [[reference_row_reference_rots_on_rebuild]] ／
[[reference_freeze_the_version_under_review]] ／ [[project_telapo_list_other_services]]
