#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack通知の共通部品 ── 判断が要ることは必ずここを通してDMへ出す

  from notify import ask, tell
  ask('受付シートの2行', {'1': 'toBとして登録', '2': '保留'})   # 判断を仰ぐ
  tell('毎朝の同期が終わりました', '408件更新／新規0')            # 報告するだけ

なぜ要るか（2026-08-20 有璽氏）
  「承認しないと進まないんでしょ。Slackに通知を出すようにして」
  ── 承認待ちで止まっているのに、それが有璽氏へ届いていなかった。
  止まっていることが本人に見えないなら、それは止まっているのではなく**消えている**。

★チャンネルへは投げない。DMのみ（他のメンバーの邪魔になるため）。
★判断を仰いだら slack_pending.json へ選択肢を書く。
  有璽氏が番号で返信すると slack_inbox.py がそれを読んで処理する。
"""

import os
import sys
import json
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DM = 'D0AT4NQ6X7D'          # 有璽氏とのDM
PENDING = os.path.join(HERE, 'slack_pending.json')
_TOK = None


def _tok():
    global _TOK
    if _TOK is None:
        for line in open(os.path.join(HERE, 'config.env')):
            if line.startswith('SLACK_BOT_TOKEN='):
                _TOK = line.split('=', 1)[1].strip().strip('"')
    return _TOK


def _post(text, unfurl=False):
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
      「これは答えないといけないのか」と迷う（2026-08-20 実地）"""
    t = '📋 *%s*  _（報告です。返信は要りません）_' % title
    if body:
        t += '\n' + body
    if link:
        t += '\n' + link
    return _post(t, unfurl=bool(link))


def ask(topic, options, detail='', link=''):
    """判断を仰ぐ。options = {'1': '説明', '2': '説明'}
    ★これを呼んだら、返事が来るまで処理は進まない。
      進まないことを本人が知っている状態にするのが、この関数の役目

    ★選択肢は2つまでにする。3つ以上あるのは、こちらが決め切れていないだけ。
      長い説明を先に置かない。「何を選ぶのか」を先に、理由は後ろに。
      （2026-08-20 有璽氏「イエス・ノーで答えられるものじゃないじゃん」）"""
    if len(options) > 2:
        import sys as _s
        _s.stderr.write('[notify] ★選択肢が%d個。2つに絞れないか考え直すこと\n' % len(options))
    t = '❓ *答えてください ： %s*' % topic
    t += '\n'
    for k in sorted(options):
        t += '\n　*%s* … %s' % (k, options[k])
    t += '\n\n_番号だけでOK。これが決まるまで先へ進めません_'
    if detail:
        t += '\n\n――― 判断の材料 ―――\n' + detail
    if link:
        t += '\n' + link
    ok = _post(t, unfurl=bool(link))
    if ok:
        json.dump({'topic': topic, 'options': options,
                   'asked_at': __import__('datetime').datetime.now().isoformat()},
                  open(PENDING, 'w'), ensure_ascii=False, indent=1)
    return ok


def pending():
    """いま判断待ちがあるか。あれば中身を返す"""
    if not os.path.exists(PENDING):
        return None
    try:
        d = json.load(open(PENDING))
        return None if d.get('answered') else d
    except Exception:
        return None


if __name__ == '__main__':
    p = pending()
    print('判断待ち ： %s' % (p['topic'] if p else 'なし'))
