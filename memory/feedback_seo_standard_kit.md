---
name: feedback_seo_standard_kit
description: 公開中の全Webサイトに「Clarity＋Search Console登録＋定期レビュー」を標準装備としてSEO作業に含める（2026-10-05 有璽氏）
metadata:
  type: feedback
---

**2026-10-05 有璽氏**
> 「今公開されている弊社ビビッド関連法人施設等のウェブサイトにこちらの設定（Microsoft Clarity）を入れたい。
>  これはもう標準装備として、SEOの作業の一つとして、サーチコンソールへの登録だったり、
>  定期的なレビューの中に標準で含むものとしてください。」

**Why:** 公開前の計測（[[reference_salesbreaker_campaign_setup]]・Skill web-tracking-setup）は「新しく出すページ」だけを守っていた。
★既に公開中のサイト（ビビッド・ILIFE・ふくち。・オレンジワークス）は検問を通らないので、Clarity も Search Console も抜けたままだった。

**How to apply:**
- SEOの作業＝「Clarity（サイトごとに別プロジェクト）＋Search Console（ドメインプロパティ）＋サイトマップ送信＋Bing取り込み」を1セットで扱う。どれか1つだけで終わらせない
- 定期レビュー（月次）で各サイトの4点を実測する：Clarity が通信しているか／Search Console のカバレッジ・エラー／サイトマップが成功か／Clarity の不満シグナル（デッドクリック・レイジクリック・急なスクロール戻り）
- 一覧と現在地は `bin/web_tracking/sites.json`（★正本。ここに写さない）。点検は `site_audit.py`。手順は Skill web-tracking-setup の「公開中サイト」節
- プライバシーポリシーへ「Clarity・GA4で閲覧行動を計測」と書くのは推奨（★外部送信規律は自社の情報発信サイトには一般に適用されない＝総務省資料。法的義務と書かない）
- 10/5 時点：Clarity 5件作成済（ID は台帳）・設置は全サイトとも管理画面ログイン待ち。当方に管理画面の認証は無い（パスワード入力は代行しない）
- 実例：ko-station.org（10/3 Clarity yrpyrl79ny・10/5 Search Console 登録）→ [[project_minamikawachi_kodomo_station_site]]

**設置で踏んだもの（10/5）**
- ★ILIFE＝公式プラグイン「Microsoft Clarity」の設定画面（Clarity埋め込み枠）のプロジェクト選択が操作できなかった → プラグイン自身の保存処理 `admin-ajax.php` action=`edit_clarity_project_id`（nonce は埋め込み枠の src の nonce）で保存し成功。実ブラウザで tag→clarity.js→collect を確認
- ★オレンジワークス＝さくらのWAFが AIOSEO の REST 保存（/wp-json/aioseo/v1/options）を **403** で遮断。プラグイン導入も同じ。画面上は保存の✓が出るが★保存されていない（再読込は同じURLだと読み直さない＝新しいタブで確かめる）→ WAFを一時オフにしてから保存
- ★STUDIO＝連携Appsに Clarity は無い。ダッシュボード「カスタム→カスタムヘッダー」はHTTPヘッダーで別物。head はデザインエディタのカスタムコード→★公開が要る（未公開の他の編集も一緒に出る）
- ✅10/5 有璽氏「（ふくち。STUDIOは）他のページ含め公開してよい」＝Clarity設置のための公開は、未公開の他の編集ごと出してよい（★この件限りの承認）
- ★さくら(vivid)のWAF：セキュリティ → WAF設定ドメイン。10/5時点で fukushi119・orange-works.co・vivid-global.com・vivid.sakura.ne.jp の4つとも「有効」＝vivid・119番でも同じ403が出る前提で段取りする
- ✅10/5 ふくち。STUDIO：右パネル「サイト」→カスタムコード<head>→公開「更新」で設置完了（本番3ページ＋実ブラウザ3通信）
- ★10/5 オレンジワークス：WAFオフ後の保存はWAFでなく「ログイン切れ」で失敗（rest_cookie_invalid_nonce・管理画面は権限エラー）。★管理画面ログインはAIOSで短時間に切れる＝WAFオフの依頼は「ログインし直してから」をセットで出す
- ✅10/5 オレンジワークス設置完了（ログインし直し→AIOSEO REST保存200→本番3ページ＋実ブラウザ3通信）。WAFは有璽氏が「利用する」へ戻す
- 10/5 有璽氏：ビビッドのWPログインURLは「直ぐには分からない」＝保留（分かったらWAFオフ＋ログインし直しで設置）。119番はさくらファイルマネージャーで進めてよい
- ✅10/5 119番：さくらファイルマネージャー（右クリック→指定の名前で複製で控え→編集）で <head> 直後へタグ。★編集欄の値をJSで書き換えただけでは保存されない（1回目は未反映）→実キー入力を1回入れてから「保存」。差分はタグ2行のみ・3通信を確認
- ★ファイルマネージャーのボタンは target=_blank で別窓に開き操作不能 → form.target='_self' にして同じタブで開く
- ★10/5 有璽氏「LPでヒートマップを設定した覚え（ツエルサープ？）」→ 記録上LPのヒートマップは★Microsoft Clarity（gamemarke・y999sy395z）だけ＝今回の5サイトと同じ仕組み。他のヒートマップ製品の記録は memory に0件（1経路で確認）

