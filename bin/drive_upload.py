#!/usr/bin/env python3
"""ローカルのファイルを Drive へ上げ、★リンクを知っている人なら誰でも見られる形にする。

★外へ出る操作。呼ぶ側が承認を取ってから使うこと。
2026-09-08 新設。Artifact は Claude を使わない相手には届かない（[[reference_artifact_is_not_public]]）ため。
"""
import sys, os, json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN = os.path.expanduser("~/.vivid-relay/google_token.json")
path, mime = sys.argv[1], sys.argv[2]
public = "--public" in sys.argv

creds = Credentials.from_authorized_user_file(TOKEN)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    open(TOKEN, "w").write(creds.to_json())

svc = build("drive", "v3", credentials=creds)
f = svc.files().create(
    body={"name": os.path.basename(path)},
    media_body=MediaFileUpload(path, mimetype=mime, resumable=True),
    fields="id,name,webViewLink,size",
).execute()
print("アップロード:", f["name"], int(f.get("size", 0)) // 1024, "KB")

if public:
    svc.permissions().create(fileId=f["id"],
                             body={"role": "reader", "type": "anyone"}).execute()
    # ★実測：本当に anyone になったかを読み返す
    perms = svc.permissions().list(fileId=f["id"], fields="permissions(type,role)").execute()
    kinds = [(p["type"], p["role"]) for p in perms["permissions"]]
    print("権限:", kinds, "／ anyone/reader:", ("anyone", "reader") in kinds)

print("リンク:", f["webViewLink"])
