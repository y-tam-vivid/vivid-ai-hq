#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_要判断 のメモ13件を、名前を規約の形に直して部門へ移す（2026-10-15）

★名前に日付が入っているのに `/` 区切りだったため、こちらの日付抽出が外れて
  _要判断 に落ちていた（POSIX層では `2026:05:13メモ.rtf`・Finderでは `2026/05/13メモ.rtf`）。

★部門の割り当ては★バックオフィス担当のセッションのAI（Sonnet）が中身を読んで付けたもの。
  ★有璽氏はまだ見ていない。決定として扱わず、移動ログにもその旨を残す。
  → memory/reference_two_sessions_built_the_same_thing.md
"""
import os, json, shutil, datetime
import unicodedata as u

DEP = ("/Users/yujimac/Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com"
       "/マイドライブ/00_部門軸アーカイブ")
LOG = os.path.join(DEP, "_整理ログ", "レガシー移行_20261014.json")
nfc = lambda s: u.normalize("NFC", s)

# (POSIX上の名前, 行き先, 題)
ROWS = [
 ("2026:05:13メモ.rtf", "_要判断_20261014", "5月13日の複数の打合せが混ざったメモ"),
 ("2026:05:14メモ.rtf", "11_事業開発",      "Claude活用とサイト修正のやること"),
 ("2026:05:15メモ.rtf", "13_営業",          "森さん 営業顧問の紹介と報酬の条件"),
 ("2026:05:18メモ.rtf", "13_営業",          "BPO定例と営業MTG"),
 ("2026:05:20メモ.rtf", "12_マーケティング", "ウェビナーほかのメモ"),
 ("2026:05:22メモ.rtf", "13_営業",          "面談3件の記録"),
 ("2026:05:26メモ.rtf", "13_営業",          "efax・松本MTG ほか"),
 ("2026:05:27メモ.rtf", "10_経営企画室",    "篠原さんMTGの準備と柏原市への電話"),
 ("2026:06:05メモ.rtf", "13_営業",          "営業BPO定例の進め方"),
 ("2026:06:12メモ.rtf", "15_施設運営",      "鈴木さんMTG"),
 ("2026:06:13メモ.rtf", "10_経営企画室",    "吉川さんMTG（BPO・給与・営業）"),
 ("2026:06:22メモ.rtf", "_要判断_20261014", "複数の面談の記録"),
 ("2026:06:29メモ.rtf", "13_営業",          "医療連携体制構築加算のメモ"),
]


def main():
    yo = [x for x in os.listdir(DEP) if nfc(x).startswith("_要判断")][0]
    base = os.path.join(DEP, yo)
    ok, moves, ng = 0, [], []
    for old, dest, title in ROWS:
        hit = [x for x in os.listdir(base) if nfc(x) == nfc(old)]
        if not hit:
            ng.append(old); print("★元が無い:", old); continue
        d = old[:10].replace(":", "-")          # 2026:05:13 → 2026-05-13
        new = "%s【メモ】%s_v1.rtf" % (d, title)
        dd = os.path.join(DEP, *dest.split("/"))
        os.makedirs(dd, exist_ok=True)
        tgt = os.path.join(dd, new)
        if os.path.exists(tgt):
            ng.append(old); print("★先に同名:", new[:50]); continue
        shutil.move(os.path.join(base, hit[0]), tgt)
        ok += 1
        moves.append({"旧": nfc(old), "新": new, "先": dest})
        print("%-22s → %-18s %s" % (old, dest, new[:52]))

    b = json.load(open(LOG, encoding="utf-8"))
    b.append({"日時": datetime.datetime.now().isoformat(timespec="seconds"),
              "元": "00_部門軸アーカイブ/_要判断_20261014（日付が / 区切りのメモ13件）",
              "判定": "★部門の割り当てはバックオフィス担当のセッションのAI（Sonnet）が"
                      "中身を読んで付けたもの。有璽氏は未確認。日付と名前はこちらが規約の形へ",
              "件数": ok, "明細": moves})
    json.dump(b, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n動かした %d ／ 飛ばした %d" % (ok, len(ng)))
    print("残り _要判断:", len([x for x in os.listdir(base) if not x.startswith(".")]), "件")


if __name__ == "__main__":
    main()
