---
name: project-legal-agent
description: ふくち。グループのCLO(法務・渉外)センゴク:サブエージェント(~/.claude/agents/legal.md)+ Claude for Legal プラグイン二層 + Notion法務ハブ(構築済み)
metadata: 
  node_type: memory
  type: project
  originSessionId: e07600ab-dba4-46aa-a867-a1bf5fb4ba44
---

ふくち。グループのCLO(最高法務責任者)=**センゴク**(元海軍元帥センゴク由来)。2026-07-08 本体構築。命名は [[project-agent-naming]]、標準手順は [[project-cxo-build-playbook]]。

# 構成:プラグイン(エンジン)＋センゴク(日本仕様ラッパー)の二層
- **サブエージェント**: `~/.claude/agents/legal.md`(name=`legal`、model=sonnet)。契約リーガルチェック/危険・欠落条項の指摘/レッドライン案/日本法コンプラ/更新期日管理。応答は日本語、一人称「センゴク」。
- **レビューエンジン**: Anthropic の **Claude for Legal**(実在・2026-05ローンチ・GitHub `anthropics/claude-for-legal`・Apache 2.0)のプラグインを使う。採用3種=`commercial-legal`(NDA/業務委託/利用規約/更新)/`privacy-legal`(個情・DPA)/`corporate-legal`(資本・M&A・法人)。
  - 導入(ユーザーがスラッシュコマンドで実行、Claude Codeからは`/plugin`実行不可): `/plugin marketplace add anthropics/claude-for-legal` → `/plugin install <name>@claude-for-legal` → 再起動 → `/<plugin>:cold-start-interview`(自社の型を教え込む=最重要)。
  - 主要スキル例: `/commercial-legal:review`、`/commercial-legal:amendment-history`、`/commercial-legal:escalation-flagger`、定期エージェント `renewal-watcher`。

# 重要な制約・立て付け
- **日本法は非対応**: プラグインは米国法・英語前提(litigation=U.S.、privacy=GDPR/EU AI Act)。日本法モジュールは無い。→ cold-start と センゴク本文の「日本法観点(下請法・独禁法・個情法・電帳法・印紙/電子契約 等)」で上書き補強する。日本の契約は特に人の弁護士レビュー必須。
- **A案の立て付け**: センゴクは指摘・分析・レッドライン案まで。締結・署名・送付・最終判断は人。これは法的助言ではない(弁護士業務の代替でない)。
- 出力導線: レビュー結果→Notion法務ハブ→ビビ集約報告→要対応は人/顧問弁護士。赤入れの最終編集は人が Claude for Word 等で。

# Notion法務ハブ「⚖️ センゴク丨CLO 法務室」(2026-07-08 構築済み・トップレベル配置=ナミ財務室と同階層)
- 親ページ: `3977b156-8b57-8197-a740-ca5480f7caac`(https://app.notion.com/p/3977b1568b578197a740ca5480f7caac)
- **契約レビューDB**: data source `collection://21b02c77-6e1c-47ac-85df-9223bbfb4eb2`(列: 契約名/相手方/種別/準拠法/レビュー日/リスク判定[高中低]/要対応/ステータス/担当/備考)
- **期日管理DB**: data source `collection://498d4f2e-b8c4-4522-bbbc-8fbbd6a85a5d`(列: 契約名/相手方/種別/契約期間/自動更新/解約通知期限/次回アクション期日/対応状況/備考)
- **リーガルチェック結果レポート(置き場)**: page `3977b156-8b57-8151-a687-ce21013531ec`
- AI名鑑([[reference_ai_org_chart]])のセンゴク行(page `3957b156-8b57-81c7-acd2-dd6b982e6860`)を「予約→稼働中」に更新済み・全項目記入済み。

# 未整備タスク(次段)
- **Claude for Legal プラグイン導入はユーザーが未実行**(`/plugin marketplace add anthropics/claude-for-legal` → install commercial/privacy/corporate → cold-start-interview)。導入後にセンゴクの実力が出る。
- 定期見張り `renewal-watcher`(更新期日)を Notion期日管理DBと連携する routine 化は未着手。
- 対象文書スコープ: NDA・業務委託・利用規約 / 個人情報・プライバシー / 資本・M&A・法人管理 の3領域。
