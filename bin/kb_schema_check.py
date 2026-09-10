#!/usr/bin/env python3
"""かわちばなし ── 表示側（.dc.html）と器（スプレッドシート）のズレを数える。

なぜ要るか ── 2026-09-10、9/9に作った器を土台にして申込フォームを設計したところ、
その翌日に表示側が器の想定していない形へ進んでいた（写真1枚→最大8枚・本文が配列・
applyUrl が独立）。★有璽氏に指摘されるまで気づかなかった。
**人の記憶に依存する検知は必ず漏れる。**

★読むだけ。器へは1文字も書かない。直すのは人。

できること     キーが増えた・減った ／ 区分が増えた・減った ／ 片方にしか無いもの
★できないこと  ★意味が変わったこと。`photo` の名前のまま「1枚」→「1枚目」へ
               変わった今回の型は、この検査では出ない。人が実物を見るしかない
               ＝「0件」は「ズレが無い」ではなく「★名前で見つかるズレは無い」

使い方   python3 bin/kb_schema_check.py
         python3 bin/kb_schema_check.py --dir "<設計フォルダのパス>"
"""
import json
import os
import pathlib
import re
import subprocess
import sys

SHEET_ID = "1mRp6CxNBGtgZ4jpQDTZzHMi074mcEmB0uH0sRFopWtI"
BASE = pathlib.Path.home() / "Downloads" / "かわちばなし_地域イベントポータルサイト設計"

# ★表示側のキー → 器の列。手で持つ（機械には読めない）。
#   新しいキーが出たら、人が意味を確かめてからここへ1行足す。
KEY_TO_COL = {
    "title": "イベント名", "city": "市", "category": "カテゴリ",
    "start": "開始日", "end": "終了日", "time": "開始時刻",
    "venue": "会場", "address": "住所", "access": "最寄り",
    "fee": "料金", "apply": "申込", "applyUrl": "申込先URL",
    "organizer": "主催", "contact": "問い合わせ",
    "links": "その他リンク", "body": "紹介文", "text": "紹介文",
    "photo": "写真URL", "photos": "写真2",
}

# ★描画のためだけに作られる値。器に対応する列は要らない。
DISPLAY_ONLY = {
    "catIconEl", "dateColor", "dateLabel", "ended", "line", "opacity",
    "photoEl", "tint", "place", "photosEl", "applyLinkEl", "linkEls",
}


def latest_dir():
    """設計フォルダのうち番号がいちばん大きいものを選ぶ。"""
    if not BASE.is_dir():
        return None
    cands = []
    for p in BASE.iterdir():
        m = re.search(r"設計\s*(\d+)\s*$", p.name)
        if p.is_dir() and m:
            cands.append((int(m.group(1)), p))
    return max(cands)[1] if cands else None


def keys_in(path):
    """.dc.html から ev.<キー> を全部拾う。"""
    s = path.read_text(encoding="utf-8", errors="replace")
    return {m for m in re.findall(r"\bev\.([a-zA-Z_][a-zA-Z0-9_]*)", s)}


def taxonomy_terms(path):
    """kawachi-taxonomy.js から区分の名前を拾う（JSのまま正規表現で読む）。"""
    s = path.read_text(encoding="utf-8", errors="replace")
    out = {}
    for block, key in (("cities", "name"), ("categories", "label"),
                       ("spotCategories", "label"), ("specialCategories", "label")):
        m = re.search(block + r":\s*\[(.*?)\n\s*\]", s, re.S)
        out[block] = re.findall(key + r":\s*'([^']+)'", m.group(1)) if m else []
    m = re.search(r"linkTypes:\s*\{(.*?)\n\s*\},\s*\n\s*//", s, re.S)
    out["linkTypes"] = re.findall(r"^\s*'([^']+)':", m.group(1), re.M) if m else []
    return out


