#!/usr/bin/env python3
"""計測の検問（hook_web_tracking_gate.py）の回帰テスト。直したら必ず全件通す。
  python3 ~/vivid-ai-hq/bin/web_tracking/test_gate.py
★テストの文字列はこのファイルの中にある＝実行コマンドには公開の文字が出ない（検問に誤って止められない）
★着地先の検査は 127.0.0.1 のローカルサーバで行う（例外：ゲームブルの1件だけ実ネット）。node が無いときは JS の項だけ SKIP"""
import http.server, importlib.util, json, os, shutil, subprocess, sys, tempfile, threading, time

HOME = os.path.expanduser("~")
HOOK = os.path.join(HOME, "vivid-ai-hq/bin/hooks/hook_web_tracking_gate.py")
BINDIR = os.path.join(HOME, "vivid-ai-hq/bin")
SNIP = os.path.join(BINDIR, "web_tracking/snippet.html")
F = os.path.join(BINDIR, "web_tracking/selfcheck_fixture")
sys.path.insert(0, BINDIR)

FILL = {"{{SB_TRACK_ID}}": "17e298ff-5e02-4630-a16d-0f4f25ede23a", "{{SB_TRACK_TOKEN}}": "x",
        "{{GTM_ID}}": "GTM-PQX3L4TQ", "{{CLARITY_ID}}": "abcd1234ef"}
s = open(SNIP, encoding="utf-8").read()
for k, v in FILL.items():
    s = s.replace(k, v)
OK_HTML = "<!doctype html><html><head>" + s + '</head><body><a data-cta="hero">x</a></body></html>'
BARE_HTML = "<!doctype html><html><head><title>t</title></head><body>計測なし</body></html>"

tmp = tempfile.mkdtemp(prefix="gate_test_")
ok_dir, empty_dir = os.path.join(tmp, "ok"), os.path.join(tmp, "empty")
os.makedirs(ok_dir); os.makedirs(empty_dir)
open(os.path.join(ok_dir, "index.html"), "w").write(OK_HTML)


# ── ローカルの着地先（ネットに出ない）
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/hang"):
            time.sleep(60)
            return
        if self.path.startswith("/r30"):  # /r307 /r308 → /untracked へ転送
            self.send_response(int(self.path[2:5])); self.send_header("Location", "/ok" if self.path.endswith("ok") else "/untracked")
            self.send_header("Content-Length", "0"); self.end_headers()
            return
        if self.path.startswith("/chain"):  # /chain4 → /chain3 → … → /untracked（308 を連鎖）
            n = int(self.path[6:])
            self.send_response(308); self.send_header("Location", "/chain%d" % (n - 1) if n > 0 else "/untracked")
            self.send_header("Content-Length", "0"); self.end_headers()
            return
        if self.path.startswith("/forbidden") or self.path.startswith("/missing"):
            code = 403 if self.path.startswith("/forbidden") else 404
            self.send_response(code); self.send_header("Content-Length", "0"); self.end_headers()
            return
        if self.path.startswith("/slow"):
            time.sleep(2)  # 遅いが応答はする（並列なら3本で約2秒・直列なら約6秒）
        body = (OK_HTML if self.path.startswith("/ok") else BARE_HTML).encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def log_message(self, *a):
        pass


class Srv(http.server.ThreadingHTTPServer):
    daemon_threads = True


srv = Srv(("127.0.0.1", 0), H)
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
U = "http://127.0.0.1:%d" % PORT
EX = os.path.join(tmp, "exempt_test.json")
json.dump({"own_domains": ["127.0.0.1"], "paths": []}, open(EX, "w"))
ENV_SB = {"VIVID_GATE_EXEMPT": EX, "VIVID_GATE_SB_BUDGET": "3", "VIVID_GATE_SB_URL_TIMEOUT": "30"}
open(os.path.join(tmp, "body.json"), "w").write('{"b":"%s/untracked"}' % U)

