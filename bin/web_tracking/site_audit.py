#!/usr/bin/env python3
"""公開中サイトのSEO標準装備を実測する（月次レビュー用・読むだけ）。

台帳 sites.json の各サイトについて、トップページと robots.txt・sitemap を取りに行き、
Clarity（台帳どおりのID）・Search Console の所有確認の痕跡・noindex・title/description・
canonical・サイトマップの到達を ✓/✗/△ で出す。どのサイトにも書き込まない。

  python3 site_audit.py              # 表を出す（✗が1つでもあれば終了コード1）
  python3 site_audit.py --md out.md  # 同じ内容を Markdown でも保存

★確かめているのは「HTMLに書かれているか」まで。Clarity が実際に送っているかは
  ブラウザで clarity.ms への通信を見る（SKILL.md 手順7）。
"""
import json, re, subprocess, sys, urllib.request, urllib.error
from pathlib import Path
from datetime import date

HERE = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Macintosh) vivid-site-audit/1.0"


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(3_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # ネット断・DNS失敗は「検査できなかった」
        return 0, str(e)


def dns_txt(host):
    try:
        out = subprocess.run(["dig", "+short", "TXT", host], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return ""
    return out


def apex(host):
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) > 2 and parts[0] == "www" else host


def audit(site):
    url = site["url"].rstrip("/") + "/"
    host = re.sub(r"^https?://", "", url).split("/")[0]
    res = {"name": site["name"], "url": url}
    code, html = fetch(url)
    res["http"] = ("✓" if code == 200 else "✗") + f" {code}"
    if code != 200:
        return res

    want = site.get("clarity", "")
    ids = set(re.findall(r'clarity["\']?\s*,\s*["\']script["\']\s*,\s*["\']([a-z0-9]{8,12})', html))
    ids |= set(re.findall(r'clarity\.ms/tag/([a-z0-9]{8,12})', html))
    if re.fullmatch(r"[a-z0-9]{8,12}", want or ""):
        res["clarity"] = "✓" if want in ids else ("✗ 別ID " + ",".join(sorted(ids)) if ids else "✗ 未設置")
    else:
        res["clarity"] = ("△ " + ",".join(sorted(ids))) if ids else "✗ 台帳にIDなし"

    noindex = bool(re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', html, re.I))
    res["noindex"] = ("✓ 想定どおり" if site.get("noindex_expected") else "✗ noindex") if noindex else (
        "✗ 想定と違う" if site.get("noindex_expected") else "✓")

    t = re.search(r"<title[^>]*>([^<]{1,200})", html, re.I)
    d = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', html, re.I)
    c = re.search(r'<link[^>]+rel=["\']canonical["\']', html, re.I)
    res["title/desc/canonical"] = "".join(["✓" if t else "✗", "✓" if d and d.group(1).strip() else "✗", "✓" if c else "✗"])

    meta_v = bool(re.search(r'google-site-verification', html))
    txt = dns_txt(apex(host))
    dns_v = "google-site-verification" in txt
    res["GSC痕跡"] = "✓ " + "+".join(x for x, ok in (("meta", meta_v), ("DNS", dns_v)) if ok) if (meta_v or dns_v) else "△ 痕跡なし"
    res["Bing痕跡"] = "✓" if ("msvalidate" in html or "ms=" in txt.lower()) else "△ 痕跡なし"

    rc, robots = fetch(url + "robots.txt", timeout=10)
    smaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots) if rc == 200 else []
    if not smaps:
        smaps = [url + "sitemap.xml", url + "sitemap_index.xml", url + "wp-sitemap.xml"]
    ok = [s for s in smaps if fetch(s, timeout=10)[0] == 200]
    res["sitemap"] = ("✓ " + ok[0].replace(url, "/")) if ok else "✗ 届かない"
    res["robots.txt"] = "✓ Sitemap行あり" if rc == 200 and re.search(r"(?im)^\s*sitemap:", robots) else ("△ Sitemap行なし" if rc == 200 else f"✗ {rc}")
    return res


def main():
    data = json.loads((HERE / "sites.json").read_text())
    rows = [audit(s) for s in data["sites"]]
    cols = ["http", "clarity", "noindex", "title/desc/canonical", "GSC痕跡", "Bing痕跡", "sitemap", "robots.txt"]
    lines = [f"# 公開中サイトの点検 {date.today().isoformat()}", "",
             "| サイト | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for r in rows:
        lines.append(f"| {r['name']} | " + " | ".join(r.get(k, "-") for k in cols) + " |")
    lines += ["", "✓=書かれている／✗=要対応／△=要確認（痕跡が無いだけで未登録とは限らない）。",
              "★Search Console の中身（カバレッジ・サイトマップの成否）はこの点検では見えない。管理画面で見る。"]
    out = "\n".join(lines)
    print(out)
    if "--md" in sys.argv:
        Path(sys.argv[sys.argv.index("--md") + 1]).write_text(out + "\n")
    sys.exit(1 if any("✗" in v for r in rows for v in r.values()) else 0)


if __name__ == "__main__":
    main()
