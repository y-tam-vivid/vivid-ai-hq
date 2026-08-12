---
name: reference_gviz_large_sheet_access
description: 大きなGoogleスプレッドシートはgvizエンドポイントをページ内fetchで列指定取得する（ブラウザ自動化下はダウンロード不可）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 72d12c17-4bf6-4c52-9291-4421d31f8dab
  modified: 2026-08-01T15:38:48.631Z
---

数MB級のGoogleスプレッドシートをClaude Codeで扱うときの成立経路。**ブラウザ自動化(claude-in-chrome)下では`export?format=csv`へのナビゲーションは成功扱いになるがファイルが生成されない**＝ダウンロードは使えない。localhostへのfetchもChromeのPrivate Network Accessで遮断される（`Access-Control-Allow-Private-Network`を付けても通らなかった）。

成立するのは**同一オリジンのページ内fetchでgvizエンドポイントを叩く**方法。

```
/spreadsheets/d/<ID>/gviz/tq?tqx=out:csv&sheet=<シート名>&tq=select B,D,G
```
- `credentials:'same-origin'` で認証を通る
- `tq=select` で列を絞れるのでデータ量を抑えられる（4MBのシートでも必要3列なら数百KB）
- `sheet=<名前>` でタブ指定可。`/gviz/tq?...` を直接ナビゲートするとeditへリダイレクトされるので**必ずページ内fetchで叩く**
- ページ遷移直後に実行すると `Failed to fetch`。読み込み完了を待つ
- ファイルごとに列レイアウトが違うことがある。**必ず `tq=limit 1` でヘッダーを確認してから列を選ぶ**（法人単位と事業所単位でB/D/Gの中身が別物だった）

集計もページ内JSで完結させ、返すのは統計値とサンプルだけにする（全データを会話に載せない）。

## gvizは黙って間違った値を返す（2026-08-01/02 実地・2件）

**gvizはエラーを出さずに嘘をつく。返り値の妥当性を毎回自分で検算すること。**

1. **シート名が一致しないと1枚目のシートを返す**（エラーにならない）。全角/半角の括弧違いで別シートを読んでいた。ヘッダーが期待どおりか必ず確認する。
2. **型推定でテキスト格納の数値状文字列を `null` にする**。法人番号列（書式`@`）で有効値50件のうち25件が空として返り、集計を誤った。ヘッダー文字列まで消えるのが兆候。

数値状の文字列（法人番号・電話番号・郵便番号）を読むときはgvizを使わず、**型推定の入らない `export?format=csv&gid=<gid>` を同一オリジンのページ内fetchで叩く**。ナビゲーションではなくfetchなら成立する（ダウンロード不可の制約は回避できる）。

gidの取り方: シートタブ `.docs-sheet-tab` に `pointerdown/mousedown/pointerup/mouseup/click` を順に dispatch（単純な `.click()` では切り替わらない）→ 1.5〜2秒待って `location.hash` から読む。

関連: [[reference_kintone_subtable_rows]]

関連: [[project_toc_customer_ledger]] [[reference_kintone_customer_master]]
