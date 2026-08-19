#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manus AI × Claude Code の橋渡し。1ファイルで2つの顔を持つ。

  python3 manus.py --mcp        stdio MCP サーバ（Claude Code から「ツール」として見える）
  python3 manus.py ask "..."    CLI（どの面からでも同じ動作をさせるため）

API: https://api.manus.ai （v2）／ 認証ヘッダ `x-manus-api-key`
  POST /v2/task.create        タスクを作る          ★クレジットを消費する
  GET  /v2/task.listMessages  状態と発話を読む      （読むだけ）
  POST /v2/task.sendMessage   追加指示・質問への回答
  POST /v2/task.confirmAction 確認要求の承認／却下

APIキーは git に入れない。次の順で探す。
  1. 環境変数 MANUS_API_KEY
  2. ~/.config/manus/api_key （中身はキーだけ・1行）
  3. ~/.vivid-relay/config.env の MANUS_API_KEY= 行

Python 3.9 互換で書く（Mac mini が 3.9 系のため。3.10 構文は本番でだけ落ちる）。
標準ライブラリのみ。
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.environ.get("MANUS_API_BASE", "https://api.manus.ai")
VERSION = "0.1.0"
DEFAULT_TIMEOUT = 60


# ---------------------------------------------------------------- 認証

def find_api_key():
    key = os.environ.get("MANUS_API_KEY", "").strip()
    if key:
        return key, "env:MANUS_API_KEY"

    path = os.path.expanduser("~/.config/manus/api_key")
    if os.path.exists(path):
        with open(path, "r") as f:
            key = f.read().strip()
        if key:
            return key, path

    path = os.path.expanduser("~/.vivid-relay/config.env")
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("MANUS_API_KEY"):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        return key, path + " の MANUS_API_KEY"

    return None, None


class ManusError(Exception):
    pass


