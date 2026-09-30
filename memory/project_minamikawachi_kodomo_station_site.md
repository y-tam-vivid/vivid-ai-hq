---
name: project_minamikawachi_kodomo_station_site
description: NPO法人 南河内こどもステーション 公式サイト素案v1 ── Claude Designの書き出しをVercelへデモ公開済み（2026-09-28）
metadata:
  type: project
---

**現在地（2026-09-28）**：Claude Design の書き出し（素案v1・4ページ＋スタイルガイド）を
そのまま Vercel へデモ公開した。**https://minamikawachi-kodomo-demo.vercel.app/**
（合言葉なし・noindex＋robots.txt で検索よけ）。本実装（静的HTML/WP等への作り直し）は未着手。

- 入力 `~/Downloads/南河内こどもステーション WEBサイト構築_design_handoff_minamikawachi_kodomo_station/`（読むだけ・無変更）
- 公開用コピー `~/kodomo-station-demo/`（Vercelプロジェクト `minamikawachi-kodomo-demo`・チーム fuku-chi-vivid）
- ページ：index（トップ）／about／activities／join／styleguide
- **★`.dc.html` は README に「単体では動かない」とあるが、HTTP配信すれば動く**
  （support.js が unpkg から React/Babel を読む）。file:// では動かない
- **★日本語ファイル名は Vercel で404になった**（macOSの濁点分解NFD。NFC化しても解消せず）
  → 英字名へ付け替えてリンクを書き換えた。次回も最初から英字にする
- 除外：`README.md`・`assets/pamphlet/`（16MB・どのページからも参照されていない）
- 【要差替】付箋・「素案（検討用）」ラベルは残したまま（デモなので意図どおり）
- **✅9/28 有璽氏が公開版を確認「問題ない」。**次は下層ページを足す相談中
  （未作成の行き先＝お知らせ一覧・活動レポート一覧・お問い合わせ・プライバシーポリシー。
  いまは「一覧を見る」等がトップ内のアンカーか `#`）
- **✅9/28 夜 v2へ更新**（入力 `~/Downloads/南河内こどもステーション WEBサイト構築/`・6ページ）。
  追加＝news.html（一覧＋`#news-N`で詳細）・report.html。**★公開用は `~/kodomo-station-demo-v2/` が正**
  （旧 `~/kodomo-station-demo/` は控えとして残置。rm が権限で止まるので作り直しは別フォルダで）
  `候補*.dc.html`（書体・ヒーロー下辺の比較用）と uploads/_ds/illustrations_png は載せていない
  **★気づき：1440pxでヘッダーのナビが2行に折れる**（LINEボタン追加で詰まった・デザイン側の話）
- **写真の差し替え（9/28 有璽氏の提案）＝Driveにまとめて共有→こちらで選ぶ**。返答待ち。
  実測：6ページで写真の表示箇所92か所に対し、元写真は★パンフ抽出の13枚だけ（同じ写真の使い回し）。
  進め方案：フォルダ1つ受領→候補を一覧画像で出す→有璽氏が○×→差し込み。★こどもの顔は掲載同意の確認が要る
- **9/29 有璽氏**：v3の入力＝Drive `…/06_イベント・講座/NPO法人南河内こどもステーション/南河内こどもステーション WEBサイト制作/南河内こどもステーション WEBサイト構築 2`。
  素材写真もDriveに格納。★手元の良質素材は祭り（プロカメラマン撮影）中心・日常活動の写真は薄い
  → 現場/NPOへ依頼中。★それまでは手元の写真で「ひとまず差し込む」でよい（完璧を待たない）
- **✅9/29 構築2版＋実写真で公開**。公開元＝`~/kodomo-station-demo-v4/`。
  **★次回からは `python3 ~/kodomo-photo-work/build_site.py <書き出し> <出力>` の1本で作る**
  （英字名化・リンク置換・写真差し替えを毎回かけ直す。差し替え表は `PHOTO_OVERRIDES`）
  素材の実体＝共有ドライブ `11-000_事業開発部門/03_デザイン制作プロジェクト/04_NPO法人南河内こどもステーション/00_素材写真`
  （7イベントへのショートカット・約3,000枚。2018は納品全データ1,551枚＋抜粋94枚）
  差し替え済み＝photo-festival←2025第36回 DSC_1116（フリマ会場）／photo-kodomo-ichi←DSC_1274（お菓子の店）。計17か所
  ★顔が正面で大きく写らない写真を選んだ（掲載同意は未確認のまま）。★こどもマルシェ2件はtaneの行事なので未使用
  ★デプロイ直後数秒は旧版が返る＝照合は少し置いてから
