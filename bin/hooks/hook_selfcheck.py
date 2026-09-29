#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フックが生きているかを毎朝みる（⑥の穴：フックが壊れても気づかない）"""
import os,sys,json,subprocess,tempfile,shutil,time
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
CASES=[
 ('hook_inject_memory.py','{"tool_name":"Bash","tool_input":{"command":"sheets_client"}}','additionalContext'),
 ('hook_catch_correction.py','{"prompt":"何回も言ってるやろ"}','additionalContext'),
 ('hook_permission_slack.py','{"tool_name":"Bash","tool_input":{"command":"ls"}}','suppressOutput'),
 # ★2026-08-29 追加（穴B・ビビ指摘）。役割違反の検問2本がPreToolUseに登録されているのに
 #   生存点検の対象外だった＝唯一の強い機械ゲートの生死を点検の外に置いていた。
 #   Bashのリダイレクト書込み疑いは exit0+JSON なのでCASES向き。
 ('hook_role_guard.py','{"tool_name":"Bash","tool_input":{"command":"cat > /tmp/selfcheck_probe.py <<EOF"},"session_id":"selfcheck"}','additionalContext'),
 ('hook_output_guard.py','{"tool_name":"Write","tool_input":{"file_path":"/tmp/selfcheck_probe.py","content":"for x in [1]:\\n    if x:\\n        print(\\\"OK\\\")\\nprint(\\\"すべて正常\\\")\\n"}}','additionalContext'),
 # ★2026-09-09 追加（Ｃ-1・有璽氏の承認）。実装済みなのに settings.json 未登録で4日間動かず、
 #   さらに★この点検の対象にも入っていなかった＝登録漏れを誰も見つけられない構造だった。
 #   ★対話セッションからの呼び出しは「警告のみ」なので additionalContext が返る。
 # ★2026-09-09 実測で判明：このフックは CLAUDE_CODE_ENTRYPOINT で対話/非対話を判定し、
 #   ★判定できないときは通す（fail-open）。cron や ssh 経由では環境変数が無く {} が返り、
 #   ★「反応しない」と誤検知する（★mini で実際に出た）。★そこで env を明示して叩く。
 ('hook_interactive_guard.py','{"tool_name":"AskUserQuestion","tool_input":{"questions":[]},"session_id":"selfcheck"}','additionalContext',{'CLAUDE_CODE_ENTRYPOINT':'cli'}),
 # ★2026-09-29 追加（有璽氏「即実装」）。計測タグの無い見本ページを公開しようとして★止まる（deny）のが正常。
 ('hook_web_tracking_gate.py','{"tool_name":"Bash","tool_input":{"command":"vercel deploy --cwd ~/vivid-ai-hq/bin/web_tracking/selfcheck_fixture"},"cwd":"/","session_id":"selfcheck"}','deny'),
]