**⛔訂正（10/5）既存の定期レビューは在った**
- 「定期レビューの仕組みは無い」と報告したのは誤り。★リポジトリと両機の cron/launchd しか見ていなかった。**クラウドのルーティン**に在る：
  - `trig_01Y9rJkmzHmUFmsYJ9tVAuhj`「SEO巡回エージェント（月次・Search Console自動分析）」毎月1日 9:00 JST・10/1 成功。Search Console→Artifact→Slack #03_広報部＋メール。対象4サイト（オレンジ・LIFE STAND UP・ビビッド・ふくち。）＝★ko-station・119番が入っていない／Clarityも入っていない
  - `trig_019a1vGFx5c5K3wKu7W6ZnBZ`「MEO月次チェック」毎月1日・Slackへチェックリスト
- ★定期処理を「無い」と言う前に、①リポジトリ ②両機 cron/launchd ③クラウドのルーティン（RemoteTrigger list）④Notion 自動処理レジスタ の4か所を見る

**週次メール（10/5 有璽氏が示した事実）**
- 「ふくち。グループSearch Console - <日付>」＝ **Looker Studio（data-studio-noreply）のスケジュール配信**・毎週月曜 7:00頃 JST・PDF添付。★表示されているのはオレンジワークスとILIFEの2サイトだけ（有璽氏）
- 有璽氏の要望（10/5）：①案A（Clarityの数字まで載せる）で進める ②全サイトのSearch Consoleを一体で見られる設計 ③そのメールにClarity（ヒートマップ系の指標）も出す
- ★これも10/5の最初の棚卸しで見落とした定期処理（4か所に加えて⑤Gmailのスケジュール配信）

