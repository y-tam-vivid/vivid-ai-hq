---
name: reference_reference_audit_false_negative
description: 参照を洗う検査そのものが偽陰性を出す。関数だけ見て定数経由を落とし、13本を1本と誤った。検査ロジックを先に検証する
metadata:
  type: reference
---

**「検査した」と「正しく検査できた」は別。** 検査そのものが偽陰性を出しうる。

2026-08-18 実地。シート名の改名前に「どこが参照しているか」をランタイムから洗った。

```
v1  グローバルの**関数だけ**を集めて .toString() を検索
      → 08_関係フォロー … 1本
v2  ★シート名を**値に持つ定数**も集め、その定数名を使う関数を探す
      → 08_関係フォロー … 13本（直接1 ／ 定数経由12）
```

実際の参照はこう書かれている。

```javascript
var RF_IO = '08_関係フォロー';        ← トップレベルの定数（関数ではない）
ss.getSheetByName(RF_IO)             ← 関数の中には RF_IO としか書かれていない
```

v1は `typeof v === 'function'` のものだけを集めていたので**定数を1つも見ていなかった**。
毎朝動いている取り込みすら「参照なし」に見えた。**v1のまま改名していたら12本が静かに壊れた。**

## 型

- **列挙する対象を絞った時点で、絞った外は「無い」ことになる。** 関数だけ／ローカルだけ／
  1つのエンドポイントだけ。→ [[reference_salesbreaker_engagement_api]] と同じ型
- **コメントに書いた根拠のない断定が、検査を信じさせる。**
  v1のコメントに「定数も関数の外なら文字列として出る」と書いた。誤り。確かめていなかった
- **照合ロジック（正規表現・部分一致の除外）は、使う前に数ケースで検証する。**
  v2では6ケース（括弧の中／部分一致を弾く／先頭／末尾／前に文字がある）を先に通した

## 実装のかたち

```javascript
var GLOBAL_XX = this;          // ★トップレベルで捕まえる。関数の中からは取れない

Object.keys(GLOBAL_XX).forEach(function (k) {
  var v = GLOBAL_XX[k];
  if (typeof v === 'function') { fns.push({name:k, src:String(v)}); }
  else if (typeof v === 'string') { strs.push({name:k, val:v}); }   // ★これを落とさない
});
```

定数名の照合は単語境界で（部分一致を弾く）。

```javascript
new RegExp('(^|[^A-Za-z0-9_$])' + name + '([^A-Za-z0-9_$]|$)')
```

## シート改名で本当に危ないのはGASだけ

```
数式内の 'シート名'!A1     改名に自動追随する。安全
入力規則の参照範囲          同上。安全
★GASの文字列               追随しない。静かに外れる
```

**見えるのはそのプロジェクトだけ。** 別プロジェクトが参照していても出ない。
「出ないから安全」とは言えない → 本番前にコピーで1回通す。

関連 [[reference_apps_script_name_collision]] [[reference_sheets_number_format_order]]
[[feedback_read_the_artifact_not_the_copy]]
