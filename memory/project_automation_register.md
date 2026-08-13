---
name: project_automation_register
description: 自動処理が動いているかを心拍で検知するNotionレジスタ。沈黙を異常として扱う。2026-08-13新設
metadata:
  node_type: memory
  type: project
---

**⚙️ 自動処理レジスタ（心拍）** — 「自動で動くはずのものが実は動いていない」を検知する。2026-08-13 新設。

- DB: page `b4e9609d99d14626a71226c84f9c6d76` / ds `collection://c293de85-cf59-4165-9f8f-ab06174d8123`（親＝ビビッド業務管理）
- ビュー **🔴 要対応** ＝ 止まっている・一度も動いていないものだけ
- 共通部品 `~/.vivid-relay/heartbeat.py`（両機に配布済み・Python3.9互換）
  - `beat("処理名", "成功|失敗|警告", "メッセージ")` ／ シェルからも `heartbeat.py "処理名" 成功 "..."`
  - **心拍の失敗で本体を落とさない**（例外を握りつぶす）／**レジスタに無い処理名では行を作らない**（勝手に増やさない）

**設計の肝：沈黙を異常として扱う。** 成功でも失敗でも心拍を書き、来なければ🚦が🔴。**設置し忘れたものは一度も心拍を打たないので初日から🔴**＝「実装した」という申告と実態の乖離が構造的に見える。心拍を書く処理自体が失敗しても🔴＝安全側に倒れる。

**判断は「最後にいつ動いたか」＋「次はいつ動くはずか」の両方で行う。** 期待間隔を文章でなく **`期待間隔(時間)` の数値**で持つのはこのため（日次=24／週次=168）。片方だけだと両方向に間違える（→ [[feedback_sales_workbook_hands_off]] の誤報事例）。

**心拍の接続状況（2026-08-13時点）**

| 済 | `notion_meeting_customer_link.py` ／ `chatwork_relay.py` ／ `~/bin/sort_downloads.py` |
|---|---|
| 未 | GAS 4本（議事録GAS・週次バックアップ・週次スナップショット・カレンダーテンプレ）＝**要承認**（バックアップ→diff→承認→実行） |
| 未 | クラウドroutine 3本（ビビ朝・ロビン会議準備・ビビ週次）＝プロンプト改修・**要承認** |
| 未 | ビビ朝ブリーフィングへの🔴集約（既存の締切ダッシュボード導線に1系統足す。**新規cronは作らない**） |

**ブロッカー**：Notionインテグレーション「Chatworkリレー」を **3DB**（🏢顧客DB `0b5455629ea6487e8dee218599587e89` ／ 🔒個人議事録DB `3026fc88c17b4420974156638eea4830` ／ ⚙️レジスタ `b4e9609d99d14626a71226c84f9c6d76`）へ「⋯→接続」する田村さんの操作。未実施だと全部 `object_not_found`。

関連 [[reference_dangerous_entrypoints]] [[reference_mac_mini_execution_env]] [[project_meeting_customer_relation_linker]] [[feedback_sales_workbook_hands_off]]
