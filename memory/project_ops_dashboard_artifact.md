---
name: project_ops_dashboard_artifact
description: 稼働盤（Artifact 98acdc66）が8/23で止まっている。真因は公開経路が無いこと。★公開中の版と機械生成の版が別物で寄せる先が未決
metadata:
  type: project
---

**有璽氏の依頼（2026-08-25）**

> AIエージェントの動きをまとめたURLについて**定期的に更新**してください。結局途中で更新が止まってる。
> **例えば2時間に一度**の頻度などで。 https://claude.ai/code/artifact/98acdc66-a511-45e0-8fb0-523a41728fe4

## 実測 ── 止まっているのは「生成」ではなく「公開」（2026-08-25）

```
dashboard_data.py   mini。動く。2026-08-25 21:55 に実行して最新値を取得できた
dashboard_build.py  mini。動く。dashboard.html を 61,820バイトで書き出した
Artifact への公開   ★ここが無い。最終更新 2026-08-23 のまま
```

**★Artifact の公開は `Artifact` ツールからしかできない。**cron からも GAS からも叩けない。
publish できるのは Claude Code のセッションだけ ―― つまり**人かAIがその場に居ないと更新されない**。
`dashboard.html` は 8/24 10:40 にも生成されていた。**作っていたが、誰も公開していなかった。**

## ★止めた理由 ── 公開中の版と機械生成の版が別物（決着が要る）

上書き公開しようとして中身を突き合わせ、**同じものではない**と分かったので止めた。

| | 公開中（Artifact 98acdc66・8/23） | 機械生成（dashboard_build.py） |
|---|---|---|
| 作り方 | **手で書いた**（`.sec-head` `.pill` `.tablewrap` 等の独自CSS） | 自動生成（`.tile` `.st` `.filters`） |
| 章 | 4章 | 3章 |
| **営業の台帳はいまどうなっているか** | **ある**（443社・法人番号なし171件の3分類まで） | **無い** |
| 自動処理の一覧 | 要約 | 53件・絞り込み・行を開くと備考 |
| エージェント13体 | あり | あり（起動のされ方・最終稼働つき） |
| 更新 | **手でしか作れない＝定期化できない** | **機械で作れる＝定期化できる** |

**★そのまま上書きすると、台帳の章と今の見た目が消える。**
規範「採用されたものを作り直さない」に反するので**publish しなかった**。
→ [[feedback_dont_remake_what_was_approved]] [[feedback_one_route_is_not_verification]]

## 有璽氏に決めてもらうこと（1つだけ）

```
案A  機械生成を正本にする（推奨）
     dashboard_build.py へ「営業の台帳」の章を足す（数字は dashboard_data.json に既にある）
     → 見た目は今の機械版に変わる。★2時間おきの自動更新ができるようになる
案B  手書きの見た目を正本にする
     dashboard_build.py の出力テンプレを手書き版の見た目へ寄せる（工数が増える）
     → 見た目は変わらない。定期化はできるが実装が重い
```

## 定期更新の経路（★どれも未実測。決まってから着手）

```
① mini の cron から claude CLI をヘッドレス起動し Artifact ツールを使わせる
   ~/.npm-global/bin/claude は mini に実在（2026-08-25 実測）。★publish が通るかは未実測
② クラウド routine から publish   ★ローカルの dashboard.html を読めない。データ受け渡しが要る
③ 人がセッションで叩く            いまの状態。★止まる（現に2日止まった）
```

## 済ませてあること

- `bin/dashboard_to_artifact.py` を新設。`dashboard.html` から Artifact 用（骨組みを外した形）へ変換する。
  **★見た目・配色・スクリプトには手を入れない。**`document.body.dataset.generated` が
  `<body>` ごと消える問題だけ `.wrap` へ移して対処。実測で変換できることを確認済み。
- レジスタには「稼働ダッシュボード データ収集 / 生成」の2行が既にあるが**どちらも止めてある**
  （有効オフ）。定期化するならここを有効にし、ドーベルマンの検査を通す。

関連: [[project_automation_register]] [[reference_ran_is_not_succeeded]]

## ★A案で決着（2026-08-25 有璽氏承認）── 実装・公開済み

> 「A案で良いです。**過去のやつは消えますか？** 設計上、今のものもそうですし、**今後含めて遡れますか？**」

**やったこと**

```
dashboard_build.py  「営業の台帳 ── いまどうなっているか」の章を追加（mini・バックアップ取得済み
                     dashboard_build.py.bak_20260825-2205）。★既存の章・見た目には触っていない
                     出すのは dashboard_data.json の実測値だけ。how をそのまま「数え方」として見せる
公開                 Artifact 98acdc66 を更新（4章＝自動処理53/エージェント13/営業の台帳/人待ち2）
                     ★公開中だった手書き版の「営業の台帳」は失わずに移行できた
履歴                 bin/dashboard_history.py 新設 → data/dashboard_history/YYYY-MM-DD.json.gz
定期                 bin/daily_jobs.conf へ2時間おき8回（08:10〜22:10）。data→build→history
```

### ★★答え ── 過去は「消えていた」。今日から残る

```
これまで   dashboard_data.json も dashboard.html も毎回まるごと上書き。履歴処理は0件（実測）
           ＝ 8/23・8/24 の数字はもうどこにも無い
           ただし Artifact 側の版はサーバーに残っていた（8/23版の全文を取得できたのが証拠）
これから   数字   data/dashboard_history/YYYY-MM-DD.json.gz（git・両機・日ごと最新1本・消さない）
           画面   Artifact のバージョン（publish のたびに積まれる。label が版の名前）
           差分   python3 bin/dashboard_history.py --diff で前日との変化だけ出る（実測済み）
```

