#!/usr/bin/env python3
"""HUG 本日の様子：共有ドライブの「利用者別」の原本へ、「月別/<YYYY-MM>/」にドライブのショートカットを作る

なぜ要るか（2026-10-20 有璽氏）
  原本は利用者別（個別支援計画は利用者ごとに読む）。月単位でも見たい＝月別にはショートカット。
  置き場：共有ドライブ 15-000_施設運営部門 › LIFE STAND UP › 本日の様子（HUG）（#17160b）
  原本は Mac の Google ドライブの同期フォルダへ hug_split_yosu.py の結果をコピーして上げる。
  Mac の symlink はドライブへ運ばれないので、ショートカットはこれで作る。
  → memory/reference_hug_record_output.md

  python3 hug_drive_shortcuts.py [--dry-run]      ★Mac mini で動かす（google のライブラリと鍵が mini にある）

  ファイル名の <YYYY-MM>_ で月を決める。月別に同じ名前があれば作らない（何度流してもよい）。
  ★氏名は画面に出さない（件数だけ）。原本は読むだけで、動かさない・消さない。
"""
import os
import re
import socket
import sys
from collections import Counter

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

socket.setdefaulttimeout(120)  # 10/20 初回、既定の待ち時間で読み取りがタイムアウトして途中で落ちた
TOKEN = os.path.expanduser("~/.vivid-relay/google_token.json")
DRIVE_NAME = "15-000_施設運営部門"
PATH = ["LIFE STAND UP", "本日の様子（HUG）"]
FOLDER = "application/vnd.google-apps.folder"
SHORTCUT = "application/vnd.google-apps.shortcut"
YM_RE = re.compile(r"^(\d{4}-\d{2})_本日の様子_")


def svc():
    c = Credentials.from_authorized_user_file(TOKEN)
    if c.expired and c.refresh_token:
        c.refresh(Request())
        open(TOKEN, "w").write(c.to_json())
    return build("drive", "v3", credentials=c)


def children(s, drive_id, parent, mime=None):
    q = f"'{parent}' in parents and trashed=false" + (f" and mimeType='{mime}'" if mime else "")
    out, tok = [], None
    while True:
        r = s.files().list(q=q, corpora="drive", driveId=drive_id, includeItemsFromAllDrives=True,
                           supportsAllDrives=True, pageSize=1000, pageToken=tok,
                           fields="nextPageToken,files(id,name,mimeType,shortcutDetails)").execute(num_retries=5)
        out += r["files"]
        if not (tok := r.get("nextPageToken")):
            return out


def folder(s, drive_id, parent, name, create):
    hit = [f for f in children(s, drive_id, parent, FOLDER) if f["name"] == name]
    if len(hit) > 1:
        sys.exit(f"同じ名前のフォルダが{len(hit)}個あります（{name}）。どれか決められないので止めます")
    if hit:
        return hit[0]["id"]
    if not create:
        return None
    return s.files().create(body={"name": name, "mimeType": FOLDER, "parents": [parent]},
                            supportsAllDrives=True, fields="id").execute(num_retries=5)["id"]


def main():
    dry = "--dry-run" in sys.argv
    s = svc()
    drives = [d for d in s.drives().list(pageSize=100).execute(num_retries=5)["drives"] if d["name"] == DRIVE_NAME]
    if len(drives) != 1:
        sys.exit(f"共有ドライブ {DRIVE_NAME} が{len(drives)}個見つかりました")
    did = drives[0]["id"]
    top = did
    for name in PATH:
        top = folder(s, did, top, name, create=False)
        if not top:
            sys.exit(f"フォルダが見つかりません：{name}（まだ同期の途中かもしれません）")
    users = folder(s, did, top, "利用者別", create=False)
    if not users:
        sys.exit("利用者別 のフォルダが見つかりません")

    originals = []
    for u in children(s, did, users, FOLDER):
        originals += [f for f in children(s, did, u["id"]) if f["mimeType"] == "application/pdf"]
    by_month = Counter(m.group(1) for f in originals if (m := YM_RE.match(f["name"])))
    print(f"原本 {len(originals)}本（月ごと {dict(sorted(by_month.items()))}）")
    if dry:
        return

    monthly = folder(s, did, top, "月別", create=True)
    made = skipped = 0
    for ym in sorted(by_month):
        mid = folder(s, did, monthly, ym, create=True)
        have = {f["name"] for f in children(s, did, mid)}
        for f in originals:
            if not f["name"].startswith(ym + "_"):
                continue
            if f["name"] in have:
                skipped += 1
                continue
            s.files().create(body={"name": f["name"], "mimeType": SHORTCUT, "parents": [mid],
                                   "shortcutDetails": {"targetId": f["id"]}},
                             supportsAllDrives=True, fields="id").execute(num_retries=5)
            made += 1

    # 実物で照合：月別の中のショートカットが、原本を指しているか
    ids = {f["id"] for f in originals}
    links = []
    for m in children(s, did, monthly, FOLDER):
        links += [f for f in children(s, did, m["id"]) if f["mimeType"] == SHORTCUT]
    ok = sum(1 for f in links if f.get("shortcutDetails", {}).get("targetId") in ids)
    print(f"ショートカット 作成 {made}本・既にあった {skipped}本 → 月別の合計 {len(links)}本（原本を指している {ok}本）")


if __name__ == "__main__":
    main()
