#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端末の承認ダイアログを Slack のボタンで解く（PermissionRequest フック）

★直したい状態（部品の言葉を使わない）
  ①「有璽氏が端末の前に居なくても、Slack のボタンだけで承認を返せる」
  ②「押す必要のない偽の通知が来ない」
  ★blocks の有無や関数名で合格を出さない。この2文で判定する。

経緯
  2026-08-20 有璽氏「この合間に挟むイエスノーってやつを、Slackでも出るようにしろ」
  2026-09-05 12:36 通知 → 12:40 有璽氏が Slack で「はい」→ ★届かなかった。
             12:45 その「はい」を slack_inbox.py が新しい依頼として拾い、別セッションが起きただけ
  2026-09-05 12:52 有璽氏「現場の構造は改修したいね」＝運用で回避せず構造を直す
  2026-09-06 有璽氏「承認ダイアログの件はもう確実に早くして」

★実測（2026-09-06・隔離HOMEで PTY まで起こして測った。★推測で書き換えない）
  対話（TUI）＋ 権限モードが dontAsk 以外
      → ★発火する。allow / deny の決定がそのまま効く（I2「Allowed by PermissionRequest hook」
        ／ I3 deny の message がモデルの応答へそのまま伝わった）
      → ★フックが返るまで親は待つ。45秒の待機を実測（I4・45.012秒）
      → ★`async: true` が付いていると決定は捨てられ、対話ダイアログが永久に残る（I5・3回再現）
  対話 ＋ dontAsk（この2機の settings.json の既定）→ ★発火しない。即拒否される（I6/I7/I8）
  非対話（claude -p）→ ★一度も発火しない（T1〜T10）。PreToolUse へ逃げても、
        ask ルールに一致した呼び出しは allow で上書きできない（P1/P3）
  → memory/reference_permission_request_hook_headless.md に全部ある

★偽の通知を止めた（2026-09-06 実測）
  有璽氏のDMに残る「承認待ちで止まっています」83件のうち ★63件が ```ls``` ちょうど。
  08:20 に18件・08:40 に18件（＝18日間、毎日2通）。
  正体：cron 08:20 の hook_selfcheck.py が、このフックへ
        {"tool_name":"Bash","tool_input":{"command":"ls"}} を流して生死を見ている。
        cron 08:40 の self_audit.py も内部で hook_selfcheck.py を呼ぶ（self_audit.py:59）。
  ★本物の PermissionRequest には必ず session_id が入る（実測キー10種）。探針には入っていない。
  → ★session_id が無い呼び出しでは投稿しない。生死の点検には今までどおり
     suppressOutput を返すので、hook_selfcheck は変更なしで通る。

★安全側の線引き（★ここは設計の分岐。変えるときは有璽氏の承認が要る）
  ① 遠隔（Slackのボタン）で許可してよい ： 下の NEVER_REMOTE_* に当たらないもの
  ② ★絶対に端末でしか許可しない ： fukuchi-core「承認が要る操作」のうち
       外へ出る／お金／正本の削除／規範の変更 ＋ この検問そのものを緩める操作
  ③ ★答えが来なかったとき（時間切れ）は★許可側へ倒さない。
       何も返さず端末のダイアログへ落とす。ここで deny にすると、
       有璽氏が戻ってきても端末で許可し直せなくなるので、そうしない
  ④ 押せる人 ： ask_hub の宛先表（ROUTES）が唯一の出口＝有璽氏のDMのみ
  ⑤ 押し間違え ： 「拒否」は可逆（もう一度やらせればよい）。「許可」は不可逆になりうるので①②で守る
  ⑥ 2026-09-06 追加 ： ★内容を全部見せられないものは遠隔で許可させない。
       Bashは長すぎるコマンド（SHOW_MAX超）、Write/Editは中身が長すぎる（CONTENT_MAX超）、
       組み立てた detail が長すぎて Slack側で末尾が切れる（DETAIL_BUDGET超）場合は
       ボタンを出さず notify_only へ回す（＝有璽氏は端末で中身を見てから押すしかない）