# ★2026-08-30 つる依頼で修正（旧 PLAIN_CASES の穴C）。
#   実測2経路（つる）：
#     経路1＝ 2026-08-30 朝08:20のcron実行 → ~/.vivid-relay/hook_selfcheck.log 末尾が
#            「異常 1件 / hook_session_writeback.py ： 反応しない」。Notion⚙️自動処理レジスタも🔴。
#     経路2＝ 同じ実体を手で叩き直す（/usr/bin/python3 ~/.vivid-relay/hook_selfcheck.py）→
#            「6本とも正常」rc=0。
#   → 一致しない＝探針側の欠陥と確定。
#   原因：旧探針は transcript_path="/nonexistent" を渡していたため、
#   hook_session_writeback.py 側の check_asked_without_looking()／check_single_route_claim()
#   が「tp not isfile」で即 None を返し、main() はその先の git status 判定
#   （10分以上さわっていない未コミットが WATCH 配下にあるか）まで進んでいた。
#   ＝ 作業ツリーがきれいな朝（＝フックが設計どおり黙る場面）を「反応しない」と誤検出する。
#   慢性化した🔴でゲートが死ぬ型（memory/reference_a_warning_nobody_owns.md）。
#   直す方針：main() 内で git status より前に評価される「検査2」を実際に発火させる
#   2行transcriptを用意し、リポジトリの状態に一切依存しない形にする。
def _probe_writeback_stop():
    """hook_session_writeback.py の検査2（探さずに人へ投げた）を実際に発火させる。

    2行のJSONL transcriptを一時ディレクトリへ作り、子プロセスの HOME もその
    一時ディレクトリへ差し替えて実行する。
    ★HOME差し替えの理由：hook_session_writeback.py の LOG は
    expanduser('~/.vivid-relay/hook_writeback.log') で決め打ちされており、毎朝の
    点検がここへ1行書き足すと ~/.vivid-relay/dashboard_data.py（805〜820行）が
    「当日行・直近3日行」を数えて稼働盤へ出す数字に毎日+1の偽データが混ざる。
    HOMEをすり替えれば LOG も一時ディレクトリ側を指すため、本物のログには一切触れない。
    戻り値: (ok: bool, detail: str)

    ★2026-08-30 ステラ検査の条件（トレードオフの明記。直す必要はないと判定済み）：
    この探針が見ているのは main() 冒頭で必ず先に return する検査2
    （探さずに人へ投げた）の生死だけである。hook_session_writeback.py 本来の主目的
    ── 10分以上前の未コミット（memory/・WORKING.md・.claude/・bin/）を検出する
    git status ロジック（main() 後半）── は、検査2が先に return するため、
    この探針では一度も実行経路に乗らない。したがって「6本とも正常」は
    「hook_session_writeback.py の全機能が生きている」ことを意味しない。
    将来 WATCH タプルの誤記・STALE_MIN の計算誤り・git status 呼び出しの破損など、
    検査2と無関係な箇所で本来機能が壊れても、この探針は検知できず「正常」と報告し続ける。
    状態非依存にするための正しいトレードオフであり、直すべき欠陥ではない。
    ★あわせてつるの検算で分かった限界：つるは hook_session_writeback.py を丸ごと
    黙る版に差し替えることで異常を検出できることを実測したが、それは
    ファイル全体が死んだケースしか見ていない。部分的な破損は捕まえられない。
    """
    tmpdir = tempfile.mkdtemp(prefix='selfcheck_writeback_')
    try:
        tp = os.path.join(tmpdir, 'transcript.jsonl')
        with open(tp, 'w', encoding='utf-8') as f:
            f.write(json.dumps(
                {"type": "user", "message": {"content": "確認して"}},
                ensure_ascii=False) + '\n')
            f.write(json.dumps(
                {"type": "assistant", "message": {"content": [
                    {"type": "text", "text": "該当のファイルは存在しません。"}]}},
                ensure_ascii=False) + '\n')
        payload = json.dumps({
            "session_id": "selfcheck-probe",
            "transcript_path": tp,
            "stop_hook_active": False,
        })
        env = dict(os.environ)
        env['HOME'] = tmpdir
        r = subprocess.run(
            ['/usr/bin/python3', os.path.join(HERE, 'hook_session_writeback.py')],
            input=payload, capture_output=True, text=True, timeout=30, env=env)
        out = (r.stdout or '') + (r.stderr or '')
        expect = '探さずに人へ投げようとしています'
        return (expect in out), out[:200]
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _check_hook_session_writeback():
    """旧 PLAIN_CASES の後継。文字列一致のダミーpayloadではなく、検査2を実際に発火させて
    生存を確かめる（＝リポジトリの状態に依存しない）。"""
    ok, detail = _probe_writeback_stop()
    if ok:
        return None
    return 'hook_session_writeback.py ： 反応しない（出力先頭: %s）' % detail

def _check_web_gate_sb():
    """★2026-09-29 追加（検査の指摘）。計測の検問の「SalesBreaker 文面」経路の生死を点検する。
    見本（vercel 側）だけ点検していると、SB 経路が壊れても気づけない。
    ネットには出ない：127.0.0.1 の一時サーバに「計測の無いページ」を置き、その URL を文面に入れた
    保存コマンドを検問へ流す。着地先を自社ドメイン扱いにするため、一時の exempt.json を
    VIVID_GATE_EXEMPT で渡す（本物の exempt.json には触らない）。deny が返れば正常。
    ★ログ ~/.vivid-relay/web_tracking_gate.log へ「止めた（SB文面）」が毎朝1行増える（既存の見本ケースと同じ）"""
    import http.server, threading

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = '<!doctype html><html><head><title>t</title></head><body>selfcheck 計測なし</body></html>'.encode()
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmpdir = tempfile.mkdtemp(prefix='selfcheck_gate_')
    try:
        ex = os.path.join(tmpdir, 'exempt.json')
        with open(ex, 'w') as f:
            json.dump({'own_domains': ['127.0.0.1'], 'paths': []}, f)
        url = 'http://127.0.0.1:%d/' % srv.server_address[1]
        cmd = ("curl -X POST https://salesbreaker.jp/api/operator/v0/templates/save -d '{\"b\":\"%s\"}'" % url)
        payload = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': cmd}, 'cwd': '/tmp', 'session_id': 'selfcheck'})
        env = dict(os.environ)
        env['VIVID_GATE_EXEMPT'] = ex
        env['VIVID_GATE_SB_BUDGET'] = '10'
        r = subprocess.run(['/usr/bin/python3', os.path.join(HERE, 'hook_web_tracking_gate.py')], input=payload,
                           capture_output=True, text=True, timeout=30, env=env)
        d = json.loads(r.stdout or '{}')
        if d.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny':
            return None
        return 'hook_web_tracking_gate.py（SB文面） ： 反応しない（出力先頭: %s）' % (r.stdout or r.stderr)[:120]
    finally:
        srv.shutdown()
        srv.server_close()
        shutil.rmtree(tmpdir, ignore_errors=True)


