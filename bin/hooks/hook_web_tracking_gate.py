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
         ★包み方に依らず拾う：url=$(…)／timeout・nohup・nice・xargs・sudo・env の後ろ／
           bash -c '…'／if …; then／pushd X && …／(cd X && …)／vercel <dir> --prod
  送信   SalesBreaker の templates/save（文面に入れた★自社ドメインのURLの着地先を検査する）

どう検査するか
  公開 → 出す場所（--cwd ／ 直前の cd・pushd ／ 位置引数 ／ payload の cwd）の HTML を全部
         bin/web_tracking_check.py の check_html() に通す。✗ が1つでもあれば deny。
         partials/components/includes 配下と <html を含まない断片は数えない。.htm も見る。
         300枚を超えたら黙らず「未検査N枚」を出す。
  送信 → コマンド文字列と @file（-d/--data/--data-binary）の中の http(s) URL を取り出し、
         exempt.json の own_domains に当たる★自社の着地先だけを取得して検査する。
         自社以外（カレンダー予約リンク等）は検査せず注記だけ。着地先は並列で取得し、全体に時間上限がある。

止めない場合（★全部ログに残す）
  ・公開先が bin/web_tracking/exempt.json に理由つきで載っている（社内画面・スタッフ確認用・
    有璽氏が「解析を入れない」と決めたサイト 等）
  ・HTML が1枚も見つからない（Next.js 等のビルド型）→ 止めずに警告だけ返す（静的検査ができないため）
  ・SB の着地先を時間内に検査できなかった → deny せず警告で通す。
    ★理由：「計測が無いものを出さない」が絶対であって、検査が終わらないことを止める理由にはしない。
      止めると SalesBreaker 側の障害・ネット断のたびに全送信が止まる。fail-open（下）と方針を揃える。
      ただし「開けない（接続拒否・DNS・404）」と「計測が無い」は従来どおり deny。
  ・このフック自身が落ちた → 通す（fail-open。検問の故障で全作業を止めない）

★守れない場面（SKILL の「効かない場面」と同じ）
  ・cron から直接走るデプロイ（kadoban_deploy.sh 等）は Claude Code を通らない
  ・SB の文面を変数やファイルの中身で組み立てて送る／Python 等のスクリプトの中から送る（コマンドに現れない）
  ・sudo -u root vercel のように、runner の値つきオプションの値が先頭語に見える形

出力  deny のときは hookSpecificOutput.permissionDecision = "deny"（exit 0・JSON）
ログ  ~/.vivid-relay/web_tracking_gate.log

テスト用の環境変数（★フックは Claude 本体の子プロセスなので、Bash コマンドの前置きでは変えられない）
  VIVID_GATE_EXEMPT          exempt.json の場所を差し替える（test_gate.py・hook_selfcheck.py が使う）
  VIVID_GATE_SB_BUDGET       SB 着地先の検査の全体上限（秒・既定20）
  VIVID_GATE_SB_URL_TIMEOUT  1本ごとの上限（秒・既定8）
