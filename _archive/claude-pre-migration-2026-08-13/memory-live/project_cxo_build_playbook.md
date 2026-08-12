---
name: project-cxo-build-playbook
description: CXO/秘書AIエージェントを1体作るときの再現手順(ビビ・ナミで確立したパターン)。別タブ・別セッションでも同じ構成で作るための手順書。
metadata: 
  node_type: memory
  type: project
  originSessionId: 91717c3b-21ec-44e9-a0c9-fabfd6b8a69e
  modified: 2026-07-21T04:23:14.513Z
---

ふくち。グループのAIエージェント(命名は [[project-agent-naming]])を1体作るときの標準手順。ビビ([[project-secretary-agent]])とナミ([[project-cfo-agent]])で確立したパターン。並行して別タブで作る場合もこの手順に揃える。

# 標準構成(3部品)
1. **呼び出し型サブエージェント**: `~/.claude/agents/<role>.md`(name はロール名)。frontmatter に name/description/model: sonnet。本文に「あなたは誰か(ONE PIECEキャラ由来・人物像・口調・一人称・応答は日本語)」「担当業務(優先度順)」「データの置き場所(Notion等のID)」「行動原則(外部影響/取り消しにくい操作は事前承認、機密厳守)」「出力スタイル(結論→詳細)」。**【必須】本文末尾に「行動規範（Fable Style・全エージェント標準）」節を必ず埋め込む**(結論先行/即行動/進捗の実証=捏造禁止/スコープ規律/境界/ターン終了規律)。既存9体と同一文面で揃える。出力スタイルはサブエージェントに自動継承されないため、埋め込みが唯一の担保。あわせて「モデル運用（Sonnet標準/Opus難所は提案/Fable封印=指名時のみ/過剰はダウングレード進言）」節も必須。さらに**「Notion運用ルール（読み書き前に必ず参照）」節も必須**（4層モデル＋鮮度ヘッダー／正本＝【正本】Notion運用ルール `3a37b1568b5781ac84e9fed2a3c0e944`。[[project_notion_operating_rules]]）。**旧「Notion整理ルール」節（旧ガイドライン `39d7b156…` を指すもの）は2026-07-21に全廃。複製しないこと**——ここを古いまま使うと廃止ルールが新エージェントごとに復活する。詳細は [[feedback_model_usage_rule]] とNotion「🤖 Claude運用ルール（モデル使い分け）」。
2. **Notionハブ**(必要な役割のみ): 親ページ + 業務DB + レポート置き場ページ。DBは notion-create-database(SQL DDL)で作成。作成したページ/DSのIDは必ず該当エージェントのメモリに記録。
3. **定期実行(cloud routine)**: RemoteTrigger(要 `ToolSearch select:RemoteTrigger`)。schedule スキル経由でも可。プロンプトは自己完結(キャラ設定+手順+参照ID+出力先)で書く。

# 固定パラメータ(これまでの実績値)
- cloud environment_id: `env_019JEywc7vB9TF9FA8cpuZAo`(Default)
- model: `claude-sonnet-5`
- 接続コネクタ(必要なものだけ mcp_connections に): Gmail `ef49629b-e193-405e-9595-b2f83d2f4912` / Google-Calendar `eaa9651b-e3e5-43dd-aa04-05f0b7ea31d8` / Slack `9b80c3b5-421f-490d-bb82-9dc377d3c577` / Notion `c2b5ccb1-1510-4d74-a7e2-c696e8ef802e`
- events[].data.uuid は毎回新規の小文字UUID(`uuidgen | tr '[:upper:]' '[:lower:]'`)。

# 時刻・cronの注意(JST→UTC)
- cronはUTC。最小間隔1時間。JST=UTC+9。
- 日付/曜日をずらしたくない定期実行は **9:00 JST 以降**にすると同日UTCに収まる:毎日=`0 23 * * *`は8:00JST(前日UTC)、毎月1日9:00JST=`0 0 1 * *`、毎週月曜9:00JST=`0 0 * * 1`。

# クラウド実行(CCR routine)の重要制約: 外部API遮断
cloud routine の実行環境はアウトバウンド通信がプロキシで制限され、**claude.ai公式MCPコネクタ(Gmail/Calendar/Slack/Notion/Drive等)以外の第三者APIへ直接アクセスできない**(2026-07-05検証: `api.chatwork.com` への CONNECT が 403 Forbidden で遮断)。
- 影響: Chatwork API、会計ソフト(freee/MF/弥生)API 等をクラウドの定期実行から直接叩くのは不可。
- 回避策: ①ローカルの Claude Code(ネットワーク可)で on-demand 実行、②ローカルの常駐リレー(Mac上の定期ジョブ)で外部API→Notionへ書き込み、クラウド側はNotionを読む、③クラウド環境のegress許可リストに対象ホストを追加(プラットフォーム設定が必要・当方ツールでは不可)。

# メモリ更新の作法
- エージェント1体ごとに project メモリを1ファイル作成し、MEMORY.md に1行追加。
- [[project-agent-naming]] の「確定済み」に追記し、残りマッピングから外す。

# 並行作業の衝突回避
- 別タブで**別のエージェント**を作る分には触るファイルが別(新 agent .md / 新 Notionページ / 新 routine)なので安全。
- ただし共有インデックス(MEMORY.md、project_agent_naming.md)は両タブが編集しうる。追記は最後にまとめて行うか、片方に寄せて衝突を避ける。
- 新タブは**そのマシンのホームディレクトリ**で開くと本メモリ群を自動読込できる（MacBook=`/Users/yujimac`／Mac mini=`/Users/yuji_macmini`）。別ディレクトリの場合は agent 定義(グローバル)は効くが、メモリは手動で参照が必要。
