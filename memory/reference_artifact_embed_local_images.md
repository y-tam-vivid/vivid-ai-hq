---
name: reference_artifact_embed_local_images
description: Artifactへ手元の画像を入れるにはdata URIで焼き込む。assets機能はこの環境で使えない
metadata:
  type: reference
---

**Artifact に手元の写真・チラシを入れる手順（2026-08-21 実地）。**

```
使えないもの   Artifact の assets 機能（upload_asset）。この環境で使える capability は
              artifact / downloads / mcp / self の4つだけで、assets は含まれない
使えないもの   外部URLの画像。CSPで全部ブロックされる（Google Fontsだけが例外）
使うもの       ★縮小して data URI（base64）で本文へ焼き込む。ページ全体で16MBまで
```

**手順**

1. HTML側に差し込み口を置く（`<img src="__P_MAIN__">` のようなトークン）
2. `sips -Z 1500 -s format jpeg -s formatOptions 66 元 --out 出力` で縮小
   （写真は長辺1500px・画質66／文字が多いチラシは1300px・画質72で読める）
3. 初回だけ差し込み口つきHTMLを `*.tpl.html` として退避し、python3でトークンを
   `data:image/jpeg;base64,...` へ置換して公開用HTMLを書き出す
4. **以後の本文修正は tpl 側を直してから焼き込み直す。** 焼き込み後のHTMLを直接編集しない
   （base64が数MB混ざっており、編集ツールで扱えない）

**実測** ── 元 3〜7MB の6枚（写真4・チラシ2）を縮小して合計約2.7MB、
data URI 化した最終HTMLは **3.45MB**。16MBには十分な余裕がある。

- **AIのセッションからは `sips` も base64 の書き出しも実行できない**（Bashの書き込みが拒否される）。
  スクリプトを scratchpad に置き、有璽氏に1行流してもらう形にする
  → [[feedback_verify_before_declining]]（人が1行貼れば済むならその1行を渡す）
- **人物が写る写真は公開許諾を先に確認する。** 顔が判別できるカットは、同意が取れているものだけ。
  取れていなければ後ろ姿・引きの構図へ差し替える。

## ★2026-09-08 「画像を入れる口は1種類」と思い込んで、ロゴだけ壊した

Claude Design の `.dc.html` を静的化して Artifact にしたとき、**ロゴ3箇所が壊れた**。
有璽氏「肝心の『かわちばなし』のロゴが切れてしまっているようです」。

```
処理したもの    <image-slot src="uploads/…png">   ★17枠すべて data URI 化した
処理し忘れ      <img src="uploads/…png">          ★ロゴ3箇所。通常のimgタグ
結果            Artifact は相対パスを解決できないので、その3箇所だけ画像が出ない
```

- **★同じ「画像」でも、ページの中では複数の書かれ方をしている。**
  独自タグ（image-slot）だけを見て「画像は全部処理した」と思うと、素の `<img>` が残る。
  **`src="相対パス"` を全部拾って、残り0件を数えるまでが完了。**
  実測の形： `残っている相対パスの src : 0 件` を出してから公開する。
- **★透明度のある画像を JPEG にすると背景が黒くなる。** 透明の有無で PNG/JPEG を分ける。
  今回のロゴは RGB（透明なし・四隅ほぼ白）だったので JPEG でよかったが、
  **確かめてから決めた**（`im.mode` と四隅の画素の2つを見た）。
- **★Claude Design 側の実体は無傷だった。壊れていたのは Artifact だけ。**
  症状を聞いたら、まずどちらの層の話かを切り分ける。→ [[feedback_read_the_artifact_not_the_copy]]
- 道具 → scratchpad `render_dc.py` ／ 経緯 [[project_kawachibanashi_portal]]
