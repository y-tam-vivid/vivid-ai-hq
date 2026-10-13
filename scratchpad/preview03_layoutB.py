# 03 の並べ方の見本を2枚作る（読むだけ。03本体・Notionには書かない）
import sys, os, re, json, urllib.request
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.expanduser("~/.vivid-relay"))
import notion_focus_sync as s
JST = timezone(timedelta(hours=9))
env = {}
for l in open(s.CONFIG_ENV):
    m = re.match(r"\s*(?:export\s+)?(\w+)=(.*)", l)
    if m: env[m.group(1)] = m.group(2).strip().strip("\"'")
H = {"Authorization": "Bearer " + env["NOTION_TOKEN"], "Notion-Version": "2025-09-03"}
lines = open(s.AI_PATH, encoding="utf-8").readlines()
tasks = s.parse_focus_file(lines, src="03")
for i, t in enumerate(tasks): t.order = i
today = s._today()
def created(t):
    if not t.marker: return None
    p = json.load(urllib.request.urlopen(urllib.request.Request(s.API_BASE + "/pages/" + t.marker, headers=H)))
    return datetime.fromisoformat(p["created_time"].replace("Z", "+00:00")).astimezone(JST).date()
PJ = re.compile(r"^【([^】]*)】")
def proj(t):
    m = PJ.match(t.title); return m.group(1) if m else "（案件名なし）"
def line(t, c):
    title = re.sub(r"\s*<!--.*?-->\s*", "", t.title)
    title = re.sub(r"\s*@\d{1,2}/\d{1,2}\b", "", title)
    title = re.sub(r"\s*#(全社|次|待機|急ぎ|今週|いつでも)\b", "", title).strip()
    d = f"{c.month}/{c.day}発行" if c else "発行日不明"
    m = PJ.match(title)
    body = f"【{m.group(1)}】{d}・{title[m.end():].lstrip()}" if m else f"{d}・{title}"
    parts = [f"- [{'x' if t.checked else ' '}] {body}"]
    if t.date_iso:
        dd = datetime.fromisoformat(t.date_iso); parts.append(f"@{dd.month}/{dd.day}")
    parts += [f"#{g}" for g in sorted(t.tags)]
    return " ".join(parts) + "\n"
C = {id(t): created(t) for t in tasks}
far = datetime(2100, 1, 1).date()
key_c = lambda t: C[id(t)] or far
NOTE = "> ★見本です（{0}）。本物の03・Notionは変えていません。目印を外してあるので、ここで [x] を付けても何も起きません。\n\n"
# 案A：5段のまま、段の中を【案件】名順→発行日順
outA = ["# 見本A：5段のまま・段の中を案件順\n\n", NOTE.format(datetime.now(JST).strftime("%m/%d %H:%M"))]
groups = {b: [] for b in s.BUCKETS}
for t in tasks: groups[s.bucket_of(t, today)].append(t)
for b in s.BUCKETS:
    outA.append(f"## {b}\n\n")
    for t in sorted(groups[b], key=lambda t: (t.checked, proj(t), key_c(t), t.order)): outA.append(line(t, C[id(t)]))
    outA.append("\n")
# 案B：案件ごとの見出し。済みは末尾の「済み」へ（全部済んだ案件は見出しごと消える）
outB = ["# 見本B：案件ごとの見出し\n\n", NOTE.format(datetime.now(JST).strftime("%m/%d %H:%M")),
        "> 案件の並び＝期日の近い行を持つ案件が上 → 次に新しく発行された案件が上。見出しは同期のたびに作り直すので、未完了が0になった案件は見出しごと消えます。\n\n"]
openp = {}
for t in tasks:
    if not t.checked: openp.setdefault(proj(t), []).append(t)
def gkey(item):
    p, ts = item
    due = min((t.date_iso for t in ts if t.date_iso), default="9999-12-31")
    newest = max((key_c(t) for t in ts if C[id(t)]), default=datetime(1900,1,1).date())
    return (due, -newest.toordinal())
for p, ts in sorted(openp.items(), key=gkey):
    outB.append(f"### 【{p}】 未完了{len(ts)}件\n\n")
    for t in sorted(ts, key=lambda t: (key_c(t), t.order)): outB.append(line(t, C[id(t)]))
    outB.append("\n")
done = [t for t in tasks if t.checked]
outB.append(f"### 済み（翌日 90_Archive へ移る） {len(done)}件\n\n")
for t in sorted(done, key=lambda t: (proj(t), key_c(t))): outB.append(line(t, C[id(t)]))
d = os.path.dirname(s.AI_PATH)
open(os.path.join(d, "見本_03_A_5段のまま案件順.md"), "w", encoding="utf-8").write("".join(outA))
open(os.path.join(d, "見本_03_B_案件ごとの見出し.md"), "w", encoding="utf-8").write("".join(outB))
print("tasks", len(tasks), "open", sum(not t.checked for t in tasks), "done", len(done), "projects(open)", len(openp), "no_created", sum(1 for t in tasks if not C[id(t)]))
