#!/usr/bin/env python3
"""画像を1枚のシートに並べる。★読むだけ（元画像は触らない）。

なぜ要るか ── 2026-09-08、かわちばなしの18枠を1枚ずつ見せると、
「揃っているか」がいちばん分からない。**揃いは並べたときにしか見えない。**
数値（bin/image_tone.py）は1経路目、このシートが2経路目の目視にあたる。

使い方
    python3 bin/contact_sheet.py ~/kb_images/*.png --out sheet.jpg --cols 3
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--cell", type=int, default=420, help="1枚の横幅(px)")
    ap.add_argument("--quality", type=int, default=76)
    a = ap.parse_args()

    paths = [pathlib.Path(p) for p in a.paths if not pathlib.Path(p).name.startswith(".")]
    paths = sorted(p for p in paths if p.exists())
    if not paths:
        print("★並べる画像が0件。", file=sys.stderr)
        return 1

    label_h = 26
    tiles = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        w = a.cell
        h = max(1, round(im.height * w / im.width))
        im = im.resize((w, h))
        tile = Image.new("RGB", (w, h + label_h), (255, 255, 255))
        tile.paste(im, (0, label_h))
        ImageDraw.Draw(tile).text((4, 7), p.stem, fill=(60, 50, 40))
        tiles.append(tile)

    cols = min(a.cols, len(tiles))
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    gap = 8
    width = cols * a.cell + (cols - 1) * gap
    height = sum(max(t.height for t in r) for r in rows) + gap * (len(rows) - 1)
    sheet = Image.new("RGB", (width, height), (255, 255, 255))

    y = 0
    for r in rows:
        x = 0
        for t in r:
            sheet.paste(t, (x, y))
            x += a.cell + gap
        y += max(t.height for t in r) + gap

    out = pathlib.Path(a.out).expanduser()
    sheet.save(out, quality=a.quality)
    print(f"{len(tiles)}枚を {cols}列で並べた → {out}  {sheet.size}")
    print("★これは縮小版。原寸は元のディレクトリにある。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
