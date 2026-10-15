#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""補助金・助成金の書類を3つに割って置き直す（有璽氏の決定 #187f61「1」・2026-10-15）

> 1 中身を直す人で3つに割る（制度＝営業／道具＝営業／自社の申請＝管理）

★高級ルール「正本は中身を直す人の部署に置く、使う人はショートカットで引く」の適用。
★見分け方は1つ ──「次に中身を書き換えるのは誰か」

  ①制度の原本（省庁・労働局・都道府県・公募を探す一覧）  → 13_営業/13-100_法人コンサル部
      誰も中身を直さない。差し替えるのは制度の改定を追う人＝商材の素
  ②自社が作った営業の道具（セミナー資料・ヒアリングシート・提案・事例・申請の流れ）
                                                      → 13_営業
  ③自社が申請した分の実務書類（自社法人の申請書・交付決定・実績報告・不備案内・支払）
      労務系（業務改善・キャリアアップ・人材開発支援・訓練計画）→ 14_管理/14-100_労務部
      経費・設備系（IT導入・ものづくり・持続化）／支払・請求   → 14_管理/14-200_経理部
  ④顧客・他社の案件（顧客の申請を支援した記録・他社の申請書） → 13_営業

★①②④が全部 13_営業 系になるのは正しい（補助金は商材だから）。
  分ける意味は★③を混ぜないこと ── 自社の申請書は営業の棚に置かない。

使い方
  python3 bin/drive_hojokin.py           提案だけ（1件も動かさない）
  python3 bin/drive_hojokin.py --apply   実行（旧名→新名→先 をログへ残す＝戻せる）
"""
import os, re, sys, json, shutil, datetime, argparse, subprocess
import unicodedata as u
import importlib.util

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("ds", os.path.join(_here, "drive_sort.py"))
ds = importlib.util.module_from_spec(_spec)
try:
    _spec.loader.exec_module(ds)
except SystemExit:
    pass

DEP = ds.DEP
LOG = os.path.join(DEP, "_整理ログ", "レガシー移行_20261014.json")
nfc = lambda s: u.normalize("NFC", s)
PAT = re.compile(r"補助金|助成金|奨励金")

# ★自社グループの法人・施設。これが申請者なら③
OURS = ["ふくち", "ビビッド", "ILIFE", "SWELL", "LIFE STAND UP", "STAND UP",
        "オレンジワークス", "リアンライフ", "いきいきステーション", "タチバナ",
        "ライフスタディ", "ILIFEスタディ"]

PROMPT = """補助金・助成金の書類を、置き場で4つに分けます。JSONだけを返してください。

★判定の基準は1つだけ ──「次にこの中身を書き換えるのは誰か」

1 … ★制度の原本。省庁・労働局・都道府県・市区町村・公的機関が出した案内・要項・
     様式・書類リスト、または公募を探すための一覧。★誰も中身を書き換えない
2 … ★自社（ふくち。グループ＝ふくち。／ビビッド／ILIFE／SWELL SOCIETY／
     LIFE STAND UP／オレンジワークス／リアンライフ）が作った営業の道具。
     セミナー資料・提案資料・ヒアリングシート・申請の流れの説明・事例・プレゼン
3 … ★自社グループの法人が申請者になっている実務書類。
     自社の申請書・交付決定通知・実績報告・不備の案内・自社が払った請求書
4 … ★顧客や他社が申請者の案件。顧客の申請書・顧客向けの要件整理・他社の資料・
     他社からの請求書・申請事業所の一覧

★3と4の違いは「申請者が自社グループか、他社か」。ここだけは必ず中身で見てください。
★1と2の違いは「公的機関が作ったか、自社が作ったか」。
★迷ったら 4 を返してください（営業の棚に入るので、後から動かしやすい）。

3 のときだけ、さらに次を返してください：
  "系": "労務"   業務改善助成金・キャリアアップ・人材開発支援・訓練計画・雇用関係
  "系": "経理"   IT導入・ものづくり・持続化・省力化・設備・経費・支払・請求

名前：%s
種類：%s
中にあるもの：%s
中身の先頭：
%s

