---
name: reference_tool_access_map
description: 道具ごとの「鍵の在り処」と「能力の確かめ方」。★能力そのものは書かない（腐るから）。bin/capability_check.sh で毎回取りに行く
metadata:
  type: reference
---

**「何ができるか」を手で書かない。書いた瞬間から腐る。**
書くのは **①鍵がどこにあるか ②どう確かめるか** の2つだけ。この2つは腐りにくい。

```
1コマンドで現在の能力を出す
    ~/vivid-ai-hq/bin/capability_check.sh          要約
    ~/vivid-ai-hq/bin/capability_check.sh --full   SalesBreakerの全ルートを route 付きで
    ~/vivid-ai-hq/bin/capability_check.sh --md     共有用のMarkdownで
```

**人が見る共有版** → Notion 🧰「AIが使える道具と、その確かめ方」
`3c57b1568b57813fa4b5ff6feace093f`
★中身は `--md` の出力を貼る。**手で書かない**（書いた瞬間に腐る）

## 接続している道具（2026-08-23 `claude mcp list` 実測）

```
MCPで繋がっている   Google Drive / Gmail / Google Calendar / Notion / Slack
                    Gamma / Figma / Canva / Manus（ローカル bin/manus.py）
MCPではない         SalesBreaker（HTTP API・鍵は .env）
                    Google Sheets（サービスアカウント・mini）
                    Vercel（CLI）
繋がっていない      さくら（DNS・FTP）／kintone（CSV手動）／Claude in Chrome（拡張未接続）
```

## 道具の索引

| 道具 | 鍵の在り処 | 能力の確かめ方 |
|---|---|---|
| **SalesBreaker** | `~/Downloads/JapanGtmAgentWorkspace/.env` の `SALESBREAKER_API_KEY` | `GET /api/operator/v0/help/capabilities` ★**叩くと自分で全能力を答える** |
| Google（Sheets/Drive） | mini `~/.vivid-relay/google_service_account.json` ／ `google_token.json` | token の `scopes` を見る（2026-08-23時点は spreadsheets と drive のみ＝**Apps Scriptは実行できない**） |
| Vercel | `~/Library/Application Support/com.vercel.cli/auth.json` | `npx vercel whoami`（失効することがある。その時は有璽氏が `npx vercel login`） |
| Notion / Slack / Chatwork | `~/.vivid-relay/config.env` | キー名の有無を grep（値は読まない） |
| さくら（DNS・FTP） | **無い** | ゾーン編集APIも存在しない → [[reference_vivid_dns_sakura]] |
| Claude in Chrome | 拡張の接続 | `tabs_context_mcp` を1回叩く。未接続なら拡張が入っていない |

## ★SalesBreaker は専用のワークスペースが cwd にある

```
~/Downloads/JapanGtmAgentWorkspace/     「JAPAN GTM Agent Workspace powered by SalesBreaker」
  START_HERE.md      操作境界（read=承認不要／assist write=保存前に承認／送信=常に人）
  AGENTS.md          エージェント向けの作法
  docs/*.md          API仕様13本（リスト品質・CRM出力・権限・制限とエラー・実例…）
  .env               ★鍵はここ
  workspace-version.json  ★SalesBreakerのAPIキーページの最新版と突き合わせる（First Rule）
```

**この存在に気づかず「できない」と3回答えた** → [[feedback_read_the_workspace_first]]

## 更新の作法

- **能力が変わったと感じたら、書き換えるのではなく叩き直す。** 台帳は「確かめ方」だけを持つ
- **鍵の置き場が変わったときだけ、この表を直す**
- 新しい道具を足したら**この表に1行**。能力は書かない
- SalesBreaker はワークスペースZIPが更新される。`workspace-version.json` を先に照合する

## ★踏んだ罠（2026-08-23）

`help/capabilities` の `availability` は **`enabled` だけではない**。
`enabled_turn75_validation_route` `enabled_turn82` のように **turnと状態が付く**。

```
✗ availability == 'enabled'          → 4/35 しか使えないと誤判定した
✓ availability.startswith('enabled') → 実際は35個すべて使える
```

**`validation` が付くものは「検証だけ実行され、本番の動作はしない」**（例：`campaign.execute` は
`enabled_turn29_validation_enqueue_only`＝キューには入るが送信されない）。
**送信そのものは常に無効**（"Worker execution and sending remain disabled"）。

**自分の集計コードのせいで「できない」と言いかけた。** フィルタの条件は、値の実物を見てから書く。
