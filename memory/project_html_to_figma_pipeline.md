---
name: project_html_to_figma_pipeline
description: bundler形式HTML(福地/スタンドアップ/プライバシーポリシー等)をFigmaへ数値化移行する定型手順
metadata: 
  node_type: memory
  type: project
  originSessionId: f556b359-cad5-412d-83e0-550760bb5e0e
---

配布用HTML（Claudeデザイン書き出しの"bundler"自己完結形式）をFigma編集可能デザインへ変換する繰り返しワークフロー。福地サイト・スタンドアップ・プライバシーポリシーを同形式で変換済み。

**bundler形式の構造**: `<script type="__bundler/manifest">`(フォントbase64・十数MB)＋`__bundler/template`(JSONエスケープされた実HTML文字列)。実デザインCSS/markupは全体の数%のみ。JSで展開するためFigma/プラグインは生ファイルを読めない。

**変換手順**:
1. templateをJSON.loadsでデコード→styleブロック分離。巨大な@font-faceブロック(block0)を捨て、Google Fonts `<link>`に置換＝クリーンHTML(数十KB)。
2. **数値化(1440px基準がユーザー既定)**: clamp/vw/max/ch/%を固定px化。`--pad`=max(24,4vw)=58、標準コンテナ内容幅=1280−116=1164、doc本文=コンテナ1100→grid 240/664(gap80)。アニメ/hover/sticky/メディアクエリ/装飾gradientは除去(「余計なパーツを含まない」)。
3. **Figma移行=Figma MCPで直接構築**(ユーザー既定)。create_new_file→カラー変数コレクション(トークン)→縦オートレイアウトのルート1440→topbar/header/hero/doc(TOC+本文)/footerを順にappendで段階構築。フォントはNoto Sans JP/Noto Serif JP/Inter。

**Figma構築の要注意点**: 固定幅セルは`resize(w,10)`後に必ず`layoutSizingVertical='HUG'`へ戻す(戻さないと高さ10pxでテキストがクリップされ非表示になる)。オートレイアウトに個別marginは無い→入れ子フレームのpaddingで間隔制御。見出しの燈色番号・太字は`setRangeFills`/`setRangeFontName`。

プライバシーポリシー成果物: Figma `MGttpWhvmLKuBLDumvBGPR`、クリーンHTML `~/Downloads/プライバシーポリシー_clean.html`。関連: [[reference_notion_knowledge_hub]] の事業×法人体系。