- **✅9/29 構築3（背景の質感を修正）で公開**。公開元＝`~/kodomo-station-demo-v5/`。
  ★有璽氏「差し替えた写真はそのまま維持」＝build_site.py の PHOTO_OVERRIDES を新版にも当て直す運用で確定
  ★構築3からデザインシステム一式（styles.css・tokens・components等）が同梱されたが、ページが読むのは
  assets/ と support.js だけ（実測）＝公開には含めない
- **9/29 有璽氏「差し替え写真をClaude Design側にも渡したい」**→ 一式を用意
  `~/Downloads/こどもステーション_ClaudeDesign用_写真_20260929/`（同じものをDrive制作フォルダにも）
  中身＝写真2枚・00_一覧.jpg・01_指示文.txt（生成不要・配置だけ）。★渡すのは有璽氏（チャットに添付）
  ★Claude Design側が差し替えを終えたら、build_site.py の PHOTO_OVERRIDES は外してよい（二重管理を解消）
- **✅9/29 構築4で公開（15ページ）**。公開元＝`~/kodomo-station-demo-v6/`。写真2枚は当て直し済み
  追加ページ＝outline(団体概要)・contact・festival(こどもまつり)・festival-lp(★どこからもリンク無し)・
  sitemap・privacy・404(Vercelが自動で使う)・sp-check(SP確認シート・スタイルガイドからリンク)
  ★build_site.py を直した：①対応表に無い.dc.htmlは警告 ②assets のサブフォルダも写す（matsuri/ が抜けていた）
  ★参照チェックは src/url( だけでなくスクリプト内の文字列 `assets/...` も数える（2経路で一致を確認）
  ★お問い合わせフォームは見た目だけ（送信先なし・【要差替】）
- **✅9/29夜 日常活動の素材が届き、写真13枠すべてを実写真へ**（公開元 `~/kodomo-station-demo-v7/`）
  00_素材写真に12フォルダ追加（もちつき・人形劇・キャンプ・デイキャンプ・冬のデイキャンプ・耐寒登山・農業体験・
  図工・習字・科学であそぼう・夏まつり・ふれあい広場＝2,287枚）。差し替え表は build_site.py の PHOTO_OVERRIDES（相対パス）
  ★パンフ写真は顔にぼかしがあったが、新しい写真は顔が写る（掲載同意は未確認）
  ★未使用：科学であそぼう・夏まつり・耐寒登山・冬のデイキャンプ（当てる写真枠が無い。科学くらぶ等は水彩の丸の仮置き）
  ★計測の検問：この公開元は「先方確認用デモ・本番公開時に外す」で対象外登録済み（exempt.json）
  Claude Design用 一式 v2（13枚）＝ `~/Downloads/こどもステーション_ClaudeDesign用_写真_20260929_v2/`（Driveにも）
- **✅9/29夜 有璽氏「光が入っているように明るく」→ 11枚を加工して公開**（公開元 `~/kodomo-station-demo-v8/`）
  ★祭り2枚（プロ撮影）は加工しない＝有璽氏の指定。build_site.py の NO_AIRY
  加工＝`~/kodomo-photo-work/airy.py`（暗いほど強く暗部を持ち上げ・暖色少し・明るい所をふんわり光らせる・色とコントラストを戻す）
  ★1回目は持ち上げすぎで霧がかった（彩度14〜17）→ 持ち上げの上限を弱め、上げた分だけ色を戻して解消。
    測定は bin/image_tone.py（暗部の割合が主指標）＋目視の2経路。人形劇は舞台なので暗めのまま（明るさ46.7）
  Claude Design用一式 v2 も加工後の写真に差し替え済み
- **✅9/29夜 有璽氏「明るすぎ。加工前との間ぐらい」「ぼかしでなくシャープを少し」→ 公開元 `~/kodomo-station-demo-v9/`**
  airy.py に strength=0.5（加工前とフル加工の中間）と UnsharpMask(半径2・70%・閾値3) を追加。明るさは前後のちょうど中間を実測
  ★有璽氏の好み：明るくしすぎない・くっきり寄り。次に写真を足すときもこの設定のまま
- **✅9/29夜 Googleマップ埋め込み（トップのアクセス欄）**。公開元 `~/kodomo-station-demo-v10/`
  APIキー不要の `maps?q=…&output=embed`。build_site.py の MAP_QUERY/MAP_RE で毎回差し込む（トップのみ）
  ★Google の登録地点「塩野マンション101号 NPO法人…」34.5573,135.6068 に解決（curlで埋め込み中身を確認）
  ★ヘッドレス撮影では地図の絵は間に合わない（枠と読み込み開始までは確認）＝実ブラウザでの目視が最後の確認
  未対応：こどもまつりLPの会場地図（会場住所が未確定）／sitemap の「地図＝未着手」表示はデザイン側の進捗表
- **✅9/29夜 有璽氏「地図を白黒に」→ `filter:grayscale(1)`（簡易版・LSUと同じ）**。公開元 `~/kodomo-station-demo-v11/`
  ★限界＝ピンも灰色。ピンだけ赤く残すには Maps JavaScript API（課金）が要る＝LSUで有璽氏が不要と判断済み
  ★計測の検問は「公開コマンドに $OUT 等の変数」を文字どおり読み、検査できないと警告する。対象外登録（~/kodomo-station-demo-v*）で実害なし
- **✅9/29夜 有璽氏「セピア調に」→ `grayscale(1) sepia(.45) contrast(.95) brightness(1.02)`**。公開元 `~/kodomo-station-demo-v12/`
  ★踏んだ：置換の文字列が一致せず空振り→差分確認が「同じもの同士」を比べて"1か所のみ"と誤って出た。
    ★差分確認は「変わった行数が0でないこと」も併せて見る（今回 2行＝1か所で確認し直した）
- **⛔9/29夜 セピアは取り下げ。有璽氏「見づらいかな。白黒に戻して」→ 白黒で確定**。公開元 `~/kodomo-station-demo-v13/`
  （v11 の白黒版とバイト単位で同一を確認）。★地図の色は白黒が正。次にセピアを提案しない
- **✅9/30 構築5で公開（18ページ）**。公開元 `~/kodomo-station-demo-v14/`
  追加＝volunteer(ボランティア募集)・calendar(年間カレンダー)・donate-steps(寄付の手順)
  ★Claude Design が写真13枚を取り込み済み（バイトは違うが中身は公開中の「中間」版と一致＝明るさ差0.0で実測）
  → build_site.py の USE_PHOTO_OVERRIDES=False（二重管理を解消・デザイン側の写真が正）。加工を変えたいときはデザイン側へ渡し直す
  ★地図（白黒）の差し込みは引き続き build_site.py 側（デザインの仮置きがまだ残っている）
  ★Vercel の初回デプロイが "error" で2回目に通る、が4回目。1回で諦めない
- **✅9/30 協力企業ロゴ（有璽氏）＝PR TIMES・オレンジワークス**。公開元 `~/kodomo-station-demo-v15/`
  ★PR TIMES 非営利サポートの募集要項に「団体HP等にPR TIMESのロゴを掲載すること」＝掲載は条件
  PR TIMES ロゴ＝NPOフォルダ `南河内こどもステーション_PRTIMES/PRTIMES_logo_fix_CMYK.ai`（中身PDF）を透過PNG化・正式RGB(41,76,122)
    ★同フォルダの「PRTIMESロゴ.png/バナー.png」はNPO自身のロゴとバナー（PR TIMESのロゴではない）
  リンク先＝NPOのPR TIMESページ https://prtimes.jp/main/html/searchrlp/company_id/184772（題名で本人確認済み）
  オレンジワークス＝公式サイトの OW_logo.svg、リンク https://orange-works.co/
  置き場所＝トップのフッター「後援・協力団体」（★この欄はトップにしか無い）と join の「ご支援いただいている企業・団体」の先頭2枠
  build_site.py の PARTNERS で毎回差し込む。素材は ~/kodomo-photo-work/partners/
  ★撮影時は data-reveal のふわっと表示で薄く写る→確認用コピーだけ動きを止めて撮る（公開版は触らない）
- **✅9/30 ILIFE追加（有璽氏「ILIFEのロゴが望ましい」）**＝公式サイト i-life-fukushi.com のヘッダーと同一の logo-ilife.png。
  トップのフッター3枠が埋まった（PR TIMES・オレンジワークス・ILIFE）／join は6枠中3
- **✅9/30 フッターのSNSボタンを各サービスの色に（有璽氏「通常通りの色で一度。派手なら変更」）**。公開元 `~/kodomo-station-demo-v17/`
  LINE=#06C755／Instagram=公式グラデーション／ブログ=サイト主色コーラル#EF856D（サービス未確定のため）。文字は白。
  SNS欄があるのは13ページ（404・festival-lp・sitemap・sp-check・styleguide には無い）。build_site.py の SNS_COLORS
  ★「派手なら変更」＝有璽氏の確認待ち。候補：淡くする／枠線だけ色／アイコンだけ色
- 要差替12項目は README「未確定・要差替 一覧」が正本

関連：[[reference_vercel_free_plan_protection]]
