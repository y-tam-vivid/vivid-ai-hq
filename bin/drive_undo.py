#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ドライブ整理の「戻す」道具 ── 有璽氏が「これ違う」と言ったら1件から戻せる

使い方
  python3 ~/vivid-ai-hq/bin/drive_undo.py --list              いま何を移したかを一覧で見る
  python3 ~/vivid-ai-hq/bin/drive_undo.py --find 輪が家        名前の一部で探す（部分一致・NFC）
  python3 ~/vivid-ai-hq/bin/drive_undo.py --undo 輪が家        1件だけ元の場所・元の名前へ戻す
  python3 ~/vivid-ai-hq/bin/drive_undo.py --undo-all 20261014  その日の移動を全部戻す

★移動とリネームを同時にやっているので、戻すときも「場所」と「名前」を両方戻す。
★戻した操作もログに足す（戻したことも記録に残る）。
"""
import os, sys, json, shutil, unicodedata as u, datetime, argparse

B = "/Users/yujimac/Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com/マイドライブ"
DEP = B + "/00_部門軸アーカイブ"
LOGDIR = DEP + "/_整理ログ"
nfc = lambda s: u.normalize("NFC", s)


def load():
    out = []
    if not os.path.isdir(LOGDIR):
        return out
    for f in sorted(os.listdir(LOGDIR)):
        if f.startswith("レガシー移行_") and f.endswith(".json"):
            try:
                for batch in json.load(open(os.path.join(LOGDIR, f), encoding="utf-8")):
                    kind = batch.get("作業", "移動")
                    for m in batch.get("明細", []):
                        out.append({"ログ": f, "日時": batch.get("日時"), "元": batch.get("元", ""),
                                    "旧": nfc(m.get("旧", "")), "新": nfc(m.get("新", "")),
                                    "先": m.get("先", ""), "種別": kind})
            except Exception as e:
                print("★ログを読めない:", f, e)
    return out


def show(rows):
    for i, r in enumerate(rows, 1):
        print("%3d  %s" % (i, r["新"][:66]))
        print("     いまの場所 %s" % r["先"])
        print("     元の名前   %s" % r["旧"][:66])
        print("     元の場所   %s" % r["元"])


def undo_one(r):
    """1件を元の場所・元の名前へ戻す。元の場所が無ければ作る"""
    src = os.path.join(DEP, r["先"], r["新"])
    if not os.path.exists(src):
        # リネームし直している場合があるので、日付だけ違う同名を探す
        d = os.path.join(DEP, r["先"])
        cand = [x for x in os.listdir(d) if nfc(x)[10:] == r["新"][10:]] if os.path.isdir(d) else []
        if len(cand) == 1:
            src = os.path.join(d, cand[0])
        else:
            print("  ★見つからない:", r["新"][:50]); return False
    dst_dir = os.path.join(B, r["元"]) if r["元"] else os.path.join(DEP, "_戻した")
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, r["旧"])
    if os.path.exists(dst):
        print("  ★戻す先に同じ名前がある:", r["旧"][:50]); return False
    shutil.move(src, dst)
    print("  戻した: %s → %s" % (r["新"][:44], r["元"] or "_戻した"))
    return True


def record(done):
    p = os.path.join(LOGDIR, "レガシー移行_20261014.json")
    old = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []
    old.append({"日時": datetime.datetime.now().isoformat(timespec="seconds"),
                "作業": "★戻した（有璽氏の指摘）", "件数": len(done), "明細": done})
    json.dump(old, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--find")
    ap.add_argument("--undo")
    ap.add_argument("--undo-all")
    a = ap.parse_args()
    rows = load()
    movable = [r for r in rows if r.get("種別", "移動") == "移動"]
    if not rows:
        print("ログがありません"); return
    if a.list:
        print("移した記録 %d 件（うち戻せる移動 %d 件）\n" % (len(rows), len(movable))); show(movable); return
    if a.find:
        k = nfc(a.find)
        hit = [r for r in movable if k in r["新"] or k in r["旧"]]
        print("「%s」に当たるもの %d 件\n" % (a.find, len(hit))); show(hit); return
    if a.undo:
        k = nfc(a.undo)
        hit = [r for r in movable if k in r["新"] or k in r["旧"]]
        if not hit:
            print("当たりません:", a.undo); return
        if len(hit) > 1:
            print("★%d 件に当たります。もう少し絞ってください\n" % len(hit)); show(hit); return
        if undo_one(hit[0]):
            record(hit)
        return
    if a.undo_all:
        hit = [r for r in movable if a.undo_all in (r["日時"] or "").replace("-", "")]
        print("%s の移動 %d 件を戻します" % (a.undo_all, len(hit)))
        done = [r for r in hit if undo_one(r)]
        if done:
            record(done)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
