---
name: reference-shared-wp-test-env-collision
description: LIFE STAND UP検証環境(_tools/wordpress)は複数セッションが同時に使う共用資源。CSS編集の反映確認で同期スクリプトを実行すると他セッションの計測を壊す恐れがある
metadata:
  type: reference
---

# ローカル検証WordPressは共用資源 ── 同期(activate_theme.php)を無条件に叩かない

**2026-09-13 チョッパー実地**。`theme/lifestandup/` を編集しても、`_tools/wordpress/
wp-content/themes/lifestandup/`（PHP内蔵サーバが実際に読む場所）は**別コピー**で、
`_tools/activate_theme.php` を実行しないと反映されない（★これ自体は既知：
「CSS編集後は`./php activate_theme.php`を再実行しないと反映されない」と複数の
過去セッションが踏んでいる）。

**★今回新たに踏んだのはここから先。** `activate_theme.php` の実装は
`rrmdir($dst); rcopy($src,$dst);`（配布先フォルダを**丸ごと削除してから再コピー**）。
このとき **別セッションが同じ `_tools/wordpress` をポート8750等で使って計測中だと、
削除〜再コピーの一瞬の間にそのセッションのHTTPリクエストが壊れたページを受け取る
リスクがある**。`tools/lsu_env.py` の `E.shoot()` は「撮れなければ例外で止まる」設計
（黙って古い画像を使わない）なので、直撃すれば相手の計測がその場でクラッシュしうる。

```
症状(今回)  sweep_widths.py が2プロセス、4時間以上CPU 0%・出力0件のまま停滞
            ★原因は未調査（このファイルは真因の記録ではない）。
            だが「動いている別プロセスと同じ検証環境を、無警告で丸ごと
            作り直す仕組みがある」という構造上のリスクは実在すると確認した
対処        activate_theme.php は実行せず、WordPressを経由しない
            ★孤立テストページ（file://＋iframe srcdoc）でCSSの効果だけを検証した
```

## ★孤立検証の作り方（再利用できる型）

WordPress・ポート8750/8761のどちらにも触れずにCSSの挙動だけを確かめたいとき：

```
1  検証用HTMLを1枚作る。<link>で theme/lifestandup/{style.css,assets/css/*.css}を
   相対パスで直接読み込み、検証したい要素のマークアップ断片だけを再現する
2  ★file://で直接開くと外側ウィンドウが500px未満にできない制約を受ける
   （tools/lsu_overflow.py が既に文書化した既知の制約と同じ）。
   → 検証用HTMLの中に<iframe>を1つ作り、幅をURLクエリ(?w=414)で指定し
     srcdocへ中身を流し込む。iframeの幅はouterウィンドウの500px制約を受けない
3  E.shoot()で"file://.../test.html?w=414&h=900"を撮る。size引数(outerウィンドウ)は
   500以上の固定値でよい（例: "1000,1100"）
4  iframe内にwindow.innerWidthを描画するタグを仕込んでおき、狙った幅どおりに
   描画されたかをスクリーンショット自体で裏取りする（decode()等の間接測定に頼らない）
```

★この型は「共用サーバに触れないが、CSSの計算結果だけ確かめたい」場面全般に使える。
WordPress側のPHPテンプレート依存のロジック（条件分岐・動的クラス付与等）は
再現できないので、**あくまでCSS/HTMLの静的な挙動の検証に限る**。

## 教訓
- **同時に走っている別プロセスの存在を知っていても、「触るファイルが違うから安全」と
  判断しない。** 触るファイルが同じディレクトリツリーであれば、間接的に共用資源。
- **「削除してから再コピー」という実装は、無人で叩くと一瞬の空白窓ができる。**
  他プロセスの利用有無を確認してから叩く（`ps aux | grep`等）。
- 関連 → [[project_web_build_rules_asset]] ／ [[reference_endpoints_pass_middle_breaks]]
  （既知：500px未満はiframe必須。今回チョッパーは同じ罠を3回踏んでから気づいた＝
  「知っている」と「毎回思い出して適用する」は別。着手時にこのファイルを先に読むこと）

## ★2026-09-14 再発（リリス）── 気づかずに`deploy.py`（同じ危険パターン）を2回実行した

有璽氏からの直接指示（recruit-interview「Kさん」表記＋5人目写真追加）に着手する際、
**着手の時点でチョッパー（responsive-engineer）が同じ `_tools/wordpress` を port 8750で
既に検証中だった**（run_agent.sh の指示文に「★リリスが同時にtheme/lifestandup/を
触っています。あなたは読むだけ」と書かれており、★逆方向＝リリス側にチョッパーの
存在を知らせる文言は無かった。片方にしか知らせていない設計だった）。

```
①  nohup ./php -S 127.0.0.1:8750 ...  → "Address already in use" で自然に失敗
    （ここでポート衝突には気づいたが、"deploy.py"がrrmdir+recopyする危険までは
    直後には気づかなかった）
②  python3 deploy.py を2回実行（LSU_VERSION編集の前後）
    → deploy.py も activate_theme.php と★同じ rrmdir/rmtree + copytree 実装
    （このファイルの既存の教訓は activate_theme.php にしか触れていなかったが、
    deploy.py は"配布"目的の別スクリプトで★同じ危険パターンを持つ、と今回判明）
③  チョッパー側のログ(/tmp/chopper_overlap_run.log)は0バイトのまま数分停滞していた
    （★因果関係は未確認。deploy.pyの実行前から既に停滞していた可能性もあり、
    「壊した証拠」ではなく「壊した疑いが晴れていない」というのが正直な状態）
```

★このファイルの「教訓」は `activate_theme.php` 限定で書かれていたため、
**「rrmdir+recopyする同型のスクリプトは他にも複数ある」ことまでは伝わっていなかった。**
`deploy.py`・`_tools/activate_theme.php` の少なくとも2本が同じ危険パターンを持つ。
**★対策は「特定のファイル名を避ける」ではなく「_tools/wordpress を書き換える操作
（ファイル名に関わらず）を、他セッションの使用有無を確かめずに実行しない」に一般化する。**

- **★オーケストレーター（ビビ）が並行担当を起こすとき、双方に「もう一方が何を触るか」を
  明示すること。** 片方向の注意書き（チョッパーへ「リリスが触っている」）だけでは、
  逆方向（リリスへ「チョッパーが読んでいる」）が伝わらず、今回と同じ事故を繰り返す。
- **`compare_demo_vs_wp.py --skip-sync` のように、危険な同期をスキップできる
  オプションが既にある場合は、着手前にまずそれを使う。** 同期は「最初に1回だけ」に
  留め、以降の確認作業は `--skip-sync` 相当で通す。