"""
import fnmatch
import json
import os
import re
import shlex
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = os.path.expanduser("~/vivid-ai-hq")
sys.path.insert(0, os.path.join(REPO, "bin"))
EXEMPT_FILE = os.environ.get("VIVID_GATE_EXEMPT") or os.path.join(REPO, "bin", "web_tracking", "exempt.json")
LOG = os.path.expanduser("~/.vivid-relay/web_tracking_gate.log")


def _envf(name, default):
    try:
        return float(os.environ.get(name, default))
    except Exception:
        return float(default)


SB_BUDGET = _envf("VIVID_GATE_SB_BUDGET", 20)
SB_URL_TIMEOUT = _envf("VIVID_GATE_SB_URL_TIMEOUT", 8)

OTHER_PUBLISH = {  # コマンド名 → 公開を意味するサブコマンド（None=コマンドだけで公開）
    "netlify": "deploy", "firebase": "deploy", "surge": None, "wrangler": "deploy",
}
SB_SEND = re.compile(r"salesbreaker\.jp/api/operator/v\d+/templates/save")
URL_RE = re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&()*+,;=%-]+")
VERCEL_READ = {"ls", "list", "inspect", "logs", "env", "whoami", "login", "logout", "link", "project",
               "projects", "domains", "alias", "firewall", "pull", "dns", "certs", "teams", "switch",
               "help", "rm", "remove", "promote", "rollback", "redeploy", "bisect", "build", "dev",
               "init", "git", "integration", "secrets", "target", "blob", "cache", "curl", "open", "telemetry"}
VERCEL_READ_FLAGS = {"--help", "-h", "--version", "-v"}
# ★値を1つ取るオプション。値を「サブコマンド」と読み違えない（vercel --scope team ls）
VERCEL_VALUE_OPTS = {"--scope", "-S", "--token", "-t", "--cwd", "-A", "--local-config", "--global-config",
                     "-Q", "--team", "--target", "-e", "--env", "-b", "--build-env", "-m", "--meta",
                     "--regions", "--archive"}
# コマンドを包む語（後ろが本体）。数値・オプション（timeout 120／nice -n 10／xargs -I{}）も一緒に飛ばす
RUNNERS = {"npx", "pnpm", "bunx", "yarn", "dlx", "exec", "--yes", "-y", "sudo", "env", "time",
           "nohup", "nice", "command", "builtin", "xargs", "timeout", "stdbuf", "setsid", "caffeinate",
           "if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "$"}
SHELLS = {"bash", "sh", "zsh"}
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
NUMERIC = re.compile(r"^\d+(\.\d+)?[smhd]?$")
# ★2周目（ステラ条件C）：archive/review/components/includes は除外しない（全ページ検査のはずが素通りしていた）。
#   除外は生成物・履歴の置き場だけ。<html を含まない断片は別途除外し、枚数と理由を出力に出す
SKIP_DIRS = {"node_modules", ".git", ".vercel", ".next", "_backup"}
OWN_EXTRA = ["vercel.app"]  # ★自社の Vercel エイリアス（例 gamemarkelp.vercel.app）も自社扱い
SSH_VALUE_OPTS = {"-p", "-i", "-l", "-o", "-F", "-J", "-L", "-R", "-D", "-b", "-c", "-E", "-e", "-I", "-m", "-O",
                  "-Q", "-S", "-W", "-w"}
MAX_FILES = 300
PUNCT = ";&|\n()`"


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


def commands(cmd, depth=0):
    """シェルの文字列を「実行されるコマンドごとのトークン列」に分ける。
    ★heredoc の本文・クォート内の文字（commit メッセージ等）はコマンドとして数えない
    ★$( ) ( ) ` ` の中も別コマンドとして数える。bash -c '…' の中身は再帰して数える"""
    cmd = re.sub(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(\n|$)", "\n", cmd, flags=re.S)
    lx = shlex.shlex(cmd, posix=True, punctuation_chars=PUNCT)
    lx.whitespace = " \t\r"
    lx.whitespace_split = True
    parts, cur = [], []
    try:
        for t in lx:
            if t and set(t) <= set(PUNCT):
                if cur:
                    parts.append(cur)
                cur = []
            else:
                cur.append(t)
    except ValueError:
        return []
    if cur:
        parts.append(cur)
    res = []
    for toks in parts:
        i, seen_runner = 0, False
        while i < len(toks):
            t = toks[i]
            if t in RUNNERS:
                seen_runner = True
            elif ASSIGN.match(t):
                pass
            elif seen_runner and (t.startswith("-") or NUMERIC.match(t)):
                pass
            else:
                break
            i += 1
        if i >= len(toks):
            continue
        toks = toks[i:]
        if os.path.basename(toks[0]) in SHELLS and depth < 3:
            rest = toks[1:]
            inner = None
            for j, t in enumerate(rest):
                if re.match(r"^-[a-zA-Z]*c[a-zA-Z]*$", t) and j + 1 < len(rest):
                    inner = rest[j + 1]
                    break
            if inner is not None:
                res.extend(commands(inner, depth + 1))
                continue
        if os.path.basename(toks[0]) == "ssh" and depth < 3:  # ssh [opts] host 'cmd' → cmd の中身も読む
            rest, k = toks[1:], 0
            while k < len(rest) and rest[k].startswith("-"):
                k += 2 if rest[k] in SSH_VALUE_OPTS else 1
            remote = rest[k + 1:]
            if remote:
                res.extend(commands(" ".join(remote), depth + 1))
                continue
        res.append(toks)
    return res


def vercel_words(toks):
    """vercel の引数から、オプションとその値を除いた語だけを返す（先頭がサブコマンド or 公開先のパス）"""
    words, skip = [], False
    for t in toks[1:]:
        if skip:
            skip = False
        elif t in VERCEL_VALUE_OPTS:
            skip = True
        elif not t.startswith("-"):
            words.append(t)
    return words


def find_publish(cmd):
    """公開コマンドを探す。見つかれば (種類, トークン列)、無ければ None。
    vercel：ls 等の閲覧・--help は公開ではない。サブコマンドが 無い／deploy／パス＝公開
    ★promote/rollback/redeploy は既にある版を出し直すだけで、中身を検査できないので対象外"""
    for toks in commands(cmd):
        if (os.path.basename(toks[0]) in SHELLS or toks[0] in ("source", ".")) and len(toks) > 1:
            toks = toks[1:]  # bash ./redeploy.sh ／ source ./redeploy.sh ／ . ./redeploy.sh の形
        name = os.path.basename(toks[0])
        if name.startswith(("vercel@", "vc@")):  # npx vercel@32 ／ pnpm dlx vercel@latest
            name = name.split("@")[0]
        if name in ("vercel", "vc"):
            if any(t in VERCEL_READ_FLAGS for t in toks[1:]):
                continue
            words = vercel_words(toks)
            if words and words[0] in VERCEL_READ:
                continue
            return "vercel", toks
        if name == "redeploy.sh":
            return "redeploy", toks
        if name in OTHER_PUBLISH and (OTHER_PUBLISH[name] is None or OTHER_PUBLISH[name] in toks):
            if any(t in ("--help", "-h") for t in toks[1:]):
                continue  # 使い方の表示は公開ではない
            return "other", toks
    return None


def _unesc(p):
    """cd の引数：引用符を外し、\\ エスケープ（My\\ Folder）を戻す"""
    return re.sub(r"\\(.)", r"\1", p.strip().strip("'\""))


def _opt_values(toks, names):
    """--opt X ／ --opt=X の値を順に返す（shlex 済みなので空白入りパスも1つの値）"""
    vals = []
    for i, t in enumerate(toks):
        for n in names:
            if t == n and i + 1 < len(toks):
                vals.append(toks[i + 1])
            elif t.startswith(n + "=") and n.startswith("--"):
                vals.append(t[len(n) + 1:])
    return vals


def deploy_dir(cmd, cwd, found):
    """公開する場所を推定する。★推定であることをログに残す"""
    kind, toks = found
    base = cwd
    for m in re.finditer(r"(?<![\w/.-])(?:cd|pushd)\s+([^;&|()]+?)\s*(?:&&|;|\)|$)", cmd):
        p = os.path.expanduser(_unesc(m.group(1)))
        base = p if os.path.isabs(p) else os.path.join(base, p)

    def at(t):
        t = os.path.expanduser(t)
        return t if os.path.isabs(t) else os.path.join(base, t)

    c = _opt_values(toks, ("--cwd",))
    if c:
        return at(c[0])  # ★相対パスは cd 後の場所からの相対
    if kind == "vercel":
        words = vercel_words(toks)
        cands = words[1:] if words and words[0] == "deploy" else words  # vercel <dir> --prod
    elif "deploy" in toks:
        cands = _opt_values(toks, ("--dir", "--publish", "-d"))  # netlify
        cands += [t for t in toks[toks.index("deploy") + 1:] if not t.startswith("-")]
    else:
        cands = []
    for t in cands:
        if os.path.isdir(at(t)):
            return at(t)
    return base


def load_exempt():
    try:
        return json.load(open(EXEMPT_FILE, encoding="utf-8"))
    except Exception:
        return {}


def _glob_match(rp, real):
    """パスのルール照合。★完全一致か「パス区切り単位」の配下だけ一致（foo が foobar に一致しない）。
    glob は1セグメントごとに照合する（* が / を跨がない）"""
    pat = os.path.expanduser(rp)
    parts = pat.split("/")
    gi = next((i for i, p in enumerate(parts) if any(c in p for c in "*?[")), None)
    if gi is None:
        base = os.path.realpath(pat)
        return real == base or real.startswith(base.rstrip("/") + "/")
    base = os.path.realpath("/".join(parts[:gi]) or "/")
    tail = [t for t in parts[gi:] if t]
    rp_, bp_ = [x for x in real.split("/") if x], [x for x in base.split("/") if x]
    if rp_[:len(bp_)] != bp_:
        return False
    rest = rp_[len(bp_):]
    return len(rest) >= len(tail) and all(fnmatch.fnmatchcase(r, t) for r, t in zip(rest, tail))


def exempt_reason(path):
    rules = load_exempt()
    is_url = path.startswith("http")
    if is_url:
        host = (urllib.parse.urlparse(path).hostname or "").lower()
    else:
        real = os.path.realpath(path)
    for r in rules.get("paths", []):
        rp = r.get("path", "")
        if rp.startswith("http") != is_url:
            continue
        if is_url:
            # ★ホスト完全一致（https://host/ ・ https://host ・ https://host* のどれで書いても同じ）。
            #   前方一致にすると host.evil.example や host@evil.example まで通る
            m = re.match(r"^https?://([^/*?\s]+)", rp)
            if m and host and host == m.group(1).lower().split(":")[0]:
                return r.get("reason", "理由未記入")
        elif _glob_match(rp, real):
            return r.get("reason", "理由未記入")
    return None


def is_document(path):
    """<html か <!doctype を持つ完全なページか（断片は数えない）"""
    try:
        with open(path, "rb") as f:
            head = f.read(65536).decode("utf-8", "replace")
    except Exception:
        return True  # 読めないものは検査に回して「読めない」と出す
    return bool(re.search(r"<html\b|<!doctype", head, re.I))


def html_files(root):
    """戻り値 (検査するファイル, 未検査の枚数, 除外した断片の枚数, {"dirs": 除外フォルダ名, "bak": .bak/.dc.html の枚数})。
    ★範囲が広すぎる（ホーム直下・/tmp 等）ときは None を返して検査しない＝警告で通す"""
    if os.path.realpath(root) in {os.path.realpath(os.path.expanduser("~")), "/", "/tmp", "/private/tmp"}:
        return None
    found, seen, unchecked, frags = [], 0, 0, 0
    info = {"dirs": set(), "bak": 0}
    for d, dirs, files in os.walk(root):
        seen += 1
        if seen > 3000:
            return None
        info["dirs"].update(x for x in dirs if x in SKIP_DIRS or x.startswith("."))
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith("."))
        for f in sorted(files):
            if not f.lower().endswith((".html", ".htm")):
                continue
            if ".bak" in f or f.endswith(".dc.html"):
                info["bak"] += 1
                continue
            p = os.path.join(d, f)
            if len(found) >= MAX_FILES:
                unchecked += 1  # ★黙って切り捨てない。数えて出す
            elif is_document(p):
                found.append(p)
            else:
                frags += 1
    info["dirs"] = sorted(info["dirs"])
    return found, unchecked, frags, info


def excl_note(frags, info):
    """★除外したものは黙らず出す（枚数と理由）"""
    parts = []
    if frags:
        parts.append(f"断片{frags}枚（<html を含まない）")
    if info.get("bak"):
        parts.append(f".bak／.dc.html {info['bak']}枚（控え・書き出し前）")
    if info.get("dirs"):
        parts.append("除外フォルダ " + ",".join(info["dirs"]) + "（ビルド生成物・履歴）")
    return ("\n除外：" + "／".join(parts)) if parts else ""


def failures(html):
    from web_tracking_check import check_html
    return [f"{name}（{note}）" for name, ok, note in check_html(html) if ok is False]


def gate_publish(cmd, cwd, found):
    root = deploy_dir(cmd, cwd, found)
    reason = exempt_reason(root)
    if reason:
        log(f"通した（対象外） {root} ／ {reason}")
        out(context=f"計測の検問：{root} は対象外として登録済み（{reason}）。")
    r = html_files(root) if os.path.isdir(root) else ([], 0, 0, {})
    if r is None:
        log(f"通した（範囲が広すぎ・警告） {root}")
        out(context=f"★計測の検問：公開する場所 {root} が広すぎて検査できなかった。"
                    "--cwd で公開フォルダを明示するか、公開後に web_tracking_check.py <URL> を通すこと。")
    files, unchecked, frags, info = r
    xn = excl_note(frags, info)
    if not files:
        log(f"通した（HTML無し・警告） {root} 断片{frags}枚 未検査{unchecked}枚")
        out(context=f"★計測の検問：{root} に検査できる HTML（<html を持つ完全なページ）が見つからず静的に検査できなかった"
                    f"（断片として除外 {frags}枚）。公開後に python3 ~/vivid-ai-hq/bin/web_tracking_check.py <URL> を必ず通すこと。" + xn)
    more_note = xn
    if unchecked:
        more_note += (f"\n★未検査{unchecked}枚（1回の検査は{MAX_FILES}枚まで）。残りは公開後に "
                     "python3 ~/vivid-ai-hq/bin/web_tracking_check.py <URL> --paths … で検査すること。")
    bad = {}
    for f in files:
        try:
            ng = failures(open(f, encoding="utf-8", errors="replace").read())
        except Exception as e:
            ng = [f"読めない（{e}）"]
        if ng:
            bad[os.path.relpath(f, root)] = ng
    if not bad:
        log(f"通した（全{len(files)}枚 ✓・未検査{unchecked}枚・断片{frags}枚） {root}")
        out(context=f"計測の検問：{len(files)}枚とも計測セットあり（発火の確認は別）。" + more_note)
    lines = [f"・{k}：{' ／ '.join(v)}" for k, v in list(bad.items())[:8]]
    more = f"\n…ほか {len(bad) - 8} 枚" if len(bad) > 8 else ""
    log(f"止めた {root} ✗{len(bad)}/{len(files)}枚 未検査{unchecked}枚")
    out("deny",
        f"★計測セットが揃っていないので公開を止めた（{len(bad)}/{len(files)}枚）。\n" + "\n".join(lines) + more + more_note +
        "\n直し方：Skill web-tracking-setup の手順どおり ~/vivid-ai-hq/bin/web_tracking/snippet.html を <head> に入れる。"
        "\n社内画面など計測が不要な場所なら、理由を書いて ~/vivid-ai-hq/bin/web_tracking/exempt.json へ載せる（有璽氏の了解が要る）。")


class _Redirect(urllib.request.HTTPRedirectHandler):
    """★307/308 も追う（/usr/bin/python3 3.9 の urllib は 308 を追わず、転送先が計測入りでも deny していた）。最大5回"""
    max_redirections = 5

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return super().redirect_request(req, fp, 307 if code == 308 else code, msg, headers, newurl)

    http_error_308 = urllib.request.HTTPRedirectHandler.http_error_302


def is_own_host(host, own):
    """自社のホストか。★末尾一致は「.」区切り（evil-vivid-global.com は一致しない）。
    own が空なら全部検査（安全側）。vercel.app（自社の Vercel エイリアス）は常に自社扱い"""
    if not own:
        return True
    host = (host or "").lower()
    return bool(host) and any(host == d or host.endswith("." + d) for d in own + OWN_EXTRA)


def _check_one(u, per):
    """着地先を1本検査する。戻り値 ("ok"|"ng"|"timeout", [✗の一覧])"""
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (fukuchi gate)"})
        with urllib.request.build_opener(_Redirect()).open(req, timeout=per) as r:
            return "ok", failures(r.read(2000000).decode("utf-8", "replace"))
    except (socket.timeout, TimeoutError):
        return "timeout", []
    except urllib.error.HTTPError as e:
        if e.code == 403:  # bot 検問など。「計測なし」とは断定できない＝検査できなかった扱い（警告で通す）
            return "blocked", []
        return "ng", [f"開けない（{str(e)[:60]}）"]
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            return "timeout", []
        return "ng", [f"開けない（{str(e)[:60]}）"]
    except Exception as e:
        return "ng", [f"開けない（{str(e)[:60]}）"]


def check_landings(urls, budget, per):
    """★並列で取得し、全体に時間上限を設ける（直列だと 1本×8秒×本数 で検問自体が固まる）。
    戻り値 {url: (状態, ✗一覧)}。上限までに終わらなかった url は入らない"""
    import web_tracking_check  # noqa: F401  ← スレッドの外で先に読み込む
    results = {}

    def work(u):
        results[u] = _check_one(u, per)

    threads = [threading.Thread(target=work, args=(u,), daemon=True) for u in urls]
    for t in threads:
        t.start()
    deadline = time.time() + budget
    for t in threads:
        t.join(max(0.0, deadline - time.time()))
    return dict(results)


def gate_sb_send(cmd, cwd):
    text = cmd
    for m in re.finditer(r"@([^\s\"']+)", cmd):  # -d @f ／ -d@f ／ --data @f ／ --data-binary @f
        p = os.path.join(cwd, os.path.expanduser(m.group(1)))
        try:
            if os.path.isfile(p):
                text += "\n" + open(p, encoding="utf-8", errors="replace").read(1000000)
        except Exception:
            pass
    text = text.replace("\\/", "/")  # JSON の https:\/\/ エスケープ
    urls = sorted(set(u.rstrip(".,)\"';") for u in URL_RE.findall(text)))
    urls = [u for u in urls if "salesbreaker.jp" not in u and "sbroute.net" not in u]
    if not urls:
        log("通した（SB文面・URL無し）")
        out(context="計測の検問：文面に着地先URLが無い（認知目的なら可）。")
    own = [d.lower() for d in load_exempt().get("own_domains", [])]  # ★無ければ全URLを検査（安全側）
    mine, others, skipped = [], [], 0
    for u in urls:
        host = (urllib.parse.urlparse(u).hostname or "").lower()
        if not is_own_host(host, [d for d in own]):
            others.append(u)
        elif exempt_reason(u):
            skipped += 1
        else:
            mine.append(u)
    note = ""
    if others:
        note = f"／自社以外のURL {len(others)}本は検査していない（{', '.join(others[:3])}）"
    res = check_landings(mine, SB_BUDGET, SB_URL_TIMEOUT) if mine else {}
    bad = [f"・{u}：{' ／ '.join(v[1])}" for u, v in res.items() if v[1]]
    late = [u for u in mine if u not in res or res[u][0] in ("timeout", "blocked")]
    if bad:
        log(f"止めた（SB文面） ✗{len(bad)} 時間切れ{len(late)}")
        out("deny", "★文面の着地先に計測セットが無いので保存を止めた。\n" + "\n".join(bad) +
            (f"\n（ほか {len(late)} 本は時間内に検査できなかった）" if late else "") +
            "\n着地先へ Skill web-tracking-setup の計測セットを入れてから保存すること。")
    if late:
        log(f"通した（SB文面・検査できなかった{len(late)}本・警告） {late}")
        out(context=f"★計測の検問：着地先 {len(late)} 本を検査できなかった（時間切れ・403 など。全体{SB_BUDGET:g}秒）。止めずに通したが、"
                    "保存前に python3 ~/vivid-ai-hq/bin/web_tracking_check.py <URL> を必ず手で通すこと。"
                    f"（{', '.join(late[:3])}）{note}")
    log(f"通した（SB文面 ✓{len(mine)}・対象外{skipped}・自社以外{len(others)}）")
    out(context=f"計測の検問：着地先 {len(mine)} 本は計測セットあり／対象外 {skipped} 本{note}。")


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
    found = find_publish(cmd)
    if found:
        gate_publish(cmd, cwd, found)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail-open
        log(f"フック自身の例外で通した：{e}")
        sys.exit(0)
