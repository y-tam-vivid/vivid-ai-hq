---
name: reference_hardcoded_option_lists
description: GASにベタ書きした選択肢リストは黙って腐る。マスタを改訂しても追随せず、エラーも出さずに値を捨てる。書き込み系5本が旧値を持ったまま残っている
metadata:
  node_type: memory
  type: reference
---

**選択肢をGASにベタ書きすると、マスタを改訂しても追随しない。しかもエラーにならない。**

2026-08-13、`import_kintone_orphans.gs` の `ROUTE_OK` が**2改訂ぶん遅れて**いた。

```
ベタ書き（10値）  フォーム営業 / テレアポ / 名刺 / 紹介 / 交流会 / イベント /
                  SNS / Web問い合わせ / セミナー / その他
実物のマスタ（16値）
                  紹介 / 友人知人 / 家族・親族 / 交流会 / コミュニティ / 出展・出店 /
                  地域・社会活動 / 自社セミナー / マッチングプラットフォーム /
                  代理店・パートナー / Web問い合わせ / SNS / 問い合わせ営業 /
                  テレアポ / 名刺 / その他
```

- `イベント` は2026-08-09に廃止（コミュニティ／出展・出店へ上書き済み）
- `セミナー` は `自社セミナー` へ改称
- 2026-08-10に足した8値が丸ごと欠落
- `フォーム営業` は2026-08-13に `問い合わせ営業` へ改称

**壊れ方が静か。** リストに無い値は「統制外」として弾かれ、流入経路が**空欄になって備考へ退避**される。例外は出ない。ログにも異常として出ない。次に見た人は「もともと空だった」と読む。

## まだ旧値を持っている7本（2026-08-13時点・未修正）

```
書く  apply_schema_v3.gs          ★実行禁止（旧10値でマスタを巻き戻す）
      update_channel_master.gs    ★選択肢マスタを書き換える側
      merge_channel_detail.gs     ★書き込み3箇所
      import_ledgers.gs
      fill_form_detail_and_verify.gs
読む  inspect_channel_mix.gs
      inspect_channels_and_dups.gs
```

**`update_channel_master.gs` と `merge_channel_detail.gs` は、今のマスタを巻き戻す力がある。**
`apply_schema_v3.gs` と同じ危険度として扱うこと。→ [[reference_dangerous_entrypoints]]

修正済みは `import_kintone_orphans.gs` の1本だけ（2026-08-13）。

## 直し方

**ベタ書きをやめて `90_選択肢マスタ` から読む。** マスタを直すだけで全部が追随し、この種のズレが構造的に消える。

読むときの注意 ── **見出し行を決め打ちしない。** `90_選択肢マスタ` の見出しは**2行目**で、流入経路は**E列**（2026-08-13実測）。1行目と決め打ちすると、選択肢の先頭に見出しの文字列「流入経路」が混ざる。同じ日にこれを実際にやりかけ、ドライランでは落ちず本実行で初めて壊れる作りになっていた（プローブで発見）。

関連: [[reference_dangerous_entrypoints]] [[project_sales_pipeline_workbook]]
[[reference_sales_workbook_column_moves]] [[feedback_sales_workbook_hands_off]]
