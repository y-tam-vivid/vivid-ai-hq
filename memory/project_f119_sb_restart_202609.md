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
~~SBタグ・クリックログは3サイトとも無し~~ → ✅2026-10-08 ふくち。・オレンジ・LSU（＋119番・gamemarke・かわちばなし）へ設置・検査 ✗0（ふくち。の誤検知は 2a75299 で解消）＝この3サイトをSB文面の着地先にしても検問は止めない。
★10/8 有璽氏：3サイトのSBタグ・クリックログは別のClaude Codeセッションへ渡す → 引き継ぎ書 `scratchpad/handoff/2026-10-08_SBタグとクリックログ_3サイト.md`（GTMの扱い＝案A共通GTM/案B検査側を直す は有璽氏の判断待ち）
★10/8 夕 有璽氏「こちらでは施設向けLPを実装し、実際にフォーム営業を進められるように動く」（3サイトのSBタグは別セッションが実装中）。
→ ビビの判断：Claude Design の修正を待たず、書き出し済み .dc.html を公開用フォルダへ複製して直接直す＝★公開版の正本はこちら（Claude Design はデザインの元として残る）。

**送信先の実測（2026-10-08 ビビ・SB API で読むだけ）**
- SBマイリスト全31,893件のうち大阪3,248件（放デイ1,576／B型1,095／児発248／移行125／A型95・複合あり）
- ★大阪3,248件のうち2,875件は★7月に医療連携の文面（template 1462）を送信済み＝今回は★2回目のアプローチ
- 除外1,766件（URL切れ587／フォーム無し512／問合せ以外のフォーム338／ポータル・SNSのURL284／営業お断り44／自社1）→ ドメイン重複を除いて★1,273件（児童684・就労586・両方3）
- 一覧 `JapanGtmAgentWorkspace/saved-lists/osaka-fukushi119-iryo-202610-targets.json`
- ★7月の率（届く約15%・届いた先のクリック1〜2%）だと、1,273件でクリックは合計数件＝★6通り（児童/就労×A/B/C）の比較は判定できない。有璽氏の判断待ち
- SB履歴APIの期間指定は `{"period":{"days":180}}`（filters.period_days は効かない）。マイリスト検索は limit が100で頭打ち

**LP組み立て（2026-10-08 リリス・commit 473cd90）** 置き場 `~/Documents/fukushi119_iryo_lp/`（★公開版の正本・git管理・未公開）
- /kids|shuro × /a|b|c の6通りをパスで出し分け（vercel.json rewrites）。375/768/1440 × 6 で横あふれ0
- 計測v2入り：SB・GTM・クリックログ・data-cta ✓／★Clarity ID が未発行で検査✗（有璽氏が作る）
- 試算欄は index.html の `LP_SIM` 1か所（クローバーが要件を裏取り中）／写真は `LP_PHOTOS`（就労系は写真なし＝null）
- 児童系B・Cのヒーローは field-staff.jpg の右側を切り出し（大人スタッフ1名の顔あり＝★掲載同意の確認待ち）。元画像は .vercelignore で非公開

**試算欄の訂正（2026-10-08 クローバーが一次資料で確認）**：区分Ⅰ〜Ⅲは★看護職員1人につき1日8人まで（告示・留意事項通知・Q&A問32）。
「対象16人で月10万〜40万円」は看護職員2人前提＝誤解を招く → LP（6d6158b）と指示文を ★月約5万〜20万円（8人・20日・1単位10円・売上の目安・委託費含まず）へ直した。
区分Ⅳ「最大128万円」は医療的ケア児16人・看護職員2人の場合＝★一般向けに使わない。★提案資料v1.1の見出しにも同じ数字がある（未修正）。
未確認：就労A/B/移行の単位数の告示原文・地域区分の単価・区分Ⅳの対象者の定義。出典URLはクローバーの報告（mhlw 001239565／001494356・cfa 留意事項通知・Q&A）。

**⛔上の「試算欄の訂正」は有璽氏の判断で取り消し（2026-10-08 夕）**
有璽氏「看護職員は★2名体制で行う想定（8人以上の場合）。★表示に間違いはない。修正しなくてよい」
「医療連携加算で取れるのは最大128万円程度。そこから★訪問看護への支払い・医師への手数料等が出て、★施設側に残るのが月10万〜40万円の額」
→ LP・指示文の試算欄は★元の「月約10万〜40万円／年約120万〜480万円／対象16人」に戻した。提案資料v1.1の128万円も直さない。
★AIの一般論（8人上限）は、現場の前提（2名体制・総額と手残りの区別）で覆った＝fukuchi-core「AIの所見はドメイン知識で覆る」の実例。
**比較のやり方＝①で確定（有璽氏 10/8）**：大阪で児童/就労×A/B/Cの6通りを第1波として送り、判定は地域を広げて積み上げる。
理由＝★医療連携加算をすぐ提供できるのは大阪府のみ。大阪で実績を作り、他府県へ広げる。

**送信準備（2026-10-08 ビビ）**
- 6通りの割り振り `saved-lists/osaka-fukushi119-iryo-202610-arms.json`（児童/就労ごとに7月の結果別に乱数seed 20261008で3等分）
  kids-a 230／kids-b 229／kids-c 228／shuro-a 196／shuro-b 196／shuro-c 194（複合3件は児童系へ）