def call_api(method, path, payload=None, query=None, timeout=DEFAULT_TIMEOUT):
    """Manus API を1回叩く。戻りは dict。失敗は ManusError。"""
    key, _ = find_api_key()
    if not key:
        raise ManusError(
            "APIキーが見つからない。次のいずれかに置く:\n"
            "  export MANUS_API_KEY=...\n"
            "  ~/.config/manus/api_key （キーだけを1行）\n"
            "  ~/.vivid-relay/config.env に MANUS_API_KEY=...\n"
            "キーの発行は https://manus.im/app?show_settings=integrations&app_name=api"
        )

    url = BASE_URL + path
    if query:
        url += "?" + urllib.parse.urlencode(
            dict((k, v) for k, v in query.items() if v is not None)
        )

    data = None
    headers = {"x-manus-api-key": key, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        # Manus はエラー本文で直し方まで教えてくる。丸ごと見せる。
        raise ManusError("HTTP %s %s\n%s" % (e.code, url, body[:4000]))
    except urllib.error.URLError as e:
        raise ManusError("接続できない: %s (%s)" % (url, e.reason))

    try:
        out = json.loads(body)
    except ValueError:
        raise ManusError("JSONで返ってこなかった:\n" + body[:2000])

    if isinstance(out, dict) and out.get("ok") is False:
        raise ManusError("Manusが拒否した:\n" + json.dumps(out, ensure_ascii=False, indent=2))
    return out


# ---------------------------------------------------------------- API 4本

def task_create(prompt, agent_profile=None, title=None, project_id=None,
                interactive_mode=False, hide_in_task_list=False, locale="ja-JP"):
    msg = {"content": [{"type": "text", "text": prompt}]}
    payload = {
        "message": msg,
        "interactive_mode": bool(interactive_mode),
        "hide_in_task_list": bool(hide_in_task_list),
    }
    if locale:
        payload["locale"] = locale
    if agent_profile:
        payload["agent_profile"] = agent_profile
    if title:
        payload["title"] = title
    if project_id:
        payload["project_id"] = project_id
    return call_api("POST", "/v2/task.create", payload=payload)


def task_list_messages(task_id, limit=50, order="desc"):
    return call_api("GET", "/v2/task.listMessages",
                    query={"task_id": task_id, "limit": limit, "order": order})


def task_list(limit=30):
    return call_api("GET", "/v2/task.list", query={"limit": limit})


def project_list(limit=50):
    return call_api("GET", "/v2/project.list", query={"limit": limit})


def task_send_message(task_id, text):
    return call_api("POST", "/v2/task.sendMessage",
                    payload={"task_id": task_id,
                             "message": {"content": [{"type": "text", "text": text}]}})


def task_confirm_action(task_id, event_id, approve=True, text=None):
    payload = {"task_id": task_id, "event_id": event_id,
               "input": {"approved": bool(approve)}}
    if text:
        payload["input"]["text"] = text
    return call_api("POST", "/v2/task.confirmAction", payload=payload)


# ---------------------------------------------------------------- 応答の読み取り
# 2026-08-19 に実データで確認した形（推測ではなく実測）:
#   {ok, request_id, task_id, has_more, next_cursor,
#    messages:[{id, timestamp, type, <type と同名のフィールド>}]}
#   type は user_message / assistant_message / status_update の3種
#   ★agent_status はトップレベルに無い。status_update の中にだけ入っている

def extract_status(res):
    """最も新しい status_update の agent_status を返す。order に依存しない。"""
    best_ts, best = -1, None
    for m in res.get("messages") or []:
        if m.get("type") == "status_update":
            su = m.get("status_update") or {}
            st = su.get("agent_status")
            if st:
                try:
                    ts = int(m.get("timestamp") or 0)
                except (TypeError, ValueError):
                    ts = 0
                if ts >= best_ts:
                    best_ts, best = ts, st
    return best


def message_text(m):
    """type と同名のフィールドから content を取る。形が変わっても落ちないようにする。"""
    body = m.get(m.get("type") or "") or {}
    if isinstance(body, dict):
        c = body.get("content")
        if isinstance(c, str):
            return c
        if isinstance(c, list):  # Text/File/Voice の配列形式
            return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
        if body.get("brief") or body.get("description"):
            return "%s（%s）" % (body.get("brief", ""), body.get("description", ""))
    return ""


def fmt_ts(ts):
    try:
        return time.strftime("%m-%d %H:%M", time.localtime(int(ts)))
    except (TypeError, ValueError):
        return "??"


LABEL = {"user_message": "有璽氏→Manus", "assistant_message": "Manus", "status_update": "状態"}


def summarize(res, max_chars=8000):
    ms = res.get("messages") or []
    status = extract_status(res) or "(status_update なし)"
    head = "agent_status: %s ／ messages: %d件" % (status, len(ms))
    if res.get("has_more"):
        head += "（さらに続きあり）"
    if status == "waiting":
        head += "\n★確認待ち。manus_reply（質問への回答）か manus_confirm（承認/却下）が要る"

    lines = []
    for m in ms:
        t = message_text(m).strip()
        if not t:
            continue
        lines.append("[%s %s] %s" % (fmt_ts(m.get("timestamp")),
                                     LABEL.get(m.get("type"), m.get("type")), t))
    body = "\n\n".join(lines)
    if len(body) > max_chars:
        body = body[:max_chars] + "\n…(以下省略。全文は raw:true で)"
    return head + "\n\n" + (body if body else "(本文なし)")


def wait_until_done(task_id, timeout_sec=120, interval=5):
    """stopped / waiting / error になるまで待つ。戻りは (status, 最後のレスポンス)。"""
    deadline = time.time() + timeout_sec
    while True:
        last = task_list_messages(task_id, limit=50, order="desc")
        st = extract_status(last)
        if st in ("stopped", "error", "waiting"):
            return st, last
        if time.time() >= deadline:
            return st or "running", last
        time.sleep(interval)


# ---------------------------------------------------------------- MCP サーバ
# stdio・改行区切りの JSON-RPC 2.0。依存パッケージなしで足りる。

TOOLS = [
    {
        "name": "manus_ask",
        "description": (
            "Manus AI に自律タスクを投げる。ブラウザ操作・調査・ファイル生成など、"
            "長時間かかる作業をManus側で回したいときに使う。"
            "★Manusのクレジットを消費する（=課金）。実行前にユーザーの承認を取ること。"
            "戻り値の task_id を manus_status / manus_wait に渡して結果を取る。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Manusへの指示。前提・成果物の形まで書く"},
                "title": {"type": "string", "description": "タスク名（任意）"},
                "agent_profile": {"type": "string", "description": "既定 manus-1.6"},
                "project_id": {"type": "string", "description": "Manusプロジェクトに属させる場合"},
                "interactive_mode": {"type": "boolean", "description": "途中で質問させる。既定 false"},
                "wait_sec": {"type": "integer",
                             "description": "投げたあと完了まで待つ秒数。0=待たない（既定）。最大600"}
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "manus_projects",
        "description": "Manus のプロジェクト一覧を返す（アカウント別の発信ラインがここに並ぶ）。読むだけで課金されない。",
        "inputSchema": {"type": "object", "properties": {
            "limit": {"type": "integer", "description": "既定50"}}}
    },
    {
        "name": "manus_tasks",
        "description": (
            "Manus のタスク一覧を返す（新しい順・状態・消費クレジット付き）。読むだけで課金されない。"
            "★API はタスクがどのプロジェクトに属するかを返さない。プロジェクト単位で絞ることはできない。"
        ),
        "inputSchema": {"type": "object", "properties": {
            "limit": {"type": "integer", "description": "既定30"}}}
    },
    {
        "name": "manus_status",
        "description": "Manusタスクの現在の状態と発話を読む。読むだけで課金されない。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "limit": {"type": "integer", "description": "取得件数。既定50"},
                "raw": {"type": "boolean", "description": "生JSONを返す。既定false"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "manus_wait",
        "description": "Manusタスクが stopped / waiting / error になるまでポーリングして結果を返す。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "timeout_sec": {"type": "integer", "description": "既定120・最大600"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "manus_reply",
        "description": (
            "実行中のManusタスクへ追加指示を送る、または waiting_for_event_type=messageAskUser "
            "の質問に答える。★続きを走らせる＝クレジットを消費する。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "text": {"type": "string"}
            },
            "required": ["task_id", "text"]
        }
    },
    {
        "name": "manus_confirm",
        "description": (
            "Manusが確認を求めてきたアクションを承認／却下する（messageAskUser 以外の waiting）。"
            "承認するとManus側が実行に進む。不可逆な操作を含み得るのでユーザーの意思を確認すること。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "event_id": {"type": "string"},
                "approve": {"type": "boolean", "description": "既定 true"},
                "text": {"type": "string", "description": "添える一言（任意）"}
            },
            "required": ["task_id", "event_id"]
        }
    },
]


