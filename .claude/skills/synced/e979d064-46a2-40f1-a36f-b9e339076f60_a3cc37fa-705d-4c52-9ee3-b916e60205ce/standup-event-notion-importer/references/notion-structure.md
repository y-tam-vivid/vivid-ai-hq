# Notion 構造リファレンス

イベント移行で使う3データベースの固定ID・全プロパティ・入力形式・MCP実務知見・文字化け辞書をまとめる。

## 目次
1. 固定リソースID
2. イベントDB スキーマ
3. 場所マスター スキーマ
4. 在庫DB スキーマ
5. Notion MCP 入力形式の注意
6. Google Drive 取得の注意
7. 文字化け修正辞書

---

## 1. 固定リソースID（ハードコード可）

| リソース | ID |
|---|---|
| 親カテゴリページ「11_イベント企画・報告管理｜LIFE STAND UP」 | `3827b156-8b57-81fd-8f84-c2cec7a0fe3d` |
| **イベントDB** data_source_id | `28976f59-037a-4e02-a702-811cb624a9bf` |
| イベントDB データベースページ | `0cbcf694fea74d2983ccd396d1704fe2` |
| **場所マスター** data_source_id | `105b99ad-4695-4ed4-be09-04bf94ab8452` |
| **在庫DB** data_source_id | `ccfb7a31-d0c3-487c-bb77-51ae9f748b52` |
| Google Drive 親フォルダ「イベント企画・報告書」 | `1qdwNrKKE3Rkyjl5XywcXWKv_wH4CcV0Q` |

### Google Drive 年度シーズンフォルダID（既知）
増える可能性があるため、不明なシーズンは親フォルダを `search_files` で一覧して確認すること。

| シーズン | フォルダID |
|---|---|
| 2026 Spring | `14rZGfofPG1863dV_vzY0XWRDGewM_qkT` |
| 2025 winter | `11zvReT6ztOi2VrMsNs2uO5uWdMAObVxU` |
| 2025 Summer | `1LJSIKjJSb4q_UjXDZbrZN2EviIHe6IQW` |
| 2025 Spring | `1O3C-R5QWHEh3-45iXVpAN5ArJQpW9Pc_` |
| 2024 Winter | `1mzFuOEiolMuZ491m9PTsaFDeXvZZkiQr` |
| 2024 Summer | `1_oAB6wUyVyyC4ySf8nxMxNZmvH47EJ89` |
| 2024 Spring | `1b0AICUR7Xc7AxkHmHdDmwVkRrXtLlyhB` |
| 2023 Winter | `1CmtcNYWyionkmWC4ySGHnJsJLzDL9rgI` |
| 2023 Summer | `1bqwTMqGQwMNmgv-sSqRMHh_rsRZQy_yW` |
| 2023 Spring | `1gtTPLmZ_jpr0KBy9DzqHjSFQ42OwvL4O` |
| 2022 Winter | `1kyNUPaiJWylPKv40lkMewAYT4ZOdySaK` |
| 2022 Summer | `1PuMbnVNKroE2-lWXAJTxl3K8YH-jpCcr` |

---

## 2. イベントDB スキーマ

親に `{"data_source_id": "28976f59-037a-4e02-a702-811cb624a9bf"}` を指定して `notion-create-pages` で登録。

| プロパティ名 | 型 | 入力形式・備考 |
|---|---|---|
| イベント名 | title | 例: `Let's go to NIFREL!!（ニフレル）` 英日併記が既定 |
| 種別 | select | `施設内` / `外出` / `複数日` |
| ステータス | select | `企画中` / `準備中` / `実施済` / `報告済`（移行は原則「報告済」） |
| 実施日 | date | `date:実施日:start`, `date:実施日:end`(任意), `date:実施日:is_datetime`(0) |
| 予定人数 | number | 素のnumber。複数日は延べ予定人数 |
| 実績人数 | number | 素のnumber。複数日は延べ実績人数 |
| 担当者 | multi_select | JSON配列文字列。値候補: `上田`/`九里`/`Xavier`/`渡辺`/`松本`/`鈴木`/`吉川`（多くの回は記録上「九里・上田」が担当だが、担当者プロパティは省略しても可） |
| ねらい・効果目的 | rich_text | 「効果目的：○○休み利用の活性化」を末尾に付すのが定型 |
| 収支メモ | rich_text | kid's負担と会社負担を分離して記載（extraction-rules.md参照） |
| 訪問先 | relation → 場所マスター | DUAL（場所側「過去利用イベント」と同期）。値はページURLのJSON配列文字列 |
| 使用品目 | relation → 在庫DB | 移行段階では省略可 |
| 振り返り | rich_text | 報告書の「振り返りと今後に向けて」を要約 |
| 保護者向け抜粋 | rich_text | コンプライアンス禁止表現を避ける |
| 写真（顔スタンプ済） | files | 移行段階では空 |
| 試算表・報告書 | files | 移行段階では空 |
| イベントID | unique_id (PREFIX `EV`) | 自動採番。**振り直しは全完了後に一括** |
| 参加者（名前） | rich_text | 報告書の参加者名リスト。複数日で膨大な場合は省略可 |
| 参加者構成 | rich_text | 人数・男女・学年・スタッフ数。複数日は日別内訳 |

