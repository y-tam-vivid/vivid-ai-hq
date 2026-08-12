---
name: project-ai-event-portal
description: ふくち。グループのイベント用AIアプリ集約ポータル（ランチャー）。Vercel公開予定の静的サイト。開発したAIアプリを順次ここに集約する
metadata:
  node_type: memory
  type: project
  originSessionId: 8ff59487-4ecb-48f7-8c3a-3a8bb8707068
  modified: 2026-07-20T09:37:29.309Z
---

イベント当日に来場者が使う、**AIアプリ集約ポータル(ランチャー)**。開発したアプリ群([[project-dev-agents]]のステラ企画9本＋[[project-irodori-app]])をここに集約していく。**URLは Vercel で公開予定**。2026-07-03 初版構築。

# ローカルのソース(Vercelにあげるファイル群)
`/Users/yujimac/fukuchi-ai-event/`（**MacBook側**。Mac mini には未移植＝miniからは触れない。移植したのは `~/.claude` 資産のみ。[[project_macmini_remote_workhorse]]）
```
index.html      ← ポータル(アプリ一覧)。公開URLのトップになる
iro/index.html  ← いろどり(美容診断アプリ本体) → /iro/ でアクセス
README.md       ← Vercelデプロイ手順
```
- **拡張方法**: アプリを足すときは `money/`, `animal/` のようにフォルダを作って `index.html` を置き、ポータルの該当カードを `soon` からリンク有効に変えるだけ。相対リンクで束ねる素朴な静的構成。
- 各アプリは外部依存なしの単一HTML(自己完結)。

# 現状の中身
- **本番公開済み(2026-07-04)**: Vercelチーム fuku-chi-vivid。トップURL **https://fukuchi-ai-event.vercel.app** 。QR画像 `~/fukuchi-ai-event/qr-portal.png`(会場掲示用)。再デプロイ `cd ~/fukuchi-ai-event && npx vercel@latest --prod --yes`。
- **公開(体験可)=15タイトル・準備中0(2026-07-05時点)**: いろどり(美容,注目枠,埋め込み ./iro/) / [[project-kids-event-apps]]の13本(おこづかい大冒険・お店やさんAI・ちょきんモンスター・お金のすごろく・おつかいクエスト・なりたい仕事しんだん・なぞなぞクイズマスター・なりきり診断・どうぶつへんしんカメラ・おえかき魔法・きおくカードめくり・ごみ分別チャレンジ・めいろ探検, 外部リンク https://fukuchi-kids-apps.vercel.app/<route>) / マネー診断(money-shindanapp.vercel.app)。全リンクHTTP200確認。
- 準備中(soon)カードは現在0。今後アプリが増えたら子どもアプリ側(kids-apps)を再デプロイ→ポータルindex.htmlにliveカード追記→ポータル再デプロイ、の順。
- 注意: 外部リンクのアプリは別ドメイン同一タブ遷移。会場でアプリ→ポータルに戻る導線は未整備(ブラウザ戻る頼み)。

# デザイン
- ふくち。グループのイベントブランド。温かみのあるクリーム地(#F7F4EF)＋テラコッタのアクセント(#C8542F)、カテゴリごとの色ドット。見出しは明朝。子供〜大人まで多様なターゲット向けに、親しみつつ上質。ライト/ダーク両対応。
- いろどり(クチュール・モード)とはレイヤーが別。ポータルは中立的な集約面。

# プレビュー
- 触れるプレビュー(Artifact, いろどりまで通しで体験可): https://claude.ai/code/artifact/5358d601-92f5-4db3-8d4f-1f867d4f224c
- ソース(Artプレビュー版): scratchpad `portal-preview.html`(いろどりリンクを既存Artifact URLに向けた版)。本番の `index.html` は相対リンク `./iro/`。

# Vercelデプロイ(READMEに詳細)
- 簡単: vercel.com ダッシュボードにフォルダをドラッグ&ドロップ、Framework=Other、ビルド不要。
- CLI: `cd fukuchi-ai-event && vercel --prod`。
- 公開後、トップURL / 各アプリURL(例 `/iro/`)をQR化してイベント掲示。独自ドメインはVercel Domainsで割当可。

# 未決 / 次
- イベント名・トップコピー(現状「AIたいけん」は仮)の確定。
- 各Coming Soonアプリの実装(順次)。
- いろどりの精度向上(顔検出・照明補正)はこの本番ホスティング上で実装予定([[project-irodori-app]])。