def _web_gate_registration_problem(s):
    """★settings.json に計測の検問が Bash 向けに登録されているか。
    settings.json は機械ローカル（git外）で手で編集される＝行が消えても誰も気づけない
    （フックが在っても登録が無ければ、点検の見本ケースは通るのに実際の公開は素通りする）"""
    for e in s.get('hooks', {}).get('PreToolUse', []):
        if any('hook_web_tracking_gate.py' in (h.get('command') or '') for h in e.get('hooks', [])):
            m = e.get('matcher')
            if m in (None, '', '*') or 'Bash' in m:
                return None
            return 'settings.json ： hook_web_tracking_gate.py の matcher が Bash を含まない（%s）＝検問が効かない' % m
    return 'settings.json ： hook_web_tracking_gate.py が PreToolUse に登録されていない＝検問が効かない'


PLAIN_CHECKS = [_check_hook_session_writeback, _check_web_gate_sb]

ng=[]
for case in CASES:
    # ★4要素目（env の上書き）は任意。既存の3要素はそのまま動く（後方互換）
    f,inp,expect = case[0],case[1],case[2]
    envx = dict(os.environ)
    if len(case) >= 4 and case[3]:
        envx.update(case[3])
    # ★2026-09-19 ロビン依頼で追加（穴①：探針が本番ログを汚染していた）。
    #   実測：hook_catch_correction.py の LOG は HERE（__file__基準）でパスを組んでおり、
    #   hook_session_writeback.py と違って HOME環境変数の差し替えでは防げなかった。
    #   同スクリプトを VIVID_CORRECTIONS_LOG 環境変数対応にしたので、探針側は
    #   ここで一時ファイルへ向ける（_probe_writeback_stop() の HOME差し替えと同じ発想）。
    tmp_corr_dir = None
    if f == 'hook_catch_correction.py':
        tmp_corr_dir = tempfile.mkdtemp(prefix='selfcheck_corr_')
        envx['VIVID_CORRECTIONS_LOG'] = os.path.join(tmp_corr_dir, 'corrections.log')
    try:
        r=subprocess.run(['/usr/bin/python3',os.path.join(HERE,f)],input=inp,
                         capture_output=True,text=True,timeout=20,env=envx)
        d=json.loads(r.stdout or '{}')
        ok = expect in json.dumps(d) or expect in json.dumps(d.get('hookSpecificOutput',{}))
        if not ok: ng.append('%s ： 反応しない' % f)
    except Exception as e:
        ng.append('%s ： %s' % (f,str(e)[:80]))
    finally:
        if tmp_corr_dir:
            shutil.rmtree(tmp_corr_dir, ignore_errors=True)
for chk in PLAIN_CHECKS:
    try:
        msg = chk()
        if msg: ng.append(msg)
    except Exception as e:
        ng.append('%s ： %s' % (getattr(chk, '__name__', 'check'), str(e)[:80]))
# settings.json に登録されているか
# ★Stop を 2026-08-29 に追加。settings.json は機械ローカル（git外）で手で編集されるため、
#   Stop の行が消えても誰も気づけなかった（それが唯一の機械ゲート）。
try:
    s=json.load(open(os.path.expanduser('~/.claude/settings.json')))
    for ev in ('PreToolUse','UserPromptSubmit','PermissionRequest','Stop'):
        if ev not in s.get('hooks',{}): ng.append('settings.json に %s が無い' % ev)
    _p = _web_gate_registration_problem(s)
    if _p: ng.append(_p)
except Exception as e:
    ng.append('settings.json を読めない ： %s' % e)
# ★本数はベタ書きしない（数えた結果を出す）。bin/hooks/hook_output_guard.py の型
_n=len(CASES)+len(PLAIN_CHECKS)
# ★2026-08-30 つる依頼：時刻を入れる。ログにタイムスタンプが無く「いつ壊れたか」が
#   読めなかった（つるが実際に困った）。
_now=time.strftime('%Y-%m-%dT%H:%M:%S')
print('%s ★フック点検 ： %s' % (_now, ('異常 %d件' % len(ng) if ng else '%d本とも正常' % _n)))
for x in ng: print('   '+x)
try:
    from heartbeat import beat
    beat('フックの生存点検','失敗' if ng else '成功', '／'.join(ng)[:180] or '%d本とも正常' % _n)
except Exception as e: sys.stderr.write('[心拍] %s\n'%e)
sys.exit(1 if ng else 0)
