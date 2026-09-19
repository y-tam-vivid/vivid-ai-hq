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
# ★2026-09-19 ロビン依頼で追加。hook_selfcheck.py の探針（毎朝08:20/08:40）が
#   このスクリプトを直接叩いており、LOG は HERE（__file__ 基準）でパスを組んでいたため
#   HOME環境変数の差し替えでは汚染を防げなかった（hook_session_writeback.py の
#   HOME差し替え方式が効かない別の実装だった）。環境変数で上書きできるようにし、
#   selfcheck側は探針実行時だけこれを一時ファイルへ向ける。
LOG = os.environ.get('VIVID_CORRECTIONS_LOG') or os.path.join(HERE, 'corrections.log')

# ★2026-09-19 ロビン依頼で追加（実測：corrections.log 637行の86%が有璽氏の発言でなかった）。
#   UserPromptSubmit は「有璽氏がキーボードで打った」場合だけでなく、
#   ①エージェント起動（`claude -p "あなたは◯◯です。…"`）
#   ②バックグラウンドタスク完了通知（<task-notification>タグ）
#   ③run_agent.sh が毎回自動で先頭に挿入する定型警告文
#   でも発火する。これらは有璽氏の発言ではないため、記録対象から外す。
#
#   ★誤除外を避けるため、判定は「有璽氏が絶対に書かない形」に限定する
#   （長さや語気の強さでは切らない。有璽氏は長文で厳しい語を使って指示することがあるため）。
#
#   実測で確認した各パターンの特徴：
#   ① 冒頭が「あなたは「◯◯」...です。」で始まり、本文中に自分の役割定義ファイル
#      （`.claude/agents/*.md`）を名指しして「読んで」と指示する構造を持つ。
#      → 冒頭に「あなたは」があり、かつ `.claude/agents/` パスがあり、かつ
#        「読んで」または「読み」がある、の3条件AND。単独の条件では有璽氏の
#        発言を誤って弾く恐れがあるため複合条件にした。
#   ② 冒頭が `<task-notification>` タグで始まる（実測：163行すべて先頭一致）。
#   ③ 「★機械が自動で付けた」と「run_agent.sh」の両方を含む
#      （実測：run_agent.sh のこの定型文を含む行は9行、全て一致）。
#
#   ★これで直ったのは①〜③の3経路だけ。実測で「重要な制約：…触れないでください」型
#   （2行・検証用テスト指示文とみられる）と「★★前回のあなたは、やり切らずに
#   終わりました」型（5行・タスク再試行のシステム通知とみられる）も見つかったが、
#   件数が少なく判定条件を一般化すると誤除外のリスクが高いため、今回は対象にしていない。
_AGENT_BOOT_HEAD_RE = re.compile(r'^\s*あなたは')


def _is_non_utterance(text):
    """有璽氏の発言でないと機械的に判定できる形なら True。"""
    head = text[:400]
    if '<task-notification>' in head:
        return True
    if '★機械が自動で付けた' in text and 'run_agent.sh' in text:
        return True
    if (_AGENT_BOOT_HEAD_RE.match(head)
            and '.claude/agents/' in text
            and ('読んで' in text or '読み' in text)):
        return True
    return False

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
    if _is_non_utterance(text):
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