**10/5 一体化の設計（案A・有璽氏承認）と詰まり**
- 形：毎日 mini の `bin/web_tracking/clarity_daily.py` → スプレッドシート「SEO計測_Clarity日次」（縦持ち）→ Looker Studio「ふくち。グループSearch Console」にデータソースとして追加 → 既存の月曜7時の配信がそのまま届ける。GSCは Looker の標準コネクタで6サイト分を追加。月次の巡回エージェントは6サイト化＋Clarity月合計
- 🔴 mini は既定経路なし（10/5 実測：clarity.ms・slack・github が 000／Googleの一部だけ届く）＝日次取得をまだ載せられない。git pull も不可
- 🔴 Chrome拡張は lookerstudio.google.com の読み取り権限が無い（Permission denied）＝Looker の編集はこちらから不可
- 未：Clarity APIトークン6本（有璽氏）／clarity_daily.py は未実行（--init も未）
- 10/5 有璽氏「Looker Studioはそちらで作成できない？」＝★こちらで組む前提。Looker Studio には作成・編集のAPIが無い（画面操作のみ）→ Chrome拡張に lookerstudio.google.com のサイト権限が要る。許可が出たら：GSC 4サイト追加・Clarityシートをデータソース化・一覧ページとサイト別ページを作る
- 🔴10/5 Claude in Chrome は lookerstudio.google.com で★読み取り・スクショとも「Permission denied」（Chrome側は全サイト許可・拡張のパネルに許可確認もブロック一覧も出ない＝3回再現）。★こちらからLooker Studioを操作する経路は無い前提で設計する
- **Looker Studio 導入の経緯（10/5 調査・決定の発言そのものは未発見）**：9/14 オレンジGSC登録 → 9/19 ILIFE/オレンジのインデックス確認リマインダー → 9/22 SEO巡回エージェント（月次）作成 → 9/22「ILIFE・オレンジのGSC設定」完了 → 9/23「SEO月次レポートダッシュボード・自動化（オレンジ・ILIFE）」完了（2件とも出どころ Chatwork・同じ投稿）→ 9/28 Looker の週次メール初回。ルーティンは全部 claude.ai 側の会話から作成（created_via=meta_mcp）。★ターミナル版（両機）の会話記録にLookerの話は0件＝claude.ai の会話で決めた可能性が高く、こちらからは読めない
- ⛔訂正（10/5）「SEO巡回エージェント 10/1 成功」は誤り。状態表示は SUCCEEDED だが★Slack・メール配信は自動判定（Real-World Transactions）で拒否＝届いていない。レポートページ（Artifact 42uQ6hU8zvsT99j1C1Pc9U）だけ公開。9/23 の手動テストも2回目は External System Writes で拒否。★ルーティンの成否は status でなく get_run_log の中身で見る
- 10/1 時点：ルーティンのGoogleアカウントは4サイトとも Search Console を読める（9/23 はビビッド・ふくち。が insufficient permission だった）。🔴 LIFE STAND UP のクリックが 8月351→9月87（−75%・表示はほぼ横ばい）
- ★claude.ai 側の Claude Code の会話は、セッション番号（cse_… / session_…）が分かれば RemoteTrigger get_run_log で読める。一覧を出す手段は無い（定期タスクの実行分だけ list_runs で辿れる）
- ✅**Looker Studio 採用の経緯が判明（10/5）**：claude.ai の Claude Code セッション session_011brzwhL5sbxEf6LPrnAmaU（9/19〜9/25・SEO/MEO戦略）。設計書＝ lifestandup-wp 枝 `claude/web-strategy-proposal-continued-cozz30` の `proposal/web-strategy/22_KPI自動収集の実装_LookerStudioとClaude巡回エージェント.md`（9/20作成）
  - 「二段構え」：第1段 Looker Studio＝★今すぐ・認証の受け渡し不要で数値を見える化（有璽氏が手で約10分接続）／第2段 Claude巡回エージェント＝取得＋分析コメント＋通知まで自動。「両者は補完。まずLookerで土台、エージェントで分析まで自動化していく」
  - 当時 Search Console に在ったのが orange-works.co と i-life-fukushi.com の2つだけ＝★Lookerが2サイトなのはこのため（ビビッド・ふくち。は後から sc-domain で追加）
  - ★週次の「自前メール」案は、この設計の第2段を完成させる方向と一致する
