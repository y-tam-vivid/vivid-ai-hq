---
name: reference_lp_tracking_tags
description: LPに入れる計測タグの構成と、ログインせずに「本当に発火しているか」を実測する3手
metadata:
  type: reference
---

# LPの計測タグ ─ 何を入れ、どう確かめるか

対象は `gamemarke.vivid-global.com`（ゲーム型販促のLP・実体は `~/Documents/gamemarke_lp/index.html`）。
**★実体を `~/Downloads` に置かない。**一度フォルダごと消えて公開版から復元した。

## 入っている4つ（2026-08-28 実測で発火を確認）

```
Sales Breaker   sb-track.js  id=17e298ff-5e02-4630-a16d-0f4f25ede23a
                ★これだけが「どの会社が来たか」を会社名で返す。他の3つは匿名
Google Tag Mgr  GTM-PQX3L4TQ    ★会社サイトと同じコンテナを共有している
Google 4        G-4D1C77WR0P    ★GTMコンテナに元から入っていた。個別に足していない
MS Clarity      y999sy395z      録画・ヒートマップ・怒りクリック
```

**役割が重なっていない。** SBが「誰が」、Clarityが「どこで離脱したか」、GA4が「どこから来たか」。
突き合わせて初めて「A社が料金の手前で離脱した」が言える。

## ★ログインせずに発火を確定させる3手

管理画面へ入る必要はない。ブラウザで開いて JS を叩けば全部分かる。

```
① 実際の通信を数える
   performance.getEntriesByType('resource').map(r => r.name)
   → /collect ・ c.gif ・ track/view が出ていれば「送っている」証拠
   ★スクリプトが読み込まれただけでは発火の証拠にならない。送信を見る

② コンテナ定義を丸ごと読む
   curl -s "https://www.googletagmanager.com/gtm.js?id=GTM-XXXXXXX"
   → 正規表現で測定IDを数える  G-  AW-(広告CV)  DC-(フロドラ)  UA-
   → タグ種別は "__gaawe"(GA4イベント) "__googtag" "__cl"(クリックリスナー) 等の識別子
   ★AW- が0本なら「コンバージョンの水増し」は起こりようがない（器が無い）

③ クリックで動くタグを、遷移させずに測る
   document.addEventListener('click', e => e.preventDefault(), true)  ← 先に遷移を殺す
   a.click()
   → dataLayer に gtm.click が入るのに新規通信が0なら、
     「リスナーは動くが紐づいたタグが無い」＝ 発火しない
```

## GTMコンテナを会社サイトと共有していることについて

**2026-08-28 時点では実害ゼロ**（上の3手で確定）。除外ルールは**入れていない**。

- 発火するタグが無い状態で除外ルールだけ足すと、**管理する対象が1つ増えるだけ**
  （fukuchi-core「新しい仕組みの採否は二重管理が増えないかで決める」）
- **★会社サイト側にコンバージョンタグを足すとき、その場でLPを例外に入れる。**
  そのとき初めて必要になる。それまでは不要

## 関連

[[project_gamebull_form_sales]] [[feedback_stop_asking_just_do_it]]
[[reference_vercel_free_plan_protection]]（LPの公開先とBasic認証の型）
