#!/bin/bash
# 思考OSコア → 各エージェント定義へ同期
#
# 正本: ~/.claude/core/00-共通.md + 10-法人.md
# 反映先: ~/.claude/agents/*.md の <!-- CORE:BEGIN --> 〜 <!-- CORE:END --> の間
#
# 使い方:
#   ./sync-agents.sh          反映を実行
#   ./sync-agents.sh --check  差分があるかだけ確認(CI/版ズレ検知用・書き換えない)
#
# 注意: エージェント側のマーカー間は自動生成。手で編集しても次回同期で消える。

set -euo pipefail
CORE_DIR="$HOME/.claude/core"
AGENT_DIR="$HOME/.claude/agents"
CHECK_ONLY=false
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=true

# 対象エージェント（pr-playbook.md は参照用プレイブックのため対象外）
AGENTS=(app-developer cfo cko design dev-producer legal pr secretary system-developer web-developer)

python3 - "$CORE_DIR" "$AGENT_DIR" "$CHECK_ONLY" "${AGENTS[@]}" <<'PY'
import sys, io, os, re

core_dir, agent_dir, check_only = sys.argv[1], sys.argv[2], sys.argv[3] == "true"
agents = sys.argv[4:]

parts = []
for f in ("00-共通.md", "10-法人.md"):
    p = os.path.join(core_dir, f)
    if not os.path.exists(p):
        print(f"ERROR: 正本が見つかりません: {p}"); sys.exit(1)
    parts.append(io.open(p, encoding="utf-8").read().strip())

core = "\n\n".join(parts)
block = (
    "<!-- CORE:BEGIN 自動生成 ─ 手で編集しない。"
    "正本は ~/.claude/core/ を編集し sync-agents.sh を実行 -->\n\n"
    + core + "\n\n<!-- CORE:END -->\n"
)

# 行頭アンカー必須。正本の散文中にマーカー記法が現れても誤爆しないようにする
MARKERS = re.compile(r"^<!-- CORE:BEGIN.*?^<!-- CORE:END -->\n?", re.M | re.S)
# 初回移行用: 末尾の共通ブロック(「# モデル運用」以降)を丸ごと差し替える
LEGACY = re.compile(r"^# モデル運用.*\Z", re.M | re.S)

changed, ok, missing = [], [], []
for name in agents:
    path = os.path.join(agent_dir, f"{name}.md")
    if not os.path.exists(path):
        missing.append(name); continue
    src = io.open(path, encoding="utf-8").read()

    if MARKERS.search(src):
        new = MARKERS.sub(lambda _: block, src, count=1)
    elif LEGACY.search(src):
        new = LEGACY.sub(lambda _: block, src, count=1)   # 初回移行
    else:
        new = src.rstrip() + "\n\n" + block               # どちらも無ければ末尾に追加

    if new == src:
        ok.append(name)
    else:
        changed.append(name)
        if not check_only:
            io.open(path, "w", encoding="utf-8").write(new)

if missing:
    print("見つからないエージェント: " + ", ".join(missing))
if check_only:
    if changed:
        print("版ズレあり: " + ", ".join(changed))
        print(f"({len(ok)}体は最新)")
        sys.exit(1)
    print(f"全{len(ok)}体が正本と一致しています")
else:
    print(f"同期: 更新{len(changed)}体 / 変更なし{len(ok)}体")
    if changed:
        print("  更新 → " + ", ".join(changed))
PY