### 🔴 満たせていないこと ── URLの自動更新はできない（2026-08-25 実測）

**mini のヘッドレス `claude -p` には Artifact ツールが存在しない。**
`--allowedTools "Artifact"` を付けても、ツール一覧に出てこないことを実測した。

```
cron でできる     数字を集める → HTMLを作る → その日の数字を残す      ← 2時間おきで稼働
cron でできない   Artifact への publish                              ← ★ここだけ人/セッション依存
```

**＝「2時間おきにURLが更新される」は、いまの経路では実現できない。** 代替は3つ。

| 案 | 中身 | 効き目 |
|---|---|---|
| ① Vercel へ静的公開 | 既に `gamemarke.vivid-global.com` で使っている経路。cron から deploy できる | **URLは変わるが完全自動になる** |
| ② Notion ページへ要点を書く | cron から書ける。ただし表止まり（画面は再現できない） | 見た目が落ちる |
| ③ いまのまま | セッションが居るときに publish | **また止まる** |

**★有璽氏の判断待ち。**HTMLは2時間おきに最新化されているので、①へ切り替えれば即日つながる。

## ★①Vercel を実行した（2026-08-25 有璽氏「①を実行して」）

```
公開先   https://fukuchi-kadoban.vercel.app   （プロジェクト fukuchi-kadoban / team fuku-chi-vivid）
経路     dashboard_data.py → dashboard_build.py → dashboard_history.py → kadoban_deploy.sh
定期     bin/daily_jobs.conf の2時間おき8回（08:10〜22:10）の各行へ結線済み
道具     Vercel 認証を mini へ配布し whoami を実測（両機で動く）
         ★mini は node/npx が /usr/local/bin にある。cron の最小PATHでは見つからないので
           スクリプト冒頭で PATH を補強した
```

### 🔴 いま中身は載せていない ── 固定URLが誰でも読めるため

**実測（2026-08-25）**

```
vercel project protection enable --sso  → deploymentType は
  "prod_deployment_urls_and_all_previews" にしかならない
  ＝ deployment 固有URL（…-5n22jywnn-…）と preview は SSO で塞がる（302を実測）
  ＝ ★固定URL <project>.vercel.app は塞がらない（素のGETで HTTP 200 を実測）
CLI に deploymentType を all にする口が無い。ダッシュボードでしか変えられない
```

稼働盤の中身は**社内の運用実態そのもの**（人名・Slackチャンネル名・会社数・仕組みの穴・DBのID）。
一度 200 で公開された事実を確認したので、**すぐに「準備中」のプレースホルダへ差し替えた。**

- **`bin/kadoban_deploy.sh` は「出す前に出していいかを確かめる」設計にした。**
  `deploymentType=all` を確認できなければ本番の中身を載せず、プレースホルダを出して
  レジスタへ**警告**の心拍を打つ。**黙って公開しない。**判定は両方向を実測済み
  （all→載せる／prod_…→載せない／空→載せない）。
- **★人が要る（押す場所）**
  https://vercel.com/fuku-chi-vivid/fukuchi-kadoban/settings/deployment-protection
  → **Vercel Authentication** の Standard Protection を **All Deployments** にして Save。
  **押した次の実行（2時間以内）から、自動で本番の中身が載る。**こちらの作業は残っていない。

### 踏んだもの（同じ型を繰り返さないため）

- **bash 3.2 の全角直後の変数**を7か所。`${var}` で必ず区切る → [[reference_bash32_multibyte_unbound_var]]
- **1経路で断定した**: 保護の判定が MacBook では JSON（stdout）、mini では
  「> ssoProtection: {...}」（**stderr**）で出る（Node 20 と 24 の差）。`2>/dev/null` にしていたため
  **mini では判定そのものが死んでいた**（安全側には倒れていたが、保護をONにしても永久に
  中身が載らない状態だった）→ [[feedback_one_route_is_not_verification]]

## ★塞げた ── 無料プランのまま（2026-08-25）

有璽氏「All Deployments は**有料プランのみ**のようです。何かそれ以外の方法は？」

**Vercel Edge Middleware の Basic 認証で解決した。無料枠で動く。**

```
実体     web/kadoban/middleware.js（repo で管理し、deploy 時に site へコピー）
合言葉   Vercel の環境変数 KADOBAN_USER / KADOBAN_PASS（暗号化保存）
         ★ソースにも memory にも書かない → reference_plaintext_credentials_handling
         ★環境変数が無いときは 503 で閉じる（設定漏れで全公開になるのを防ぐ）
実測     認証なし → HTTP 401（WWW-Authenticate: Basic）
         認証あり → HTTP 200・4章すべて表示（自動処理53／エージェント13／営業の台帳／人待ち2）
         両機（MacBook・Mac mini）で同じ結果
```

### 守りを2段にした（★「かかっているつもり」を作らない）

```
出す前    middleware.js があるか ／ 環境変数が2本揃っているか
          → 欠けていれば中身を載せず、プレースホルダを出して★警告の心拍
出した後  ★素の GET が 401 を返すか
          → 401でなければ自動でプレースホルダへ差し戻し、★失敗の心拍を打つ
```

**＝ 認証が壊れた日に、中身が晒されたまま放置されることが構造的に起きない。**

**これで①は完了。**有璽氏の操作は残っていない。2時間おきに数字が更新される。
`https://fukuchi-kadoban.vercel.app` を開くとブラウザが合言葉を聞いてくる。
