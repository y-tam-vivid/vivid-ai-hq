"""試作 index.html から協力先向けの公開版 public/ を組み立てる。

外すもの：構想書タブ・内部の数字（困りごとリスト118件）・参考サイトへの言及。
足すもの：noindex・完全なHTMLの骨組み・計測セット（bin/web_tracking/snippet.html v2）。
使い方：python3 scratchpad/f119-portal/build_public.py  → 最後に計測の検査を走らせる
"""
import re
import shutil
import subprocess
import render_data
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PUB = HERE / "public"
SB_ID = "17e298ff-5e02-4630-a16d-0f4f25ede23a"
SB_TOKEN = "8d63c4ed-05b5-4cd8-90cd-d1a8a89e947b"  # 自社の公開ページに出ている値（gamemarke・ko-station で一致）
GTM_ID = "GTM-PQX3L4TQ"
CLARITY_ID = "z431w59a74"
NOTICE = "協力先さま確認用の試作です。掲載している会社名・人名・事例はすべて架空です。ご意見は福祉施設の119番の担当までお寄せください。"
SITE_URL = "https://fukushi119-web.vercel.app/"  # 119番Webサイト
NOTICE_MIXED = "協力先さま確認用の試作です。「架空」と書いた掲載は見本です。「確認中」と書いた掲載は、内容をご本人に確認しているところです。ご意見は福祉施設の119番の担当までお寄せください。"
FORBIDDEN = ["構想書", "118", "SparkLabo", "諸橋", "宮原", "齋藤", "井上", "CAS", "△", "職業安定法", "参考サイト", "concept"]


def rep(s, a, b, count=1):
    n = s.count(a)
    if n != count:
        raise SystemExit(f"置換対象の数が想定と違う（{n}件）: {a[:60]}")
    return s.replace(a, b)


def main():
    render_data.main()
    rows = [r for _, n in render_data.SETS for r in render_data.load(n)]
    notice = NOTICE if all(r["sample"] for r in rows) else NOTICE_MIXED
    s = (HERE / "index.html").read_text(encoding="utf-8")
    # 帯の文言・フッターの構想書リンク
    s = re.sub(r'<div class="notice"><div class="wrap">.*?</div></div>',
               f'<div class="notice"><div class="wrap"><span>{notice}</span></div></div>', s, count=1, flags=re.S)
    s = rep(s, ' ／ <a href="#concept">構想書</a>', '')
    s = rep(s, '解決パートナー（仮称）・試作 ／', '解決パートナー（仮称）・確認用の試作 ／')
    # 構想書の本文と経路
    i = s.index("const CONCEPT=`")
    j = s.index("`;", i) + 2
    s = s[:i] + s[j:]
    s = rep(s, '  else if(h==="concept"){html=CONCEPT}\n', '')
    s = re.sub(r"/\* concept \*/.*?(?=\n/\*)", "", s, count=1, flags=re.S)
    # 内部の数字・参考サイト
    s = s.replace("困りごとリスト118件の10分類＋経営者ご自身の悩み", "施設経営の10分類＋経営者ご自身の悩み")
    s = rep(s, "<span>お悩みの分類（困りごとリスト118件から）</span>", "<span>お悩みの分類</span>")
    s = rep(s, "困りごとリスト118件を10分類にまとめ、経営者ご自身の悩みを加えました。",
            "施設経営のお悩みを10の分類にまとめ、経営者ご自身の悩みを加えました。")
    s = rep(s, "掲載料と紹介料の扱いは検討中です（構想書§9）。決まるまでは表示しません。", "掲載料・紹介料の扱いは検討中です。")
    s = rep(s, "参考サイトの「部活」にあたる場。採用・送迎・加算など、お悩み分類ごとに集まる。",
            "採用・送迎・加算など、お悩み分類ごとに集まる場。")
    s = re.sub(r"/\* Layout:[^*]*\*/", "/* Layout: 福祉施設の119番 Design System v0.1 */", s, count=1)
    s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    s = s.replace("https://fukushi119-web.vercel.app/", SITE_URL)
    # 骨組み・noindex・計測
    snippet = (REPO / "bin/web_tracking/snippet.html").read_text(encoding="utf-8")
    snippet = (snippet.replace("{{SB_TRACK_ID}}", SB_ID).replace("{{SB_TRACK_TOKEN}}", SB_TOKEN)
               .replace("{{GTM_ID}}", GTM_ID).replace("{{CLARITY_ID}}", CLARITY_ID))
    head = ('<!doctype html>\n<html lang="ja">\n<head>\n' + snippet + '\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
    k = s.index("</style>") + len("</style>")
    s = head + s[:k] + "\n</head>\n<body>" + s[k:] + "\n</body>\n</html>\n"
    s = s.replace("<title>119番 解決パートナー</title>",
                  '<title>119番 解決パートナー</title>\n<meta name="robots" content="noindex,nofollow">', 1)
    s = s.replace('<a href="#consult" class="cta-s" data-nav="consult">', '<a href="#consult" class="cta-s" data-nav="consult" data-cta="header-consult">')
    s = s.replace('<a class="btn p" href="${href}">${label}</a></div>`;', '<a class="btn p" href="${href}" data-cta="band">${label}</a></div>`;')
    s = s.replace('<a class="btn p w" href="#consult-p-${c.id}">', '<a class="btn p w" href="#consult-p-${c.id}" data-cta="partner-side">')
    for fid in ("consultform", "joinform", "memberform"):
        s = s.replace(f'<form class="form" id="{fid}">', f'<form class="form" id="{fid}" data-cta="{fid}-submit">')
    body = s[s.index("<body>"):]
    left = [w for w in FORBIDDEN if w in body]
    if left:
        raise SystemExit(f"公開版に残ってはいけない語が残っている: {left}")
    # 書き出し
    if PUB.exists():
        for p in PUB.iterdir():
            if p.name in ("index.html", "assets", "photos"):
                shutil.rmtree(p) if p.is_dir() else p.unlink()
    PUB.mkdir(exist_ok=True)
    (PUB / "index.html").write_text(s, encoding="utf-8")
    (PUB / "assets").mkdir(exist_ok=True)
    for f in ("119ban-logo-tight.png", "fukushi119_logo_symbol_white.svg"):
        shutil.copy(HERE / "assets" / f, PUB / "assets" / f)
    shutil.copytree(HERE / "photos", PUB / "photos")
    (PUB / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (PUB / ".vercelignore").write_text("*.md\n*.bak*\n", encoding="utf-8")
    (PUB / "vercel.json").write_text('{\n  "headers": [\n    { "source": "/(.*)", "headers": [ { "key": "X-Robots-Tag", "value": "noindex, nofollow" } ] }\n  ]\n}\n', encoding="utf-8")
    subprocess.run(["python3", str(REPO / "bin/web_tracking_check.py"), str(PUB / "index.html")], check=True)


if __name__ == "__main__":
    main()
