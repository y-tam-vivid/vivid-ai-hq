---
name: reference_vercel_free_plan_protection
description: Vercel無料プランでは固定URLを保護できない。塞ぐならMiddlewareのBasic認証（無料枠で動く）
metadata:
  type: reference
---

**Vercel の無料プラン（Hobby）では、`<project>.vercel.app` の固定URLを塞げない。**
2026-08-25 実測＋有璽氏の確認。

```
vercel project protection enable --sso
  → deploymentType は "prod_deployment_urls_and_all_previews" にしかならない
  → deployment固有URL（…-5n22jywnn-…）と preview は SSO で塞がる（302を実測）
  → ★固定URL <project>.vercel.app は塞がらない（素のGETで HTTP 200 を実測）

ダッシュボードで "All Deployments" にすれば塞がる
  → ★有璽氏の確認: **その設定は有料プランのみ**（Hobby では選べない）
```

## ★前回の実物がそのまま残っている（2026-09-05 実測）

```
~/.vivid-relay/kadoban_site/
  index.html ／ ★middleware.js ／ vercel.json
＝ ★Basic認証の実装を書き直さなくてよい。コピーして合言葉だけ差し替える
```
**★次に「社内向けに仮公開したい」が来たら、ここを見る。**ゼロから書かない。

```
道具の状況（同日 実測）
  vercel CLI  ★入っていない
  npm 10.8.2  ★ある（nvm経由 /Users/yujimac/.nvm/versions/node/v20.20.2）
              ＝ sudo 不要で `npm i -g vercel` が通る見込み
              ★brew は無く sudo も無い（この環境の制約）→ npm 経由が唯一の道
```

**Why:** Vercel の Deployment Protection は「本番の固定URLまで守る」部分が有料機能。
CLI にも deploymentType を `all` にする口が無い。**プランの壁で、設定では解けない。**

**How to apply:**

```
塞ぎたいのが「社内向けの画面」なら ── ★Middleware の Basic認証を使う（無料枠で動く）
  middleware.js をプロジェクト直下に置くだけ。ビルド設定は要らない
  合言葉は Vercel の環境変数（暗号化保存）。★ソースにも memory にも書かない
  ブラウザが標準のログインダイアログを出すので、スマホでも見られる
```

- **★「保護がかかっているつもり」を作らない。**設定画面の表示ではなく、
  **素の `curl` で HTTP 401 が返ることを実測してから**中身を載せる。
- 公開してよい内容なら Basic認証は要らない。**判断の分かれ目は中身**
  （稼働盤は人名・Slackチャンネル名・会社数・仕組みの穴・DBのIDを含む＝社内限定）。
- 他の道と、選ばなかった理由
  | 案 | なぜ採らなかったか |
  |---|---|
  | 推測されにくいURLにする | 塞いだことにならない。漏れたら終わり |
  | Cloudflare Access | 無料枠はあるが独自ドメインが要る。DNSはさくらで当方に権限が無い → [[reference_vivid_dns_sakura]] |
  | GitHub Pages | private リポジトリの Pages は有料 |
  | 有料プランへ上げる | お金＝要承認。まず無料で解けるかを先に試す |

## 🔴 配ったURLは黙って死ぬ（2026-09-05 有璽氏「デモサイト見れなくなってるよ」）

**LIFE STAND UP の仮公開 `lifestandup-preview.vercel.app` が見えなくなった。実測は下のとおり。**

```
経路1  素のGET          404 NOT_FOUND（x-vercel-error: NOT_FOUND）
経路2  合言葉つきGET     ★同じく 404 ＝ 合言葉やBasic認証の問題ではない
対照   稼働盤 fukuchi-kadoban.vercel.app  → ★401（生きている・認証が効いている）
```

- **★401と404を混ぜない。** 401＝配備は在って認証で弾いている（正常）。
  404＝**そのホスト名に配備が無い**（消えた／別名になった／本番に昇格していない）。
  「見えない」の一言で保護の不具合と読むと、直す場所を間違える。

### ⛔訂正（2026-09-05 ピタゴラス実測）── 404は1種類ではない。**2種類あって意味が逆**

上の「404＝そのホスト名に配備が無い」は**足りない**。Vercel は `x-vercel-error` で
2つを区別しており、**どちらかで直す場所が変わる。**

