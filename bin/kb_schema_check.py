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
    """設計フォルダのうち番号がいちばん大きいものを選ぶ。

    ★番号がいちばん大きいものと、更新がいちばん新しいものを両方見る。
      食い違ったらそれ自体を知らせる ── フォルダ名の付け方が変わったとき、
      番号だけを見ていると★新しい版を見落としたまま「0件」を出してしまうため。
    """
    if not BASE.is_dir():
        return None, None
    cands = []
    for p in BASE.iterdir():
        m = re.search(r"設計\s*(\d+)\s*$", p.name)
        if p.is_dir() and m:
            cands.append((int(m.group(1)), p))
    if not cands:
        return None, None
    by_num = max(cands)[1]
    # ★番号の付いていないフォルダも含めて、更新のいちばん新しいものを見る
    alls = [p for p in BASE.iterdir() if p.is_dir()]
    by_time = max(alls, key=lambda p: p.stat().st_mtime) if alls else by_num
    return by_num, (None if by_time == by_num else by_time)


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


PROC_NAME = "かわちばなし 器と表示側のズレ検査"

# ★前回の「形」を置く場所。名前が変わらない変更を出すために要る。
STATE = pathlib.Path.home() / ".vivid-relay" / "kb_schema_state.json"


def shapes(path):
    """★キーの名前だけでなく「値の形」を覚える。

    なぜ要るか ── 2026-09-10、本文が「テキスト」から「段落と写真の配列」へ変わったのに、
    ★キー名（body）が同じだったので名前の突合では出なかった。
    **意味の変化の多くは、構造の変化として現れる。**
    """
    s = path.read_text(encoding="utf-8", errors="replace")
    i = s.find("get samples()")
    if i < 0:
        return {}
    body = s[i:]
    seen = {}
    for m in re.finditer(r"[\s{,]([a-zA-Z_][a-zA-Z0-9_]*):\s*(.)", body):
        key, first = m.group(1), m.group(2)
        kind = {"'": "文字列", '"': "文字列", "[": "配列", "{": "かたまり"}.get(first)
        kind = kind or ("数値" if first.isdigit() else "その他")
        # ★同じキーは複数のサンプルに出る。出てきた形を「全部」持つ。
        #   いちばん重い形だけを採ると、★一部のサンプルだけ変わったときに出ない
        #   （2026-09-10 実測で見つけた欠陥。body が1件だけ文字列へ戻っても出なかった）
        seen.setdefault(key, set()).add(kind)
    out = {k: "／".join(sorted(v)) for k, v in seen.items()}

    # ★配列の中身まで見る。長さと、要素の種類が変わったら出す
    lens = [len(re.findall(r"['\"]", m.group(1))) // 2
            for m in re.finditer(r"photos:\s*\[([^\]]*)\]", body)]
    if lens:
        out["_写真の最大枚数"] = str(max(lens))
    tags = sorted({m.group(1) for m in re.finditer(r"\[\s*'([a-z]+)'\s*,", body)})
    if tags:
        out["_本文に出てくる種類"] = "／".join(tags)
    return out


def compare_shapes(now, prev):
    """前回と今回の形を比べる。★初回は基準を作るだけで、食い違いには数えない。"""
    if prev is None:
        return ["   ・前回の記録が無いので、いまの形を基準として保存した"], 0
    lines, ng = [], 0
    for k in sorted(set(now) | set(prev)):
        a, b = prev.get(k), now.get(k)
        if a == b:
            continue
        ng += 1
        if a is None:
            lines.append("   ★%s が新しく出てきた（%s）" % (k, b))
        elif b is None:
            lines.append("   ★%s が消えた（前回は %s）" % (k, a))
        else:
            lines.append("   ★%s の形が変わった ： %s → %s" % (k, a, b))
    return (lines or ["   ✓ 前回と同じ形"]), ng


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_state(d):
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception as e:
        print("   ★形を保存できなかった：%s" % e)