SB = "https://salesbreaker.jp/api/operator/v0/templates/save"
CASES = [  # (説明, コマンド, cwd, 期待: deny / note / none, {env:…, has:…, max_sec:…})
    ("heredoc内の vercel deploy・redeploy.sh", "python3 - <<'E'\nx='''\n  vercel deploy --prod\n  redeploy.sh\n'''\nE", F, "none", {}),
    ("commitメッセージ内の文字", 'git commit -m "redeploy.sh を直した; vercel deploy"', F, "none", {}),
    ("ゲームブルLP（クリックログ無し）", "vercel deploy --prod", HOME + "/Documents/gamemarke_lp", "deny", {}),
    ("稼働盤（対象外）", "cd ~/vivid-ai-hq/web/kadoban && npx vercel deploy --prod --yes", "/tmp", "note", {}),
    ("見本 --cwd", "vercel deploy --cwd ~/vivid-ai-hq/bin/web_tracking/selfcheck_fixture", "/tmp", "deny", {}),
    ("計測入り", "vercel deploy --prod", ok_dir, "note", {"has": "1枚とも計測セットあり"}),
    ("HTML無し（警告で通す）", "vercel --prod", empty_dir, "note", {}),
    ("npx --yes vercel --prod", "npx --yes vercel --prod", F, "deny", {}),
    ("環境変数つき", "VERCEL_ORG_ID=x vercel --prod", F, "deny", {}),
    ("cd してから素の vercel", "cd %s && vercel" % F, "/", "deny", {}),
    ("改行の2行目で vercel", "echo start\nvercel --prod", F, "deny", {}),
    ("echo vercel deploy", "echo vercel deploy", F, "none", {}),
    ("vercel ls --prod（閲覧）", "npx vercel ls --prod", "/tmp", "none", {}),
    ("vercel env pull（閲覧）", "vercel env pull", F, "none", {}),
    ("redeploy.sh（プレビュー対象外）", "cd ~/lifestandup-wp/static-preview && ./redeploy.sh", "/tmp", "note", {}),
    ("redeploy.sh（見本の場所）", "cd %s && bash ./redeploy.sh" % F, "/", "deny", {}),
    ("netlify deploy", "netlify deploy --prod", F, "deny", {}),
    ("こどもステーション demo（対象外）", "vercel deploy --prod", HOME + "/kodomo-station-demo-v6", "note", {}),
    ("SB文面：着地先ゲームブル（実ネット）", 'curl -X POST %s -d "{\\"b\\":\\"https://gamemarke.vivid-global.com/\\"}"' % SB, "/tmp", "deny", {}),
    ("SB文面：着地先JFBI（対象外）", 'curl -X POST %s -d "{\\"b\\":\\"https://jfbi.vivid-global.com/\\"}"' % SB, "/tmp", "note", {}),
    ("SBのURLを文中に書いただけ", 'echo "%s を叩く予定"' % SB, "/tmp", "none", {}),
    ("/tmp で vercel --prod（広すぎ）", "vercel --prod", "/tmp", "note", {}),
    ("無関係", "ls -la", "/tmp", "none", {}),

    # ── 項目4：コマンドの取りこぼし（すべて計測無しの見本 F を公開する → 止まるのが正しい）
    ("小文字変数 url=$(…)", "url=$(vercel --prod)", F, "deny", {}),
    ("export URL=$(…)", "export URL=$(vercel --prod --yes)", F, "deny", {}),
    ("timeout 120 vercel", "timeout 120 vercel --prod", F, "deny", {}),
    ("nohup vercel", "nohup vercel --prod", F, "deny", {}),
    ("nice -n 10 vercel", "nice -n 10 vercel --prod", F, "deny", {}),
    ("bash -c '…'", "bash -c 'vercel --prod'", F, "deny", {}),
    ("bash -lc 'cd … && …'", "bash -lc 'cd %s && vercel --prod'" % F, "/", "deny", {}),
    ("if vercel …; then", "if vercel --prod; then echo done; fi", F, "deny", {}),
    ("xargs vercel", "echo x | xargs vercel --prod", F, "deny", {}),
    ("pushd X && vercel", "pushd %s && vercel --prod" % F, "/", "deny", {}),
    ("(cd X && vercel)", "(cd %s && vercel --prod)" % F, "/", "deny", {}),
    ("vercel <dir> --prod（位置引数＝公開先）", "vercel %s --prod" % F, "/", "deny", {}),
    ("vercel <計測入りdir> --prod", "vercel %s --prod" % ok_dir, F, "note", {"has": "1枚とも計測セットあり"}),
    ("echo \"vercel --prod\"（クォート内）", 'echo "vercel --prod"', F, "none", {}),

    # ── 項目5：閲覧の誤検知
    ("vercel --scope team ls（閲覧）", "vercel --scope team ls", F, "none", {}),
    ("npx vercel --scope team ls（閲覧）", "npx vercel --scope team ls", F, "none", {}),
    ("vercel --token abc ls（閲覧）", "vercel --token abc ls", F, "none", {}),
    ("vercel --help（閲覧）", "vercel --help", F, "none", {}),
    ("vercel -h（閲覧）", "vercel -h", F, "none", {}),
    ("vercel deploy --help（閲覧）", "vercel deploy --help", F, "none", {}),
    ("vercel --scope team --prod（公開）", "vercel --scope team --prod", F, "deny", {}),
    ("vercel --scope team deploy（公開）", "vercel --scope team deploy", F, "deny", {}),

    # ── 項目2・3：SalesBreaker 側（着地先は 127.0.0.1 のローカルサーバ）
    ("SB：http:// の着地先", "curl -X POST %s -d '{\"b\":\"%s/untracked\"}'" % (SB, U), "/tmp", "deny", {"env": ENV_SB}),
    ("SB：JSON の \\/ エスケープ", "curl -X POST %s -d '{\"b\":\"http:\\/\\/127.0.0.1:%d\\/untracked\"}'" % (SB, PORT), "/tmp", "deny", {"env": ENV_SB}),
    ("SB：--data-binary @file", "curl -X POST %s --data-binary @body.json" % SB, tmp, "deny", {"env": ENV_SB}),
    ("SB：--data @file", "curl -X POST %s --data @body.json" % SB, tmp, "deny", {"env": ENV_SB}),
    ("SB：-d @file", "curl -X POST %s -d @body.json" % SB, tmp, "deny", {"env": ENV_SB}),
    ("SB：-d@file（空白なし）", "curl -X POST %s -d@body.json" % SB, tmp, "deny", {"env": ENV_SB}),
    ("SB：他社URL（カレンダー予約）だけ", "curl -X POST %s -d '{\"b\":\"https://calendar.app.google/abc\"}'" % SB, "/tmp", "note", {"env": ENV_SB, "has": "自社以外"}),
    ("SB：自社の計測入り＋他社URL", "curl -X POST %s -d '{\"b\":\"%s/ok と https://calendar.app.google/x\"}'" % (SB, U), "/tmp", "note", {"env": ENV_SB, "has": "自社以外"}),
    ("SB：自社の計測無し＋他社URL", "curl -X POST %s -d '{\"b\":\"%s/untracked と https://calendar.app.google/x\"}'" % (SB, U), "/tmp", "deny", {"env": ENV_SB}),

    # ── 項目1：着地先の検査は並列・全体上限つき（応答しない3本。直列なら 3×URL上限）
    ("SB：応答しない着地先3本 → 時間内に返り警告で通す",
     "curl -X POST %s -d '{\"b\":\"%s/hang1 %s/hang2 %s/hang3\"}'" % (SB, U, U, U), "/tmp", "note",
     {"env": ENV_SB, "max_sec": 9, "has": "検査できなかった"}),
    ("SB：2秒かかる着地先3本 → 並列なので約2秒（直列なら6秒）",
     "curl -X POST %s -d '{\"b\":\"%s/slow1 %s/slow2 %s/slow3\"}'" % (SB, U, U, U), "/tmp", "deny",
     {"env": {"VIVID_GATE_EXEMPT": EX}, "max_sec": 4.5}),
    ("SB：計測無し1本＋応答しない2本 → 計測無しは止める",
     "curl -X POST %s -d '{\"b\":\"%s/untracked %s/hang1 %s/hang2\"}'" % (SB, U, U, U), "/tmp", "deny",
     {"env": ENV_SB, "max_sec": 9}),
]