def read_sheet():
    """器は mini からしか読めない（認証がminiにある）。ssh で取ってくる。"""
    code = (
        'import sys,json; sys.path.insert(0,"/Users/yuji_macmini/.vivid-relay"); '
        'from sheets_client import Sheets; sh=Sheets(); '
        'ev=sh.read("%s","イベント"); ch=sh.read("%s","選択肢"); '
        'print(json.dumps({"cols":ev[0],"choices":ch}, ensure_ascii=False))' % (SHEET_ID, SHEET_ID)
    )
    r = subprocess.run(["ssh", "mini", "python3 -c '%s'" % code],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("器を読めなかった：%s" % (r.stderr.strip()[-300:] or "理由不明"))
    return json.loads(r.stdout.strip().splitlines()[-1])


def column_of(choices, name):
    """選択肢タブの1行目から列を探し、その下の値を並べる。"""
    head = choices[0]
    if name not in head:
        return None
    i = head.index(name)
    return [row[i] for row in choices[1:] if len(row) > i and row[i]]


def main():
    d = None
    if "--dir" in sys.argv:
        d = pathlib.Path(sys.argv[sys.argv.index("--dir") + 1])
    d = d or latest_dir()
    if not d or not d.is_dir():
        print("★設計フォルダが見つからない：%s" % BASE)
        return 1

    detail = d / "イベント詳細.dc.html"
    tax = d / "kawachi-taxonomy.js"
    for p in (detail, tax):
        if not p.exists():
            print("★%s が無い（%s）" % (p.name, d.name))
            return 1

    print("★見ているもの")
    print("  表示側 ： %s" % d.name)
    print("  器     ： かわちばなし イベント情報（mini 経由で読む）")
    print("")

    sheet = read_sheet()
    cols = [c for c in sheet["cols"] if c]
    keys = keys_in(detail) - DISPLAY_ONLY
    terms = taxonomy_terms(tax)

    ng = 0

    # ① 表示側のキー ⇄ 器の列
    unknown = sorted(k for k in keys if k not in KEY_TO_COL)
    missing = sorted({KEY_TO_COL[k] for k in keys if k in KEY_TO_COL} - set(cols))
    print("① 表示側のキー %d個 ⇄ 器の列 %d個" % (len(keys), len(cols)))
    if unknown:
        ng += len(unknown)
        print("   ★対応表に無いキー %d件 ── 意味を確かめて KEY_TO_COL へ足すこと" % len(unknown))
        for k in unknown:
            print("      ev.%s" % k)
    if missing:
        ng += len(missing)
        print("   ★器に無い列 %d件 ── 列を足すこと" % len(missing))
        for c in missing:
            print("      %s" % c)
    if not unknown and not missing:
        print("   ✓ 対応している")

    # ② 区分（taxonomy ⇄ 選択肢タブ）
    print("")
    print("② 区分（kawachi-taxonomy.js ⇄ 選択肢タブ）")
    for block, colname in (("cities", "市"), ("categories", "カテゴリ"),
                           ("linkTypes", "リンクの種類")):
        want, got = terms.get(block, []), column_of(sheet["choices"], colname)
        if got is None:
            ng += 1
            print("   ★選択肢タブに『%s』の列が無い" % colname)
            continue
        # 「その他」は taxonomy 側が fallback で持つことがあるので差の判定から外す
        a, b = set(want) - {"その他"}, set(got) - {"その他"}
        if a == b:
            print("   ✓ %-12s %d件" % (colname, len(b)))
        else:
            ng += 1
            print("   ★%s が食い違う" % colname)
            if a - b:
                print("      表示側にあって器に無い ： %s" % "／".join(sorted(a - b)))
            if b - a:
                print("      器にあって表示側に無い ： %s" % "／".join(sorted(b - a)))

    # ③ 器がまだ無い区分
    print("")
    print("③ 器がまだ無いもの")
    for block, label in (("spotCategories", "スポット"), ("specialCategories", "特集・読みもの")):
        if terms.get(block):
            print("   ★%s の区分が %d件あるが、器（スプレッドシート）はまだ無い"
                  % (label, len(terms[block])))

    print("")
    if ng:
        print("★食い違い 合計 %d 件。★人が中身を確かめて直すこと" % ng)
    else:
        print("★名前で見つかる食い違いは 0 件。")
        print("  ただし★これは「ズレが無い」ではない。")
        print("  ★同じ名前のまま意味が変わった変更（写真1枚→1枚目 など）は出ない。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("★検査そのものが落ちた：%s: %s" % (type(e).__name__, e))
        sys.exit(1)
