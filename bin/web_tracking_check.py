#!/usr/bin/env python3
"""公開したWebページに「ふくち。計測セット」が入っているかを検査する（読むだけ）。

使い方
  python3 bin/web_tracking_check.py https://example.com/                 # 1ページ
  python3 bin/web_tracking_check.py https://example.com/ --paths /kids/a /kids/b /ig
  python3 bin/web_tracking_check.py ./index.html                          # 公開前のファイル

見るもの（★どれか1つでも ✗ なら終了コード1＝送信・公開してはいけない）
★HTML コメントの中のタグは数えない。タグ・cta_click は <script> の中に在ることを条件にする
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
import uuid

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


def strip_comments(html):
    """HTML コメント（条件付きコメント含む）を除く。★コメントの中のタグは実行されない"""
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


def script_text(html):
    """<script …>…</script> を連結する。★本文（<p> 等）に文字列があるだけでは計測が入っているとは言えない"""
    return "\n".join(m.group(0) for m in re.finditer(r"<script\b[^>]*>.*?</script>", html, flags=re.S | re.I))


def check_html(html):
    rows = []
    html = strip_comments(html)
    sc = script_text(html)
    sb = re.search(r"salesbreaker\.jp/v1/sb-track\.js\?id=([0-9a-f-]{36})", sc)
    rows.append(("SalesBreaker 1行タグ", bool(sb), sb.group(1) if sb else "無い"))
    gtm = re.findall(r"GTM-[A-Z0-9]{6,}", sc)
    rows.append(("GTM コンテナ", bool(gtm), ",".join(sorted(set(gtm))) or "無い"))
    cl = re.search(r'clarity\.ms/tag/"\s*\+\s*i.*?"clarity"\s*,\s*"script"\s*,\s*"([a-z0-9]+)"', sc, re.S) \
        or re.search(r"clarity\.ms/tag/([a-z0-9]{8,})", sc)
    rows.append(("Microsoft Clarity", bool(cl), cl.group(1) if cl else "無い"))
    logger = "cta_click" in sc
    rows.append(("クリックログ（cta_click）", logger, "あり" if logger else "snippet.html の部品が無い（<script> の中に必要）"))
    ctas = re.findall(r'data-cta="([^"]+)"', html)
    rows.append(("data-cta の付いたボタン", None if not ctas else True,
                 f"{len(ctas)}個 " + ",".join(ctas[:6]) if ctas else "0個（押された場所が区別できない）"))
    left = re.findall(r"\{\{(SB_TRACK_ID|SB_TRACK_TOKEN|GTM_ID|CLARITY_ID)\}\}", html)
    rows.append(("差し替え忘れ {{…}}", not left, ",".join(left) or "無し"))
    return rows


def _is_html(body):
    head = body[:2000].lower()
    return "<html" in head or "<!doctype html" in head


def _title(body):
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def leak_verdict(path, code, body, probe_code, probe_body):
    """社内向けファイル path が外へ出ているか。戻り値 (出ている?, 理由1行)。
    ★200 でも STUDIO 等の SPA は存在しないパスにトップページを返す。
      存在しない乱数パスと同じ HTML なら「SPA の受け皿＝中身は出ていない」。
    ★.md 本文など HTML でない中身が 200 で返れば従来どおり出ている（安全側）。"""
    if code != 200:
        return False, f"{code}"
    if not (_is_html(body) and probe_code == 200 and _is_html(probe_body)):
        return True, "200 で中身が返っている"
    same = body.split() == probe_body.split() or (_title(body) is not None and _title(body) == _title(probe_body))
    if same or not path.endswith(".html"):
        return False, "200だが存在しないパスと同じHTML＝SPAの受け皿"
    return True, "200 で存在しないパスと違うHTMLが返っている"


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
        probe_code, probe_body = fetch(base + "/zzz-not-exist-" + uuid.uuid4().hex[:12])
        leaks, spa = [], []
        for p in ("/README.md", "/配布URL一覧.md", "/index.bak.html"):
            c, b = fetch(base + urllib.parse.quote(p))
            leaked, why = leak_verdict(p, c, b, probe_code, probe_body)
            if leaked:
                leaks.append(p)
            elif c == 200:
                spa.append(p)
        note = ",".join(leaks) or ("200だが存在しないパスと同じHTML＝SPAの受け皿（" + ",".join(spa) + "）" if spa else "404 を確認")
        rows.append(("社内向けファイルが塞がっている", not leaks, note))
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