- 文面6本 `campaigns/fukushi119-iryo-202610/03_templates_6.json`。SBの templates/preview を全本通過（件名29〜35字・本文383〜414字・未解決タグ0・警告0）。URLは★仮（LP-DOMAIN）
- ★SB templates/preview は `{"draft":{subject,body},"sample_target":{company,url}}` で渡す（`template` キーは無視されて空のプレビューになる）
- 残り：Clarity ID／公開先ドメイン／写真の掲載同意 → LP公開 → 文面のURL確定 → 文面保存とリスト作成（★要承認）→ 送信（有璽氏）

**2026-10-08 夜 有璽氏**
- 「Claude Design 側で写真は全て差し替えている」＝★Drive の書き出し（9/29）は古い版。公開前に★新しい書き出しを受け取り、写真だけ取り込む（DesignSync はデザインシステム専用で通常案件は読めない）
- 公開先ドメイン＝★iryo.vivid-global.com で進めてよい。「さくらのDNSに増やす作業もそちらで」＝★AIがDNS追加まで実装（有璽氏の承認済み）
- 段取り：Vercelプロジェクト作成＋ドメイン追加（中身はまだ出さない）→ さくらDNSにCNAME → Clarity作成 → 新しい写真を取り込み → 公開

**公開先の設定（2026-10-08 19:16 済）**：Vercel プロジェクト `fukushi119-iryo-lp`（fuku-chi-vivid）＋ドメイン iryo.vivid-global.com 登録（verified）。
さくらDNSに iryo CNAME 670a13cd2721617e.vercel-dns-016.com. を追加（ns1・ns2・8.8.8.8 で一致／他の行は無傷）。★中身はまだ出していない（新しい写真の版待ち）

**最新版で組み直し（2026-10-08 夜・LP commit 7a63dd7）**：有璽氏が Claude Design で直した最新版（`~/Downloads/福祉施設119番サービス紹介WEBページ 2/`）に、こちらの指示（kids/shuro×A/B/Cのパス・data-cta・consul_vi@・切替バー非表示・写真・試算 月約13万〜40万円・就労系の別の声）がほぼ全部入っていた
→ ★Claude Design 側を正本にし、こちらは計測v2と公開設定（相対パス用 rewrites 48件・.vercelignore）だけを足す形に切り替えた。uploads/（提案資料PDF）は公開物から外した
写真：medical-team.jpg＝uploads/35066767_m.jpg、doctor-consult.webp＝tomaturiHFKE2155_TP_V（★どちらも有璽氏が入れた素材写真）
残り：★Clarity（Chromeが未ログイン＝有璽氏のサインイン待ち）→ ID を入れる → 公開 → /kids/support.js 等が200か確認

**★公開済み（2026-10-08 夜）** https://iryo.vivid-global.com/（/kids|shuro/a|b|c）・Vercel 本番・LP commit d3fb26c
- Clarity ★yuh9dj2874（AIがログイン済みChromeで作成）／計測の検問を通過（全✓）／uploads・README は404
- 実ブラウザ（/shuro/b?utm_source=salesbreaker）：見出しどおり・clarity/sb-track/gtm/GA4 collect の4通信・cta_click（shuro-b/salesbreaker/hero）を確認
- 文面6本のURLを本物へ差し替え・SB preview 警告0（03_templates_6.json）
残り：★SBへ文面6本の保存とリスト6本の作成（有璽氏の承認待ち）→ 送信（有璽氏）

**有璽氏の承認（2026-10-08 夜）**：送信者名は★松本のまま／SBへ①文面6本の保存 ②リスト6本の作成 を承認。送信は有璽氏が押す。

**SB保存の結果（2026-10-08 夜）**
- ✅文面6本を保存：template_id ★1744 kids-a／1745 kids-b／1746 kids-c／1747 shuro-a／1748 shuro-b／1749 shuro-c（company_profile_id 481・送信者 松本）。読み返して件名・本文が一字一句一致
  ★templates/save は company_profile_id が必須（無いと400）
- 🔴リスト：API `saved-lists/save` に★マイリストの番号を渡すと「SB側の企業データ(master)」の番号として登録される（target_source=master・会社名が空）。
  list_type/target_type を付けても変わらない＝★このAPIはマイリスト対象のリストを作れない。誤って作った 767 は送信前に削除・404で消えたことを確認
  → マイリストの施設で送信先を作るのは★SBの画面側（7月と同じ道）。調査中

**送信先の作り方（2026-10-08 夜・確定）**：SBの送信画面は「営業リスト（マイリスト）」を★リストタグで絞って送る作り。
→ 大阪1,273件のマイリストに★案ごとのタグ `119医療202610_<kids|shuro>-<a|b|c>` を足した（my-lists/upsert で全項目＋タグ追記・action=updated）
実測2経路：①全31,893件を取り直し＝タグ件数 230/229/228/196/196/194・タグ以外の変化0・対象外の変化0 ②送信画面でkids-aタグを検索＝★230件
★my-lists/upsert は url 必須＝既存行を更新するときは★全項目を渡す（足りないと400）。控え `~/.vivid-relay/_backups/sb_mylist_osaka_before_tag_20261008.json`
送信手順 `campaigns/fukushi119-iryo-202610/04_送信の手順.md`。★送信は有璽氏（まだ押していない）

**送信予定（2026-10-08 有璽氏）**：★10/9 に有璽氏が6通りを送る。導線＝文面のURL→LP（iryo）→LPの「無料相談を予約する」→Googleカレンダー予約 calendar.app.google/c5aJoxPMVB5brw9b8
