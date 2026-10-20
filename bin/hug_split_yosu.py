#!/usr/bin/env python3
"""HUG「本日の様子一括印刷」のPDFを、利用者ごと×月ごとのPDFに分けて名前を付ける

なぜ要るか（2026-10-20 有璽氏・★恒久ルール）
  日々の様子をもとに個別支援計画等を作る＝原本は利用者別。月単位でも見たい＝月別にはショートカット。
  HUG の出力は印刷画面＝有璽氏が「すべてチェック→印刷→PDFを出力する」で保存し、受け取りフォルダに置く。
  → memory/reference_hug_record_output.md

  python3 hug_split_yosu.py [<PDF> ...] [--facility STANDUP] [--dry-run]
      PDF を省くと ~/Documents/_機微_HUG本日の様子/受け取り（HUGから保存）/ の全部を処理する

  区切り：ページの冒頭に「利用者名（ 氏 名 ）」の行があれば、その利用者の始まり。無いページは前の人の続き。
  行    ：表の左端の日付（YYYY/MM/DD）が1行の始まり。次の日付の手前までがその行。
  月    ：★期間を広げた1本でもよい。各月のPDFには、その月の行があるページだけを入れ、
          ほかの月の行は★文字ごと消して白で塗る（切り貼りで隠すだけだと、見えない文字が残るため）。
          1か月だけの利用者はページをそのまま写す。
  同一人物：受け取りの1つ上の _同一人物.tsv（別名<TAB>正の名・空白は無視）。★氏名は git に書かない。
          例：「＜藤＞」付きの氏名は付いていない氏名と同一（有璽氏 10/20）。表に無い「＜…＞」付きは知らせる。
  出力  ：受け取りの1つ上に
            利用者別/<氏名>/<YYYY-MM>_本日の様子_<施設>_<氏名>.pdf   原本
            月別/<YYYY-MM>/<同じ名前>                              原本への相対の symlink（ドライブでは hug_drive_shortcuts.py）
            元PDF/<最初の月>〜<最後の月>_本日の様子_<施設>.pdf        受け取ったPDF（名前を付けて移す）
          既に同じ名前があれば1本も書かずに止める。
  照合  ：書き出した全ファイルの日付の行を数え直し、①元の行数と一致 ②ほかの月の日付が0件 を確かめる。
  ★最終の置き場：共有ドライブ 15-000_施設運営部門 › LIFE STAND UP › 本日の様子（HUG）（#17160b）
  ★氏名・本文は画面に出さない（件数とページ数だけ）。
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import fitz

BASE = Path("~/Documents/_機微_HUG本日の様子").expanduser()
INBOX = "受け取り（HUGから保存）"
ALIASES = "_同一人物.tsv"
NAME_RE = re.compile(r"^利用者名[（(]\s*(.+?)\s*[）)]\s*$")
DATE_W = re.compile(r"^(20\d\d)/(\d\d)/\d\d$")
DATE_X = 40   # 日付の列の右端（左端の日付だけを行の始まりとみる。本文中の日付は数えない）
PAD = 4       # 行の上の罫線のぶん


def norm(s):
    return re.sub(r"\s+", "", s)


def load_aliases():
    path = BASE / ALIASES
    if not path.exists():
        return {}
    pairs = [l.split("\t") for l in path.read_text(encoding="utf-8").splitlines() if "\t" in l]
    return {norm(a): norm(b) for a, b in pairs}


def date_rows(page):
    """(y, 年月) の並び・ページの文字の下端"""
    ws = page.get_text("words")
    rows = sorted((w[1], f"{m.group(1)}-{m.group(2)}") for w in ws
                  if w[0] < DATE_X and (m := DATE_W.match(w[4])))
    return rows, max((w[3] for w in ws), default=0)


def persons(doc, aliases):
    """利用者ごとに [(ページ, y0, y1, 年月)] の行を集める。別名は正の名へまとめる"""
    out, order, cur, unknown_tag = defaultdict(list), [], None, set()
    for i, page in enumerate(doc):
        lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
        if name := next((m.group(1) for l in lines[:6] if (m := NAME_RE.match(l))), None):
            cur = aliases.get(norm(name), norm(name))
            if cur.startswith("＜"):
                unknown_tag.add(cur)
            if cur not in order:
                order.append(cur)
        elif cur is None:
            sys.exit(f"1ページ目に利用者名の行がありません。HUGの出力の形が変わった可能性")
        rows, bottom = date_rows(page)
        for j, (y, ym) in enumerate(rows):
            y1 = rows[j + 1][0] - PAD if j + 1 < len(rows) else bottom + PAD
            out[cur].append((i, y - PAD, y1, ym))
    return {n: out[n] for n in order}, unknown_tag


def write_month(doc, rows, ym, dest):
    """その月の行があるページだけを写し、ほかの月の行を文字ごと消す"""
    pages = sorted({p for p, *_, m in rows if m == ym})
    other = defaultdict(list)
    for p, y0, y1, m in rows:
        if m != ym and p in pages:
            other[p].append((y0, y1))
    out = fitz.open()
    for p in pages:
        out.insert_pdf(doc, from_page=p, to_page=p)
        pg = out[-1]
        for y0, y1 in other.get(p, []):
            pg.add_redact_annot(fitz.Rect(0, y0, pg.rect.width, y1), fill=(1, 1, 1))
        if other.get(p):
            pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                                graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    out.save(dest, garbage=3, deflate=True)


def count_rows(path):
    c = Counter()
    for page in fitz.open(path):
        c.update(ym for _, ym in date_rows(page)[0])
    return c


def split_one(src, facility, dry_run, aliases):
    doc = fitz.open(src)
    people, unknown_tag = persons(doc, aliases)
    total = Counter(ym for rows in people.values() for *_, ym in rows)
    yms = sorted(total)
    print(f"[{src.name}] {len(doc)}ページ → 利用者 {len(people)}人・月 {yms[0]}〜{yms[-1]}（{len(yms)}か月）・日付の行 {sum(total.values())}")
    if unknown_tag:
        print(f"  ★同一人物の表に無い「＜…＞」付きの氏名が {len(unknown_tag)}人。別人のまま分けます（同じ人なら {ALIASES} に足す）")

    root = BASE
    plan = []
    for name, rows in people.items():
        for ym in sorted({m for *_, m in rows}):
            fname = f"{ym}_本日の様子_{facility}_{name}.pdf"
            plan.append((name, rows, ym, root / "利用者別" / name / fname, root / "月別" / ym / fname))
    src_name = root / "元PDF" / f"{yms[0]}〜{yms[-1]}_本日の様子_{facility}.pdf" if len(yms) > 1 \
        else root / "元PDF" / f"{yms[0]}_本日の様子_{facility}.pdf"
    clash = [p for *_, o, l in plan for p in (o, l) if p.exists() or p.is_symlink()]
    if src_name.exists() and src_name != src:
        clash.append(src_name)
    print(f"  書き出す予定 {len(plan)}本（月ごと {dict(sorted(Counter(ym for _, _, ym, _, _ in plan).items()))}）")
    if clash:
        sys.exit(f"  同じ名前のファイルが既に{len(clash)}本あります。上書きしないので止めます")
    if dry_run:
        return

    for name, rows, ym, orig, link in plan:
        orig.parent.mkdir(parents=True, exist_ok=True)
        link.parent.mkdir(parents=True, exist_ok=True)
        write_month(doc, rows, ym, orig)
        link.symlink_to(Path("..", "..", "利用者別", name, orig.name))

    # 照合：書き出した側で日付の行を数え直す
    got, stray = Counter(), 0
    for _, _, ym, orig, _ in plan:
        c = count_rows(orig)
        got[ym] += c[ym]
        stray += sum(v for k, v in c.items() if k != ym)
    broken = sum(1 for *_, l in plan if not l.resolve().exists())
    print(f"  照合：日付の行 元 {sum(total.values())} ／ 書き出し {sum(got.values())}"
          f"（月ごと一致 {'○' if got == total else '×'}）・ほかの月の行の混入 {stray}件・切れたショートカット {broken}本")
    if got != total or stray:
        sys.exit("  ★照合が合いません。元PDFは受け取りに残したまま止めます")

    src_name.parent.mkdir(exist_ok=True)
    src.rename(src_name)
    print(f"  元PDF → {src_name.relative_to(root)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="*")
    ap.add_argument("--facility", default="STANDUP")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    srcs = [Path(p).expanduser() for p in a.pdf] or sorted((BASE / INBOX).glob("*.pdf"))
    if not srcs:
        sys.exit(f"受け取りフォルダに PDF がありません：{BASE / INBOX}")
    aliases = load_aliases()
    for s in srcs:
        split_one(s, a.facility, a.dry_run, aliases)


if __name__ == "__main__":
    main()