```
実測（3ホストの対照・同時刻）
  lifestandup-preview.vercel.app       404 ★NOT_FOUND             ← 今回のこれ
  zzz-nonexistent-test-9x8y7z…         404 ★DEPLOYMENT_NOT_FOUND  ← ホスト名が無い側
  fukuchi-kadoban.vercel.app           401（対照・生きている）

  ★NOT_FOUND ≠ DEPLOYMENT_NOT_FOUND
    DEPLOYMENT_NOT_FOUND … そのホスト名に配備そのものが無い
    NOT_FOUND            … ★ホスト名も配備も解決している。そのパスに中身が無い
```

- **★今回はホスト名が死んだのではない。**`/` `/index.html` `/stand-up/` `/news/`
  `/_next/` の5経路すべて 404 NOT_FOUND。**中身が1枚も乗っていない側の壊れ方**（＝推測：
  書き出し物を上げていない／出力ルート違い。どちらかまではこの実測では確定できない）。
- **★Basic認証は1度も走っていない。**401 も `WWW-Authenticate` も返らない。
  **合言葉を配り直しても直らない**（ここまでは実測）。
  ★「middleware まで到達していない」は**この応答ヘッダー1経路からの推測**。
  2経路目（Vercel の配備一覧・ビルドログ）は**ロビン・ピタゴラス・つるの3体とも権限を拒否され、
  誰も見ていない。** → [[feedback_one_route_is_not_verification]]
- **⛔「URLの記録が0件」も誤り。**grep したのが `vivid-ai-hq` 側だけだった。
  実物は **`~/lifestandup-wp` の commit `24a60ca` の本文**に
  「デプロイ先: https://lifestandup-preview.vercel.app (Basic認証・非公開)」と在る。
  → **リポジトリが2つある案件で「0件」と言うときは、両方を数える。**
    [[feedback_one_route_is_not_verification]]
- **★静的書き出し `static-preview/` は .gitignore で履歴に入れていない**（同 commit で明記）。
  ＝ **生成物は MacBook のディスク上にしか無い。**mini からは作り直せない
  （元が `_tools/wordpress` のローカルWordPress＝これも `_tools/` ごと git 管理外）。
  **配った器の再発行が、1台のマシンが起きていることに依存している。**
  → [[reference_offload_long_work_to_mini]]
- **⛔この行は誤り（上の「記録が0件も誤り」で訂正済み・消さずに残す）。**
  数えた2経路が**どちらも `vivid-ai-hq` 側だけ**で、経路が2本あっても**同じ場所を2回数えていた**。
  ★2経路とは「別の道」であって「別のコマンド」ではない。
  ~~**★URLがどこにも記録されていなかった。** 2経路で0件 ── ①作業ツリーの全文grep
  ②git全履歴の `-S` 検索。**Slackのメッセージと、そのセッションの記憶にしか無かった。**~~
  **★ここから下は今も正しい** ── WORKING.md は「着手」のままで、完成もURLも書かれていない。
  ＝ **セッションが終わった時点で、社内の誰も再発行先を辿れない状態だった。**
- **★仮公開は「配って終わり」にできない。**これは写真32枠の○×確認を兼ねる器で、
  スタッフが見るまでが仕事。**落ちていれば確認が止まる**（そして止まったことは黙っている）。

**How to apply（次に仮公開を出す人へ）**

```
出した直後に   ① URLと保護の実測結果（401）を memory と WORKING.md の両方へ書く
               ② ★合言葉は書かない（環境変数のまま）。書くのは「どこに在るか」
生きているか   ③ ⚙️自動処理レジスタへ1行足し、素のGETが 401 を返すかを定期で見る
               ★心拍と同じ理屈 ── 在庫（プロジェクトが在る）でなく応答で見る
                 → [[reference_heartbeat_proves_life_not_results]]
```

関連: [[project_ops_dashboard_artifact]] [[reference_plaintext_credentials_handling]]
[[feedback_verify_before_declining]]（できないと言う前に、別の道を数える）

## 🔴 「デプロイした」と「そのURLで見えている」は別（2026-09-05 実地・有璽氏が発見）

有璽氏「**そもそもデモサイトを見れない状態なのですが**確認してもらって」。

