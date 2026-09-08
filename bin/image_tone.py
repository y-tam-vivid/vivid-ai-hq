#!/usr/bin/env python3
"""画像のトーン（明るさ・彩度・暗部）を測って合否を返す。★読むだけ。書き込まない。

なぜ要るか ── 2026-09-08、地域ポータル「かわちばなし」で有璽氏の指摘
「素材写真の明るさとかが異なっているように思います」を数字にしたのが発端。
5枚の明るさが 10.9〜35.4（ひらき24.5・最明と最暗で3.2倍）でバラついていた。
**「揃っているか」を目で決めると「まあ揃っている」で通る。** だから測る。

★ただし数値の合格は目視の合格ではない。同日、補正版は数値5/5合格・目視4/5不合格だった。
  判定は必ず 数値 → 目視 の2経路。このスクリプトは1経路目でしかない。
  → memory/project_kawachibanashi_portal.md

使い方
    python3 bin/image_tone.py 画像1 画像2 ...          # 既定の合否線で測る
    python3 bin/image_tone.py --json 画像...            # JSONで出す（他スクリプトから使う用）
    python3 bin/image_tone.py --min-l 60 --max-l 70 ... # 合否線を変える

合否線の既定（かわちばなしの値。案件が変われば引数で変える）
    明るさ 60〜70 ／ 彩度 35〜45 ／ 暗部 15%未満 ／ 枚数間のひらき ±8以内
"""
import argparse
import colorsys
import json
import sys

from PIL import Image

# 既定の合否線
L_MIN, L_MAX = 60.0, 70.0
S_MIN, S_MAX = 35.0, 45.0
DARK_MAX = 15.0
SPREAD_MAX = 8.0

# 測るときの縮小サイズ。★これを変えると数字が変わる。比較するときは必ず揃えること
SAMPLE = 260


def measure(path):
    """1枚を測る。明るさ・彩度・暗部率（いずれも0-100）を返す。"""
    im = Image.open(path).convert("RGB")
    im.thumbnail((SAMPLE, SAMPLE))
    px = list(im.getdata())
    n = len(px)
    lum = [(0.299 * r + 0.587 * g + 0.114 * b) / 255 * 100 for r, g, b in px]
    lightness = sum(lum) / n
    sat = sum(colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)[1] for r, g, b in px) / n * 100
    dark = sum(1 for v in lum if v < 25) / n * 100
    return {"path": str(path), "lightness": round(lightness, 1),
            "saturation": round(sat, 1), "dark_ratio": round(dark, 1)}


def judge(m, l_min=L_MIN, l_max=L_MAX, s_min=S_MIN, s_max=S_MAX, dark_max=DARK_MAX):
    """1枚ぶんの不合格理由を並べる。空リスト＝合格。"""
    ng = []
    if not l_min <= m["lightness"] <= l_max:
        ng.append(f"明るさ{m['lightness']}（{l_min}〜{l_max}の外）")
    if not s_min <= m["saturation"] <= s_max:
        ng.append(f"彩度{m['saturation']}（{s_min}〜{s_max}の外）")
    if m["dark_ratio"] >= dark_max:
        ng.append(f"暗部{m['dark_ratio']}%（{dark_max}%以上）")
    return ng


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-l", type=float, default=L_MIN)
    ap.add_argument("--max-l", type=float, default=L_MAX)
    ap.add_argument("--min-s", type=float, default=S_MIN)
    ap.add_argument("--max-s", type=float, default=S_MAX)
    ap.add_argument("--max-dark", type=float, default=DARK_MAX)
    ap.add_argument("--max-spread", type=float, default=SPREAD_MAX)
    a = ap.parse_args()

    rows = []
    for p in a.paths:
        try:
            m = measure(p)
        except Exception as e:              # 開けないものは飛ばす。黙って落とさない
            print(f"★開けなかった: {p} ({e})", file=sys.stderr)
            continue
        m["ng"] = judge(m, a.min_l, a.max_l, a.min_s, a.max_s, a.max_dark)
        rows.append(m)

    if not rows:
        print("★測れた画像が0件。", file=sys.stderr)
        return 1

    ls = [r["lightness"] for r in rows]
    spread = round(max(ls) - min(ls), 1)
    result = {"images": rows, "spread": spread,
              "spread_ok": spread <= a.max_spread,
              "passed": sum(1 for r in rows if not r["ng"]), "total": len(rows)}

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            mark = "○" if not r["ng"] else "×"
            name = r["path"].split("/")[-1]
            print(f"{mark} {name:<34} 明るさ{r['lightness']:5.1f}  彩度{r['saturation']:5.1f}  "
                  f"暗部{r['dark_ratio']:5.1f}%" + ("   " + " / ".join(r["ng"]) if r["ng"] else ""))
        mark = "○" if result["spread_ok"] else "×"
        print(f"\n{mark} 枚数間のひらき {spread}（上限 {a.max_spread}）"
              f"   合格 {result['passed']}/{result['total']}")
        print("★これは1経路目。数値が通っても、必ず実物を目で見てから採用すること。")
    return 0 if (result["passed"] == result["total"] and result["spread_ok"]) else 2


if __name__ == "__main__":
    sys.exit(main())