★できないこと（正直に）
  ・Bash の中身は完全には見分けられない（`bash -c "$(...)"` のような包み方は素通りする）
  ・非対話（claude -p）では、そもそもこのフックが呼ばれない。効くのは対話セッションだけ
  ・時間切れで畳んだ問いは、ask_hub の台帳では open のまま残る
    （★AIが人の回答を騙って answered にしないため。ボタンは消すので押し損ねは起きない）

★2026-09-07 追加 ── MacBook からの承認待ちも Slack で返せるようにした（ビビ依頼）
  MacBook には SLACK_APP_TOKEN が無く、ask_hub.ask() を直接呼ぶと _require_receiver() で
  RuntimeError になる（設計どおり・正しい防御）。MacBook → mini の ssh は通る
  （逆は通らない・2026-09-07 ビビが実測）ので、この機に受信能力が無ければ
  `ssh mini` 経由で ask_hub.py の CLI（--ask / --answer-of / --close）を叩き、
  発行・照会・時間切れの畳みを mini へ委託する。台帳は常に mini の1か所に揃う。
  ★ssh が届かない場合は notify_only へ落ちる（無言で失敗しない）。
"""

import os
import sys
import json
import time
import socket
import hashlib
import re
import subprocess
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

DM = 'D0AT4NQ6X7D'                                   # 有璽氏とのDM（ask_hub と同じ宛先）
LAST = os.path.join(HERE, '.hook_last_notify.json')
LOG = os.path.join(HERE, 'hook_permission_slack.log')
ME = os.path.basename(__file__)

SSH_TARGET = 'mini'                              # ~/.ssh/config のエイリアス。MacBook→mini方向のみ通る
SSH_ASK_HUB = '~/.vivid-relay/ask_hub.py'         # mini 側の実体パス（展開はssh先のシェルに任せる）
SSH_ASK_TIMEOUT = 20                              # 秒。発行1回ぶん
SSH_POLL_TIMEOUT = 10                             # 秒。answer_of の照会1回ぶん
SSH_POLL_SEC = 5                                  # 秒。ssh越しのポーリング間隔（ローカルのPOLL_SECより長め。ssh起動コストを考慮）


def settings_paths():
    """★自分の登録が書いてある設定ファイルの候補（近い順）

    ★`~/.claude/settings.json` を決め打ちにしない。`CLAUDE_CODE_CONFIG_DIR`
    ではなく `CLAUDE_CONFIG_DIR` が立っているとそちらが正で、決め打ちだと
    ★効いていない方の設定を読んで判定する（2026-09-06 実測 ： 通し確認の
    隔離セッションで、本番の async: true を読み「遠隔承認できない」と誤判定した）。
    """
    out = []
    cd = os.environ.get('CLAUDE_CONFIG_DIR')
    if cd:
        out.append(os.path.join(cd, 'settings.json'))
    out.append(os.path.expanduser('~/.claude/settings.json'))
    return out

COOLDOWN = 90        # 秒。同じ内容の通知を連投しない
REUSE_SEC = 1800     # 秒。同じ内容は★新しく聞き直さず、同じ受付番号を見に行く
MIN_TIMEOUT = 60     # 秒。登録の timeout がこれ未満なら遠隔承認をしない
WAIT_MARGIN = 20     # 秒。登録の timeout より必ず手前で自分から返る
POLL_SEC = 2
MAX_WAIT = 3000

# ★内容を全部見せられないものは遠隔で許可させない（2026-09-06 有璽氏の線引き）
# 人が後から数字だけ変えられるよう1か所にまとめる。
SHOW_MAX = 300        # 文字。Bashのコマンドをこの長さまで見せる
CONTENT_MAX = 600     # 文字。Write/Edit の中身をこの長さまで見せる
DETAIL_BUDGET = 900   # 文字。ask_hub.py の DETAIL_MAX と同じ値にすること。
                      # ★片方だけ変えると、Slackの画面では末尾が切れているのに
                      # ボタンは出る、という食い違いが起きる

MACHINES = (('mac-mini', 'Mac mini'), ('macbook', 'MacBook'))

# ★遠隔では許可させない ── 端末でしか通さないもの（②の実体）
NEVER_REMOTE_TOOLS = (
    'mcp__claude_ai_Gmail__send_message',
    'mcp__claude_ai_Gmail__reply',
    'mcp__claude_ai_Gmail__forward',
    'mcp__claude_ai_Gmail__trash_message',
    'mcp__claude_ai_Gmail__trash_thread',
    'mcp__claude_ai_Slack__slack_send_message',
    'mcp__claude_ai_Slack__slack_schedule_message',
    'mcp__claude_ai_Google_Drive__trash_file',
    'mcp__claude_ai_Google_Calendar__create_event',
    'mcp__claude_ai_Google_Calendar__delete_event',
)
NEVER_REMOTE_PATHS = (
    '.claude/skills/',           # 規範の変更
    '.claude/settings.json',     # この検問そのもの
    'config.env',                # 鍵
    'hook_permission_slack.py',  # このファイル
    'ask_hub.py',                # 押す経路そのもの
)
NEVER_REMOTE_BASH = (
    (r'\brm\s+-rf\b', 'まとめて消す'),
    (r'\bsudo\b', '管理者権限'),
    (r'\bdd\s+if=', 'ディスクへの直接書き込み'),
    (r'\bdiskutil\b', 'ディスク操作'),
    (r'\bshutdown\b', '停止'),
    (r'\bmkfs', '初期化'),
    (r'git\s+push\b[^|;]*(--force|\s-f\b)', '履歴の強制上書き'),
    (r'\bcurl\b[^|;]*-X\s*(POST|PUT|DELETE)', '外へ出る'),
    (r'chat\.postMessage', 'Slackへ投稿'),
    (r'\bosascript\b', 'GUI操作'),
)


def log(msg):
    try:
        with open(LOG, 'a') as f:
            f.write('[%s] %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S %Z'), msg))
    except Exception:
        pass


def tok(name='SLACK_BOT_TOKEN'):
    try:
        for line in open(os.path.join(HERE, 'config.env')):
            if line.startswith(name + '='):
                return line.split('=', 1)[1].strip().strip('"')
    except Exception:
        pass
    return None


def muted():
    return os.environ.get('VIVID_NOTIFY_OFF') == '1'


def post(text):
    """★ボタンの無いただの通知。判断を求めない場面だけで使う"""
    if muted():
        log('★投げていない（VIVID_NOTIFY_OFF=1）')
        return
    t = tok()
    if not t:
        log('★投げていない（SLACK_BOT_TOKEN が無い）')
        return
    try:
        r = urllib.request.Request(
            'https://slack.com/api/chat.postMessage',
            data=json.dumps({'channel': DM, 'text': text,
                             'unfurl_links': False}).encode(),
            headers={'Authorization': 'Bearer ' + t,
                     'Content-Type': 'application/json; charset=utf-8'})
        urllib.request.urlopen(r, timeout=8)
    except Exception as e:
        log('★投稿できなかった ： %s' % e)


def _kv_preview(inp):
    """dict(tool_input) の中身を CONTENT_MAX まで見せる（JSON化）。

    ★mcp__ とその他（keysしか分からないツール）の両方から呼ぶ共通処理。
    ここに書く長さチェックを他の分岐へコピーしないこと。
    戻り値は (見せる文字列, cut)。空 dict なら ('', '')。
    """
    if not inp:
        return '', ''
    try:
        text = json.dumps(inp, ensure_ascii=False)
    except Exception:
        text = str(inp)
    cut = ''
    shown = text
    if len(text) > CONTENT_MAX:
        shown = text[:CONTENT_MAX]
        cut = '引数の中身が長すぎる（%d文字）' % len(text)
    return shown, cut


def brief(tool, inp):
    """何を承認しようとしているかを1〜2行で

    ★戻り値は (body, cut) の2つ。cut は「見せ切れなかった理由」の文字列
    （見せ切れたなら空文字）。★内容を全部見せられないものは、遠隔では
    許可させない（main() 側で cut を見て notify_only へ回す）。
    """
    if tool == 'Bash':
        cmd = str(inp.get('command', ''))
        desc = str(inp.get('description', ''))
        cut = ''
        shown = cmd
        if len(cmd) > SHOW_MAX:
            shown = cmd[:SHOW_MAX]
            cut = 'コマンドが長すぎる（%d文字）' % len(cmd)
        body = ('```%s```' % shown) + (('\n' + desc) if desc else '')
        return body, cut
    if tool == 'Edit':
        old = str(inp.get('old_string', ''))
        new = str(inp.get('new_string', ''))
        path = inp.get('file_path', '（不明）')
        cut = ''
        total = len(old) + len(new)
        show_old, show_new = old, new
        if total > CONTENT_MAX:
            half = CONTENT_MAX // 2
            show_old, show_new = old[:half], new[:half]
            cut = '書き換える中身が長すぎる（%d文字）' % total
        body = ('`%s`\n変更前 ：\n```%s```\n変更後 ：\n```%s```'
                % (path, show_old, show_new))
        return body, cut
    if tool in ('Write', 'NotebookEdit'):
        path = inp.get('file_path', '（不明）')
        content = str(inp.get('content', '') or inp.get('new_source', ''))
        cut = ''
        shown = content
        if len(content) > CONTENT_MAX:
            shown = content[:CONTENT_MAX]
            cut = '書き込む中身が長すぎる（%d文字）' % len(content)
        body = '`%s`\n```%s```' % (path, shown)
        return body, cut
    # ★mcp__ とその他は同じ扱い ── inp の中身を実際に見せる。長ければ cut を立てる。
    #   （長さチェックは _kv_preview() の1か所だけに書く。ここで2度書かない）
    if tool.startswith('mcp__'):
        parts = tool.split('__')
        svc = parts[1] if len(parts) > 1 else '?'
        act = parts[2] if len(parts) > 2 else '?'
        label = '%s の %s' % (svc, act)
    else:
        label = '引数'
    kv, cut = _kv_preview(inp)
    body = ('%s\n```%s```' % (label, kv)) if kv else label
    return body, cut


def where(d):
    """★どの機・どのセッション・どの権限モードか（第1段の中身）"""
    host = socket.gethostname()
    label = host
    for frag, name in MACHINES:
        if frag in host.lower():
            label = '%s（%s）' % (name, host)
            break
    ep = os.environ.get('CLAUDE_CODE_ENTRYPOINT', '')
    if ep == 'cli':
        kind = '対話（端末のTUI）'
    elif ep.startswith('sdk-'):
        kind = '非対話（claude -p）'
    else:
        kind = '判定不能（%s）' % (ep or '環境変数なし')
    return {'machine': label, 'kind': kind, 'entrypoint': ep,
            'session': str(d.get('session_id') or ''),
            'cwd': str(d.get('cwd') or ''),
            'mode': str(d.get('permission_mode') or ''),
            'transcript': str(d.get('transcript_path') or '')}


def head(w):
    lines = ['機 ： %s' % w['machine'],
             'セッション ： %s ・ %s' % (w['kind'], (w['session'] or '?')[:8])]
    if w['mode']:
        lines.append('権限モード ： %s' % w['mode'])
    if w['cwd']:
        lines.append('作業場所 ： `%s`' % w['cwd'])
    return '\n'.join(lines)


def reg():
    """★いま効いている設定から自分の登録を読む。遠隔承認が成立するかはここで決まる"""
    out = {'found': False, 'async': False, 'timeout': 0, 'why': '', 'src': ''}
    tried = []
    for path in settings_paths():
        try:
            d = json.load(open(path, encoding='utf-8'))
        except Exception as e:
            tried.append('%s（%s）' % (path, e))
            continue
        for blk in (d.get('hooks') or {}).get('PermissionRequest') or []:
            for h in blk.get('hooks') or []:
                if ME in str(h.get('command', '')):
                    out['found'] = True
                    out['async'] = bool(h.get('async'))
                    out['timeout'] = int(h.get('timeout') or 0)
                    out['src'] = path
                    return out
        tried.append('%s（登録なし）' % path)
    out['why'] = 'PermissionRequest への登録が見つからない ： %s' % ' / '.join(tried)
    return out


def can_ask(r):
    """★押しても効かない形でボタンを出さない（記述式より悪くなるのを防ぐ）"""
    if not r['found']:
        return False, r['why']
    if r['async']:
        return False, ('登録に async: true が付いている'
                       '（★押した結果を返せない。実測 I5 ： 対話ダイアログが永久に残る）')
    if r['timeout'] < MIN_TIMEOUT:
        return False, ('登録の timeout が %d秒しかない（%d秒以上が要る）'
                       % (r['timeout'], MIN_TIMEOUT))
    return True, ''


def never_remote(tool, inp):
    """★遠隔で許可させないものに当たるなら、その理由を返す（当たらなければ空文字）"""
    if tool in NEVER_REMOTE_TOOLS:
        return '外へ出る／消える操作（%s）' % tool
    hay = str(inp.get('file_path') or inp.get('path') or '')
    if tool == 'Bash':
        hay = hay + ' ' + str(inp.get('command') or '')
    for frag in NEVER_REMOTE_PATHS:
        if frag in hay:
            return '規範・鍵・検問そのものに触る（%s）' % frag
    if tool == 'Bash':
        cmd = str(inp.get('command') or '')
        for pat, why in NEVER_REMOTE_BASH:
            if re.search(pat, cmd):
                return '%s' % why
    return ''


def load_last():
    try:
        return json.load(open(LAST))
    except Exception:
        return {}


def save_last(o):
    try:
        json.dump(o, open(LAST, 'w'))
    except Exception:
        pass


def notify_only(w, tool, body, why):
    """第1段 ： ボタンは出せない。★どこで押せばよいかまで書く"""
    key = hashlib.md5(('%s|%s|%s' % (w['session'], tool, body)).encode()).hexdigest()
    st = load_last()
    if st.get('key') == key and time.time() - st.get('at', 0) < COOLDOWN:
        return {'suppressOutput': True}
    save_last({'key': key, 'at': time.time()})
    post('⏸ *承認待ちで止まっています*\n%s\n\n*%s*\n%s\n\n'
         '_★この通知にはボタンがありません（%s）。_\n'
         '_Slackで「はい」と返しても解けません。上の機の端末で押してください。_'
         % (head(w), tool, body, why))
    log('通知のみ ： %s ／ %s' % (tool, why))
    return {'suppressOutput': True}


def close_buttons(ask_hub, ask_id, headline):
    """★時間切れのときボタンだけ消す。台帳の status は書き換えない
       （AIが人の回答を騙って answered にしない ── 2026-09-06 #960e67 の反省）"""
    try:
        d = ask_hub._load() or {'items': {}}
        it = d['items'].get(ask_id)
        if not it or not it.get('ts'):
            return
        blocks = [b for b in ask_hub.build_blocks(it) if b.get('type') != 'actions']
        blocks.insert(0, {'type': 'section',
                          'text': {'type': 'mrkdwn', 'text': '*%s*' % headline}})
        ask_hub.api_post('chat.update', {'channel': it['channel'], 'ts': it['ts'],
                                         'text': headline, 'blocks': blocks})
    except Exception as e:
        log('★ボタンを畳めなかった #%s ： %s' % (ask_id, e))