```
実測   https://lifestandup-preview.vercel.app/    ★404 NOT_FOUND
       個別のデプロイURL                          302（Vercelのログイン画面へ飛ぶ）
原因   `vercel deploy --prod` は新しいデプロイを作るが、
       ★固定URL（別名/alias）を必ずそこへ付け替えるとは限らない。
       別名が古いデプロイを指したまま残り、そのデプロイが消えて404になった
直し   deploy で出たURLを拾い、★`vercel alias set <URL> <固定URL>` を明示的に実行する
```

- **★私は「200が返った」ことを1時間前に確認していた。それでも見られなくなった。**
  ＝**公開は一度確かめて終わりではない。別名は後から外れる。**
- **★デプロイの出力に固定URLは出ない。** 出るのは個別のデプロイURL。
  **出力を見て「出せた」と判断すると、誰も見られない状態に気づけない。**
- **★確かめるのは必ず「人に渡したURL」で。** 個別のデプロイURLで確認しても意味がない
  （そちらはVercelのログイン保護が掛かっていて、そもそも挙動が違う）。
- ★出し直したら毎回この3つを人に渡すURLで測る ── ①合言葉なし=401 ②合言葉あり=200
  ③主要ページが200。→ [[feedback_one_route_is_not_verification]]

[[project_lifestandup_website_wordpress]] [[reference_delivered_but_unread]]

## ⛔この節は上の「デプロイしたと見えているは別」と同じ話（2026-09-05 リリス／mini）

**★別のセッションが先に同じことを書いていた**（133行目の節）。
mini 側で作業していて気づかず、下に同じ話を足してしまった。
**判断の正は上の節（133行目）。** ここは消さずに残すが、
**この先ここを読む必要は無い。上を読むこと。**
→ [[reference_two_sessions_built_the_same_thing]] ／ [[reference_stale_premise_daily]]
（同じ事実を2箇所に置くと、訂正が片方にしか届かない）

**★上の節に無いことだけ、下に残す。**

```
やったこと         npx vercel deploy --prod --yes --scope <team>
起きたこと         配備そのものは成功し、固有URL（…-xxxx.vercel.app）では見える
                   ★固定URL lifestandup-preview.vercel.app は 404 NOT_FOUND のまま
直し方（★必須）   npx vercel alias set <deployの出力URL> <固定ホスト名> --scope <team>
```

- **★`--prod` は「本番として配備する」であって「固定URLを付け替える」を必ずしも含まない。**
  名前が示す挙動と実際の挙動が違う入口 → [[reference_dangerous_entrypoints]]

### 🔴 上の節に無いこと ── 大きい静的サイトは、上がりきる前に沈黙する（mini 実測）

**2026-09-05、写真を139枚入れた（54MB・234ファイル）ら、デプロイが2回とも
`UNKNOWN` のまま20分・9分と進まず終わった。**

```
症状      vercel ls の Status が ★UNKNOWN のまま。Ready にならない
          個別のデプロイURLを叩くと 302 が返るので★「生きている」と読みたくなる
          → ★誤り。302 は入口の応答で、中身が上がりきったかとは別
          alias set を打つと Error: The deployment ... is not ready. で弾かれる
直し方    ★vercel deploy に --archive=tgz を付ける。
          234個のファイルを1つにまとめて送るので、ファイル数由来の遅さが消える
```

- **★`302` で「デプロイは生きている」と断定しない。** 判定に使えるのは
  `vercel ls` の `Ready` か、`alias set` が通ること。**1経路で読むと必ず外す**
  → [[feedback_one_route_is_not_verification]]
- **★写真を増やすほど、出し直しが重くなる。**仮公開は「確認のたびに出し直す」器なので、
  重さは毎回効く。次に写真を足す人はこの点を見込むこと。

### ★静的書き出しは作り直す前に空にする（同日 実測で踏んだ）

`~/lifestandup-wp/crawl_static.py` は**既に在るファイルを飛ばす**（アセットが
`if out_path.exists(): continue`）。写真やCSSを差し替えても**古いものが残って出る**。
**`static-preview/` を一度消してから作り直すこと。**

### 🔴 真因はもう1つあった ── **GitHubへの push で自動デプロイが走り、固定URLを奪う**

