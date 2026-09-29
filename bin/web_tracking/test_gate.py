#!/usr/bin/env python3
"""計測の検問（hook_web_tracking_gate.py）の回帰テスト。直したら必ず全件通す。
  python3 ~/vivid-ai-hq/bin/web_tracking/test_gate.py
★テストの文字列はこのファイルの中にある＝実行コマンドには公開の文字が出ない（検問に誤って止められない）"""
import json, os, subprocess, sys, tempfile

HOME = os.path.expanduser("~")
HOOK = os.path.join(HOME, "vivid-ai-hq/bin/hooks/hook_web_tracking_gate.py")
SNIP = os.path.join(HOME, "vivid-ai-hq/bin/web_tracking/snippet.html")
F = os.path.join(HOME, "vivid-ai-hq/bin/web_tracking/selfcheck_fixture")

tmp = tempfile.mkdtemp(prefix="gate_test_")
ok_dir, empty_dir = os.path.join(tmp, "ok"), os.path.join(tmp, "empty")
os.makedirs(ok_dir); os.makedirs(empty_dir)
s = open(SNIP, encoding="utf-8").read()
for k, v in {"{{SB_TRACK_ID}}": "17e298ff-5e02-4630-a16d-0f4f25ede23a", "{{SB_TRACK_TOKEN}}": "x",
             "{{GTM_ID}}": "GTM-PQX3L4TQ", "{{CLARITY_ID}}": "abcd1234ef"}.items():
    s = s.replace(k, v)
open(os.path.join(ok_dir, "index.html"), "w").write(s + '<a data-cta="hero">x</a>')

SB = "https://salesbreaker.jp/api/operator/v0/templates/save"
CASES = [  # (説明, コマンド, cwd, 期待: deny / note / none)
    ("heredoc内の vercel deploy・redeploy.sh", "python3 - <<'E'\nx='''\n  vercel deploy --prod\n  redeploy.sh\n'''\nE", F, "none"),
    ("commitメッセージ内の文字", 'git commit -m "redeploy.sh を直した; vercel deploy"', F, "none"),
    ("ゲームブルLP（クリックログ無し）", "vercel deploy --prod", HOME + "/Documents/gamemarke_lp", "deny"),
    ("稼働盤（対象外）", "cd ~/vivid-ai-hq/web/kadoban && npx vercel deploy --prod --yes", "/tmp", "note"),
    ("見本 --cwd", "vercel deploy --cwd ~/vivid-ai-hq/bin/web_tracking/selfcheck_fixture", "/tmp", "deny"),
    ("計測入り", "vercel deploy --prod", ok_dir, "note"),
    ("HTML無し（警告で通す）", "vercel --prod", empty_dir, "note"),
    ("npx --yes vercel --prod", "npx --yes vercel --prod", F, "deny"),
    ("環境変数つき", "VERCEL_ORG_ID=x vercel --prod", F, "deny"),
    ("cd してから素の vercel", "cd %s && vercel" % F, "/", "deny"),
    ("改行の2行目で vercel", "echo start\nvercel --prod", F, "deny"),
    ("echo vercel deploy", "echo vercel deploy", F, "none"),
    ("vercel ls --prod（閲覧）", "npx vercel ls --prod", "/tmp", "none"),
    ("vercel env pull（閲覧）", "vercel env pull", F, "none"),
    ("redeploy.sh（プレビュー対象外）", "cd ~/lifestandup-wp/static-preview && ./redeploy.sh", "/tmp", "note"),
    ("redeploy.sh（見本の場所）", "cd %s && bash ./redeploy.sh" % F, "/", "deny"),
    ("netlify deploy", "netlify deploy --prod", F, "deny"),
    ("こどもステーション demo（対象外）", "vercel deploy --prod", HOME + "/kodomo-station-demo-v6", "note"),
    ("SB文面：着地先ゲームブル", 'curl -X POST %s -d "{\\"b\\":\\"https://gamemarke.vivid-global.com/\\"}"' % SB, "/tmp", "deny"),
    ("SB文面：着地先JFBI（対象外）", 'curl -X POST %s -d "{\\"b\\":\\"https://jfbi.vivid-global.com/\\"}"' % SB, "/tmp", "note"),
    ("SBのURLを文中に書いただけ", 'echo "%s を叩く予定"' % SB, "/tmp", "none"),
    ("/tmp で vercel --prod（広すぎ）", "vercel --prod", "/tmp", "note"),
    ("無関係", "ls -la", "/tmp", "none"),
]


def run(payload):
    r = subprocess.run([sys.executable, HOOK], input=payload, capture_output=True, text=True, timeout=60)
    if not r.stdout.strip():
        return "none", ""
    h = json.loads(r.stdout)["hookSpecificOutput"]
    if h.get("permissionDecision") == "deny":
        return "deny", h.get("permissionDecisionReason", "")
    return "note", h.get("additionalContext", "")


ng = 0
for name, cmd, cwd, want in CASES:
    got, msg = run(json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": cwd}))
    mark = "✓" if got == want else "✗"
    ng += got != want
    print(f"{mark} {name:<34} 期待={want:<4} 結果={got:<4} {msg[:70].replace(chr(10), ' ')}")
got, _ = run("not json")
print(("✓" if got == "none" else "✗") + " 壊れた入力（fail-open）"); ng += got != "none"
print(f"\n{'✗ 失敗 %d 件' % ng if ng else '✓ 全件合格'}（{len(CASES) + 1}件）")
sys.exit(1 if ng else 0)
