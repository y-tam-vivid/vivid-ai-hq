---
name: reference_kintone_subtable_rows
description: kintoneエクスポートCSVは行番号≠レコード番号。サブテーブル継続行を数えないと行参照が全部ズレる
metadata: 
  node_type: memory
  type: reference
  originSessionId: 72d12c17-4bf6-4c52-9291-4421d31f8dab
  modified: 2026-08-12T02:40:30.181Z
---

kintoneのエクスポートCSVは**1レコードが複数行にまたがる**。A列 `レコードの開始行` が `*` の行だけがレコードの先頭で、それ以外は前レコードの継続行。

**「A列が`*`の行だけ抽出した配列のindex」をそのままシート行番号として使うと、継続行のぶんだけ下方向にズレる。** 顧客管理アプリの実例では83行/77レコード、継続行が41〜44行と60行の5行あり、41番目以降の参照が最大5行ズレた。GASで `getRange(row, col)` する時にこれをやると、**別のレコードの値を読んでいるのにエラーにならない**。

正しい変換は、抽出時に実シート行を記録しておくこと。

```javascript
const map=[]; rows.forEach((r,i)=>{ if(i>0 && r[0]==='*') map.push(i+1) });  // 実シート行(1始まり)
const actualRow = map[recordIndex];
```

サブテーブル継続行では、テキスト列に同じ値がタブ区切りで繰り返し連結されて見えることがある（例: 法人番号が `4120101064498\t\t\t4120101064498...`）。桁数チェックだけだと無効判定になるので、数字だけ抜いて先頭13桁を見る。

**件数を数えるときも同じ罠がある**（2026-08-12に実際に踏んだ）。継続行にも `レコード番号` は入っているので、`レコード番号が非空` で絞っても継続行が混ざる。継続行は多くの列が空なので、**「値が空の件数」だけが静かに水増しされる**。顧客管理の実例では 387行 / 382レコード（継続行5行）で、流入経路の空欄が167→172に見えた。他の区分は一致するのに空欄だけずれたら、まずこれを疑う。

```javascript
// 数えるときは必ず開始行で絞る
const recs = rows.slice(1).filter(r => r[iStart].trim() === '*');
```

関連: [[reference_kintone_customer_master]] [[project_kintone_csv_to_notion_mirror]] [[reference_gviz_large_sheet_access]]
