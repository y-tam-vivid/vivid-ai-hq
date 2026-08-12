# vivid-ai-hq ─ AI設定の地図（置き場所と参照元）

**この1枚がAI設定ファイルの索引。** どこに何があり、誰がそれを読むかを、ここだけで確認できる。
迷ったらここへ戻る。ここに書いていない場所へファイルを置かない。

## 置き場所 × 参照元

| 何 | 置き場所（1箇所のみ） | 誰が読むか |
|---|---|---|
| 共通規範（判断軸・行動規範・モデル運用・Notion整理・作業ログ・ファイアウォール） | `.claude/skills/fukuchi-core/SKILL.md` | 10体すべて（frontmatter `skills:`）＋主セッション（CLAUDE.md の @import） |
| 営業部門の判断軸 | `.claude/skills/fukuchi-sales/SKILL.md` | 営業の作業時のみ。全体へ注入しない |
| 個人層の判断軸 | `.claude/skills/fukuchi-personal/SKILL.md` | 個人の作業時のみ。法人エージェントには載せない |
| 各エージェントの固有部分（役割・データ置き場・口調） | `.claude/agents/<name>.md` | そのエージェントのみ |
| 広報の研修プレイブック | `.claude/agents/pr-playbook.md` | モルガンズ（pr）が参照 |
| 口調・体裁 | `.claude/output-styles/fable-mode.md` | 主セッション（全cwd） |
| 規範の変更履歴 | `.claude/output-styles/CHANGELOG.md` | 人／改善ループ |
| 定型作業の手順（顧客DB同期・Downloads整理・思考OS） | `.claude/skills/<name>/SKILL.md` | 必要時に Skill として |
| 圧縮を越えて残す事実 | `memory/MEMORY.md`（索引）＋ `memory/*.md`（本体） | 毎セッション（索引行）／関連時（本体） |
| セッション設定 | `.claude/settings.json` | 全セッション |
| 移行作業の現在地 | `PLAN.md` | 作業者（人・AI） |
| 役目を終えたもの | `_archive/` | 誰も読まない（履歴として保存のみ） |

MCPは claude.ai コネクタ（アカウント紐づけ）を使うため `.mcp.json` は置かない。
user-scope の MCP サーバーは 0 件であることを確認済み（2026-08-12）。

## 3つの禁止

1. **共通規範の本文を、この表の「置き場所」以外へ書かない。** 参照だけを配る。
   貼り直した瞬間に二重管理になり、過去に実際8項目ズレた。
2. **版番号を並べない。** 現行は常に1本。役目を終えたら `_archive/YYYY-MM-DD-理由/` へ移す。
   `_v2` `_backup` `_old` `最新` `コピー` をファイル名に使わない（`check.sh` が検出する）。
3. **ここに載っていない場所へ設定ファイルを置かない。** 増やすときは、まずこの表に行を足す。

## 使い方

```
./check.sh     置き場所・参照元・複製・版の並存・索引の整合をまとめて検査
               commit 前と、セッション開始時に実行する
```

検査項目は7つ:
正本の存在／規範本文の複製／全エージェントの参照／memory索引の整合／
symlink の向き／リポジトリ外に取り残された `.md`／版の並存。

## 構成

```
vivid-ai-hq/
├── README.md      この地図
├── PLAN.md        移行作業の正本（完了後はNotionへ降格）
├── CLAUDE.md      全cwd・全面で読まれる。@import のみで本文を持たない
├── check.sh
├── memory/        MEMORY.md（索引）＋ 本体
├── _archive/      旧方式の実物。判断根拠にしない
└── .claude/
    ├── skills/    fukuchi-core ★正本 ／ fukuchi-sales ／ fukuchi-personal
    │              customer-db-sync ／ downloads-weekly-sweep ／ thinking-os
    ├── agents/    10体 ＋ pr-playbook.md
    ├── output-styles/
    └── settings.json
```
