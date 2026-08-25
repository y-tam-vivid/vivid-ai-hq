#!/bin/bash
# いま何ができるかを、書いてあるものではなく道具本人に聞く。
# 台帳へ書き写すと腐るので、必要になるたびここで取り直す。★鍵の値は絶対に出力しない。
#   使い方   capability_check.sh          要約
#            capability_check.sh --full   SalesBreakerの全ルートを route 付きで出す
#            capability_check.sh --md     Notion/共有へ貼れる Markdown で出す
# 索引 → memory/reference_tool_access_map.md

set -u
GTM="$HOME/Downloads/JapanGtmAgentWorkspace"
MODE="${1:-}"
[ "$MODE" = "--md" ] && H="### " || H="== "

echo "${H}接続している道具（claude mcp list）"
if command -v claude >/dev/null 2>&1; then
  claude mcp list 2>/dev/null | grep -E "Connected|Failed|✔|✘" | sed 's/^/  /'
else
  echo "  claude CLI が無い"
fi

echo
echo "${H}SalesBreaker（HTTP API・MCPではない）"
if [ -f "$GTM/.env" ] && grep -q '^SALESBREAKER_API_KEY=' "$GTM/.env"; then
  python3 - "$GTM" "$MODE" <<'PY'
import io, json, sys, urllib.request, urllib.error
gtm, mode = sys.argv[1], sys.argv[2]
env = {}
for line in io.open(gtm + '/.env', encoding='utf-8'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
base = env.get('SALESBREAKER_BASE_URL', 'https://salesbreaker.jp').rstrip('/')
key = env.get('SALESBREAKER_API_KEY', '')

def call(path):
    req = urllib.request.Request(base + path, headers={'Authorization': 'Bearer ' + key, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

try:
    d = call('/api/operator/v0/help/capabilities')
    caps = d.get('data', {}).get('capabilities', [])
    # ★availability は 'enabled' 'enabled_turn75_validation_route' など turn 付き。前方一致で見る
    on = [c for c in caps if str(c.get('availability', '')).startswith('enabled')]
    print('  contract   :', d.get('data', {}).get('contract_version'))
    print('  使える口   : %d / %d' % (len(on), len(caps)))
    if mode == '--full' or mode == '--md':
        print()
        if mode == '--md':
            print('| capability | route | 変更 | 状態 |')
            print('|---|---|---|---|')
            for c in sorted(on, key=lambda x: x.get('capability', '')):
                gate = '検証のみ' if 'validation' in str(c.get('availability')) else ('読取' if c.get('mutation') == 'read-only' else '書込')
                print('| `%s` | `%s` | %s | %s |' % (c.get('capability'), c.get('route', ''), gate, c.get('risk', '')))
        else:
            for c in sorted(on, key=lambda x: x.get('capability', '')):
                gate = '検証のみ' if 'validation' in str(c.get('availability')) else ('読取  ' if c.get('mutation') == 'read-only' else '書込  ')
                print('    %-34s %s %s' % (c.get('capability'), gate, c.get('route', '')))
    else:
        ro = [c['capability'] for c in on if c.get('mutation') == 'read-only']
        wr = [c['capability'] for c in on if c.get('mutation') != 'read-only']
        print('  読み取り   :', ', '.join(ro) or '(なし)')
        print('  書き込み系 :', ', '.join(wr) or '(なし)')
    gate = [c['capability'] for c in on if 'validation' in str(c.get('availability'))]
    print()
    print('  ★検証のみ（実行されない）:', ', '.join(gate) or '(なし)')
    print('  ★送信は常に無効 ── "Worker execution and sending remain disabled"')
    try:
        a = call('/api/operator/v0/account/status')['data']
        sub = a.get('subscription', {}); rd = a.get('readiness', {})
        print('  プラン     : %s（%s）' % (sub.get('plan_name'), sub.get('status')))
        print('  送信準備   : sender_verified=%s / dkim=%s / company_profile=%s'
              % (rd.get('sender_verified'), rd.get('dkim_tokens_present'), rd.get('company_profile_present')))
        for s in a.get('sender_profiles', [])[:3]:
            print('    送信者   : %s / %s / %s' % (s.get('profile_name'), s.get('company_name'), s.get('sender_email')))
    except Exception as e:
        print('  account.status 取得できず:', type(e).__name__)
except urllib.error.HTTPError as e:
    print('  ★HTTP', e.code, '── 鍵が失効しているか権限バンドル不足。管理画面で新しい鍵を発行する')
except Exception as e:
    print('  ★到達できず:', type(e).__name__, str(e)[:120])
PY
  V="$GTM/workspace-version.json"
  [ -f "$V" ] && echo "  workspace  : $(python3 -c "import json,sys;d=json.load(open('$V'));print(d.get('version'),d.get('workspace_name'))" 2>/dev/null)"
  echo "  ★First Rule: SalesBreakerの「APIキー / AI連携」ページの最新版と上を突き合わせる"
  echo "  API仕様    : $GTM/docs/ に13本（リスト品質・CRM出力・権限・制限とエラー・実例…）"
else
  echo "  ★.env に SALESBREAKER_API_KEY が無い（$GTM）"
fi

echo
echo "${H}Google（Sheets / Drive）"
if ssh -o ConnectTimeout=6 -o BatchMode=yes mini 'test -f ~/.vivid-relay/google_token.json' 2>/dev/null; then
  ssh -o ConnectTimeout=6 -o BatchMode=yes mini 'python3 -c "
import json,io
d=json.load(io.open(\"/Users/yuji_macmini/.vivid-relay/google_token.json\"))
sc=d.get(\"scopes\") or d.get(\"scope\") or []
if isinstance(sc,str): sc=sc.split()
print(\"  scopes     :\", \", \".join(s.replace(\"https://www.googleapis.com/auth/\",\"\") for s in sc))
"' 2>/dev/null
  echo "  ★script が無ければ Apps Script は実行できない（GAS経由の道は無い）"
else
  echo "  mini へ到達できないか token が無い"
fi

echo
echo "${H}Vercel"
if command -v npx >/dev/null 2>&1; then
  echo "  whoami     : $(npx --yes vercel@latest whoami 2>&1 | tail -1)"
  echo "  ★失効したら有璽氏が npx vercel login（ログインは代行不可）"
fi

echo
echo "${H}鍵の有無（値は読まない）"
[ -f "$HOME/.vivid-relay/config.env" ] && echo "  config.env :" $(grep -o '^[A-Z_]*' "$HOME/.vivid-relay/config.env" | sort -u | tr '\n' ' ')
[ -f "$GTM/.env" ] && echo "  GTM/.env   :" $(grep -o '^[A-Z_]*' "$GTM/.env" | sort -u | tr '\n' ' ')
echo "  さくらDNS  : 鍵なし・ゾーン編集APIも無い → 人の手"
echo "  kintone    : CSV手動のまま（API未接続）"
echo "  Chrome拡張 : claude-in-chrome は未接続（入れれば管理画面の操作を代行できる）"
echo
echo "※ 能力を台帳へ書き写さない。変わったと思ったら、このスクリプトを叩き直す。"
