---
name: reference_plaintext_credentials_handling
description: 平文の認証情報ファイルを見つけたときの扱い。中身は読まない・削除はパス指定で1件だけ・破棄のたびに横断調査をセットで行う
metadata:
  node_type: memory
  type: reference
---

**機微（トークン・鍵・認証情報）を扱うときの型。** 2026-08-20 につるが指摘し、
2026-08-22 に有璽氏承認で破棄した `_要確認_slackトークン断片_20260818.txt`（mini側）を
題材に確立。

## 型

```
① 中身は絶対に読まない       cat/head/grep -A等で内容を開かない。
                            場所・作成日時・サイズ・パーミッションだけで扱う
② 破棄は「パス指定・1件だけ」  ワイルドカード禁止。誤って隣接ファイルを巻き込まない
③ 1件消して終わりにしない     ★同じ経路で他に漏れていないかを毎回セットで横断調査する
④ 権限が緩い認証情報ファイルは消さない  正規に使っているかどうかは中身を読まないと
                                     判断できない。「絞るべき」と報告するだけに留める
```

## 実測（2026-08-22・mini側とMacBook側の横断調査）

対象4箇所（両機）: `~/.vivid-relay/` `~/vivid-ai-hq/` `~/bin/` `~/Downloads`
名前で拾う（token/secret/credential/key/.env/要確認/password/passwd）。中身は開かない。

| 見つかったもの | 権限 | 判定 |
|---|---|---|
| mini `.vivid-relay/config.env` | 600 | 正規使用・適正 |
| mini `.vivid-relay/config.env.bak_20260818` | 600 | 正規のバックアップ・適正 |
| mini `.vivid-relay/google_token.json` | 600 | 正規使用・適正 |
| MacBook `.vivid-relay/config.env` | 600 | 正規使用・適正 |
| 両機 `Downloads/JapanGtmAgentWorkspace/.env` | `rw-rw-r--@`（グループ書込可・他ユーザー読取可） | **権限が緩い。要 有璽氏判断**（中身未読・正規利用かも不明のため消していない） |
| vivid-ai-hq 内の `*secret*` 系ヒット | ― | **誤検出**。`secretary.md` のファイル名に `secret` が部分一致しているだけで、認証情報ファイルではない |

「`config.env　これは何処に貼る？`」（2026-08-19 にビビが mini で発見・37バイト・644）は
2026-08-22 時点で**存在しない**。すでに解消済みとみられる（誰が・いつ・どう処理したかは未確認）。

## 教訓

- **ファイル名検索だけでは誤検出が出る。** `secretary`→`secret` のような部分一致は
  人が最終判定する前提で見る（AIは「それらしい」までしか言えない）。
- **緩い権限の認証情報ファイルは、消すか締めるかを本人に判断してもらう。** 中身を読まずに
  「正規か不要か」を確定できないため、AI側で独断で締める・消すをしない。
- **破棄の承認は個別ファイル単位。** 横断調査で新たに見つかったものは、たとえ同種でも
  今回の承認の対象外として扱い、別途報告する。

関連 [[feedback_confidential_two_layer_rule]] [[reference_shared_drive_permission_floor]]
