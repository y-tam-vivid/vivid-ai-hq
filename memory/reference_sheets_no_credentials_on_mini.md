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

## ⛔2026-09-05 訂正 ── 解消したのはサービスアカウントではなく「有璽氏本人のOAuth」

**上の「解消の道」は実際に採られた形と違う。** 実測（2026-09-05・mini）：

```
経路1  sheets_client の KEY_PATH（google_service_account.json）  → ★存在しない
       TOKEN_PATH（google_token.json）                          → 存在する
経路2  drive.about().get(fields='user')                          → y_tam@vivid-global.com
→ 一致。★いま動いている認証は 有璽氏本人のOAuthトークン
```

**ここから2つ、実務が変わる。**

- **★AIが作ったファイルは「共有」しなくても有璽氏が見える。**所有者が本人だから。
  「サービスアカウントが作ったので共有が要る」という前提で手順を組むと、要らない工程が増える。
  ただし**置き場が共有ドライブなら権限はドライブから継承される**ので、確認は
  `drive.permissions().list()` で読み返す（2026-09-05 実測：有璽氏 role=organizer）。
- **★共有ドライブ上のファイルは `supportsAllDrives=True` が無いと Drive API が 404 を返す。**
  Sheets API では読めるので「共有されていない」と誤診しやすい。**404 を「無い」の証拠にしない。**

**★Skill `sheets-access` の「鍵の扱い」節はこの訂正を反映していない**
（`~/.vivid-relay/google_service_account.json` を実体と書いている）。
`.claude/skills/` 配下はAIから書けないため、修正は人の手が要る
→ [[reference_permissions_are_part_of_the_environment]]

関連 [[reference_mac_mini_execution_env]] [[project_automation_register]] [[project_sales_workbook_read_first]] [[feedback_read_the_artifact_not_the_copy]]
