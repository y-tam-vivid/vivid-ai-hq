#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""レガシー17分類 → 部門軸アーカイブ の仕分け（段1=機械／段2=Haiku／段3=人）

  python3 drive_sort.py --cat 08_契約・法務              提案を作る（動かさない）
  python3 drive_sort.py --cat 08_契約・法務 --apply      提案どおりに動かす（ログを残す）

★段1（AIを使わない）で決まるものは段2へ流さない
★段2は Haiku だけ（--model haiku）。迷ったら上位へ上げず _要判断 へ
★機微（個人名・処分・診断・給与）はモデルに関係なく規則で _機微 へ寄せる
★日付は ①名前の中の日付 ②中身の日付 ③作成日(birthtime) の順。更新日は使わない
"""
import os, re, sys, json, subprocess, unicodedata as u, datetime, argparse, zipfile, hashlib

B = "/Users/yujimac/Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com/マイドライブ"
ARC = B + "/Downloads書類アーカイブ"
DEP = B + "/00_部門軸アーカイブ"
nfc = lambda s: u.normalize("NFC", s)

# ── 段1：機械で決まるもの ───────────────────────────────
BIZ = {  # 名前に出たら確定する固有名詞 → 部門
    "オレンジワークス": "15_施設運営", "SWELL": "15_施設運営", "リアンライフ": "15_施設運営",
    "LIFE STAND UP": "15_施設運営", "STAND UP": "15_施設運営", "ILIFE": "15_施設運営",
    "こどもステーション": "12_マーケティング", "かわちばなし": "12_マーケティング",
    "社畜眼鏡": "12_マーケティング", "マネーシンギュラリティ": "12_マーケティング",
    "GameBull": "13_営業", "ゲームブル": "13_営業",
}
SENSITIVE = ["是正勧告", "勧告書", "診断", "障害者手帳", "給与", "賃金台帳", "源泉", "扶養",
             "児童管理", "個人情報", "履歴書", "職務経歴", "健康診断", "返戻", "過誤",
             "退職", "懲戒", "示談", "訴訟", "被害", "通帳", "マイナンバー"]
DATE_RE = [
    (re.compile(r"(20\d{2})[-_./年]\s*(\d{1,2})[-_./月]\s*(\d{1,2})"), lambda m: "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))),
    (re.compile(r"(20\d{2})[-_./年]\s*(\d{1,2})月?"), lambda m: "%s-%02d-01" % (m.group(1), int(m.group(2)))),
    (re.compile(r"\b(\d{2})[.年](\d{1,2})[.月](\d{1,2})"), lambda m: "20%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))),
    (re.compile(r"(20\d{2})年度"), lambda m: "%s-04-01" % m.group(1)),
]


def date_from_name(name):
    for rx, f in DATE_RE:
        m = rx.search(name)
        if m:
            try:
                y = int(f(m)[:4])
                if 2015 <= y <= datetime.date.today().year + 1:
                    return f(m)
            except Exception:
                pass
    return None


def birth(path):
    st = os.stat(path)
    return datetime.date.fromtimestamp(getattr(st, "st_birthtime", st.st_mtime)).isoformat()


def folder_date(path):
    """フォルダは中でいちばん新しいファイルの作成日（★フォルダ自身の日付は使わない）"""
    best = None
    for root, _, fs in os.walk(path):
        for f in fs:
            if f.startswith("."):
                continue
            d = date_from_name(nfc(f)) or birth(os.path.join(root, f))
            if best is None or d > best:
                best = d
    return best or birth(path)


def extract(path, limit=1200):
    """中身の先頭を取る。取れない種類は空文字（★取れないことを隠さない）"""
    e = os.path.splitext(path)[1].lower()
    try:
        if e in (".txt", ".md", ".csv", ".rtf"):
            t = open(path, "rb").read(20000).decode("utf-8", "ignore")
            if e == ".rtf":
                t = re.sub(r"\\[a-z]+-?\d*\s?|[{}]", " ", t)
            return t[:limit]
        if e == ".pdf":
            import pypdf
            r = pypdf.PdfReader(path)
            return "".join((p.extract_text() or "") for p in r.pages[:3])[:limit]
        if e in (".docx", ".doc"):
            return subprocess.run(["textutil", "-convert", "txt", "-stdout", path],
                                  capture_output=True, text=True, timeout=30).stdout[:limit]
        if e in (".xlsx", ".xlsm"):
            with zipfile.ZipFile(path) as z:
                if "xl/sharedStrings.xml" in z.namelist():
                    x = z.read("xl/sharedStrings.xml").decode("utf-8", "ignore")
                    return " ".join(re.findall(r"<t[^>]*>([^<]+)</t>", x))[:limit]
        if e in (".pptx",):
            with zipfile.ZipFile(path) as z:
                out = []
                for n in [n for n in z.namelist() if n.startswith("ppt/slides/slide")][:4]:
                    out += re.findall(r"<a:t>([^<]+)</a:t>", z.read(n).decode("utf-8", "ignore"))
                return " ".join(out)[:limit]
    except Exception:
        return ""
    return ""


def peek(path):
    """対象（ファイル or フォルダ）の手がかりを集める"""
    name = nfc(os.path.basename(path))
    if os.path.isdir(path):
        inner = []
        for root, _, fs in os.walk(path):
            for f in fs[:40]:
                if not f.startswith("."):
                    inner.append(nfc(f))
        body = ""
        for root, _, fs in os.walk(path):
            for f in sorted(fs):
                if f.startswith("."):
                    continue
                body = extract(os.path.join(root, f))
                if body.strip():
                    break
            if body.strip():
                break
        return {"name": name, "kind": "フォルダ", "inner": inner[:25],
                "date": date_from_name(name) or folder_date(path), "body": body}
    return {"name": name, "kind": "ファイル", "inner": [],
            "date": date_from_name(name) or birth(path), "body": extract(path)}


def stage1(info):
    """機械で決まるもの＝日付・機微・★対象のヒント（固有名詞）

    ★2026-10-14 修正：固有名詞で部門を決めてはいけない。
      同じ ILIFE 宛でも、契約書は法務・請求書は経理・支援記録は施設運営。
      固有名詞は「誰の書類か（対象）」であって「どの部門の仕事か」ではない。
    """
    hay = info["name"] + " " + " ".join(info["inner"]) + " " + info["body"][:400]
    sens = [w for w in SENSITIVE if w in hay]
    hints = [k for k in BIZ if k in hay]
    return {"ヒント": hints, "機微": sens}


HAIKU_PROMPT = """あなたはふくち。グループの書類を仕分けます。JSONだけを返してください。