**2026-09-05 mini 実測。9/5の404の説明がつく、いちばん確からしい筋。**

```
実測   git push した★7秒後に、打っていないデプロイが Production として現れる
       その別名に <project>-git-main-… が付く ＝ Vercel が GitHub の main を見ている
中身   ★リポジトリのルート。書き出し物（static-preview/）は .gitignore で入っていない
結果   CLIで上げて alias を張っても、★次の push で固定URLが「空のデプロイ」へ移る
       → 素のGETが 404 NOT_FOUND（ホスト名は生きているが中身が無い側の壊れ方）
```

- **★これは「保護の不具合」でも「合言葉の問題」でもない。**別のデプロイに付け替わっていた。
- **止め方**：リポジトリのルートへ `vercel.json` を置き `"git":{"deploymentEnabled":false}`。
  CLIからの `vercel deploy` は今までどおり通る。
- **★「書き出し物を履歴に入れない」設計と、「pushで自動デプロイ」の既定がぶつかっている。**
  片方だけ見ていると原因に辿り着けない。**リポジトリを持つ案件で仮公開を作るときは、
  最初に自動デプロイの有無を確かめる。**

### ⛔ここは誤診だった（同日・自分で切り分けて訂正）── `UNKNOWN` は「ビルド中」の表示

~~失敗したデプロイが居座ると、以降が全部止まる~~ ── **そうではなかった。**

```
誤診   「新しいデプロイが3つとも UNKNOWN ＝ 順番待ちが詰まっている」と読んだ
       → 古いデプロイを3つ消した。★それでも動かなかった＝仮説が外れた
切り分け  ★同じプロジェクトへ index.html 1枚だけを上げてみた
       → 数秒で "readyState": "READY" が返る＝★プロジェクトは正常
実際   `vercel ls` の Status=UNKNOWN は「まだ READY になっていない」の表示。
       ★大きい配備は数分から十数分そのまま。詰まりでも異常でもない
```

- **★「動かない」を見たら、まず同じ場所へ★極小のものを1つ通す。**
  通れば「対象が重いだけ」、通らなければ「場所が壊れている」。
  この対照を先に置かないと、詰まり説のような**外れた仮説のまま操作してしまう**
  （実際、消す必要のなかったデプロイを3つ消した）。
  → [[feedback_one_route_is_not_verification]]
- **★CLI は完了時に JSON で `readyState` を返す。** ログが `Building…` で
  止まって見えるうちは、まだ終わっていないだけ。**待てばよい。**
- 消すときは `npx vercel remove <deployment-url> --yes --scope <team>`。
  ★**いま固定URLが指しているものは絶対に消さない**（そこだけは今も正しい）。

### ★写真は原寸で置かない（同日 実測）

既存サイトは Jetpack が `?resize=1024,768` で縮めたものを配信している。
本家の原寸を落とすと **139枚で48MB**（うち111枚が1024px超）。
`sips --resampleWidth 1024` で **31MB** になり、**見え方も既存サイトに近づく**。
**仮公開は確認のたびに出し直す器なので、重さは毎回効く。入口で削る。**

### 🔴 ファイル数が増えると出せなくなる ── `--archive=tgz` で通る（2026-09-05 実測）

ブログ5本＋写真139枚を足したら、**出し直しが4回連続で止まった。**

```
状態     `vercel ls` が ★UNKNOWN のまま（Ready にならない・ビルドの記録も取れない）
規模     37MB / 251ファイル（それまでは 3.6MB / 少数 → 7秒で Ready）
切り分け ★mini からも MacBook からも同じ ＝ 機械の問題ではない
直し     `vercel deploy --prod --yes --archive=tgz` → ★11秒で Ready
```

- **★1ファイルずつ上げる既定の形が、ファイル数で詰まる。** まとめて1つにして上げれば通る。
  **写真を含む静的サイトを出すときは、最初から `--archive=tgz` を付ける。**
- **★止まったデプロイはエラーを返さない。** 「失敗した」ではなく「終わらない」。
  ログも取れないので、待っても原因は分からない。**規模が変わったら形を変える。**
- ★出し直したら**必ず** `vercel alias set <出たURL> <固定URL>` を実行する
  （この節の上に書いたとおり、`--prod` だけでは付け替わらない）。