### ビュー
- 進行ボード（board, 種別でグループ）
- 年間カレンダー（calendar, 実施日）

---

## 3. 場所マスター スキーマ

親に `{"data_source_id": "105b99ad-4695-4ed4-be09-04bf94ab8452"}`。

| プロパティ名 | 型 | 備考 |
|---|---|---|
| 施設名 | title | 例: `NIFREL（ニフレル）` |
| エリア | select | `藤井寺`/`羽曳野`/`堺`/`東大阪`/`橿原`/`その他`（左記以外は「その他」） |
| 住所 | rich_text | |
| 電話 | phone | |
| アクセス・所要時間 | rich_text | 「STAND UPから車で約○分」 |
| 駐車場 | rich_text | |
| トイレ | rich_text | |
| 料金・減免 | rich_text | 手帳減免の有無 |
| 危険箇所・注意点 | rich_text | 施設名が推定の場合はその旨もここに明記 |
| 下見写真 | files | 移行段階では空 |
| 過去利用イベント | relation → イベントDB | イベント側「訪問先」と同期（DUAL）。イベント側で紐付ければ自動で埋まる |

---

## 4. 在庫DB スキーマ

`data_source_id`: `ccfb7a31-d0c3-487c-bb77-51ae9f748b52`。
移行段階では原則使わない（夏祭り等の物品は収支メモに記録）。使用品目リレーションを張る場合のみ照合する。

---

## 5. Notion MCP 入力形式の注意（落とし穴）

- **親は `data_source_id`**。`page_id` を指定するとデータベース配下に入らない。
- **日付**は必ず分解する: `date:実施日:start`（"2024-12-25"）, `date:実施日:end`（任意・複数日のみ）,
  `date:実施日:is_datetime`（0）。
- **リレーション値はページURLのJSON配列文字列**。page_id `3837b156-8b57-81bf-8036-e4977eefb647` なら
  `"[\"https://app.notion.com/p/3837b1568b5781bf8036e4977eefb647\"]"`（ハイフン無し32桁hexをURLに）。
- **multi_select** も JSON配列文字列（例: `"[\"上田\",\"九里\"]"`）。
- **数値**は素のJS number（文字列にしない）。
- **チェックボックス**は `"__YES__"` / `"__NO__"`。
- プロパティ名が `id` / `url` の場合のみ `userDefined:` プレフィックスが必要（本DBには該当なし）。
- **STATUS型はDDLでoptionを作れない** → 種別・ステータスは SELECT 型で設計済み。
- **ページ削除／ゴミ箱移動はこのMCPツール群では不可**。`notion-move-pages` は親変更のみ。重複処理は
  タイトルに `【重複・削除予定】` を付けてユーザーに手動削除を依頼する。
- レコード検索は `notion-search(data_source_url="collection://<id>", query=...)`。
  `notion-fetch` を data_source に対して使うとスキーマだけが返り、レコードは返らない。

---

## 6. Google Drive 取得の注意

- `read_file_content(fileId=...)` は動作する。`google_drive_fetch` は空を返すことがある。
  日常の主力は `search_files` の `contentSnippet`。
- `search_files` クエリ構文: `parentId = '<id>'`（`"X in parents"` ではない）。
  `and title contains 'report'` で報告書だけに絞れる。`excludeContentSnippets=true` で軽量一覧。
- 「report」表記ゆれ（report / report! / report！！ / report2）は `title contains 'report'` で概ね拾える。
- 巨大ファイル（40KB超）はスニペットがコンテキストを圧迫するので、`not title contains '<除外語>'` で
  一括取得から外し、個別に `read_file_content` する。

---

## 7. 文字化け修正辞書

出力時に頻出する変換アーティファクト。**書く時点で正しい字を使う**のが第一。崩れた場合は最後にまとめて
置換修正する。

| 誤（崩れ） | 正 |
|---|---|
| 畵 | 男 |
| 梣 | 梓 |
| 嵌 | 嵜 |
| 遙 | 遥 |
| 菉 | 莉 |
| 掛 / 掃(文脈次第) | 掃 |
| 邁 | 遽 |
| 阯倍野 | 阿倍野 |
| 驻車 | 駐車 |
| 昂食 / 昀食 | 昼食 |
| 隔(材料費の文脈) | 費 |
| 刓(kids分の文脈) | 分 |
| 甜い | 甘い |
| 送送 | 送り／送って(文脈次第) |
| 邁(急邁の文脈) | 遽（急遽） |

※ 子どもの氏名・地名は特に注意。固有名詞は报告書原文の字に合わせる。
