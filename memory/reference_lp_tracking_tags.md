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

## ★流入経路を分ける ─ 2026-08-28 実測で確定

有璽氏「来週あたりからInstagramのDMでもこのLPを使いたい。**どちらからクリックされたか
分けられるか**」。**分けられる。** 4つの計測すべてで分かれることを実物で確かめた。

```
配るURL
  フォーム営業（SalesBreaker）  https://gamemarke.vivid-global.com/
  Instagram DM                  https://gamemarke.vivid-global.com/ig?utm_source=instagram&utm_medium=dm&utm_campaign=gamebull
```

**実測の結果（`/ig?utm_source=instagram...` を1回開いた直後）**

```
SalesBreaker  pages[] に /ig?utm_source=... が別行で出た
              ★sources[] に "Instagram" が新しく現れた
              ＝ SBは utm_source を読んで参照元に分類している（仕様書に記載なし・実測で判明）
GA4           dl に UTM付きの完全URLを送信。cs/cm/cn が空なのは正常
              （GA4は dl のクエリをサーバー側で解釈する）。管理画面に出るのは数時間後
Clarity       関数あり・4回送信。★Page URL でのセグメント分けは未実測（管理画面が要る）
GTM           そのまま動く
```

## パスの分岐（Vercel rewrites）

`~/Documents/gamemarke_lp/vercel.json` に置いた。`/form` `/ig` `/dm` `/mail` の4本が
同じ index.html を返す（URLは書き換わらない）。存在しないパスは404のまま。

```json
"rewrites": [{ "source": "/(form|ig|dm|mail)", "destination": "/" }]
```

- **★`destination` を `/index.html` にすると 404 になる。** `cleanUrls: true` と干渉する。
  `"/"` を指定すること（2026-08-28 に実測で踏んだ）
- **なぜクエリだけに頼らないか** ── SBはメール内リンクを**自前のトラッキングドメインへ
  書き換えてリダイレクト**させる（docs/salesbreaker-agent-operating-manual.md）。
  そのときクエリが生き残るかは、実際に送信・クリックされるまで検証できない。
  **パスはリダイレクトで落ちない。** 保険として二重に持つ

## フォーム営業側のテンプレは触っていない

`/` に来たものはフォーム営業と読める（IG側が `/ig` を使うため）。**触らないことで
テンプレ更新のリスクを負わずに分離できる。** 経路が3つ以上に増えたら `/form` へ寄せる。
テンプレ更新の手順は `scratchpad/sb_fix_templates.py` の型（本文ごと save で上書き）。
★`templates/list` は 403（production_gate）で読めない。**save は通る**という非対称がある。

## 経路別の配布URL ─ 2026-08-28 に6本へ拡張（全パス実測済み）

**正本の一覧は `~/Documents/gamemarke_lp/配布URL一覧.md`**（有璽氏へ渡す用・コピーしやすい形）。
ここには**規則**だけ置く。規則が分かれば組み立てられるので、URLを二重に持たない。

```
規則   https://gamemarke.vivid-global.com/<パス>?utm_source=<source>&utm_medium=<medium>

  /            （なし）                      フォーム営業 ★SBテンプレ1609。触ると第2波が壊れる
  /ig          instagram / dm                Instagram DM
  /line        line      / message           LINE
  /dm          messenger / dm                Messenger
  /mail        email     / direct            メール個別送信
  /sign        email     / signature         メール署名（★パスだけでも識別できる）
```

- **識別はパスとUTMの二重。** どちらか片方が落ちても経路が分かる
- **新しい経路を足す** ── `vercel.json` の rewrites の `(form|ig|line|dm|mail|sign)` に
  1語足してデプロイするだけ。HTMLは触らない
- **★`.vercelignore` に `*.md` を入れた**（2026-08-28）。入れないと
  `https://gamemarke.vivid-global.com/配布URL一覧.md` で**社内向けの注記が外から読める**。
  `*.bak*.html` も同様に除外済み（308→404 を実測）
- 一覧に無いパスは404のまま（`/adminpanel` で実測）
