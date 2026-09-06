#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack通知の共通部品 ── 判断が要ることは必ずここを通し、★押せるボタンで出す

  from notify import ask, tell
  ask('受付シートの2行', {'1': 'toBとして登録', '2': '保留'})   # 判断を仰ぐ（★ボタンで出る）
  tell('毎朝の同期が終わりました', '408件更新／新規0')            # 報告するだけ

なぜ要るか（2026-08-20 有璽氏）
  「承認しないと進まないんでしょ。Slackに通知を出すようにして」
  ── 承認待ちで止まっているのに、それが有璽氏へ届いていなかった。
  止まっていることが本人に見えないなら、それは止まっているのではなく**消えている**。

★チャンネルへは投げない。DMのみ（他のメンバーの邪魔になるため）。

────────────────────────────────────────────────────────────
★★このファイルの置き場所について（2026-09-05・4回目の巻き戻りで真因が判明）
────────────────────────────────────────────────────────────
  **正本は `~/vivid-ai-hq/bin/hooks/notify.py`。`~/.vivid-relay/notify.py` は複製。**

  `bin/vivid-sync.sh`（cron */15）が `bin/setup_hooks.sh` を無条件で呼び、
  `setup_hooks.sh` が `bin/hooks/*.py` を `~/.vivid-relay/` へ**上書きコピー**する。
  ＝ `~/.vivid-relay/notify.py` だけを直すと、**15分以内に旧版へ戻される。**

  実測（2026-09-05）── 9/4・9/5 に2回、この改修が完成直後に消えた。
  消えた回は「vivid-relay 側だけ」を直しており、同じ日に `bin/hooks/self_audit.py` を
  直した分は生き残っていた。**差は git 管理下に書いたかどうかの1点だけ。**

  ★次にこのファイルを直す人へ ： **必ず `bin/hooks/` 側を編集し、commit する。**
    `~/.vivid-relay/` 側を直接編集しない（15分後に消える）。
────────────────────────────────────────────────────────────

★判断は必ずボタンで出す（2026-09-04・09-05 有璽氏・★4回目の指摘）
  「クリックするだけのタイプであれば、私でも確認は取れます。今はSlack側への
    通知方法がバラバラです。クリックして答えられるような状況にしてください」

  ask()  … 中身は ask_hub.ask() へ委譲する。★ボタン付きで届く
           出せなかったら False を返す。★記述式（番号を打たせる形）へは落とさない
           落とすと「選択式にしろ」という指示が静かに巻き戻るため
  tell() … 報告だけ。判断語が混ざっていたら stderr へ警告する（ブロックはしない）