def answered(ask_id, a):
    label = str(a.get('label') or '')
    free = str(a.get('free_text') or '')
    by = str(a.get('by') or '')
    if str(a.get('key')) == '1' and label.startswith('許可'):
        log('許可 #%s（%s）' % (ask_id, by))
        return {'hookSpecificOutput': {'hookEventName': 'PermissionRequest',
                                       'decision': {'behavior': 'allow'}},
                'systemMessage': '★Slackで「%s」が押されました（#%s ／ %s）'
                                 % (label, ask_id, by)}
    msg = ('Slackで「%s」が返りました（#%s ／ %s）。この操作は行わないでください。'
           % (label or '（無回答）', ask_id, by))
    if free:
        msg += '\n有璽氏のコメント ： %s' % free
    log('拒否 #%s ： %s' % (ask_id, label))
    return {'hookSpecificOutput': {'hookEventName': 'PermissionRequest',
                                   'decision': {'behavior': 'deny', 'message': msg}}}


def _has_local_receiver():
    """この機は Slack から答えを受け取れるか（＝SLACK_APP_TOKEN があるか＝mini か）

    ★ask_hub._require_receiver() と同じ判定をここでも行う。あちらは「投げさせない
    （例外を投げる）」役、こちらは「投げる前にどちらの経路を使うか決める」役。
    """
    try:
        import ask_hub
        ask_hub._tok('SLACK_APP_TOKEN')
        return True
    except Exception:
        return False