部門は次のどれか1つ：
10_経営企画室 / 11_事業開発 / 12_マーケティング / 13_営業 / 14_管理 / 15_施設運営 / _個人(本人限定) / 不明

種類は次のどれか1つ：
契約書 / 請求書 / 提案書 / 議事録 / 資料 / 様式 / 報告書 / 申請 / データ / 記録 / 素材 / 不明

返す形（JSONのみ・説明文を付けない）：
{"部門":"13_営業","種類":"資料","対象":"相手や案件の名前","要点":"短く","確信":"高|中|低"}

★迷ったら 確信:"低" にして 部門:"不明" を返すこと。無理に当てない。
★「対象」は人名・社名・案件名。分からなければ空文字。

--- 名前
%s
--- 種別
%s
--- 中の主なファイル
%s
--- 中身の先頭
%s
--- 名前に出てくる関係先（★部門の決め手にはしない。対象の手がかり）
%s
"""


def stage2(info, hints=()):
    p = HAIKU_PROMPT % (info["name"], info["kind"], " / ".join(info["inner"][:12]),
                        info["body"][:1200], "・".join(hints) or "なし")
    try:
        r = subprocess.run(["claude", "-p", "--model", "haiku", p],
                           capture_output=True, text=True, timeout=120)
        t = r.stdout.strip()
        m = re.search(r"\{.*\}", t, re.S)
        return json.loads(m.group(0)) if m else {"部門": "不明", "確信": "低"}
    except Exception as e:
        return {"部門": "不明", "確信": "低", "err": type(e).__name__}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cat", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    src = None
    for x in os.listdir(ARC):
        if nfc(x) == nfc(a.cat):
            src = os.path.join(ARC, x)
    if not src:
        print("カテゴリが無い:", a.cat); sys.exit(1)

    items = [x for x in sorted(os.listdir(src)) if not x.startswith(".")]
    if a.limit:
        items = items[:a.limit]
    print("対象 %d 個（%s）\n" % (len(items), a.cat))
    plan = []
    for x in items:
        p = os.path.join(src, x)
        info = peek(p)
        s1 = stage1(info)
        tgt = stage2(info, s1["ヒント"])
        conf = tgt.get("確信", "低")
        why = "段2：Haiku" + ("（手がかり %s）" % "・".join(s1["ヒント"]) if s1["ヒント"] else "")
        if s1["機微"]:
            why += " ／★機微語 " + "・".join(s1["機微"][:3])
        dep = tgt.get("部門", "不明")
        if dep == "不明" or conf == "低":
            dest = "_要判断_20261014"
            newname = info["name"]
        else:
            dest = dep + ("/_機微" if s1["機微"] else "")
            tai = (tgt.get("対象") or "").strip()
            you = (tgt.get("要点") or "").strip()[:24]
            if not (tai or you):   # ★Haikuが何も返さなければ元の名前を掃除して使う
                raw = os.path.splitext(info["name"])[0]
                raw = re.sub(r"^\s*20\d{2}[-_./年]\s*\d{1,2}[-_./月]?\s*\d{0,2}日?\s*", "", raw)
                raw = re.sub(r"【[^】]*】", "", raw).strip(" _-")
                tai = raw[:34]
            base = "【%s】%s" % (tgt.get("種類", "資料"), "_".join([t for t in (tai, you) if t])[:46])
            ext = os.path.splitext(info["name"])[1] if info["kind"] == "ファイル" else ""
            newname = "%s%s_v1%s" % (info["date"], base, ext)
        plan.append({"元": info["name"], "先": dest, "新": newname, "根拠": why, "確信": conf})
        print("%-40s → %-28s %s" % (info["name"][:40], dest, conf))
        if dest != "_要判断_20261014":
            print("     %s" % newname[:76])
        print("     %s" % why)

    print("\n合計 %d ／ 要判断 %d" % (len(plan), sum(1 for x in plan if x["先"].startswith("_要判断"))))
    out = "/tmp/drive_sort_%s.json" % re.sub(r"\W", "_", a.cat)
    json.dump(plan, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("提案:", out)
    if not a.apply:
        print("★動かしていません。--apply で実行します")
        return
    import shutil
    ok = 0
    for r in plan:
        s = os.path.join(src, r["元"])
        d = os.path.join(DEP, r["先"])
        os.makedirs(d, exist_ok=True)
        t = os.path.join(d, r["新"])
        if not os.path.exists(s) or os.path.exists(t):
            print("  ★飛ばす:", r["元"][:40]); continue
        shutil.move(s, t); ok += 1
    print("移した:", ok)
    log = os.path.join(DEP, "_整理ログ", "レガシー移行_20261014.json")
    old = json.load(open(log, encoding="utf-8")) if os.path.exists(log) else []
    old.append({"日時": datetime.datetime.now().isoformat(timespec="seconds"),
                "元": "Downloads書類アーカイブ/" + a.cat, "件数": ok,
                "明細": [{"旧": r["元"], "新": r["新"], "先": r["先"]} for r in plan]})
    json.dump(old, open(log, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ログ:", log)


if __name__ == "__main__":
    main()