# ── 項目7：300枚超は「未検査N枚」を出す（計測入りを305枚）
many = os.path.join(tmp, "many")
os.makedirs(many)
for i in range(305):
    open(os.path.join(many, "p%03d.html" % i), "w").write(OK_HTML)
CASES.append(("305枚 → 未検査5枚を出す", "vercel --prod", many, "note", {"has": "未検査5枚"}))
# ── 項目7：断片・partials・.htm
tree = os.path.join(tmp, "tree")
for d in ("partials", "components", "includes", "sub", "archive", "review", "node_modules"):
    os.makedirs(os.path.join(tree, d))
open(os.path.join(tree, "a.html"), "w").write(BARE_HTML)
open(os.path.join(tree, "b.htm"), "w").write(BARE_HTML)
open(os.path.join(tree, "sub", "c.html"), "w").write(BARE_HTML)
open(os.path.join(tree, "frag.html"), "w").write("<div class='x'>断片</div>")
for d in ("partials", "components", "includes", "archive", "review"):
    open(os.path.join(tree, d, "p.html"), "w").write(BARE_HTML)
open(os.path.join(tree, "components", "frag2.html"), "w").write("<header>断片</header>")
open(os.path.join(tree, "node_modules", "n.html"), "w").write(BARE_HTML)
CASES.append(("C：archive/review/components/includes も検査（8枚とも計測無し）", "vercel --prod", tree, "deny", {"has": "8/8枚"}))
CASES.append(("C：除外した断片の枚数が出る", "vercel --prod", tree, "deny", {"has": "断片2枚"}))
CASES.append(("C：除外フォルダ名が出る", "vercel --prod", tree, "deny", {"has": "node_modules"}))
okt = os.path.join(tmp, "okt")
os.makedirs(os.path.join(okt, "archive")); os.makedirs(os.path.join(okt, ".vercel"))
open(os.path.join(okt, "archive", "a.html"), "w").write(OK_HTML)
open(os.path.join(okt, "frag.html"), "w").write("<div>x</div>")
CASES.append(("C：計測入り（archive も検査）でも断片1枚を出す", "vercel --prod", okt, "note", {"has": "断片1枚"}))