def _ssh_run(args_list, input_bytes, timeout):
    """★共通のssh実行。到達できなければ None を返す（例外を外へ投げない）"""
    try:
        proc = subprocess.run(
            ['ssh', SSH_TARGET] + args_list,
            input=input_bytes, capture_output=True, timeout=timeout)
    except Exception as e:
        log('★ssh %s へ到達できない（%r）： %r' % (SSH_TARGET, args_list, e))
        return None
    out = (proc.stdout or b'').decode('utf-8', 'replace').strip()
    if not out:
        log('★ssh %s の応答が空（%r・rc=%s・stderr=%r）'
            % (SSH_TARGET, args_list, proc.returncode, (proc.stderr or b'')[:300]))
        return None
    try:
        return json.loads(out.splitlines()[-1])
    except Exception as e:
        log('★ssh %s の応答を読めない（%r・%s）： %r' % (SSH_TARGET, args_list, e, out[:300]))
        return None


def _ssh_ask(payload):
    """★MacBook（SLACK_APP_TOKEN が無い機）から、mini へ発行を委託する
    （2026-09-07・ビビの実測：MacBook→mini は通る／逆は通らない）。
    戻り値 (ask_id, posted)。到達できなければ (None, False)。
    """
    r = _ssh_run(['/usr/bin/python3 %s --ask' % SSH_ASK_HUB],
                 json.dumps(payload, ensure_ascii=False).encode('utf-8'), SSH_ASK_TIMEOUT)
    if not r or r.get('error'):
        if r and r.get('error'):
            log('★mini 側で発行できなかった ： %s' % r['error'])
        return None, False
    return r.get('ask_id'), bool(r.get('posted'))