"""

import os
import sys
import json
import datetime
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RELAY = os.path.join(os.path.expanduser('~'), '.vivid-relay')
DM = 'D0AT4NQ6X7D'          # 有璽氏とのDM
PENDING = os.path.join(RELAY, 'slack_pending.json')
# ★config.env は自分と同じディレクトリに置かれる（＝配布先の ~/.vivid-relay/）。
#   兄弟の ask_hub.py / hook_permission_slack.py と同じ書き方に揃えてある。
#   ★RELAY を使って絶対パスで書くと、bin/manus.py の同じ定義と二重定義になり
#     check.sh 項目8 が鳴る（2026-09-05 実測）。パスの正本を増やさない。
CONFIG_ENV = os.path.join(HERE, 'config.env')
_TOK = None


# ── 判断語 ──────────────────────────────────────────────────
# 報告 tell() にこれが混ざっていたら、それは報告ではなく判断依頼。
# ★ブロックはしない（誤検知で報告が止まる方が害が大きい）。stderr に出すだけ。
CLAIM_WORDS = (
    '判断を仰', '判断をお願い', 'ご判断', '判断が要', '判断待ち',
    'どちらにしま', 'どうしますか', 'どうしましょう', 'いかがしますか',
    'よろしいでしょうか', 'よろしいですか',
    '承認をお願い', 'ご承認', '決めてください', '選んでください',
    'ご指示', '指示をください', '進めてよいか', '進めますか', '投げますか',
    '可否をご',
)


def contains_judgment_words(text):
    """判断語が入っていれば、当たった語の一覧を返す（無ければ空リスト）。

    ★self_audit.py / memory_sweep.py のように、AIの自由出力をそのまま
      tell() へ渡す側が、送る前にこれを呼んで ask_hub.ask() へ回すために公開している。
    """
    t = text or ''
    return [w for w in CLAIM_WORDS if w in t]


def _muted():
    """★検査・テスト中は本物のSlackへ飛ばさない（2026-08-20 実地）

    つるの検査が本番のNotionへは1文字も書かなかった一方、
    **Slack通知だけは本物の有璽氏のDMへ飛んでいた**（09:30〜09:32に8件）。
    「書き込みを止めた」と「副作用を全部止めた」は別。
    検査ハーネスは VIVID_NOTIFY_OFF=1 を立てること。
    """
    return os.environ.get('VIVID_NOTIFY_OFF') == '1'


def _ask_hub():
    """ask_hub モジュールを取りに行く。★実際に動く方（~/.vivid-relay）を優先する。

    ask_hub.py は git 管理外で ~/.vivid-relay/ にしか無い。
    HERE（bin/hooks）だけを見ると、リポジトリ側で実行したときに黙って失敗する。
    """
    for p in (RELAY, HERE):
        if p not in sys.path:
            sys.path.insert(0, p)
    import ask_hub          # noqa: E402
    return ask_hub


def _tok():
    global _TOK
    if _TOK is None:
        for line in open(CONFIG_ENV):
            if line.startswith('SLACK_BOT_TOKEN='):
                _TOK = line.split('=', 1)[1].strip().strip('"')
    return _TOK


def _post(text, unfurl=False):
    """★報告（tell）専用の送信口。判断依頼はここを通さない（ボタンが付かないため）。"""
    try:
        r = urllib.request.Request(
            'https://slack.com/api/chat.postMessage',
            data=json.dumps({'channel': DM, 'text': text,
                             'unfurl_links': unfurl}).encode(),
            headers={'Authorization': 'Bearer ' + _tok(),
                     'Content-Type': 'application/json; charset=utf-8'})
        return json.load(urllib.request.urlopen(r)).get('ok', False)
    except Exception as e:
        sys.stderr.write('[Slack] 送れず ： %s\n' % e)
        return False


def tell(title, body='', link=''):
    """報告するだけ。返事は要らない。
    ★冒頭に「返信不要」を必ず付ける。付けないと有璽氏が
      「これは答えないといけないのか」と迷う（2026-08-20 実地）

    ★判断語が混ざっていたら警告する（2026-09-04）。報告の中に判断を紛れ込ませるのが
      いちばん悪い形 ── 「返信は要りません」と書いた同じ文で判断を求めることになる。
    """
    hits = contains_judgment_words('%s\n%s' % (title, body))
    if hits:
        sys.stderr.write(
            '[notify] ★報告に判断語が入っています（%s）。\n'
            '         判断は tell() ではなく ask() で、ボタン付きで出してください。\n'
            % '／'.join(hits))
    if _muted():
        sys.stderr.write('[notify] ★検査中のため送らない\n')
        return False
    t = '📋 *%s*  _（報告です。返信は要りません）_' % title
    if body:
        t += '\n' + body
    if link:
        t += '\n' + link
    return _post(t, unfurl=bool(link))


def _as_option_list(options):
    """既存の呼び出し方 {'1': '説明', '2': '説明'} を ask_hub の並びへ直す。

    先頭だけ primary（押してほしい既定）にする。list/tuple で渡されたらそのまま使う。
    """
    if isinstance(options, dict):
        pairs = [options[k] for k in sorted(options)]
    else:
        pairs = list(options)
    out = []
    for i, o in enumerate(pairs):
        if isinstance(o, (list, tuple)):
            label, style = (list(o) + [None])[:2]
        else:
            label, style = o, ('primary' if i == 0 else None)
        out.append((label, style))
    return out


def ask(topic, options, detail='', link='', kind='その他', asked_by='AI',
        question=''):
    """判断を仰ぐ。★中身は ask_hub.ask() へ委譲する＝Slackにボタンが出る。

    呼び方と戻り値（bool）は 2026-08-20 版から変えていない。
    既存の呼び出し元（findings_escalate.py）は無改修で動く。

    ★出せなかったときに記述式（_post で番号を打たせる形）へは落とさない。
      落とすと、有璽氏の指示「選択式にしろ」が事故のたびに静かに巻き戻る。
      出せなかったことは False で返し、呼んだ側が失敗として扱う。

    ★kind は ask_hub.KINDS の8種（開発／営業／福祉／広報／財務／法務／個人／その他）
      のどれか。ここに無い値を渡すと ValueError で落ちる（2026-09-04 に '経営' で
      予約通知が落ちた実例がある）。
    """
    if _muted():
        sys.stderr.write('[notify] ★検査中のため送らない\n')
        return False
    opts = _as_option_list(options)
    if len(opts) > 4:
        sys.stderr.write('[notify] ★選択肢が%d個。ask_hub の上限は4つ\n' % len(opts))
    try:
        ask_hub = _ask_hub()
        r = ask_hub.ask(subject=topic,
                        question=question or 'どうしますか（押すだけで返せます）',
                        options=opts, detail=detail, link=link,
                        asked_by=asked_by, kind=kind)
    except Exception as e:
        sys.stderr.write('[notify] ★ボタン付きで出せなかった ： %r\n'
                         '         ★記述式へは落としません（指示が巻き戻るため）\n' % e)
        return False
    if not r or not r.get('posted'):
        sys.stderr.write('[notify] ★投稿されませんでした（ask_id=%s）\n'
                         % (r or {}).get('ask_id'))
        return False

    # ★塞ぐ役はこちら側に残す。ask_hub は「誰も止めない」設計のまま触らない。
    try:
        json.dump({'topic': topic,
                   'options': options if isinstance(options, dict)
                   else {str(i + 1): o[0] for i, o in enumerate(opts)},
                   'ask_id': r['ask_id'],
                   'asked_at': datetime.datetime.now().isoformat()},
                  open(PENDING, 'w'), ensure_ascii=False, indent=1)
    except Exception as e:
        sys.stderr.write('[notify] ★pending を書けませんでした ： %r\n' % e)
    return True


def _blocked_hours(d):
    try:
        t = datetime.datetime.fromisoformat(d.get('asked_at'))
        return round((datetime.datetime.now() - t).total_seconds() / 3600.0, 1)
    except Exception:
        return None


def pending():
    """いま判断待ちがあるか。あれば中身を返す（無ければ None）。

    ★answered の正は ask_hub_queue.json 側に置く（2026-09-05）。
      押したのに解けない、が 9.1時間 続いた実例があるため、こちらの
      slack_pending.json を見て判定しない。ask_id があれば都度問い合わせる。

    ★問い合わせに失敗したら、旧ファイルの中身で判定する（塞いだままにする）。
      推測で解くより塞ぐ方が安全。ただし黙らない（stderr に出す）。
    """
    if not os.path.exists(PENDING):
        return None
    try:
        d = json.load(open(PENDING))
    except Exception:
        return None
    if d.get('answered'):          # ★旧経路（slack_inbox が番号で答えた分）も今も効く
        return None

    aid = d.get('ask_id') or d.get('superseded_by')
    if aid:
        try:
            ask_hub = _ask_hub()
            if ask_hub.answer_of(aid):
                return None        # ★ボタンが押されている＝解けた
        except Exception as e:
            sys.stderr.write('[notify] ★答えを確かめられませんでした ： %r\n'
                             '         塞いだまま扱います\n' % e)
    d['blocked_hours'] = _blocked_hours(d)
    return d


def link_pending(ask_id, by=''):
    """この pending の答えは、あちらのボタン（ask_id）で決まる、と宣言する。

    ★「回答済みにする」操作ではない。押されるまでは塞いだまま。
    件名が違うために機械が同一と判定できない孤児を、★人の宣言を根拠に結ぶための口。
    件名の近さで自動的に結ばない（似た件名の古い依頼の答えで誤って解けるため）。

    戻り値 ： 結べたら True。台帳にその受付番号が無ければ False（拒否する）。
    """
    try:
        d = json.load(open(PENDING))
    except Exception:
        return False
    try:
        ask_hub = _ask_hub()
        if not any(i.get('ask_id') == ask_id
                   for i in (ask_hub._load() or {'items': {}})['items'].values()):
            sys.stderr.write('[notify] ★台帳に受付番号 %s がありません\n' % ask_id)
            return False
    except Exception as e:
        sys.stderr.write('[notify] ★台帳を読めませんでした ： %r\n' % e)
        return False
    d['superseded_by'] = ask_id
    d['linked_by'] = by
    d['linked_at'] = datetime.datetime.now().isoformat()
    json.dump(d, open(PENDING, 'w'), ensure_ascii=False, indent=1)
    return True


if __name__ == '__main__':
    p = pending()
    if not p:
        print('判断待ち ： なし')
    else:
        print('判断待ち ： %s（%s時間 塞がっています）'
              % (p['topic'], p.get('blocked_hours')))