# ═══ 2周目：条件B（307/308 を追う・403 は断定しない）と小さな取りこぼし
CASES += [
    ("B：308 転送先が計測無し → deny", "curl -X POST %s -d '{\"b\":\"%s/r308\"}'" % (SB, U), "/tmp", "deny", {"env": ENV_SB}),
    ("B：308 転送先が計測入り → 通る（誤って deny しない）", "curl -X POST %s -d '{\"b\":\"%s/r308ok\"}'" % (SB, U), "/tmp", "note", {"env": ENV_SB, "has": "計測セットあり"}),
    ("B：307 転送先が計測入り → 通る", "curl -X POST %s -d '{\"b\":\"%s/r307ok\"}'" % (SB, U), "/tmp", "note", {"env": ENV_SB, "has": "計測セットあり"}),
    ("B：307 転送先が計測無し → deny", "curl -X POST %s -d '{\"b\":\"%s/r307\"}'" % (SB, U), "/tmp", "deny", {"env": ENV_SB}),
    ("B：308 が4回連鎖 → deny", "curl -X POST %s -d '{\"b\":\"%s/chain4\"}'" % (SB, U), "/tmp", "deny", {"env": ENV_SB}),
    ("B：403 → 警告で通す（断定しない）", "curl -X POST %s -d '{\"b\":\"%s/forbidden\"}'" % (SB, U), "/tmp", "note", {"env": ENV_SB, "has": "検査できなかった"}),
    ("B：404 は従来どおり deny", "curl -X POST %s -d '{\"b\":\"%s/missing\"}'" % (SB, U), "/tmp", "deny", {"env": ENV_SB}),
]
sp = os.path.join(tmp, "sp ace")
os.makedirs(sp)
open(os.path.join(sp, "index.html"), "w").write(BARE_HTML)
SPESC = sp.replace(" ", "\\ ")
CASES += [
    ("vc（別名）", "vc --prod", F, "deny", {}),
    ("vc ls（閲覧）", "vc ls", F, "none", {}),
    ("npx vercel@32.0.0", "npx vercel@32.0.0 --prod", F, "deny", {}),
    ("pnpm dlx vercel@latest", "pnpm dlx vercel@latest --prod", F, "deny", {}),
    ("source ./redeploy.sh", "cd %s && source ./redeploy.sh" % F, "/", "deny", {}),
    (". ./redeploy.sh", "cd %s && . ./redeploy.sh" % F, "/", "deny", {}),
    ("ssh host 'cmd'（中身を読む）", "ssh host 'cd %s && vercel --prod'" % F, "/", "deny", {}),
    ("ssh -p 22 -i key host cmd", "ssh -p 22 -i key host vercel --prod", F, "deny", {}),
    ("ssh host ls（閲覧）", "ssh host ls", F, "none", {}),
    ("netlify --dir=X（空白\\エスケープ）", "netlify deploy --dir=%s --prod" % SPESC, "/", "deny", {}),
    ("netlify --publish X", "netlify deploy --publish '%s' --prod" % sp, "/", "deny", {}),
    ("netlify -d X", "netlify deploy -d '%s'" % sp, "/", "deny", {}),
    ("--cwd 相対パス", "vercel --cwd selfcheck_fixture --prod", os.path.dirname(F), "deny", {}),
    ("--cwd=相対パス", "vercel --cwd=selfcheck_fixture --prod", os.path.dirname(F), "deny", {}),
    ("--cwd 空白入りパス", "vercel --cwd '%s' --prod" % sp, "/", "deny", {}),
    ("cd の \\ エスケープ", "cd %s && vercel --prod" % SPESC, "/", "deny", {}),
    ("cd の引用符つき空白パス", "cd '%s' && vercel --prod" % sp, "/", "deny", {}),
    ("vercel open（閲覧）", "vercel open", F, "none", {}),
    ("vercel telemetry status（閲覧）", "vercel telemetry status", F, "none", {}),
    ("vercel curl（閲覧）", "vercel curl /api/x", F, "none", {}),
    ("firebase deploy --help（閲覧）", "firebase deploy --help", F, "none", {}),
    ("netlify deploy --help（閲覧）", "netlify deploy --help", F, "none", {}),
    ("netlify deploy -h（閲覧）", "netlify deploy -h", F, "none", {}),
    ("kodomo-station-demo 本体（対象外）", "vercel deploy --prod", HOME + "/kodomo-station-demo", "note", {}),
    ("kodomo-station-demo-v9/x（対象外）", "vercel deploy --prod", HOME + "/kodomo-station-demo-v9/x", "note", {}),
]



