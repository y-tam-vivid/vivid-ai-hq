#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webページを外へ出す直前に「計測セット」が入っているかを検査し、揃っていなければ止める ── PreToolUse フック

なぜ要るか（2026-09-29 有璽氏）
  「LPにクリックログ・ヒートマップを。普通のWebでも同じように。★絶対に構築するように。
   即実装。一般のサイトでも★標準にする。サイトの改善にもつなげる」
  スキル web-tracking-setup は「その作業のときに読まれる」だけで、読み飛ばしを止められない。
  送ってから・公開してからでは、その間の記録は永久に取り返せない（2026-08 ゲームブル第1波の18社）。
  → 公開・送信のコマンドそのものの前で、機械が検査して止める。

何を止めるか（Bash のコマンド文字列で判定）
  公開   vercel deploy / vercel --prod ／ netlify deploy ／ wrangler pages deploy ／ firebase deploy
         ／ surge ／ redeploy.sh
  送信   SalesBreaker の templates/save（文面に入れたURLの着地先を検査する）

どう検査するか
  公開 → 出す場所（--cwd ／ 直前の cd ／ 位置引数 ／ payload の cwd）の HTML を全部
         bin/web_tracking_check.py の check_html() に通す。✗ が1つでもあれば deny。
  送信 → コマンド文字列と -d @file の中の https URL を取得して検査。✗ なら deny。

止めない場合（★全部ログに残す）
  ・公開先が bin/web_tracking/exempt.json に理由つきで載っている（社内画面・スタッフ確認用・
    有璽氏が「解析を入れない」と決めたサイト 等）
  ・HTML が1枚も見つからない（Next.js 等のビルド型）→ 止めずに警告だけ返す（静的検査ができないため）
  ・このフック自身が落ちた → 通す（fail-open。検問の故障で全作業を止めない）

★cron から直接走るデプロイ（kadoban_deploy.sh 等）は Claude Code を通らないので、このフックは効かない。
  対象は「AIが Bash で公開・送信するとき」。

