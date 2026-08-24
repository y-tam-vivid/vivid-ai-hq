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

## ★「0件」と言う検査が、そもそも見ていない経路がある（2026-08-24 実測）

自動処理の突合（`automation_inventory_check.py`）は 2026-08-23 に「登録漏れ 0件」と報告した。
**翌日、登録漏れが2件見つかった。**

```
この検査が見る範囲   crontab ／ bin/daily_jobs.conf に載っている実体
見ていなかった経路   ★launchd（常駐）      → slack_socket.py
                     ★手動実行のみのもの  → dashboard_build.py
＝ 同じ盲点で2件とも検知できなかった
```

**★「0件」は「異常が無い」ではなく「見た範囲に異常が無い」。**
実行の経路は4つある（cron／daily_jobs／launchd／GASトリガー）のに、検査は2つしか見ていなかった。

- **検査を作ったら、「何を見ていないか」を必ず出力に書かせる。**
  見た範囲を書かない検査は、0件が何を意味するか読む側に伝わらない
- **★経路を1つ増やしたら、検査の対象にも同じ経路を足すまでが1作業。**
  launchd を使い始めた時点で、この盲点は生まれていた
- → [[reference_monitor_must_exclude_parked]]（検査役2体が違う数字を出したら分類の基準が違う）

### 実行の経路は4つある（数えるときはこれで確認する）

```
cron              crontab -l
日次ジョブ        bin/daily_jobs.conf ＋ ~/.vivid-relay/daily_jobs_state/
launchd（常駐）   ~/Library/LaunchAgents/ ／ launchctl list
GASトリガー       Apps Script 側（外から読めない。心拍で代理判定）
★手動実行のみ    どこにも載らない。★人が思い出さないと動かない
```
