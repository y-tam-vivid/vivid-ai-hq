#!/usr/bin/env python3
"""Claude Design の .dc.html の image-slot の src を、手元の画像へ差し替える。

★既定はドライラン。--run のときだけ書き換える。書き換える前に必ず控えを取る。

なぜ要るか ── 2026-09-08、地域ポータル「かわちばなし」の18枠を作り直したあと、
1枠ずつ画面で貼ると枠を取り違える（v2-j1 が「今月のイチ押し」に居る等、IDと用途が
一致していない）。**idで機械的に当てる。**

使い方
    python3 bin/swap_image_slots.py "<v4.dc.html>" --images ~/kb_images
        → ★ドライラン。どのidをどう書き換えるかを出すだけ
    python3 bin/swap_image_slots.py "<v4.dc.html>" --images ~/kb_images --run
        → 画像を <html と同じ場所>/uploads/ へコピーし、src を差し替える

★注意
- **Claude Design でそのファイルを開いたまま実行しない。** 向こうが上書きし返す。
- src は2箇所に書かれている（HTMLの `<image-slot src=...>` と、末尾スクリプトの
  `src: '...'`）。★両方直さないと、片方だけ古い画像が残る。
"""
import argparse
import pathlib
import re
import shutil
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--images", required=True, help="<id>.png が入っているディレクトリ")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()

    html = pathlib.Path(a.html).expanduser()
    imgs = pathlib.Path(a.images).expanduser()
    if not html.exists():
        print(f"★ファイルが無い: {html}", file=sys.stderr)
        return 1
    src = html.read_text(encoding="utf-8")

    found = sorted(p for p in imgs.glob("*.png") if not p.name.startswith("."))
    if not found:
        print(f"★画像が無い: {imgs}", file=sys.stderr)
        return 1

    plan = []
    for p in found:
        sid = p.stem
        # ① <image-slot id="xxx" ... src="..."> ② 末尾スクリプトの imgId: 'xxx', src: '...'
        n1 = len(re.findall(rf'(<image-slot[^>]*id="{re.escape(sid)}"[^>]*src=")[^"]*(")', src))
        n2 = len(re.findall(rf"(imgId: '{re.escape(sid)}', src: ')[^']*(')", src))
        plan.append((sid, p, n1, n2))

    print(f"HTML   {html}")
    print(f"画像   {imgs}  （{len(found)}枚）\n")
    print(f"{'id':<16}{'HTMLのsrc':>10}{'スクリプトのsrc':>16}   差し替え先")
    hit = 0
    for sid, p, n1, n2 in plan:
        mark = "" if (n1 or n2) else "   ★このidはHTMLに無い"
        hit += n1 + n2
        print(f"{sid:<16}{n1:>10}{n2:>16}   uploads/{p.name}{mark}")
    print(f"\n書き換える箇所 合計 {hit}")

    if not a.run:
        print("\n★ドライラン。1文字も書いていない。実行するには --run を付ける。")
        return 0

    backup = html.with_name(html.stem + f".bak_{time.strftime('%Y%m%d-%H%M')}" + html.suffix)
    shutil.copy2(html, backup)
    print(f"\n控え   {backup}")

    up = html.parent / "uploads"
    up.mkdir(exist_ok=True)
    for sid, p, n1, n2 in plan:
        if n1 or n2:
            shutil.copy2(p, up / p.name)

    out = src
    for sid, p, n1, n2 in plan:
        rel = f"uploads/{p.name}"
        out = re.sub(rf'(<image-slot[^>]*id="{re.escape(sid)}"[^>]*src=")[^"]*(")',
                     lambda m: m.group(1) + rel + m.group(2), out)
        out = re.sub(rf"(imgId: '{re.escape(sid)}', src: ')[^']*(')",
                     lambda m: m.group(1) + rel + m.group(2), out)
    html.write_text(out, encoding="utf-8")

    # ★書いたあと実物で数え直す（申告で終わらせない）
    left = len(re.findall(r'cdn\.gamma\.app', out))
    print(f"書き換え完了。★実測：残っている cdn.gamma.app の参照 {left}件")
    print("★戻すのは控えを本体へ戻す1手。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
