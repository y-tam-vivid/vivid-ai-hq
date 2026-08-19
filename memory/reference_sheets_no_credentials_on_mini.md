---
name: reference_sheets_no_credentials_on_mini
description: mini に Google 認証が無いため、スプレッドシートの作業をAIが実行できず毎回GASを人が貼っていた。サービスアカウント1つで解消する
metadata:
  node_type: memory
  type: reference
---

**「AIが作業を代われない」の正体は能力ではなく認証。** 2026-08-19 実測。

```
mini の実測結果
  gcloud                 無い
  ~/.config/gcloud       無い
  サービスアカウント鍵    無い
  googleapiclient        未インストール
  google-auth            未インストール
→ Sheets API を叩く手段がゼロ
→ だから GAS を Drive に置いて有璽氏が貼って実行する運用になっていた
```

**この構造のせいで、調査1回ごとに有璽氏の手が要る。** 有璽氏から「この作業すら私がやるべきなの？」と指摘が出た（2026-08-19）。**正当な指摘。**開発中は毎回スクリプトが変わるので、貼る回数が積み上がる。

## AIが今できること／できないこと

| | 手段 | 限界 |
|---|---|---|
| 読む | Drive MCP `read_file_content` | **各シート先頭88行まで**。806行の 00_企業マスタ は先頭87行しか出ない。**打ち切りに気づかず「無い」と断定する事故の源** |
| 読む | 結果ファイルを python で検索 | 上の88行の範囲内でのみ有効 |
| 書く | **手段なし** | Drive MCP の `update_file` はファイル本体の置換であってセル書き込みではない |

**教訓の再確認** ── 打ち切られた書き出しを根拠に「無い」と言わない（→ [[feedback_read_the_artifact_not_the_copy]]）。2026-08-19 も 00 の書き出しが B-0087 で切れており、B-0406 の実在は**08のB列（00を引く数式）に社名が出ていること**から逆算して確かめた。

## 解消の道

```
有璽氏がやること（初回1回だけ・AIは代行できない）
   ① Google Cloud でサービスアカウントを1つ作る
   ② JSON鍵をダウンロードして mini の ~/.vivid-relay/ へ置く
   ③ 対象ファイルをそのサービスアカウントのメールアドレスへ共有（編集者）
        営業案件管理ワークブック 1lcSexlRLHtV2zzBm0Te_KKmR2uzCawQLzkyY50nPoNY
        受付シート               1XCqGDG1kUMg6Mh0xUfWzudqvG_PyLcNpJNJKuszyJe0

以後
   AI が python から Sheets API を直接読み書きできる
   → 調査も移送も AI が実行する。GASを貼る運用が消える
   → cron に載る。⚙️自動処理レジスタの心拍も打てる
```

**ログイン・認証情報の入力は代行しない**規約があるため ①②はAI側で実施できない。**鍵が置かれた後の実装・設定・検証はすべてAI側で行う。**

関連 [[reference_mac_mini_execution_env]] [[project_automation_register]] [[project_sales_workbook_read_first]] [[feedback_read_the_artifact_not_the_copy]]
