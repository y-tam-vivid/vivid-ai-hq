#!/usr/bin/env python3
"""公開したWebページに「ふくち。計測セット」が入っているかを検査する（読むだけ）。

使い方
  python3 bin/web_tracking_check.py https://example.com/                 # 1ページ
  python3 bin/web_tracking_check.py https://example.com/ --paths /kids/a /kids/b /ig
  python3 bin/web_tracking_check.py ./index.html                          # 公開前のファイル

見るもの（★どれか1つでも ✗ なら終了コード1＝送信・公開してはいけない）
  1. SalesBreaker 1行タグ   どの会社が来たか
  2. GTM コンテナ           GA4 の受け皿
  3. Microsoft Clarity      録画・ヒートマップ・クリック
  4. クリックログ           cta_click を dataLayer と Clarity へ送る部品（snippet.html）
  5. data-cta の付いたボタン 何が押されたかを区別できるか（0個なら△）
  6. 置きっぱなしの {{…}}   差し替え忘れ
  7. 社内向けファイル        /README.md 等が外から読めないか（URLのときだけ）
  8. 経路・案のパス          --paths で渡した全パスが 200 か（URLのときだけ）

★これは「タグが書かれているか」の検査。「実際に送信しているか」は別。
  発火の確認は reference_lp_tracking_tags.md の3手（ブラウザで performance を読む）で行う。
"""
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (fukuchi web_tracking_check)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # 名前解決できない等
        return 0, str(e)


def check_html(html):
    rows = []
    sb = re.search(r"salesbreaker\.jp/v1/sb-track\.js\?id=([0-9a-f-]{36})", html)
    rows.append(("SalesBreaker 1行タグ", bool(sb), sb.group(1) if sb else "無い"))
    gtm = re.findall(r"GTM-[A-Z0-9]{6,}", html)
    rows.append(("GTM コンテナ", bool(gtm), ",".join(sorted(set(gtm))) or "無い"))
    cl = re.search(r'clarity\.ms/tag/"\s*\+\s*i.*?"clarity"\s*,\s*"script"\s*,\s*"([a-z0-9]+)"', html, re.S) \
        or re.search(r"clarity\.ms/tag/([a-z0-9]{8,})", html)
    rows.append(("Microsoft Clarity", bool(cl), cl.group(1) if cl else "無い"))
    logger = "cta_click" in html
    rows.append(("クリックログ（cta_click）", logger, "あり" if logger else "snippet.html の部品が無い"))
    ctas = re.findall(r'data-cta="([^"]+)"', html)
    rows.append(("data-cta の付いたボタン", None if not ctas else True,
                 f"{len(ctas)}個 " + ",".join(ctas[:6]) if ctas else "0個（押された場所が区別できない）"))
    left = re.findall(r"\{\{(SB_TRACK_ID|SB_TRACK_TOKEN|GTM_ID|CLARITY_ID)\}\}", html)
    rows.append(("差し替え忘れ {{…}}", not left, ",".join(left) or "無し"))
    return rows


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    target, paths = args[0], []
    if "--paths" in args:
        paths = args[args.index("--paths") + 1:]

    is_url = target.startswith("http")
    if is_url:
        code, html = fetch(target)
        if code != 200:
            print(f"✗ {target} が開けない（{code}）")
            return 1
    else:
        html = open(target, encoding="utf-8").read()

    rows = check_html(html)
    if is_url:
        base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(target))
        leaks = [p for p in ("/README.md", "/配布URL一覧.md", "/index.bak.html")
                 if fetch(base + urllib.parse.quote(p))[0] == 200]
        rows.append(("社内向けファイルが塞がっている", not leaks, ",".join(leaks) or "404 を確認"))
        bad = [f"{p}={c}" for p in paths for c in [fetch(base + p)[0]] if c != 200]
        if paths:
            rows.append(("経路・案のパス", not bad, ",".join(bad) or f"{len(paths)}本とも200"))

    ng = 0
    for name, ok, note in rows:
        mark = "✓" if ok else ("△" if ok is None else "✗")
        ng += ok is False
        print(f"{mark} {name:<24} {note}")
    print("\n" + ("✗ 計測が揃っていない。公開・送信しないこと" if ng else "✓ 計測セットは揃っている（発火の確認は別）"))
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
