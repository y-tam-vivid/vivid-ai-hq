#!/usr/bin/env python3
"""MEMORY.md の索引行が1行180バイトを超えていないか見る。★読むだけ。

なぜ要るか ── 2026-09-09、MEMORY.md が上限（24,986B）を2度超えた。
数えたら **問題は本数ではなく1本の長さ** だった。

    索引行 78本  合計 25,213B
    ★規範値180Bを守れば 78×180 = 14,040B ＝ 上限の56%。★守れば収まる
    実際は 平均323B・中央値190B・★180B超えが40本・最長1,490B（1本で上限の6%）

**★真因：索引行に「履歴」を書いている。** 新しい発見のたびに「／」で継ぎ足し、
削らない。最長の1本には★指摘が9個連なっていた。索引は現在地を運ぶ場所で、履歴の置き場ではない。

**★直し方は「降ろす」ではなく「本文へ戻す」。**
2026-09-09 に上位2本で実演したところ、索引に書いてあった項目の
**ほぼ全部が既に本文に在った**（1,490Bの行では7項目中6項目・1,153Bの行では7項目全部）。
＝ **索引から消しても情報は1バイトも失われない。** 実測してから消すこと。

使い方
    python3 bin/check_index_line_length.py            # 超えている行を出す
    python3 bin/check_index_line_length.py --top 10   # 長い順に10本
"""
import argparse
import pathlib
import re
import sys

LIMIT = 180
MEMORY = pathlib.Path(__file__).resolve().parent.parent / "memory" / "MEMORY.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=0, help="長い順にN本だけ出す")
    a = ap.parse_args()

    if not MEMORY.exists():
        print(f"★{MEMORY} が無い", file=sys.stderr)
        return 1
    lines = [l for l in MEMORY.read_text(encoding="utf-8").split("\n") if l.startswith("- [")]
    rows = sorted(((len(l.encode()), l) for l in lines), reverse=True)
    over = [(b, l) for b, l in rows if b > LIMIT]

    show = rows[:a.top] if a.top else over
    for b, l in show:
        name = re.search(r"\]\(([^)]+)\)", l)
        mark = "✗" if b > LIMIT else "✓"
        print(f"  {mark} {b:>5}B  {name.group(1) if name else '?'}")

    total = sum(b for b, _ in rows)
    print(f"\n  索引 {len(rows)}本 / 合計 {total}B / 平均 {total//max(1,len(rows))}B")
    print(f"  ★{LIMIT}B超え {len(over)}本")
    if over:
        print(f"  ★上位1本を詰めるだけで -{over[0][0]-LIMIT}B 減る")
        print("  ★直し方：索引から消す前に、その項目が本文に在るかを1つずつ数える。")
        print("           在れば消してよい。無ければ★本文へ戻してから消す。")
    return 0 if not over else 2


if __name__ == "__main__":
    sys.exit(main())
