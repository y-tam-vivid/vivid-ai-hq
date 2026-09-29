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
- 要差替12項目は README「未確定・要差替 一覧」が正本

関連：[[reference_vercel_free_plan_protection]]
