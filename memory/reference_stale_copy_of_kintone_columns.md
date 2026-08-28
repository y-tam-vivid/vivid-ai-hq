---
name: reference_stale_copy_of_kintone_columns
description: kintoneの列は写しの写ししか見ていない。Drive雛形62列もSkill61列もkintone本体より短い
metadata:
  type: reference
---

**kintone に API で繋がっていない（`reference_tool_access_map`＝CSV手動）。
だから列の話は必ず「写しの写し」を根拠にしており、腐り続ける構造になっている。**

```
kintone（正本）        BQ・BR に「代表者役職名称」「先方担当者役職名称」がある
                       ★2026-08-29 有璽氏が実物CSVで確認。こちらは未接続で見られない
   ↓ 人が書き出す
Drive の雛形           62列・BJ止まり。役職の列は無い     最終確認 2026-08-01
   [有璽]/[松本]顧客情報kintone反映csv.xlsx
   マイドライブ/Downloads書類アーカイブ/11_取引先・人物別/顧客情報kintone反映csv/
   ↓ 写す
Skill customer-db-sync 61列（追記シート相当）。同じく役職の列は無い
```

## 実測（2026-08-29）

- 雛形の「マスター（全顧客一覧）」= **62列（A=kintone反映 + 61列）・最終列 BJ**
- 「追記_YYYYMMDD（雛形）」= **61列・最終列 BI**
- **どちらにも役職・URL・ホームページの列は無い。** BQ・BR まで届いていない

## ★ここで一度間違えた

「Skill に役職の列が1つも無い」と報告したが、**同じファイルの39行目に
「余剰列(役職名称・コーポレートサイトURL…)はプロフィール/メモへ集約」と書いてあった。**
33行目の列リストだけを見て、3行下を読まずに断定した。
→ [[feedback_read_the_artifact_not_the_copy]]

## 矛盾（未修正・Skill編集は要承認）

- 24行目「**ホームページ**(url=公式サイト1本)」＝Notion に URL 列が在る
- 39行目「コーポレートサイトURL は**プロフィールへ集約**」＝在るのに畳めと書いてある
- 有璽氏「URLもプロフィールじゃないと思う。URLはURLの項目があるでしょ、どこも」＝正しい

## 次に触る人へ

1. **列の有無をこの写しだけで断定しない。** 「無い」と言う前に kintone 実物を見る
2. 見られないなら「**この写し（2026-08-01時点）には無い。kintone 実物は未確認**」と書く
3. 根本の解は **kintone を API で繋ぐこと**。繋がるまで写しは必ずズレ続ける（要判断）

関連: [[project_meishi_to_kintone_pipeline]] [[reference_kintone_customer_master]]
[[reference_no_gate_on_asking_the_human]] [[reference_kintone_lookup_is_a_copy]]
