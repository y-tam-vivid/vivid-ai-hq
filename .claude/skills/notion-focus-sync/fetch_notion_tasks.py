#!/usr/bin/env python3
"""Notion ✅ビビッドタスク管理DB → Obsidian 02_Current_Focus.md の差分を出す（★読むだけ）。

書き込みは一切しない（Notion へも Obsidian へも）。仕様は同じフォルダの SKILL.md。

  python3 fetch_notion_tasks.py            # 🔥 次のアクション だけ
  python3 fetch_notion_tasks.py --open     # 未完了すべて（✅ 完了・🗄 アーカイブ 以外）
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

DATA_SOURCE_ID = "62c7fadf-3fb1-409d-bc90-238fdce29b0f"  # ★データソースID（DBのIDとは別物）
NOTION_VERSION = "2025-09-03"
OWNER = "有璽氏個人"
FIRE = "🔥 次のアクション"
CLOSED = ("✅ 完了", "🗄 アーカイブ")
CONFIG = Path.home() / ".vivid-relay" / "config.env"
FOCUS = Path.home() / "Documents" / "Core_Brain" / "00_System" / "02_Current_Focus.md"

MARKER = re.compile(r"<!--\s*n:([0-9a-f]+)\s*-->")
TASK_LINE = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$")


def load_token():
    token = os.environ.get("NOTION_TOKEN")
    if token:
        return token
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.startswith("NOTION_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"NOTION_TOKEN が見つからない（{CONFIG}）")


def query(token, status_filter):
    url = f"https://api.notion.com/v1/data_sources/{DATA_SOURCE_ID}/query"
    body = {"filter": {"and": [{"property": "オーナー区分", "select": {"equals": OWNER}}] + status_filter},
            "page_size": 100}
    pages = []
    while True:
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers={
            "Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.load(res)
        pages += data["results"]
        if not data.get("has_more"):
            return pages
        body["start_cursor"] = data["next_cursor"]


def title_of(page):
    return "".join(t["plain_text"] for t in page["properties"]["Name"]["title"]).strip()


def norm(text):
    return re.sub(r"\s+", "", MARKER.sub("", text)).lower()


def read_focus():
    """Current_Focus のタスク行を (目印ID or None, 文言) で返す。"""
    if not FOCUS.exists():
        return []
    rows = []
    for line in FOCUS.read_text(encoding="utf-8").splitlines():
        m = TASK_LINE.match(line)
        if m:
            mk = MARKER.search(m.group(2))
            rows.append((mk.group(1) if mk else None, m.group(2)))
    return rows


def main():
    open_all = "--open" in sys.argv[1:]
    if open_all:
        status_filter = [{"property": "Status", "select": {"does_not_equal": s}} for s in CLOSED]
        label = "未完了すべて（✅ 完了・🗄 アーカイブ 以外）"
    else:
        status_filter = [{"property": "Status", "select": {"equals": FIRE}}]
        label = FIRE

    pages = query(load_token(), status_filter)
    focus = read_focus()
    ids = {i for i, _ in focus if i}
    titles = {norm(t) for _, t in focus}

    missing = []
    for p in pages:
        pid = p["id"].replace("-", "")
        if any(pid.startswith(i) for i in ids) or norm(title_of(p)) in titles:
            continue
        missing.append(p)

    print("【ドライラン・書き込みなし】")
    print(f"対象      オーナー区分={OWNER} ／ Status={label}")
    print(f"Notion    {len(pages)}件")
    print(f"Obsidian  タスク行 {len(focus)}件（目印あり {len(ids)}件）")
    print(f"★Notionにあって Obsidianに無い  {len(missing)}件")
    for p in missing:
        st = (p["properties"]["Status"]["select"] or {}).get("name", "（空）")
        due = (p["properties"]["Due Date"]["date"] or {}).get("start", "")
        print(f"  - [ ] {title_of(p)}  [{st}{' / ' + due if due else ''}]  <!-- n:{p['id'].replace('-', '')[:8]} -->")


if __name__ == "__main__":
    main()
