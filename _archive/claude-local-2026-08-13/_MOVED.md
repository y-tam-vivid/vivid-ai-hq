# ⛔ core/ はここではなくなりました（2026-08-13）

正本は `~/vivid-ai-hq/.claude/skills/fukuchi-core/SKILL.md` です。
`00-共通.md` ＋ `10-法人.md` は統合済み（見出し差ゼロ・本文差12行で突合の上）。
`11-営業部門.md` → `skills/fukuchi-sales/`、`20-個人.md` → `skills/fukuchi-personal/`。

旧実物は `~/.claude-backup-2026-08-13/core/` に退避してあります（削除していません）。
`sync-agents.sh` は不要になりました（テキストを複製せず、frontmatter の
`skills: [fukuchi-core]` で参照するため配布先リスト自体が存在しません）。

`~/.claude/{agents,skills,output-styles}` と memory は `~/vivid-ai-hq` への symlink です。
**ここを編集しないでください。** 編集先は `~/vivid-ai-hq/` で、変更後は `./check.sh` を通します。
経緯は `~/vivid-ai-hq/PLAN.md`、置き場所の地図は `README.md` にあります。