def run_tool(name, args):
    if name == "manus_ask":
        wait_sec = min(int(args.get("wait_sec") or 0), 600)
        res = task_create(
            args["prompt"],
            agent_profile=args.get("agent_profile"),
            title=args.get("title"),
            project_id=args.get("project_id"),
            interactive_mode=args.get("interactive_mode", False),
        )
        head = "task_id: %s\ntask_url: %s\ntitle: %s" % (
            res.get("task_id"), res.get("task_url"), res.get("task_title"))
        if wait_sec > 0 and res.get("task_id"):
            st, last = wait_until_done(res["task_id"], timeout_sec=wait_sec)
            return head + "\n\n" + summarize(last)
        return head + "\n\n（実行中。manus_status / manus_wait で結果を取る）"

    if name == "manus_projects":
        res = project_list(limit=int(args.get("limit") or 50))
        rows = res.get("data") or []
        out = ["プロジェクト %d件" % len(rows)]
        for r in rows:
            out.append("  %s  %s" % (r.get("id"), r.get("name")))
        return "\n".join(out)

    if name == "manus_tasks":
        res = task_list(limit=int(args.get("limit") or 30))
        rows = res.get("data") or []
        out = ["タスク %d件（has_more=%s）" % (len(rows), res.get("has_more"))]
        for r in sorted(rows, key=lambda x: -int(x.get("created_at") or 0)):
            out.append("  %s [%s] cr=%s %s | %s" % (
                fmt_ts(r.get("created_at")), r.get("status"),
                r.get("credit_usage"), r.get("id"), (r.get("title") or "")[:50]))
        return "\n".join(out)

    if name == "manus_status":
        res = task_list_messages(args["task_id"], limit=int(args.get("limit") or 50))
        if args.get("raw"):
            return json.dumps(res, ensure_ascii=False, indent=2)[:20000]
        return summarize(res)

    if name == "manus_wait":
        st, last = wait_until_done(args["task_id"],
                                   timeout_sec=min(int(args.get("timeout_sec") or 120), 600))
        return summarize(last)

    if name == "manus_reply":
        task_send_message(args["task_id"], args["text"])
        return "送った。manus_status で続きを読む。"

    if name == "manus_confirm":
        task_confirm_action(args["task_id"], args["event_id"],
                            approve=args.get("approve", True), text=args.get("text"))
        return "確認を返した（approve=%s）。" % args.get("approve", True)

    raise ManusError("知らないツール: %s" % name)


