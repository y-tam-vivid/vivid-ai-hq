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
