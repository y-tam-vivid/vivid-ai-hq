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
