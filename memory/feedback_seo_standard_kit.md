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