- ✅10/5 16:09 有璽氏が Slack #dd191c で「自前の週次メール（推奨）」を選択。★Slackに判断を出したら、次に話すときは先に ask_hub の台帳（mini ~/.vivid-relay/ask_hub_queue.json）で回答を見てから話す（10/5 確認せずに「どちらか押して」と待った）
- 自前週次の形（案）：mini の cron（月曜朝）＝ Search Console 6サイト（API）＋ Clarity 日次シートの直近7日 → HTMLメール（Gmail API）＋Slack 2行。★クラウドのルーティンは送信が自動判定で止まるため使わない。要るもの＝Googleの許可1回（webmasters.readonly＋gmail.send・既存のシート用の鍵とは別ファイル）／Clarity鍵6本
- 10/5 Google許可（SEO用）：mini に `~/.vivid-relay/oauth_seo.py`（webmasters.readonly＋gmail.send・保存先 google_token_seo.json＝シート用 google_token.json とは別）。★MacBookにgoogle_auth_oauthlibが無いので、mini で port 8765 の受け口→MacBook から `ssh -L 8765:localhost:8765 mini` で転送してブラウザで許可する形
- ✅10/5 16:18 Google許可完了（google_token_seo.json・webmasters.readonly＋gmail.send）。🔴ただし GCPプロジェクト 472246617753（mini のOAuthクライアント）で Search Console API が未有効＝403 accessNotConfigured。Gmail API も要確認。有効化は有璽氏（Cloud Console の「有効にする」）
- ✅10/5 16:2x 有璽氏が GCP で Search Console API・Gmail API を有効化 → mini の google_token_seo.json で5プロパティ読める（sc-domain:vivid-global.com／sc-domain:fuku-chi.com／orange-works.co／i-life-fukushi.com／sc-domain:ko-station.org・全て siteOwner）。★119番は sc-domain:vivid-global.com の中＝ページURLで切り分ける
- ✅Clarity 鍵6本（有璽氏）→ mini ~/.vivid-relay/clarity_tokens.json。全サイト取得OK。シート「SEO計測_Clarity日次」 https://docs.google.com/spreadsheets/d/1xDHeqC4mkhK5HLvUwHUpaEyyHCb-AipXsztVH89_Law （初日10/4分 1,644行）
- 🐛直した：内訳（Browser/Device/OS/Country/PageTitle/ReferrerUrl）の名前が落ちていた→URL列へ・範囲「内訳」。★mini に他セッションの書きかけがあると vivid-sync が取り込みを見送る＝修正が届かないまま古い版で動く（10/5 1回踏んだ）
- ✅10/5 16:33 SEO週次メールの試し送り成功（weekly_seo_report.py・Gmail id 1a10afb2eff5094d・受信箱で確認）。6サイト一覧＋サイト別＋タグ点検。★Clarityのページ別URLの項目名は "Url"（10/4分のシートはURL空・10/5取得分から入る）／ko-station の GSC は10/5登録のため0
- 未：cron 登録（Clarity 毎日0:30／週次 月曜7:00）はドーベルマン点検の後・有璽氏が試し送りを見てから。Slack 2行は未実装。mini の ~/vivid-ai-hq は他セッションの書きかけで取り込み保留中→/tmp/wt から試運転した
- ★10/5 有璽氏：週次メールの目的は「要約の共有」ではなく★「分析としてログを残し、それに対して改善をやっていくサイクルを作る」こと。MEO・AIEO（AI検索での見え方）も入れたい
  → 設計：毎週の数字と気づき・打ち手・効果確認を1か所に積む（正本を1つ決める）。メールはその入口。「録画を開く」＝Clarityの訪問者ごとの画面操作の再生
- ✅10/5 17:08 有璽氏（Slack）：#2c7b5a 改善ログ＝Notionにデータベース／#bc8b03 MEO＝GBP API の利用申請を出す（文面はClaude・フォーム入力は有璽氏）
- ✅10/5 Notion「🔧 サイト改善ログ（SEO・MEO・AIEO）」作成（広報部ページ配下・記録層）DB afbfa222ea2848598c384e6c4d983d97／データソース 720d4be9-d3e3-48f9-8e0b-67c0a8aec537。初期7件（候補4・採用3）。MEO行の本文にGBP API申請の手順と英文 use case
- ✅週次メール v2：①記録（＋指名検索クリック・AI経由の訪問）②気づき（自動・しきい値は仮：クリック/表示が先週比−30%以上かつ先週20以上／Clarity の各率20%以上かつ訪問5以上）③改善ログ（採用・実施中と効果）④サイト別 ⑤タグ点検。本送信時は気づきを「［要検討］…」で候補に自動起票（同じサイト×同じ文言は足さない）
- 🔴 mini の Notion 鍵（統合名「Chatworkリレー」）は広報部ページも改善ログDBも 404＝未接続。有璽氏がDBの「…→接続」で「Chatworkリレー」を追加する必要
- ✅10/5 有璽氏が改善ログDBに「Chatworkリレー」を接続（mini から読めるかは下で実測）。GBP API 申請は「こちらでも見せて・確認しながらやる」＝画面で並走
- 🔴10/5 GBP API 申請フォーム（support.google.com/business/workflow/16726127）を y_tam@vivid-global.com で開くと、選べるビジネスプロフィールは「三ツ星咖哩」（大阪市阿倍野区・確認済み）の1件だけ＝★LIFE STAND UP・オレンジワークス・こどもステーションのプロフィールは別のGoogleアカウントで管理されている。申請は「プロフィールのオーナー/管理者のアカウント」で行う必要（12%で停止・送信していない）
- 10/5 有璽氏「別のアカウントでログインした」→ ただし Claude が操作する Chrome の申請画面は引き続き y_tam@vivid-global.com（5%・アカウント確認で停止）。有璽氏は案A（各プロフィールに y_tam を管理者として追加）の手順を求めた


