---
name: project_f119_sb_restart_202609
description: 福祉施設の119番 SalesBreakerフォーム営業の再開（2026-09-29〜）。LP A/B/C のABテスト・大阪のみ・5種別。いまLPのURL受領待ち
metadata:
  type: project
---

# 福祉施設の119番 ── SalesBreaker フォーム営業の再開（2026-09-29 有璽氏）

**有璽氏の決定（2026-09-29）**
```
エリア     大阪府のみ
対象種別   放課後等デイ／児童発達支援／就労継続A型／B型／就労移行支援
着地先     有璽氏が作ったLP A・B・C の3本 → ABテストを含めて実施
```

**LPの置き場（2026-09-29 有璽氏）**: `共有ドライブ/11-000_事業開発部門/03_デザイン制作プロジェクト/12_福祉施設の119番/02_LP・Webページ/2026-09-29【LP】福祉施設の119番_サービス紹介ページ/`（Claude Design の書き出し .dc.html・未公開）★10/6 Downloads から移送（Downloads にはエイリアスを残した）
```
医療連携加算 LP ABテスト.dc.html   A/B/Cは1ファイル内で ?v=A|B|C で切替（A=医療連携を前面／B=加算の最大化／C=守り→収益）
福祉施設の119番 LP.dc.html        サービス全体のページ（健康診断→遡及点検→月額3本）
```
**★直しは Claude Design 側で行う**（ローカルの .dc.html を書き換えても反映されない → [[reference_claude_design_local_edit_not_reflected]]）

**レビューで出た「公開前に必須」**: ①試算欄の数値が「—」のまま ②B・Cのヒーロー写真が空枠 ③A/B切替バーが既定で表示
④計測タグ4本が2本とも0 ⑤お客様の声（社名は仮名）の実在確認 ⑥対象の表記が「放デイ・児発」だけ（就労A/B/移行も送る）
⑦連絡先メールが sales-consulting@ と consul_vi@ で分かれている（template 1462 は consul_vi@）

**有璽氏の決定②（2026-09-29 夕）**
```
就労系      ★児童系（放デイ・児発）と就労系（A/B/移行）で文言と写真を分けたLPにする＝2系統×A/B/C
119番LP     今すぐでなくてよい（位置づけは未定・保留）
受付アドレス LPは consul_vi@vivid-global.com で統一（sales-consulting@ は使わない）
お客様の声   医療連携LPの引用（放デイ運営法人・社名仮名）は★実在の声
```
fukushi119.vivid-global.com は Vercel ではなく nginx（210.224.185.82・さくら系と推定）で配信中。

**前回（2026-07）の実績**：大阪の My List 1,576件 → SUCCESS 231（14.7%）／DEAD_URL 328／SALES_REJECTED 29
（`JapanGtmAgentWorkspace/saved-lists/osaka-history-result2.json`）。文面は template_id 1462（医療連携体制加算・完全成果報酬）。
**★前回送った先・断られた29件は再送の扱いを先に決める。**

**★ABテストの落とし穴**：文面が同じでLPだけ変えると、**クリック率は差が出ない**（受信者はLPを見る前に押す）。
LPの差は「クリック後の予約率」でしか測れず、1本あたり数件のクリックでは判定できない。
→ LPごとに件名・冒頭も合わせて変える（ゲームブルの「訴求別テスト」と同じ型）か、判定指標を予約率に置くかを決める。

関連: [[project_gamebull_form_sales]] [[reference_salesbreaker_campaign_setup]] [[project_f119_service_menu]] [[project_telapo_list_other_services]]

**成果物（2026-09-29）** `JapanGtmAgentWorkspace/campaigns/fukushi119-iryo-202610/`
01_ClaudeDesign修正指示.md（対象kids/shuroをパス /kids/a〜/shuro/c で切替・必須修正・計測）／02_送信文面_6本.md（件名と冒頭2文だけ変える）
**★試算欄の数値は区分Ⅰ〜Ⅲで作る。提案資料v1.1の「最大128万円」は区分Ⅳ（医療的ケアを要する利用者）なので一般向けの見出しに使わない。**
残：Claude Design での修正 → 公開先ドメイン決定 → タグ4本 → リスト6分割 → SBへ文面登録（保存は要承認）

**現在地（2026-10-08）**：LPの .dc.html は★9/29から未変更（大きさ・更新日時とも同じ）＝Claude Designでの修正はまだ。
修正指示（01_ClaudeDesign修正指示.md）の§3を計測v2に合わせて直した（タグはこちらで入れる・data-cta は header/hero/bottom/see-support/mail）。
03に「Claude Designに貼って直し、書き出してDriveの同じフォルダへ置く」を #今週 で足した。
★3サイト（fuku-chi.com／orange-works.co／i-life-fukushi.com）は別セッションで Clarity まで入った（10/8 実測）。
SBタグ・クリックログは3サイトとも無し＝この3サイトをSB文面の着地先にすると、いまも検問で保存が止まる。
★10/8 有璽氏：3サイトのSBタグ・クリックログは別のClaude Codeセッションへ渡す → 引き継ぎ書 `scratchpad/handoff/2026-10-08_SBタグとクリックログ_3サイト.md`（GTMの扱い＝案A共通GTM/案B検査側を直す は有璽氏の判断待ち）
