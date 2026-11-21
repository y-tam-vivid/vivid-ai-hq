---
name: project_f119_public_site
description: 福祉施設の119番の公開サイト（119.fuku-chi.com）の直し方。正本は scratchpad/f119-site/build.py。public/ の HTML は生成物で、直接直すと次の build で消える
metadata:
  type: project
---

# 119番 公開サイトの作り方（2026-11-20 時点）

**正本は `scratchpad/f119-site/build.py`。`public/*.html` は build.py が書き出す生成物。**
- 直すのは build.py（ヘッダー・フッター・各ページ本文・/iryo・sitemap・llms.txt をここで1か所にまとめている）。
- `public/` の HTML だけを直すと、次に build.py を回した時点で消える。
- 出力先は `OUT = <build.py と同じ場所>/public`（build.py:4）。`/iryo` は `public/iryo/index.html`（build.py:596）。
- 全リンクのクリック名（`data-cta`）は `name_ctas()` が毎回付ける（build.py:94）。手で付けた名前も上書きされる。

**スイッチ**
- `PARTNERS_OPEN = False`（build.py:16）：解決パートナーは「準備中」表示。公開するときだけ True。
- 検索公開（noindex 解除・canonical・sitemap・OGP・構造化データ）は 2026-11-20 に有璽氏が承認して入った（commit 62a0281）。

**本番**
- Vercel の fukushi119-web は `scratchpad/f119-site/` を gitSource で出す（WORKING.md の記述・11/20）。
- 本番へ出すのは commit してからの反映。build.py の出力を commit に含めないと本番と食い違う。

**地雷（踏んだもの）**
- ロゴSVG（fullcolor）は色をクラスで指定していて、単独のファイルとして使うと外部CSSが届かず真っ黒になった（commit 7e48efb）。色は要素に直接の塗りで持たせる。
- フッターの文字サイズ 14→12px が効いていなかった（commit 8b6483e）。直した後は computed style で数字を見る。

**残りの作業と現在地は WORKING.md が正**（ここには書かない）。
