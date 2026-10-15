#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_機微 に入れすぎたものを出す ── 有璽氏の判断 #03479b「3」（2026-10-15 09:03）

> 3 公的機関の案内・様式・自社の商材だけ _機微 から出す

★なぜ要るか
  10/15 朝、機微語に当たったものを全部 _機微 へ寄せる形にしたところ、
  ★本文の先頭400字に語が1回出ただけで隔離していた（実測76件中40件）。
  厚労省の助成金案内と、従業員Nの雇用契約が同じ箱に入った。
  規則側は「名前に出たときだけ隔離」へ直した（drive_sort.py・commit 5ed38c8）が、
  ★すでに入れてしまった40件は、この道具で出す。

★出すのは2種類だけ（有璽氏の選択どおり・それ以外は触らない）
  ① 公的機関（省庁・自治体・労働局・公的基金）が出した案内・様式・要項・申請書
  ② ふくち。グループ自身の商材・サービスの説明（売り物の紹介）
  ★それ以外（特定の個人・特定の取引先の内情を含みうるもの）は _機微 のまま

使い方
  python3 bin/drive_unkibi.py            提案だけ（1件も動かさない）
  python3 bin/drive_unkibi.py --apply    実行（旧名→新名→先 をログへ残す＝戻せる）
"""
import os, sys, json, re, shutil, datetime, argparse, subprocess
import unicodedata as u

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "ds", os.path.join(os.path.dirname(os.path.abspath(__file__)), "drive_sort.py"))
ds = importlib.util.module_from_spec(_spec)
try:
    _spec.loader.exec_module(ds)
except SystemExit:
    pass

DEP = ds.DEP
LOG = os.path.join(DEP, "_整理ログ", "レガシー移行_20261014.json")
nfc = lambda s: u.normalize("NFC", s)

PROMPT = """次の書類が、どれに当たるかを判定してください。JSONだけを返します。

区分は3つだけです。
1 … ★公的機関（省庁・労働局・都道府県・市区町村・公的な基金や財団）が出した
     案内・様式・要項・申請書・書類リスト。★誰でも手に入る「制度の説明」
2 … ★ふくち。グループ自身の商材・サービスの説明（売り物の紹介・提供項目の一覧・
     自社の会社案内・自社の提案の型）。★特定の相手の事情が書かれていないもの
3 … ★上のどちらでもない。とくに次のどれかに当たるなら必ず 3
     ・特定の個人の情報（氏名のある勤怠・給与・経歴・診断・資産・契約）
     ・特定の取引先の内情（債権債務・破産・値引き・社内限りの面談メモ）
     ・自社の従業員・利用者・児童の情報
     ・ログインの情報やアカウントの引き継ぎ

★迷ったら 3 を返してください（出さないほうが安全です）。

名前：%s
種類：%s
中にあるもの：%s
中身の先頭：
%s

返す形（JSONだけ・説明を書かない）
{"区分": 1, "理由": "20字以内"}
"""


def judge(info):
    p = PROMPT % (info["name"], info["kind"], " / ".join(info["inner"][:12]),
                  info["body"][:1200])
    try:
        r = subprocess.run(["claude", "-p", "--model", "haiku", p],
                           capture_output=True, text=True, timeout=120)
        m = re.search(r"\{.*\}", r.stdout.strip(), re.S)
        return json.loads(m.group(0)) if m else {"区分": 3, "理由": "返りを読めない"}
    except Exception as e:
        return {"区分": 3, "理由": type(e).__name__}


def body_only(old_name):
    """★名前では機微に当たらない＝本文だけで隔離していたもの"""
    s1 = ds.stage1({"name": nfc(old_name), "inner": [], "body": "", "kind": "ファイル"})
    return not (s1.get("契約原本") or s1.get("労務") or s1.get("採用") or s1["機微"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    batches = json.load(open(LOG, encoding="utf-8"))
    targets = []
    for b in batches:
        if b.get("作業", "移動") != "移動":
            continue
        for m in b.get("明細", []):
            dest = m.get("先", "")
            if "_機微" not in dest:
                continue
            if not body_only(m["旧"]):
                continue
            targets.append({"旧": nfc(m["旧"]), "新": nfc(m["新"]), "先": dest})

    print("★本文だけで _機微 へ入れたもの … %d件\n" % len(targets))
    plan = []
    for t in targets:
        p = os.path.join(DEP, t["先"], t["新"])
        if not os.path.exists(p):
            # NFD で置かれている場合に備えて実体から引く
            d = os.path.join(DEP, t["先"])
            hit = [x for x in os.listdir(d) if nfc(x) == t["新"]] if os.path.isdir(d) else []
            if not hit:
                print("  ★実体が無い（誰かが動かした）:", t["新"][:60]); continue
            p = os.path.join(d, hit[0])
        info = ds.peek(p)
        j = judge(info)
        k = j.get("区分", 3)
        out = t["先"].rsplit("/_機微", 1)[0]          # _機微 を外した親
        if k in (1, 2):
            plan.append({**t, "出す先": out, "区分": k, "理由": j.get("理由", "")})
            print("  出す   %-56s → %s" % (t["新"][:56], out))
            print("         区分%s %s" % (k, j.get("理由", "")))
        else:
            print("  残す   %-56s （区分3 %s）" % (t["新"][:56], j.get("理由", "")))

    print("\n出す %d ／ _機微 に残す %d" % (len(plan), len(targets) - len(plan)))
    out_json = "/tmp/drive_unkibi.json"
    json.dump(plan, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("提案:", out_json)
    if not a.apply:
        print("★1件も動かしていません。--apply で実行します")
        return

    ok, moves = 0, []
    for r in plan:
        d_old = os.path.join(DEP, r["先"])
        hit = [x for x in os.listdir(d_old) if nfc(x) == r["新"]] if os.path.isdir(d_old) else []
        if not hit:
            print("  ★飛ばす（実体が無い）:", r["新"][:50]); continue
        s = os.path.join(d_old, hit[0])
        d = os.path.join(DEP, r["出す先"])
        tgt = os.path.join(d, r["新"])
        if os.path.exists(tgt):
            print("  ★飛ばす（先に同名）:", r["新"][:50]); continue
        os.makedirs(d, exist_ok=True)
        shutil.move(s, tgt)
        ok += 1
        # ★戻せる形で残す：旧＝_機微に在ったときの名前／先＝出した先
        moves.append({"旧": r["新"], "新": r["新"], "先": r["出す先"], "元の先": r["先"]})
        print("  出した:", r["新"][:60], "→", r["出す先"])

    batches.append({"日時": datetime.datetime.now().isoformat(timespec="seconds"),
                    "元": "00_部門軸アーカイブ（_機微 から出す・有璽氏 #03479b の「3」）",
                    "件数": ok, "明細": moves})
    json.dump(batches, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n出した %d 件 ／ ログ: %s" % (ok, LOG))


if __name__ == "__main__":
    main()
