---
name: reference_salesbreaker_campaign_setup
description: SalesBreakerで外へ送る前に、着地先(LP)へ必ず入れる3点 ── 計測タグ・経路の分離・非公開。案件を問わず全件で守る
metadata:
  type: reference
---

# SalesBreaker で送る前に、着地先へ必ず入れる3点

**2026-08-28 有璽氏の指示。ゲームブル案件に限らない。今後 SalesBreaker を経由する
すべての案件で、送信の前にこれを済ませる。**

```
① 計測タグ4本を入れる      SalesBreaker 1行タグ ／ Clarity ／ GA4 ／ GTM
② 経路をパスとUTMで分ける   フォーム営業 ／ IG DM ／ LINE ／ メール ／ 署名 …
③ 社内向けファイルを塞ぐ    .vercelignore に *.md と *.bak*
                            ↓
                     ★どれも「送ってから」では取り返せない
```

## なぜ ── 送ってしまうと永久に取り返せないから

**第1波 13,709件が実例。** 2026-08-24〜27 に送信し、18社がLPをクリックした。
だがタグを入れたのは **8/27**。**その18社がLPで何を読み、どこで離脱したかは永久に分からない。**
会社名しか残っていない。

```
SalesBreaker が返すもの     どの会社が来たか・何回クリックしたか  ★会社名が出るのはSBだけ
SalesBreaker が返さないもの  その会社がLPのどこまで読んだか
                            どこで離脱したか／何を押したか
                            ＝ 反応が悪いとき「文面が悪い」のか
                              「LPのどこが悪い」のかを切り分けられない
```

経路の分離も同じ。**後から分けられない。** 送信済みの分は経路不明のまま固定される。

## ① 計測タグ4本

`<head>` に置く。役割が重なっていないので4本とも要る。

| | 何が分かるか | 無いと困ること |
|---|---|---|
| **SalesBreaker 1行タグ** | ★どの会社が来たか（社名） | 誰が反応したか分からない |
| **Microsoft Clarity** | ★どこで離脱したか（録画・ヒートマップ） | LPのどこを直せばよいか分からない |
| **GA4** | 流入元・滞在時間 | 経路別の比較ができない |
| GTM | 上記の受け皿 | （GA4がここに入っていることが多い） |

- **Clarity は無料。プロジェクトを作ってタグIDを取るだけ**（数分）。ゲームブルは `y999sy395z`
- **★GTMを既存の会社サイトと共有してよい。** 誤発火は起きないことを実測で確認済み
  （→ [[reference_lp_tracking_tags]] に確かめ方の3手）

## ② 経路の分離

```
規則   https://<ドメイン>/<パス>?utm_source=<source>&utm_medium=<medium>

  /            （なし）                 SalesBreakerのフォーム営業
  /ig          instagram / dm           Instagram DM
  /line        line      / message      LINE
  /dm          messenger / dm           Messenger
  /mail        email     / direct       メール個別送信
  /sign        email     / signature    メール署名
```

- **★パスとUTMの二重で持つ。** SalesBreakerはメール内リンクを**自前のトラッキング
  ドメインへ書き換えてリダイレクト**させるので（docs/salesbreaker-agent-operating-manual.md）、
  クエリが生き残る保証がない。**パスはリダイレクトで落ちない**
- **★SalesBreaker は utm_source を読んで参照元に分類する**（仕様書に記載なし・実測で判明）。
  SBのダッシュボードだけで経路別の数が見える
- Vercel なら `vercel.json` の rewrites 1行で足りる。**HTMLは触らない**

```json
"rewrites": [{ "source": "/(form|ig|line|dm|mail|sign)", "destination": "/" }]
```

**★`destination` を `/index.html` にすると404。** `cleanUrls: true` と干渉する。`"/"` にする。

## ③ 社内向けファイルを塞ぐ

公開ディレクトリに置いた `.md` や `.bak` は**そのままURLで読める**。2026-08-28、
配布URL一覧（「触ると第2波が壊れる」等の社内注記入り）が実際に外から読めていた。

```
.vercelignore   *.md
                *.bak*.html
```

**塞いだら実測する。** `curl -s -o /dev/null -w '%{http_code}' <URL>` が 404 になること。
`.html` は 308 でリダイレクトされるので、**リダイレクト先まで追って404を確かめる**。

## 送信前の確認（コピーして使う）

```bash
# 1. タグ4本が動いているか（ブラウザで開いてJSを叩く。管理画面のログインは不要）
#    typeof window.clarity === 'function'
#    Object.keys(window.google_tag_manager).filter(k=>k.startsWith('GTM'))
#    performance.getEntriesByType('resource').filter(u=>/collect|sb-trk|clarity/.test(u.name))

# 2. 経路のパスが全部通るか
for p in "" /form /ig /line /dm /mail /sign; do
  echo "$p $(curl -s -o /dev/null -w '%{http_code}' "https://<ドメイン>$p")"
done

# 3. 社内向けファイルが塞がっているか（404であること）
curl -sIL "https://<ドメイン>/配布URL一覧.md" | grep -i '^HTTP'
```

## 関連

[[reference_lp_tracking_tags]]（ゲームブルLPの実装と、タグの発火を確かめる3手）
[[project_gamebull_form_sales]]（第1波・第2波の実績）
[[reference_salesbreaker_engagement_api]]（API側の作法）
[[feedback_stop_asking_just_do_it]]（懸念は自分で潰してから渡す）
