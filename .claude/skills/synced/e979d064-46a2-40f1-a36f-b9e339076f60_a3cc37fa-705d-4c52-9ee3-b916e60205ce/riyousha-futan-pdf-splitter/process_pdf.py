#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
利用者負担上限額管理結果表 自動分割・施設別結合スクリプト

【処理内容】
1. 入力PDFを1ページずつに分割
2. 各ページに含まれる「事業所名」のユニーク数だけ複製
3. 施設ごとに該当ページを結合し1つのPDFに
4. ファイル名を「YYYY_MM_施設名_利用者負担上限額管理結果表.pdf」にリネーム
5. <out-base>/YYYY-MM/ 配下に保存

【使い方】
$ python3 process_pdf.py <input_pdf> <mapping_json> [--out-base <folder>]

  input_pdf        : 処理対象のPDFパス
  mapping_json     : Claudeが抽出したマッピングJSONのパス
  --out-base       : 出力先のベースフォルダ（省略時はinput_pdfと同じ階層）

【mapping_json のフォーマット】
{
  "year": 2026,
  "month": 4,
  "pages": {
    "1": ["LIFE STAND UP", "スバル・トータルプランニング(株)ぱすてる"],
    "2": ["LIFE STAND UP"],
    ...
  }
}

==============================================================================
【別書類への流用ポイント】
このスクリプトを別書類用に流用する場合、以下の箇所を書き換えてください。
詳細は同梱の README.md の「7. 別書類への流用方法」も参照。

(A) ファイル名のフォーマット
   → process() 関数内の filename = f"..." の行
(B) 出力サブフォルダ名（年月）のフォーマット
   → process() 関数内の out_dir = ... の行
(C) ファイル名で使えない文字の除去ルール
   → safe_filename() 関数
==============================================================================
"""

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader, PdfWriter


# ------------------------------------------------------------------
# ユーティリティ
# ------------------------------------------------------------------

def normalize_facility(name: str) -> str:
    """事業所名の正規化キー（表記揺れ吸収用）

    - NFKC で全角半角統一
    - 連続するスペース類を1つに圧縮
    - 前後の空白を除去
    """
    if name is None:
        return ""
    s = unicodedata.normalize("NFKC", name)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def safe_filename(name: str) -> str:
    """ファイル名として使えない文字を除去/置換（Windows/macOS両対応）

    ===== カスタマイズポイント (C) =====
    必要に応じて置換ルールを調整してください。
    """
    s = name
    # Windows禁止文字
    s = re.sub(r'[\\/:*?"<>|]', "", s)
    # 行末のドット/スペースはWindowsで問題になる
    s = s.rstrip(". ")
    # 過度に連続するスペースを1つに
    s = re.sub(r"\s+", " ", s)
    return s


def collapse_facilities(names):
    """ページ内の事業所リストから、正規化キーで重複を排除しつつ、
    元の表記（最初に現れたもの）を返す。

    例：["LIFE STAND UP", "LIFE  STAND UP", "Snuggle UP"]
        → display = ["LIFE STAND UP", "Snuggle UP"]
        → keys    = ["LIFE STAND UP", "Snuggle UP"]
    """
    seen = {}
    for n in names:
        key = normalize_facility(n)
        if not key:
            continue
        if key not in seen:
            seen[key] = n  # 元表記を保持
    return list(seen.values()), list(seen.keys())


# ------------------------------------------------------------------
# メイン処理
# ------------------------------------------------------------------

def process(input_pdf: Path, mapping: dict, out_base: Path):
    year = int(mapping["year"])
    month = int(mapping["month"])
    page_map = mapping["pages"]  # {"1": [...], "2": [...]}

    reader = PdfReader(str(input_pdf))
    total_pages = len(reader.pages)
    print(f"[INFO] 入力PDF: {input_pdf.name}（{total_pages}ページ）")

    # 施設キー → [page_index, ...] のマップを構築
    facility_to_pages = defaultdict(list)
    facility_display = {}  # 施設キー → 表示用の事業所名（最初の出現）

    for page_str, facilities in page_map.items():
        page_idx = int(page_str) - 1  # 0始まりに変換
        if page_idx < 0 or page_idx >= total_pages:
            print(f"[WARN] ページ {page_str} はPDF範囲外。スキップ")
            continue
        display_names, keys = collapse_facilities(facilities)
        for disp, key in zip(display_names, keys):
            facility_to_pages[key].append(page_idx)
            facility_display.setdefault(key, disp)

    if not facility_to_pages:
        print("[ERROR] 事業所マッピングが空です。処理を中断します。")
        sys.exit(1)

    # ===== カスタマイズポイント (B): 出力サブフォルダ名のフォーマット =====
    out_dir = out_base / f"{year:04d}-{month:02d}"
    if out_dir.exists():
        print(f"[WARN] 出力フォルダが既に存在します: {out_dir}（既存ファイルは上書きされます）")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 施設ごとにマージしたPDFを書き出し
    print(f"[INFO] 施設数: {len(facility_to_pages)}")
    written = []
    for key, page_indices in facility_to_pages.items():
        display = facility_display[key]
        writer = PdfWriter()
        for idx in page_indices:
            writer.add_page(reader.pages[idx])

        # ===== カスタマイズポイント (A): ファイル名フォーマット =====
        filename = f"{year:04d}_{month:02d}_{safe_filename(display)}_利用者負担上限額管理結果表.pdf"
        out_path = out_dir / filename
        with open(out_path, "wb") as f:
            writer.write(f)
        written.append((display, len(page_indices), out_path))
        print(f"  - {display}: {len(page_indices)}ページ → {out_path.name}")

    print(f"\n[DONE] {len(written)}件のPDFを出力しました")
    print(f"[OUT ] {out_dir}")
    return out_dir, written


# ------------------------------------------------------------------
# エントリポイント
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="利用者負担上限額管理結果表 自動分割・施設別結合スクリプト"
    )
    parser.add_argument("input_pdf", type=Path, help="入力PDFのパス")
    parser.add_argument("mapping_json", type=Path, help="ページ→事業所マッピングのJSONパス")
    parser.add_argument(
        "--out-base",
        type=Path,
        default=None,
        help="出力先のベースフォルダ（省略時はinput_pdfと同じ階層）",
    )
    args = parser.parse_args()

    if not args.input_pdf.exists():
        print(f"[ERROR] 入力PDFが見つかりません: {args.input_pdf}")
        sys.exit(1)
    if not args.mapping_json.exists():
        print(f"[ERROR] マッピングJSONが見つかりません: {args.mapping_json}")
        sys.exit(1)

    with open(args.mapping_json, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    out_base = args.out_base if args.out_base else args.input_pdf.parent
    process(args.input_pdf, mapping, out_base)


if __name__ == "__main__":
    main()
