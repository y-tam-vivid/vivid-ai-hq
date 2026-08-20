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