def _ssh_answer_of(ask_id):
    """★答えを mini へ問い合わせる。到達できなければ None（＝まだ、として扱う）"""
    r = _ssh_run(['/usr/bin/python3 %s --answer-of %s' % (SSH_ASK_HUB, ask_id)],
                 b'', SSH_POLL_TIMEOUT)
    return (r or {}).get('answer')


def _ssh_close(ask_id, headline):
    """★時間切れのボタンをmini経由で畳む"""
    r = _ssh_run(['/usr/bin/python3 %s --close %s' % (SSH_ASK_HUB, ask_id)],
                 json.dumps({'headline': headline}, ensure_ascii=False).encode('utf-8'),
                 SSH_ASK_TIMEOUT)
    if not r or not r.get('closed'):
        log('★ssh経由でボタンを畳めなかった #%s' % ask_id)


def remote(w, tool, body, r):
    """第2段 ： Slack のボタンで許可／拒否を受け取り、その決定を返す

    ★この機が Slack から答えを受け取れなければ（SLACK_APP_TOKEN が無ければ）、
      ssh mini 経由で発行・照会する（2026-09-07・MacBookの承認待ちを解くため）。
      台帳は常に mini の1か所（受信側の常駐＝slack_socket.py がそこに居るため）。
      ★ssh が届かないときは通知だけに落とす（無言で失敗しない）。
    """
    local = _has_local_receiver()
    ask_hub = None
    if local:
        try:
            import ask_hub
        except Exception as e:
            return notify_only(w, tool, body, 'ask_hub を読み込めない（%s）' % e)

    key = hashlib.md5(('%s|%s|%s' % (w['session'], tool, body)).encode()).hexdigest()
    st = load_last()
    ask_id = None
    if (st.get('key') == key and st.get('ask_id')
            and time.time() - st.get('at', 0) < REUSE_SEC):
        ask_id = st['ask_id']          # ★同じ問いを新しく聞き直さない
        log('同じ内容なので #%s を見に行く' % ask_id)
    if not ask_id:
        subject = '端末の承認（%s）' % tool
        question = 'この操作を許可しますか。★押さないと、この作業はここで止まります。'
        detail = '%s\n\n*%s*\n%s' % (head(w), tool, body)
        if local:
            try:
                res = ask_hub.ask(subject=subject, question=question,
                                  options=[('許可する', 'primary'), ('拒否する', 'danger')],
                                  detail=detail, asked_by='承認ゲート', kind='開発')
            except Exception as e:
                return notify_only(w, tool, body, 'ask_hub へ出せなかった（%s）' % e)
            if not res.get('posted'):
                return notify_only(w, tool, body, 'ask_hub が投稿しなかった')
            ask_id = res['ask_id']
        else:
            payload = {'subject': subject, 'question': question,
                      'options': [['許可する', 'primary'], ['拒否する', 'danger']],
                      'detail': detail, 'asked_by': '承認ゲート', 'kind': '開発'}
            ask_id, posted = _ssh_ask(payload)
            if not ask_id or not posted:
                return notify_only(w, tool, body,
                                   'mini へ発行できなかった（ssh %s へ届かないか、'
                                   'mini 側の発行に失敗しました）' % SSH_TARGET)
        save_last({'key': key, 'at': time.time(), 'ask_id': ask_id})
        log('ボタンで聞いた #%s ： %s（経路=%s）' % (ask_id, tool, 'local' if local else 'ssh %s' % SSH_TARGET))

    wait = min(MAX_WAIT, max(0, r['timeout'] - WAIT_MARGIN))
    poll = POLL_SEC if local else SSH_POLL_SEC
    deadline = time.time() + wait
    while True:
        try:
            a = ask_hub.answer_of(ask_id) if local else _ssh_answer_of(ask_id)
        except Exception:
            a = None
        if a:
            return answered(ask_id, a)
        if time.time() >= deadline:
            break
        time.sleep(poll)

    headline = ('⌛ 時間切れ ── %d分待ちました。押しても解けません。もう一度やらせてください'
                % max(1, wait // 60))
    if local:
        close_buttons(ask_hub, ask_id, headline)
    else:
        _ssh_close(ask_id, headline)
    log('時間切れ #%s（%d秒・経路=%s）' % (ask_id, wait, 'local' if local else 'ssh %s' % SSH_TARGET))
    return {'suppressOutput': True,
            'systemMessage': ('★Slackへ承認を出しましたが %d 秒のあいだ回答がありません。'
                              '端末のダイアログで押してください。' % wait)}


def main():
    try:
        raw = sys.stdin.read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        d = {}
    tool = d.get('tool_name', '（不明）')
    inp = d.get('tool_input') or {}
    w = where(d)

    # ★自己点検の探針には投稿しない（2026-09-06 ： DMの83件中63件がこれだった）
    if not w['session']:
        return {'suppressOutput': True}

    body, cut = brief(tool, inp)
    r = reg()
    ok, why = can_ask(r)
    blocked = never_remote(tool, inp)
    if blocked:
        ok, why = False, '★遠隔では許可しない種類 ： %s' % blocked
    if ok and cut:
        ok, why = False, '★遠隔では許可しない ： 内容を全部は見せられない（%s）' % cut
    if ok and len(head(w)) + len(tool) + len(body) > DETAIL_BUDGET:
        # ★組み立てた detail が長すぎて Slack 側で末尾が切れる＝全部見せられていない
        ok, why = False, '★遠隔では許可しない ： 内容を全部は見せられない（表示欄に収まらない）'
    if ok:
        return remote(w, tool, body, r)
    return notify_only(w, tool, body, why)


if __name__ == '__main__':
    out = {'suppressOutput': True}
    try:
        out = main() or {'suppressOutput': True}
    except Exception as e:
        log('★例外で終わった ： %r' % (e,))
    try:
        sys.stdout.write(json.dumps(out, ensure_ascii=False))
    except Exception:
        pass
    sys.exit(0)      # ★何があっても本体を止めない