def run(payload, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.time()
    r = subprocess.run([sys.executable, HOOK], input=payload, capture_output=True, text=True, timeout=120, env=e)
    dt = time.time() - t0
    if not r.stdout.strip():
        return "none", "", dt
    h = json.loads(r.stdout)["hookSpecificOutput"]
    if h.get("permissionDecision") == "deny":
        return "deny", h.get("permissionDecisionReason", ""), dt
    return "note", h.get("additionalContext", ""), dt


ng = 0
total = 0


def check(name, cond, detail=""):
    global ng, total
    total += 1
    ng += (not cond)
    print(("✓ " if cond else "✗ ") + name + ("" if cond else " ／ " + str(detail)[:160]))


for name, cmd, cwd, want, opt in CASES:
    got, msg, dt = run(json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": cwd}), opt.get("env"))
    good = got == want
    if opt.get("has") and opt["has"] not in msg:
        good = False
    if opt.get("max_sec") and dt > opt["max_sec"]:
        good = False
    total += 1
    ng += (not good)
    print(f"{'✓' if good else '✗'} {name:<40} 期待={want:<4} 結果={got:<4} {dt:4.1f}s {msg[:60].replace(chr(10), ' ')}")
got, _, _ = run("not json")
check("壊れた入力（fail-open）", got == "none")

# ── 単体：exempt の照合（項目8）
spec = importlib.util.spec_from_file_location("gate", HOOK)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
ex_json = os.path.join(tmp, "exempt_unit.json")
json.dump({"paths": [
    {"path": "~/gt-site", "reason": "非glob"},
    {"path": "~/gt-demo*", "reason": "glob"},
    {"path": "~/gt-a*/deep", "reason": "glob途中"},
    {"path": "https://ok.example.com*", "reason": "URL(*)"},
    {"path": "https://ok2.example.com/", "reason": "URL(/)"},
    {"path": "https://ok3.example.com", "reason": "URL"},
]}, open(ex_json, "w"))
gate.EXEMPT_FILE = ex_json
E = os.path.expanduser
for p in ("~/gt-site", "~/gt-site/sub/x", "~/gt-demo", "~/gt-demo-v6", "~/gt-demo-v6/x/y", "~/gt-ax/deep", "~/gt-ax/deep/z"):
    check("exempt 一致: " + p, bool(gate.exempt_reason(E(p))), gate.exempt_reason(E(p)))
for p in ("~/gt-site-evil", "~/gt-sit", "~/gt-ax/y/deep", "~/gt-ax", "~/other"):
    check("exempt 非一致: " + p, not gate.exempt_reason(E(p)), gate.exempt_reason(E(p)))
for u in ("https://ok.example.com", "https://ok.example.com/x?y=1", "https://ok2.example.com/a", "https://ok3.example.com/b",
          "https://OK.example.com:8443/z"):
    check("exempt URL 一致: " + u, bool(gate.exempt_reason(u)), gate.exempt_reason(u))
for u in ("https://ok.example.com.evil.example/", "https://ok.example.com@evil.example/", "https://evil.example/ok.example.com",
          "https://notok.example.com/", "https://ok2.example.com.evil.example"):
    check("exempt URL 非一致: " + u, not gate.exempt_reason(u), gate.exempt_reason(u))
gate.EXEMPT_FILE = os.path.join(BINDIR, "web_tracking/exempt.json")
check("実 exempt.json：jfbi 一致", bool(gate.exempt_reason("https://jfbi.vivid-global.com/")))
check("実 exempt.json：jfbi に似た別ホストは非一致", not gate.exempt_reason("https://jfbi.vivid-global.com.evil.example/"))

# ── 単体：条件A（*.vercel.app も自社扱い・末尾一致は「.」区切り）
own4 = ["vivid-global.com", "orange-works.co", "i-life-fukushi.com", "fuku-chi.com"]
real_own = gate.load_exempt().get("own_domains", [])
check("実 exempt.json：own_domains 4つが残っている", set(own4) <= set(real_own), real_own)
for h in ("gamemarkelp.vercel.app", "a.b.vercel.app", "vercel.app", "x.vivid-global.com", "vivid-global.com", "www.fuku-chi.com"):
    check("自社扱い: " + h, gate.is_own_host(h, real_own), h)
for h in ("evil-vivid-global.com", "vivid-global.com.evil.example", "xvercel.app", "vercel.app.evil.example", "calendar.app.google", ""):
    check("自社扱いでない: " + h, not gate.is_own_host(h, real_own), h)
check("own_domains が空なら全部検査（安全側）", gate.is_own_host("anything.example", []))

# ── 単体：html_files（項目7）
r = gate.html_files(tree)
names = sorted(os.path.relpath(x, tree) for x in r[0]) if r else None
want = sorted(["a.html", "b.htm", os.path.join("sub", "c.html")] + [os.path.join(d, "p.html") for d in ("partials", "components", "includes", "archive", "review")])
check("html_files：archive/review/components/includes も入り、node_modules と断片だけ除く", names == want, names)
check("html_files：断片を2枚除外と数える", bool(r) and r[2] == 2, r and r[2])
check("html_files：除外フォルダ名を返す", bool(r) and "node_modules" in r[3].get("dirs", []), r and r[3])
r2 = gate.html_files(many)
check("html_files：300枚で切り、未検査5枚", bool(r2) and len(r2[0]) == 300 and r2[1] == 5, r2 and (len(r2[0]), r2[1]))

# ── 単体：check_html（項目6）
import web_tracking_check as W


def fails(h):
    return [n for n, ok, _ in W.check_html(h) if ok is False]


check("check_html：完全なセットは ✗ 0", fails(OK_HTML) == [], fails(OK_HTML))
body_only = s[s.index("-->") + 3:].replace("<!-- ===== ここまで ===== -->", "")  # 先頭・末尾のコメントを除いた本体
commented = "<html><head><!-- " + body_only + " --></head><body></body></html>"
check("check_html：コメント内のタグは数えない",
      set(fails(commented)) >= {"SalesBreaker 1行タグ", "GTM コンテナ", "Microsoft Clarity", "クリックログ（cta_click）"}, fails(commented))
prose = ("<html><body><p>GTM-ABCDEF1 と clarity.ms/tag/abcdefgh12 と cta_click と "
         "salesbreaker.jp/v1/sb-track.js?id=17e298ff-5e02-4630-a16d-0f4f25ede23a</p></body></html>")
check("check_html：本文の文字列だけでは通らない（4つとも ✗）", len(fails(prose)) == 4, fails(prose))
inline = "<html><head><script>var a='cta_click';</script></head></html>"
check("check_html：script 内の cta_click は数える", "クリックログ（cta_click）" not in fails(inline), fails(inline))
raw = open(SNIP, encoding="utf-8").read()
head_comment = raw[:raw.index("-->")]
check("snippet.html 先頭コメントに {{…}} が無い", "{{" not in head_comment, head_comment[:120])
half = raw
idx = half.index("-->")
body_part = half[idx:]
for k, v in FILL.items():
    body_part = body_part.replace(k, v)
half = half[:idx] + body_part  # 本体4か所だけ差し替え（コメントはそのまま）
check("check_html：本体だけ差し替えてコメントを残しても誤爆しない",
      "差し替え忘れ {{…}}" not in fails("<html><head>" + half + "</head></html>"), fails("<html><head>" + half + "</head></html>"))
check("check_html：未差し替えは ✗", "差し替え忘れ {{…}}" in fails("<html><head>" + raw + "</head></html>"))

# ── JS（項目9）
if shutil.which("node"):
    r = subprocess.run(["node", os.path.join(BINDIR, "web_tracking/test_snippet.js"), SNIP], capture_output=True, text=True, timeout=60)
    for line in r.stdout.strip().splitlines():
        if line.startswith(("✓ JS", "✗ JS")):
            total += 1
            ng += line.startswith("✗")
            print(line)
    check("JS：node の終了コード 0", r.returncode == 0, r.stderr[:160])
else:
    print("- JS の項は node が無いので SKIP")

try:
    srv.shutdown()
except Exception:
    pass
shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{'✗ 失敗 %d 件' % ng if ng else '✓ 全件合格'}（{total}件）")
sys.exit(1 if ng else 0)