def _relay():
    sys.path.insert(0, str(pathlib.Path.home() / ".vivid-relay"))


def send(title, body):
    """★食い違いが出たときだけ呼ぶ。0件のときは黙る（慢性の通知を作らない）。"""
    _relay()
    import notify
    return notify.tell(title, body)


def beat(result, message):
    _relay()
    import heartbeat
    heartbeat.beat(PROC_NAME, result, message)


def run():
    d, newer = None, None
    if "--dir" in sys.argv:
        d = pathlib.Path(sys.argv[sys.argv.index("--dir") + 1])
    else:
        d, newer = latest_dir()
    if not d or not d.is_dir():
        print("★設計フォルダが見つからない：%s" % (d or BASE))
        return -1   # ★食い違い1件（=1）と区別するため負の値を返す

    detail = d / "イベント詳細.dc.html"
    tax = d / "kawachi-taxonomy.js"
    for p in (detail, tax):
        if not p.exists():
            print("★%s が無い（%s）" % (p.name, d.name))
            return -1

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

    # ④ ★前回からの「形」の変化 ── 名前が変わらない変更はここで出る
    print("")
    print("④ 前回からの形の変化（★名前が同じままの変更をここで出す）")
    now = shapes(detail)
    st = load_state() or {}
    lines, dng = compare_shapes(now, st.get("イベント詳細"))
    ng += dng
    for L in lines:
        print(L)

    # ★鳴った日を残す。「鳴ったのに直さないまま忘れた」を後から追えるようにする
    hist = st.get("履歴", [])
    if dng:
        import datetime
        hist.append({"日": datetime.date.today().isoformat(),
                     "見たフォルダ": d.name, "変化": [x.strip() for x in lines]})
    save_state({"イベント詳細": now, "最後に見たフォルダ": d.name, "履歴": hist[-20:]})
    if hist and dng == 0:
        print("   （前に形が変わった日 ： %s。直したかどうかは人が見ること）"
              % "／".join(h["日"] for h in hist[-3:]))

    # ⑤ ★見ているフォルダが本当に最新か（番号だけを信じない）
    if newer is not None:
        ng += 1
        print("")
        print("⑤ ★見ているフォルダより新しいものがある")
        print("   見た     ： %s" % d.name)
        print("   ★新しい ： %s" % newer.name)
        print("   ★フォルダ名の付け方が変わった可能性。どちらが正か人が確かめること")

    print("")
    if ng:
        print("★食い違い 合計 %d 件。★人が中身を確かめて直すこと" % ng)
    else:
        print("★名前で見つかる食い違いは 0 件。")
        print("  ただし★これは「ズレが無い」ではない。")
        print("  ★同じ名前のまま意味が変わった変更（写真1枚→1枚目 など）は出ない。")
    return ng


def main():
    """★画面へは必ず全部出す。Slackへは食い違いがあるときだけ出す。"""
    import contextlib
    import io
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            ng = run()
    except Exception as e:
        print(buf.getvalue(), end="")
        msg = "★検査そのものが落ちた：%s: %s" % (type(e).__name__, e)
        print(msg)
        if "--beat" in sys.argv:
            beat("失敗", msg[:200])
        return 1

    text = buf.getvalue()
    print(text, end="")

    if ng is None or ng < 0:          # 設計フォルダが無い等（run が 1 を返した場合を含む）
        if "--beat" in sys.argv:
            beat("警告", "見に行く先が見つからなかった")
        return 1

    if "--notify" in sys.argv and ng:
        # ★本文はそのまま送る。人が読んで判断する材料だけを渡し、直し方は書かない
        send("かわちばなし ── 器と表示側のズレ %d件" % ng, text.strip())
    if "--beat" in sys.argv:
        beat("成功", "食い違い %d件" % ng)
    return 0


if __name__ == "__main__":
    sys.exit(main())
