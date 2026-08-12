# ふくち。グループ ─ AI共通設定

このリポジトリが全AIの正本。ターミナル（MacBook / Mac mini）・claude.ai/code・スマホの
どこから起動しても、同じ規範・同じ10体・同じ記憶が載る状態を保つ。

## 置き場所の索引

**どこに何があるかは `README.md` の1枚に集約してある。** 迷ったらそこへ戻る。
そこに載っていない場所へ設定ファイルを置かない。増やすときはまずあの表に行を足す。

## 読み込まれるもの

@.claude/skills/fukuchi-core/SKILL.md

@memory/MEMORY.md

## 編集のルール（これを破るとズレが再発する）

- **共通規範の本文は `.claude/skills/fukuchi-core/SKILL.md` にしか書かない。**
  エージェント定義・このファイル・出力スタイルへ本文を貼り直さない。参照だけを置く。
- エージェント定義（`.claude/agents/*.md`）には、そのエージェント固有の役割・データ置き場・
  口調だけを書く。共通規範は frontmatter の `skills: [fukuchi-core]` で自動注入される。
- 出力スタイル（`.claude/output-styles/fable-mode.md`）は口調のみ。組織ルールを持たせない。
- 変更したら `./check.sh` を通してから commit する。

## 構成

```
vivid-ai-hq/
├── CLAUDE.md                          このファイル（全cwd・全面で読まれる）
├── PLAN.md                            移行作業の正本（完了後はNotionへ降格）
├── check.sh                           規範の複製・ズレを検出
├── memory/                            ローカル記憶（MEMORY.md が索引）
└── .claude/
    ├── skills/fukuchi-core/SKILL.md   ★共通規範の唯一の正本
    ├── skills/{customer-db-sync,downloads-weekly-sweep,thinking-os}/
    ├── agents/                        10体 + pr-playbook.md（固有部分のみ）
    ├── output-styles/fable-mode.md    口調のみ
    └── settings.json                  outputStyle: Fable Style
```

MCPは claude.ai コネクタ（アカウント紐づけ）を使うため `.mcp.json` は置かない。
user-scope の MCP サーバーは 0 件であることを確認済み（2026-08-12）。