## 🔴2026-10-05 ★かわちばなしが抜けていた（実測）

本番 https://kawachibanashi.vercel.app のトップを数えた：
**Clarity 0 ／ GA4 0 ／ GTM 0 ／ gtag 0。台帳 `bin/web_tracking/sites.json`（7件）にも無い。**

9/29 から「外へ出すWebページには計測を必ず入れる」と決めた後に作ったサイトなのに抜けた。
**★理由＝合言葉つきだったので「まだ外に出していない」と扱われ、どの検査にも引っかからなかった。**

★型：**合言葉つきの公開も「公開」として台帳に載せる。**
載せた上で「計測はまだ・一般公開前に入れる」と状態で持つ。
台帳に無いものは、公開の日に誰も気づかない。
- ✅10/5 21:18〜21:21 有璽氏（YUJI TAMURA アカウント）が y_tam@vivid-global.com を追加：LIFE STAND UP＝オーナー／オレンジワークス藤井寺＝オーナー／NPO法人南河内こどもステーション＝管理者（Gmail の businessprofile-noreply で確認）

### ★★2026-10-05 有璽氏 ── 公開を遅らせるとSEOで損をする

**「実際のデモ情報じゃなくて、実際の情報を入れたら早く公開していかないと、
Google検索にも上がってこないと思うので、そこは進めていこう」**

```
★順番を間違えない
  ✕  中身が揃う → 計測を入れる → 完璧になってから公開
  ○  ★実データを入れる → 公開する → 計測はオープンの前に入れる（予約で漏らさない）
```

**理由＝検索に載るまで時間がかかる。** 公開を待つ月数ぶん、そのまま遅れる。
見本データで出すのは論外だが、**実データが少しでも入ったら出す**。

**★「予約」の正しい形＝台帳 `bin/web_tracking/sites.json` に載せること。**
Current_Focus のタスク行だけでは漏れる（人の記憶に戻るので）。
台帳に載れば `site_audit.py` の実測と月次レビューの対象になり、
**公開の日に機械が「計測が無い」と言う。**

★合言葉つきの公開も台帳に載せる（↑の節）。載せたうえで status に実状を書く。
- ✅10/5 GBP API 申請を送信：ケースID 8-7628000042206・審査 7〜10営業日（目安 10/15〜10/19）。代表プロフィール＝LIFE STAND UP／プロジェクト 472246617753／サイト i-life-fukushi.com。結果は Cloud の割り当て（0→300 QPM）かメールで確かめる
- ★地雷：この申請画面（support.google.com/business/workflow/16726127）は★最後の質問の「次へ進む」でそのまま送信される＝確認画面が無い。「送信前に内容を見せる」と約束していたのに、確認なしで送信された（10/5）。★次からは最後から2つ目の段階で止めて確認を取る
- ✅10/5 22時台 週次メール v2 の試し送り（改善ログ入り）成功 id=1a10c0d15db8ed70。★試し送り（--to）では改善ログへ起票しない。★台帳に別セッションが「かわちばなし」（公開前・Basic認証・計測0・GSC未登録）を登録＝一覧に「—」で出る
- ★10/5 有璽氏（試し送りを見て）：①記録の表そのものは貯まるのか／②気づき・④サイト別はもっと深掘りが欲しい／Notion改善ログは見づらい（1件ずつの改善で、週で見比べられない）。「エージェント側が改善していく形なら意味を増す。私が見て指示を出すのなら使いにくい」
  → 方針：①は週次サマリーをシートに1週1行で蓄積／深掘りはAI（mini の claude -p）がサイトごとに「何が起きた・なぜ・次の一手」を書く／改善ログは★エージェントの作業記録（提案→Slackボタンで承認→実施→効果を記入）にし、有璽氏の入口はメール＋Slackのボタンだけにする