返す形（JSONだけ・説明を書かない）
{"区分": 1, "系": "", "申請者": "誰が申請者か20字以内", "理由": "20字以内"}
"""

DEST = {1: "13_営業/13-100_法人コンサル部", 2: "13_営業", 4: "13_営業"}


def judge(info):
    s, wd = ds._iso()
    p = PROMPT % (info["name"], info["kind"], " / ".join(info["inner"][:12]),
                  info["body"][:1200])
    try:
        r = subprocess.run(["claude", "-p", "--model", "haiku", "--settings", s, p],
                           capture_output=True, text=True, timeout=180, cwd=wd)
        m = re.search(r"\{.*\}", r.stdout.strip(), re.S)
        if m:
            return json.loads(m.group(0))
        return {"区分": 0, "理由": "JSONなし", "生": r.stdout.strip()[:120]}
    except Exception as e:
        return {"区分": 0, "理由": type(e).__name__}


def targets():
    """★部門直下・部直下・_機微直下・_要判断直下だけ。
    他の集まりの中に在るものは、その集まりの持ち物なので触らない"""
    out = []
    for dep in sorted(os.listdir(DEP)):
        dp = os.path.join(DEP, dep)
        if not os.path.isdir(dp) or nfc(dep).startswith(("_整理", "_運用")):
            continue
        levels = [("", dp)]
        for sub in sorted(os.listdir(dp)):
            sp = os.path.join(dp, sub)
            if os.path.isdir(sp) and (re.match(r"\d\d-\d00_", nfc(sub)) or nfc(sub) == "_機微"):
                levels.append((nfc(sub), sp))
        for subname, path in levels:
            for x in sorted(os.listdir(path)):
                if x.startswith(".") or not PAT.search(nfc(x)):
                    continue
                rel = nfc(dep) + ("/" + subname if subname else "")
                out.append({"元の先": rel, "名前": nfc(x), "実体": os.path.join(path, x)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    t = judge({"name": "検証.pdf", "kind": "ファイル", "inner": [],
               "body": "厚生労働省が出した業務改善助成金の制度案内です。"})
    if t.get("区分") == 0:
        print("★段2（Haiku）が使えない：", t.get("理由"), t.get("生", ""))
        sys.exit(2)
    print("段2の動作確認 OK（区分=%s）\n" % t.get("区分"))

    rows = targets()
    if a.limit:
        rows = rows[:a.limit]
    print("対象 %d 件（部門直下・部直下・_機微直下・_要判断直下だけ）\n" % len(rows))

    plan, ng = [], 0
    for r in rows:
        info = ds.peek(r["実体"])
        j = judge(info)
        k = j.get("区分", 0)
        if k == 0:
            ng += 1
            print("★判定できず %-52s （%s）" % (r["名前"][:52], j.get("理由")))
            continue
        if k == 3:
            kei = (j.get("系") or "").strip()
            dest = "14_管理/14-100_労務部" if kei == "労務" else "14_管理/14-200_経理部"
        else:
            dest = DEST[k]
        # ★機微は名前の規則が優先（_機微 の下に在るものは _機微 のまま）
        if "_機微" in r["元の先"]:
            dest += "/_機微"
        if nfc(dest) == nfc(r["元の先"]):
            print("そのまま 区分%s %-50s （既に %s）" % (k, r["名前"][:50], dest))
            continue
        plan.append({**r, "先": dest, "区分": k,
                     "申請者": j.get("申請者", ""), "理由": j.get("理由", "")})
        print("動かす 区分%s %-50s" % (k, r["名前"][:50]))
        print("        %s → %s" % (r["元の先"], dest))
        print("        申請者=%s ／ %s" % (j.get("申請者", ""), j.get("理由", "")))

    print("\n動かす %d ／ そのまま %d ／ ★判定できず %d" % (
        len(plan), len(rows) - len(plan) - ng, ng))
    out = "/tmp/drive_hojokin.json"
    json.dump(plan, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("提案:", out)
    if not a.apply:
        print("★1件も動かしていません。--apply で実行します")
        return

    ok, moves = 0, []
    for r in plan:
        if not os.path.exists(r["実体"]):
            print("★飛ばす（元が無い）:", r["名前"][:50]); continue
        d = os.path.join(DEP, *r["先"].split("/"))
        os.makedirs(d, exist_ok=True)
        tgt = os.path.join(d, os.path.basename(r["実体"]))
        if os.path.exists(tgt):
            print("★飛ばす（先に同名）:", r["名前"][:50]); continue
        shutil.move(r["実体"], tgt)
        ok += 1
        moves.append({"旧": r["名前"], "新": r["名前"], "先": r["先"],
                      "元の先": r["元の先"], "区分": r["区分"], "理由": r["理由"]})
        print("動かした:", r["名前"][:50], "→", r["先"])

    b = json.load(open(LOG, encoding="utf-8"))
    b.append({"日時": datetime.datetime.now().isoformat(timespec="seconds"),
              "元": "00_部門軸アーカイブ（補助金・助成金を3分割・有璽氏 #187f61 の「1」）",
              "件数": ok, "明細": moves})
    json.dump(b, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n動かした %d 件 ／ ログ: %s" % (ok, LOG))


if __name__ == "__main__":
    main()
