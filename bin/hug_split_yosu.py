#!/usr/bin/env python3
"""HUG「本日の様子一括印刷」を「PDFに保存」した1本を、利用者ごとのPDFに分けて名前を付ける

なぜ要るか（2026-10-20 有璽氏）
  月単位で保存していきたい。何月の・どなたの分かが分かるファイル名にしたい。
  HUG の出力はPDFでなく印刷画面＝有璽氏が「すべてチェック→印刷→PDFに保存」で1本にまとめる。
  分けると名前付けはこちら。→ memory/reference_hug_record_output.md

  python3 hug_split_yosu.py <保存したPDF> [<別の月のPDF> ...] [--facility STANDUP] [--dry-run]
  ★期間を広げるときも、HUGでは1か月ずつ保存する（1人の分の中で月が替わるページに2か月が混ざり、ページでは切れないため）

  区切り：ページの冒頭に「利用者名（ 氏 名 ）」の行があれば、その利用者の始まり。無いページは前の人の続き。
  年月  ：その利用者の分に出る日付（YYYY/MM/DD）。★複数の月にまたがれば止める（月単位の前提が崩れている）。
  出力  ：元のPDFと同じ場所に（★原本は利用者別・月別はショートカット＝個別支援計画は利用者ごとに読むため。有璽氏 10/20）
            利用者別/<氏名>/<YYYY-MM>_本日の様子_<施設>_<氏名>.pdf   原本
            月別/<YYYY-MM>/<同じ名前>                              原本への相対の symlink（★Driveへ移すならドライブのショートカットで作り直す）
          元のPDFは消さない。分け終えたら 元PDF/<YYYY-MM>_本日の様子_<施設>.pdf へ名前を付けて移す（同名があれば触らない）。
          既に同じ名前があれば1本も書かずに止める。
          ★最終の置き場は STAND UP の共有ドライブのフォルダ（有璽氏 10/20・15-000_施設運営部門 › LIFE STAND UP › 本日の様子（HUG）・#17160b）。
  ★氏名・本文は画面に出さない（件数とページ数だけ）。
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import fitz

INBOX = "受け取り（HUGから保存）"  # ~/Documents/_機微_HUG本日の様子/ の下。有璽氏がHUGのPDFを置く所（10/20）
NAME_RE = re.compile(r"^利用者名[（(]\s*(.+?)\s*[）)]\s*$")
DATE_RE = re.compile(r"(20\d\d)/(\d\d)/\d\d")


def groups(doc):
    out = []
    for i, page in enumerate(doc):
        lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
        name = next((m.group(1) for l in lines[:6] if (m := NAME_RE.match(l))), None)
        if name:
            out.append({"name": re.sub(r"\s+", "", name), "pages": [i], "months": Counter()})
        elif not out:
            sys.exit(f"1ページ目に利用者名の行がありません（{i + 1}ページ）。HUGの出力の形が変わった可能性")
        else:
            out[-1]["pages"].append(i)
        out[-1]["months"].update(f"{y}-{m}" for y, m in DATE_RE.findall(page.get_text()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="+", help="1か月ずつ保存したPDF（何本でも）")
    ap.add_argument("--facility", default="STANDUP")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    for p in a.pdf:
        split_one(Path(p).expanduser(), a.facility, a.dry_run)


def split_one(src, facility, dry_run):
    doc = fitz.open(src)
    print(f"[{src.name}]")
    gs = groups(doc)

    names = Counter(g["name"] for g in gs)
    if dup := [n for n, c in names.items() if c > 1]:
        sys.exit(f"同じ氏名が{len(dup)}人ぶん重複しています。名前が衝突するので止めます")
    for g in gs:
        if len(g["months"]) != 1:
            sys.exit(f"{len(g['months'])}か月にまたがる（または日付が無い）利用者がいます。月単位で出し直してください")

    print(f"元のPDF {len(doc)}ページ → 利用者 {len(gs)}人（ページ数の内訳 {sorted(Counter(len(g['pages']) for g in gs).items())}）")
    print("  ★この人数が HUG の「出力人数」と合うかを見る（取り忘れの目安）")

    # 有璽氏は 受け取り（HUGから保存）/ に置く。結果はその1つ上（利用者別・月別・元PDF の並ぶ所）へ出す
    root = src.parent.parent if src.parent.name == INBOX else src.parent
    plan = []
    for g in gs:
        ym = next(iter(g["months"]))
        fname = f"{ym}_本日の様子_{facility}_{g['name']}.pdf"
        plan.append((g, ym, root / "利用者別" / g["name"] / fname, root / "月別" / ym / fname))
    if clash := [p for _, _, o, l in plan for p in (o, l) if p.exists() or p.is_symlink()]:
        sys.exit(f"同じ名前のファイルが既に{len(clash)}本あります。上書きしないので止めます")
    if dry_run:
        return

    for g, ym, orig, link in plan:
        orig.parent.mkdir(parents=True, exist_ok=True)
        link.parent.mkdir(parents=True, exist_ok=True)
        out = fitz.open()
        out.insert_pdf(doc, from_page=g["pages"][0], to_page=g["pages"][-1])
        out.save(orig)
        link.symlink_to(Path("..", "..", "利用者別", g["name"], orig.name))
    pages = sum(len(fitz.open(o)) for _, _, o, _ in plan)
    broken = sum(1 for *_, l in plan if not l.resolve().exists())
    print(f"原本 {len(plan)}本 → {root / '利用者別'}（合計 {pages}ページ・元 {len(doc)}ページ）")
    print(f"ショートカット {len(plan)}本 → {root / '月別'}（切れているもの {broken}本）")

    # 元PDFにも名前を付ける（氏名なし・有璽氏 10/20）。既にあれば触らない
    yms = sorted({ym for _, ym, _, _ in plan})
    renamed = root / "元PDF" / f"{'_'.join(yms)}_本日の様子_{facility}.pdf"
    if src != renamed and not renamed.exists():
        renamed.parent.mkdir(exist_ok=True)
        src.rename(renamed)
        print(f"元PDF → {renamed.relative_to(root)}")


if __name__ == "__main__":
    main()