出力  deny のときは hookSpecificOutput.permissionDecision = "deny"（exit 0・JSON）
ログ  ~/.vivid-relay/web_tracking_gate.log
"""
import fnmatch
import json
import os
import re
import shlex
import sys
import time
import urllib.request

REPO = os.path.expanduser("~/vivid-ai-hq")
sys.path.insert(0, os.path.join(REPO, "bin"))
EXEMPT_FILE = os.path.join(REPO, "bin", "web_tracking", "exempt.json")
LOG = os.path.expanduser("~/.vivid-relay/web_tracking_gate.log")

OTHER_PUBLISH = {  # コマンド名 → 公開を意味するサブコマンド（None=コマンドだけで公開）
    "netlify": "deploy", "firebase": "deploy", "surge": None, "wrangler": "deploy",
}
SB_SEND = re.compile(r"salesbreaker\.jp/api/operator/v\d+/templates/save")
VERCEL_READ = {"ls", "list", "inspect", "logs", "env", "whoami", "login", "logout", "link", "project",
               "projects", "domains", "alias", "firewall", "pull", "dns", "certs", "teams", "switch",
               "help", "rm", "remove", "promote", "rollback", "redeploy", "bisect", "build", "dev",
               "init", "git", "integration", "secrets", "target", "blob", "cache", "--version", "-v"}
RUNNERS = {"npx", "pnpm", "bunx", "yarn", "dlx", "exec", "--yes", "-y", "sudo", "env", "time"}
SKIP_DIRS = {"node_modules", ".git", ".vercel", ".next", "_backup", "archive", "review"}
MAX_FILES = 300


def log(msg):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S %Z") + " " + msg + "\n")
    except Exception:
        pass


def out(decision=None, reason="", context=""):
    h = {"hookEventName": "PreToolUse"}
    if decision:
        h["permissionDecision"] = decision
        h["permissionDecisionReason"] = reason
    if context:
        h["additionalContext"] = context
    print(json.dumps({"hookSpecificOutput": h}, ensure_ascii=False))
    sys.exit(0)


def commands(cmd):
    """シェルの文字列を「実行されるコマンドごとのトークン列」に分ける。
    ★heredoc の本文・クォート内の文字（commit メッセージ等）はコマンドとして数えない"""
    cmd = re.sub(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(\n|$)", "\n", cmd, flags=re.S)
    lx = shlex.shlex(cmd, posix=True, punctuation_chars=";&|\n")
    lx.whitespace = " \t\r"
    lx.whitespace_split = True
    out, cur = [], []
    try:
        for t in lx:
            if t and set(t) <= set(";&|\n"):
                if cur:
                    out.append(cur)
                cur = []
            else:
                cur.append(t)
    except ValueError:
        return []
    if cur:
        out.append(cur)
    res = []
    for toks in out:
        i = 0
        while i < len(toks) and (toks[i] in RUNNERS or re.match(r"^[A-Z_][A-Z0-9_]*=", toks[i])):
            i += 1
        if i < len(toks):
            res.append(toks[i:])
    return res


def is_publish(cmd):
    """実行されるコマンドの先頭語で判定する。
    vercel：後ろの最初の言葉が 無い／deploy／パス＝公開。ls 等の閲覧は公開ではない
    ★promote/rollback/redeploy は既にある版を出し直すだけで、中身を検査できないので対象外"""
    for toks in commands(cmd):
        if os.path.basename(toks[0]) in {"bash", "sh", "zsh"} and len(toks) > 1:
            toks = toks[1:]  # bash ./redeploy.sh の形
        name = os.path.basename(toks[0])
        words = [t for t in toks[1:] if not t.startswith("-")]
        sub = words[0] if words else None
        if name == "vercel":
            if sub in VERCEL_READ or "--version" in toks:
                continue
            return True
        if name == "redeploy.sh":
            return True
        if name in OTHER_PUBLISH and (OTHER_PUBLISH[name] is None or OTHER_PUBLISH[name] in toks):
            return True
    return False


def deploy_dir(cmd, cwd):
    """公開する場所を推定する。★推定であることをログに残す"""
    m = re.search(r"--cwd[= ]+(\S+)", cmd)
    if m:
        return os.path.expanduser(m.group(1).strip("'\""))
    base = cwd
    for m in re.finditer(r"\bcd\s+([^;&|]+?)\s*(&&|;)", cmd):
        p = os.path.expanduser(m.group(1).strip().strip("'\""))
        base = p if os.path.isabs(p) else os.path.join(base, p)
    try:
        toks = shlex.split(cmd.split("&&")[-1].split(";")[-1])
    except ValueError:
        toks = []
    if "deploy" in toks:
        rest = toks[toks.index("deploy") + 1:]
        for t in rest:
            if not t.startswith("-") and os.path.isdir(os.path.join(base, os.path.expanduser(t))):
                return os.path.join(base, os.path.expanduser(t))
    return base


def exempt_reason(path):
    try:
        rules = json.load(open(EXEMPT_FILE, encoding="utf-8"))
    except Exception:
        return None
    is_url = path.startswith("http")
    real = path if is_url else os.path.realpath(path)
    for r in rules.get("paths", []):
        rp = r["path"]
        if rp.startswith("http") != is_url:
            continue
        pat = rp if (is_url or "*" in rp) else os.path.realpath(os.path.expanduser(rp))
        pat = os.path.expanduser(pat)
        if fnmatch.fnmatch(real, pat) or real == pat or real.startswith(pat.rstrip("/*") + "/"):
            return r.get("reason", "理由未記入")
    return None


def html_files(root):
    """★範囲が広すぎる（ホーム直下・/tmp 等）ときは None を返して検査しない＝警告で通す"""
    if os.path.realpath(root) in {os.path.realpath(os.path.expanduser("~")), "/", "/tmp", "/private/tmp"}:
        return None
    found, seen = [], 0
    for d, dirs, files in os.walk(root):
        seen += 1
        if seen > 3000:
            return None
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
        for f in files:
            if f.endswith(".html") and ".bak" not in f and not f.endswith(".dc.html"):
                found.append(os.path.join(d, f))
                if len(found) >= MAX_FILES:
                    return found
    return found


def failures(html):
    from web_tracking_check import check_html
    return [f"{name}（{note}）" for name, ok, note in check_html(html) if ok is False]


def gate_publish(cmd, cwd):
    root = deploy_dir(cmd, cwd)
    reason = exempt_reason(root)
    if reason:
        log(f"通した（対象外） {root} ／ {reason}")
        out(context=f"計測の検問：{root} は対象外として登録済み（{reason}）。")
    files = html_files(root) if os.path.isdir(root) else []
    if files is None:
        log(f"通した（範囲が広すぎ・警告） {root}")
        out(context=f"★計測の検問：公開する場所 {root} が広すぎて検査できなかった。"
                    "--cwd で公開フォルダを明示するか、公開後に web_tracking_check.py <URL> を通すこと。")
    if not files:
        log(f"通した（HTML無し・警告） {root}")
        out(context=f"★計測の検問：{root} に HTML が見つからず静的に検査できなかった。"
                    "公開後に python3 ~/vivid-ai-hq/bin/web_tracking_check.py <URL> を必ず通すこと。")
    bad = {}
    for f in files:
        try:
            ng = failures(open(f, encoding="utf-8", errors="replace").read())
        except Exception as e:
            ng = [f"読めない（{e}）"]
        if ng:
            bad[os.path.relpath(f, root)] = ng
    if not bad:
        log(f"通した（全{len(files)}枚 ✓） {root}")
        out(context=f"計測の検問：{len(files)}枚とも計測セットあり（発火の確認は別）。")
    lines = [f"・{k}：{' ／ '.join(v)}" for k, v in list(bad.items())[:8]]
    more = f"\n…ほか {len(bad) - 8} 枚" if len(bad) > 8 else ""
    log(f"止めた {root} ✗{len(bad)}/{len(files)}枚")
    out("deny",
        f"★計測セットが揃っていないので公開を止めた（{len(bad)}/{len(files)}枚）。\n" + "\n".join(lines) + more +
        "\n直し方：Skill web-tracking-setup の手順どおり ~/vivid-ai-hq/bin/web_tracking/snippet.html を <head> に入れる。"
        "\n社内画面など計測が不要な場所なら、理由を書いて ~/vivid-ai-hq/bin/web_tracking/exempt.json へ載せる（有璽氏の了解が要る）。")


def gate_sb_send(cmd, cwd):
    text = cmd
    for m in re.finditer(r"@(\S+)", cmd):
        p = os.path.join(cwd, os.path.expanduser(m.group(1).strip("'\"")))
        if os.path.isfile(p):
            text += "\n" + open(p, encoding="utf-8", errors="replace").read()
    urls = sorted(set(u.rstrip(".,)\"'\\") for u in re.findall(r"https://[^\s\"'<>\\]+", text)
                      if "salesbreaker.jp" not in u and "sbroute.net" not in u))
    if not urls:
        log("通した（SB文面・URL無し）")
        out(context="計測の検問：文面に着地先URLが無い（認知目的なら可）。")
    bad, skipped = [], 0
    for u in urls:
        if exempt_reason(u):
            skipped += 1
            continue
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (fukuchi gate)"})
            with urllib.request.urlopen(req, timeout=15) as r:
                ng = failures(r.read().decode("utf-8", "replace"))
        except Exception as e:
            ng = [f"開けない（{str(e)[:60]}）"]
        if ng:
            bad.append(f"・{u}：{' ／ '.join(ng)}")
    if not bad:
        log(f"通した（SB文面 ✓{len(urls) - skipped}・対象外{skipped}）")
        out(context=f"計測の検問：着地先 {len(urls) - skipped} 本は計測セットあり／対象外 {skipped} 本。")
    log(f"止めた（SB文面） ✗{len(bad)}")
    out("deny", "★文面の着地先に計測セットが無いので保存を止めた。\n" + "\n".join(bad) +
        "\n着地先へ Skill web-tracking-setup の計測セットを入れてから保存すること。")


def main():
    try:
        p = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if p.get("tool_name") != "Bash":
        sys.exit(0)
    cmd = (p.get("tool_input") or {}).get("command", "") or ""
    cwd = p.get("cwd") or os.getcwd()
    # ★文中に URL の文字があるだけ（commit メッセージ・メモ等）では反応しない。送る道具で叩いたときだけ
    if any(os.path.basename(t[0]) in {"curl", "wget", "http", "https", "xh"} and any(SB_SEND.search(x) for x in t)
           for t in commands(cmd)):
        gate_sb_send(cmd, cwd)
    if is_publish(cmd):
        gate_publish(cmd, cwd)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail-open
        log(f"フック自身の例外で通した：{e}")
        sys.exit(0)
