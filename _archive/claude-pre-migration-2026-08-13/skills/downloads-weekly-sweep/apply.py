#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
downloads-weekly-sweep / apply.py

承認済みの提案CSVを読み、承認(y)行だけを実行する。
**移動のみ・削除なし・原本名をログ保存＝完全可逆。**

- 格納X : Downloads → <ARCHIVE>/<提案カテゴリ>/  （新名案があれば改名して移動）
- 隔離C : Downloads → Downloads/_不要候補_確認用/ （削除はしない。最終確認は人が別途）
- 保留/未承認 : 何もしない
- ネイティブ形式(.gsheet等) : ローカル改名は無効なので**現在名のまま移動**し、ログに「Drive側で改名」を残す
- 名前衝突 : 末尾に _dup2, _dup3 … を付けて回避（上書きしない）

使い方:
  python3 apply.py "<提案CSVのパス>"            # 実行
  python3 apply.py "<提案CSVのパス>" --dry-run  # 動作確認（移動しない）

実行ログ: <ARCHIVE>/_整理ログ/週次整理_実行_YYYY-MM-DD.csv
"""
import csv
import os
import shutil
import sys
from datetime import datetime

HOME = os.path.expanduser("~")
DOWNLOADS = os.path.join(HOME, "Downloads")
ARCHIVE = os.path.join(
    HOME,
    "Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com",
    "マイドライブ", "Downloads書類アーカイブ",
)
LOGDIR = os.path.join(ARCHIVE, "_整理ログ")
QUARANTINE = os.path.join(DOWNLOADS, "_不要候補_確認用")
NATIVE_EXT = {".gdoc", ".gsheet", ".gslides", ".gform", ".gdraw", ".gvid", ".gmap", ".gsite"}
YES = {"y", "yes", "Y", "はい", "1"}


def unique_dest(dest_dir, name):
    """衝突時は _dup2.. を付けて一意化（上書き禁止）。"""
    target = os.path.join(dest_dir, name)
    if not os.path.exists(target):
        return target
    base, ext = os.path.splitext(name)
    n = 2
    while True:
        cand = os.path.join(dest_dir, "%s_dup%d%s" % (base, n, ext))
        if not os.path.exists(cand):
            return cand
        n += 1


def main():
    if len(sys.argv) < 2:
        print("使い方: python3 apply.py <提案CSVのパス> [--dry-run]")
        sys.exit(1)
    csv_path = sys.argv[1]
    dry = "--dry-run" in sys.argv[2:]
    if not os.path.isfile(csv_path):
        print("CSVが見つかりません: %s" % csv_path)
        sys.exit(1)

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    log = []
    moved = skipped = errors = 0
    for r in rows:
        approve = (r.get("承認(y/n)") or "").strip()
        if approve not in YES:
            skipped += 1
            continue
        src = (r.get("元パス") or "").strip()
        cur = (r.get("現在名") or "").strip()
        judge = (r.get("判定") or "").strip()
        cat = (r.get("提案カテゴリ") or "").strip()
        newname = (r.get("新名案") or "").strip()
        native = (r.get("ネイティブ") or "no").strip() == "yes"

        if not src or not os.path.exists(src):
            log.append([cur, "", src, "", "元ファイルなし(スキップ)", ""])
            errors += 1
            continue

        # 行き先ディレクトリ
        if judge.startswith("隔離"):
            dest_dir = QUARANTINE
            note = "junk隔離(削除は別途最終確認)"
            final_name = cur
        else:
            if not cat:
                log.append([cur, "", src, "", "カテゴリ未確定(スキップ)", ""])
                skipped += 1
                continue
            dest_dir = os.path.join(ARCHIVE, cat)
            # ネイティブは改名無効 → 現在名のまま
            if native or not newname:
                final_name = cur
                note = "Drive側で改名要" if (native and newname) else "改名なし"
            else:
                final_name = newname
                note = "改名: %s → %s" % (cur, newname)

        dest = unique_dest(dest_dir, final_name)
        if dry:
            log.append([cur, os.path.basename(dest), src, dest, "[dry-run] " + note, ""])
            moved += 1
            continue
        try:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(src, dest)
            log.append([cur, os.path.basename(dest), src, dest, note,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            moved += 1
        except Exception as e:  # noqa
            log.append([cur, "", src, dest, "エラー:%s" % e, ""])
            errors += 1

    ts = datetime.now()
    os.makedirs(LOGDIR, exist_ok=True)
    tag = "_dryrun" if dry else ""
    out = os.path.join(LOGDIR, "週次整理_実行_%s%s.csv" % (ts.strftime("%Y-%m-%d"), tag))
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["原本名", "新名", "元パス", "行き先パス", "動作/備考", "実行日時"])
        w.writerows(log)

    head = "[DRY-RUN] " if dry else ""
    print("%s実行ログ: %s" % (head, out))
    print("%s処理 %d 件 / 未承認スキップ %d 件 / エラー %d 件" % (head, moved, skipped, errors))
    if not dry:
        print("すべて移動のみ・削除なし。原本名は実行ログに記録済み＝元へ戻せます。")


if __name__ == "__main__":
    main()
