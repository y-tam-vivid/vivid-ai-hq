#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown を日本語の .pdf へ変換する。

なぜ在るか ── この機には pandoc も LibreOffice も weasyprint の依存(pango/cairo等の
ネイティブライブラリ)も無い（2026-08-29 実測）。bin/md2docx.py / bin/md2pptx.py と
同じ思想・同じ検算の作法で作った（新しい流儀を持ち込まない）。

使い方:
    python3 bin/md2pdf.py <入力.md> [出力.pdf]

★フォントは reportlab 組み込みの CID フォント（HeiseiMin-W3 / HeiseiKakuGo-W5）を使う。
  ★★非埋め込み方式（グリフ実体をPDFへ埋め込まない）。理由は下記「選ばなかった手段」参照。
  社内利用・日本語環境のPCで開く前提なら実用上問題ない。**社外へ厳密な体裁保証が要る
  文書（契約書等）は bin/md2docx.py で Word を経由すること。**

選ばなかった手段（2026-08-29 実測して落とした）:
    weasyprint      pip installは通るが実行時に libgobject-2.0 等のネイティブ依存が要り、
                    この機にはHomebrewが無く導入できない（brew自体が無い機がある）
    reportlab+TTF   macOSの日本語システムフォント（ヒラギノ角ゴ/明朝/丸ゴ）は全てCFF
                    (PostScript)アウトラインで、reportlabのTTFontローダーは非対応
    CFF→TTF変換     fontTools+otf2ttfで変換は可能だが実測14秒/フォント・8.9MB/本かかり、
                    毎回変換は非現実的。かつAppleフォントの変換ファイルをリポジトリへ
                    コミットするのはライセンス上のリスクがある（再配布に当たりうる）
    docx/pptx経由   LibreOffice(soffice)が無く自動変換できない。GUI操作(Word/Keynote)は
                    自動化に向かない

扱える記法（md2docx.pyに準拠。契約書のような厳密な記法ではなく、企画書・報告書向け）:
    # ## ###  見出し（H1中央寄せ／H2/H3左寄せ・ゴシック体）
    | a | b | 表（1行目をヘッダ・網掛け）
    - 項目    箇条書き
    1. 項目   番号付き
    **強調**  ゴシック体に切り替えて強調を表現（CIDフォントに太字バリアントが無いため）
    ---       区切り（余白）

★変換した .pdf は必ず開いて目視すること。禁則処理・折り返しは reportlab 標準のままで、
  契約書のような厳密な体裁確認はしていない。
"""

import re
import sys
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem,
)

GOTHIC = "HeiseiKakuGo-W5"
MINCHO = "HeiseiMin-W3"

pdfmetrics.registerFont(UnicodeCIDFont(GOTHIC))
pdfmetrics.registerFont(UnicodeCIDFont(MINCHO))

BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def bold_to_font_tag(text):
    """**強調** を reportlab の <font name=...> タグへ変換する（太字の代わりにゴシック体）。"""
    return BOLD_RE.sub(lambda m: f'<font name="{GOTHIC}">{m.group(1)}</font>', text)


STYLES = {
    "h1": ParagraphStyle("h1", fontName=GOTHIC, fontSize=16, leading=22,
                          alignment=TA_CENTER, spaceAfter=14),
    "h2": ParagraphStyle("h2", fontName=GOTHIC, fontSize=13, leading=18,
                          alignment=TA_LEFT, spaceBefore=12, spaceAfter=6),
    "h3": ParagraphStyle("h3", fontName=GOTHIC, fontSize=11, leading=16,
                          alignment=TA_LEFT, spaceBefore=8, spaceAfter=4),
    "body": ParagraphStyle("body", fontName=MINCHO, fontSize=10.5, leading=16,
                            alignment=TA_LEFT, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName=MINCHO, fontSize=9.5, leading=13),
    "cell_head": ParagraphStyle("cell_head", fontName=GOTHIC, fontSize=9.5, leading=13),
    "li": ParagraphStyle("li", fontName=MINCHO, fontSize=10.5, leading=15),
}


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_separator_row(line):
    return bool(re.fullmatch(r"\|[\s:\-|]+\|", line.strip()))


def convert(src: Path, dst: Path):
    lines = src.read_text(encoding="utf-8").splitlines()
    doc = SimpleDocTemplate(
        str(dst), pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
    )
    story = []

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # 表
        if stripped.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                if not is_separator_row(lines[i]):
                    rows.append(split_row(lines[i]))
                i += 1
            if rows:
                width = max(len(r) for r in rows)
                data = []
                for r_idx, row in enumerate(rows):
                    cells = []
                    style = STYLES["cell_head"] if r_idx == 0 else STYLES["cell"]
                    for c_idx in range(width):
                        text = row[c_idx] if c_idx < len(row) else ""
                        cells.append(Paragraph(bold_to_font_tag(text), style))
                    data.append(cells)
                table = Table(data, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ]))
                story.append(table)
                story.append(Spacer(1, 8))
            continue

        # 区切り
        if re.fullmatch(r"-{3,}", stripped):
            story.append(Spacer(1, 10))
            i += 1
            continue

        # 見出し
        if stripped.startswith("### "):
            story.append(Paragraph(bold_to_font_tag(stripped[4:]), STYLES["h3"]))
            i += 1
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(bold_to_font_tag(stripped[3:]), STYLES["h2"]))
            i += 1
            continue
        if stripped.startswith("# "):
            story.append(Paragraph(bold_to_font_tag(stripped[2:]), STYLES["h1"]))
            i += 1
            continue

        # 箇条書き
        m_ul = re.match(r"^-\s+(.*)$", stripped)
        if m_ul:
            items = []
            while i < n and re.match(r"^-\s+(.*)$", lines[i].strip()):
                text = re.match(r"^-\s+(.*)$", lines[i].strip()).group(1)
                items.append(ListItem(Paragraph(bold_to_font_tag(text), STYLES["li"])))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", start="・",
                                       leftIndent=14))
            story.append(Spacer(1, 4))
            continue

        m_ol = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if m_ol:
            items = []
            while i < n and re.match(r"^\d+[.)]\s+(.*)$", lines[i].strip()):
                text = re.match(r"^\d+[.)]\s+(.*)$", lines[i].strip()).group(1)
                items.append(ListItem(Paragraph(bold_to_font_tag(text), STYLES["li"])))
                i += 1
            story.append(ListFlowable(items, bulletType="1", leftIndent=14))
            story.append(Spacer(1, 4))
            continue

        # 引用は本文として扱う
        if stripped.startswith("> "):
            stripped = stripped[2:]

        story.append(Paragraph(bold_to_font_tag(stripped), STYLES["body"]))
        i += 1

    doc.build(story)
    return dst


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = Path(sys.argv[1]).expanduser()
    if not src.exists():
        print("入力が見つかりません: %s" % src)
        sys.exit(1)
    dst = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else src.with_suffix(".pdf")
    convert(src, dst)
    print("書き出しました: %s (%d バイト)" % (dst, dst.stat().st_size))


if __name__ == "__main__":
    main()
