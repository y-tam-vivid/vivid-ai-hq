#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有璽氏の指摘を取りこぼさない ── UserPromptSubmit フック

  発言に「訂正・叱責・繰り返しの指摘」の型が出たら、
  **その場で記録するよう、モデルの文脈へ割り込ませる。**

なぜ要るか（2026-08-20 有璽氏）
  「なんでその記録に残してないの？ 同じこと何回も繰り返してんねや。
    それをなくせって、一番何度も何度も言ってるのに、
    どうやったらなくなんねん、ほんまに」

  規範には「一度踏んだ地雷は手順書（Skill／メモリ）に落として再発を止める」とある。
  だが実行するのはモデルの規律で、規律は切れる。
  規範自身が「読む規律に依存する対策は、規律が切れた回にだけ効かない」と書いている。
  ★だから機械にやらせる。

やること
  ① 指摘の型を検出する
  ② `additionalContext` でモデルの文脈へ「いま記録しろ」を差し込む（無視できない）
  ③ 発言そのものを ~/.vivid-relay/corrections.log へ残す（あとで棚卸しできる）

★止めない。ブロックしない。指摘でなければ何もしない。
"""

import os
import re
import sys
import json
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'corrections.log')

# ★2026-08-20 有璽氏の指摘で作り直した。
#   最初の版は「怒り」を検出する作りだった。それでは**怒られるまで記録しない**。
#   > 「訂正し、指摘繰り返しの指摘の方が出たらとかそういう話じゃない。
#   >   そうなる前にやれよっていう話やろ。
#   >   怒った時だけやりますってなっとるやろうが、それが一番おかしいねん」
#
#   直し：怒りではなく「**新しい事実が出た合図**」を拾う。
#   有璽氏が事実・前提・やり方を1つでも足したら、その時点で記録の対象。
#   怒っているかどうかは関係ない。
PATTERNS = [
    # ── 新しい事実・前提が示された（★怒っていなくても記録する）──
    (r'(ある|あります|いる|います|できる|できます|だった|でした|してる|しています)', '事実が示された'),
    (r'(ない|ません|いない|できない|無理|不可|してない|やってない)', '制約が示された'),
    (r'(です|だよ|やで|やねん|なんです|なのよ|ですよ)$', '前提が示された'),
    (r'こうして|こうやって|こっち|そっち|こういう|そういう風に', 'やり方の指定'),
    (r'今後|以後|次から|これから|毎回|常に|必ず', '恒久のルール'),
    (r'やめて|しないで|するな|禁止|触らない', 'してはいけないこと'),
    # ── 訂正（怒る前の段階も拾う）──
    (r'違う|ちゃう|そうじゃない|誤り|間違|正しく(は|ない)', '訂正'),
    (r'実は|本当は|正確には|というより', '認識のずれ'),
    # ── 積み上がると怒りになるもの（早い段階で拾う）──
    (r'何回|何度|また|毎回|いつも|繰り返', '繰り返しの指摘'),
    (r'なんで|なぜ|どういうこと|意味がわからん|意味わからん|謎', '理由を問われている'),
    (r'甘い|漏れ|抜け|確認しろ|調べ(ろ|て)', '確認不足の指摘'),
    (r'煩わし|面倒|手間|しんどい|うんざり', '手間への不満'),
    (r'遅い|進んで(ない|へん)|止まって', '進捗への不満'),
    (r'できてない|やってない|やれてない|残せ|記録', '未実施の指摘'),
]


def main():
    try:
        raw = sys.stdin.read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({}))
        return

    text = str(d.get('prompt') or d.get('user_prompt') or '')
    if not text.strip():
        print(json.dumps({}))
        return

    hits = []
    for pat, label in PATTERNS:
        if re.search(pat, text):
            hits.append(label)
    if not hits:
        print(json.dumps({}))
        return

    # 記録（棚卸し用）
    try:
        with open(LOG, 'a') as f:
            f.write('%s\t%s\t%s\n'
                    % (datetime.datetime.now().isoformat(timespec='seconds'),
                       '/'.join(sorted(set(hits))), text.replace('\n', ' ')[:400]))
    except Exception:
        pass

    msg = (
        '★この発言に「%s」が含まれます。**怒られているかどうかは関係ありません。**\n'
        '有璽氏が事実・前提・制約・やり方を1つでも足したら、その時点で記録の対象です。\n'
        'ふくち。グループの規範（fukuchi-core）はこう定めています ── '
        '「一度踏んだ地雷は個別に直さず、手順書（Skill／メモリ）に落として再発を止める」。\n\n'
        '**いま、次を必ず行ってください（作業を進める前に）**\n'
        '1. `~/vivid-ai-hq/memory/` に該当する feedback / reference のファイルが既にあるか探す\n'
        '   → あれば追記して更新する。無ければ新規に作る\n'
        '2. `~/vivid-ai-hq/memory/MEMORY.md` に1行の索引を足す'
        '（索引はラベルではなく**現在地**を運ぶこと）\n'
        '3. 記録したことを一言だけ報告する（長い謝罪は書かない）\n\n'
        '★「あとで書く」は禁止です。**指摘される前に書くのが正しい形**です。\n'
        '  怒られてから記録するのでは、1度目は必ず取りこぼします。'
        % '／'.join(sorted(set(hits)))
    )
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': msg,
        },
        'suppressOutput': True,
    }, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(json.dumps({}))
    sys.exit(0)