def mcp_serve():
    def send(obj):
        sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue

        method = req.get("method")
        rid = req.get("id")

        if method == "initialize":
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "manus", "version": VERSION},
            }})
        elif method in ("notifications/initialized", "initialized"):
            continue
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            params = req.get("params") or {}
            try:
                text = run_tool(params.get("name"), params.get("arguments") or {})
                send({"jsonrpc": "2.0", "id": rid,
                      "result": {"content": [{"type": "text", "text": text}]}})
            except ManusError as e:
                send({"jsonrpc": "2.0", "id": rid,
                      "result": {"content": [{"type": "text", "text": str(e)}], "isError": True}})
            except Exception as e:  # 落ちてもサーバは生かす
                send({"jsonrpc": "2.0", "id": rid,
                      "result": {"content": [{"type": "text",
                                              "text": "%s: %s" % (type(e).__name__, e)}],
                                 "isError": True}})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": rid, "result": {}})
        elif rid is not None:
            send({"jsonrpc": "2.0", "id": rid,
                  "error": {"code": -32601, "message": "未実装: %s" % method}})


# ---------------------------------------------------------------- CLI

USAGE = """使い方:
  manus.py --mcp                      MCPサーバとして起動（Claude Code がこれを呼ぶ）
  manus.py check                      APIキーの在り処と疎通を確認（書き込みなし）
  manus.py ask "指示" [--wait 180] [--title X]   タスクを投げる ★課金
  manus.py projects                   プロジェクト一覧（読むだけ）
  manus.py tasks [--limit 30]         タスク一覧（読むだけ）
  manus.py status <task_id> [--raw]   状態と発話を読む
  manus.py wait <task_id> [--timeout 300]
  manus.py reply <task_id> "追加指示"  ★課金
  manus.py confirm <task_id> <event_id> [--reject]
"""


def opt(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def main():
    argv = sys.argv[1:]
    if not argv:
        print(USAGE)
        return 0
    if argv[0] == "--mcp":
        mcp_serve()
        return 0

    cmd = argv[0]
    try:
        if cmd == "check":
            key, src = find_api_key()
            if not key:
                print("APIキー: 見つからない")
                print("  発行: https://manus.im/app?show_settings=integrations&app_name=api")
                print("  置き場: ~/.config/manus/api_key （キーだけ1行・chmod 600）")
                return 1
            print("APIキー: 見つかった（%s / 末尾4桁 …%s）" % (src, key[-4:]))
            # 読み取り専用の疎通確認。存在しない task_id を投げて、認証が通るかだけ見る
            try:
                task_list_messages("task_probe_does_not_exist", limit=1)
                print("疎通: OK（応答あり）")
            except ManusError as e:
                s = str(e)
                if "401" in s or "unauthorized" in s.lower() or "invalid_api_key" in s.lower():
                    print("疎通: 認証NG\n" + s)
                    return 1
                print("疎通: 認証は通った（想定内のエラー本文）\n" + s[:600])
            return 0

        if cmd == "ask":
            prompt = argv[1]
            res = task_create(prompt, title=opt(argv, "--title"))
            print(json.dumps(res, ensure_ascii=False, indent=2))
            w = int(opt(argv, "--wait", 0) or 0)
            if w and res.get("task_id"):
                st, last = wait_until_done(res["task_id"], timeout_sec=min(w, 600))
                print("\n" + summarize(last))
            return 0

        if cmd == "projects":
            res = project_list()
            for r in res.get("data") or []:
                print("%s  %s" % (r.get("id"), r.get("name")))
            return 0

        if cmd == "tasks":
            res = task_list(limit=int(opt(argv, "--limit", 30)))
            rows = sorted(res.get("data") or [], key=lambda x: -int(x.get("created_at") or 0))
            for r in rows:
                print("%s [%s] cr=%s %s | %s" % (fmt_ts(r.get("created_at")), r.get("status"),
                      r.get("credit_usage"), r.get("id"), (r.get("title") or "")[:50]))
            return 0

        if cmd == "status":
            res = task_list_messages(argv[1], limit=int(opt(argv, "--limit", 50)))
            print(json.dumps(res, ensure_ascii=False, indent=2) if "--raw" in argv
                  else summarize(res))
            return 0

        if cmd == "wait":
            st, last = wait_until_done(argv[1], timeout_sec=int(opt(argv, "--timeout", 300)))
            print(summarize(last))
            return 0

        if cmd == "reply":
            task_send_message(argv[1], argv[2])
            print("送った。")
            return 0

        if cmd == "confirm":
            task_confirm_action(argv[1], argv[2], approve=("--reject" not in argv))
            print("確認を返した。")
            return 0

        print(USAGE)
        return 1
    except ManusError as e:
        sys.stderr.write(str(e) + "\n")
        return 1
    except IndexError:
        print(USAGE)
        return 1


if __name__ == "__main__":
    sys.exit(main())
