#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作業の直前に、その作業で踏んだ地雷を突きつける ── PreToolUse フック

なぜ要るか（2026-08-20 有璽氏）
  > 「同じことを繰り返さないでくださいという話をしてるんですよ。
  >   一度言ったことが何度も何度も起こっているから言っているんだよ。
  >   そうならないようにどうしたらいいの？」

  ★繰り返す理由は「知らないから」ではない。**知っているのに適用しないから**。
  実例（2026-08-20）：
    `reference_sheets_number_format_order.md` に「A列がキーとは限らない」と
    自分で書いた2時間後、40_活動ログをA列で数えて「2行」と誤報告した（実際は25行）。

  memory は毎ターン「索引1行」しか届かない。本文は関連しそうなときだけ引かれる。
  規範は全文届くが量が多く、適用点で気づかない。
  ★だから、**その作業をする直前に、その作業で踏んだ地雷だけ**を突きつける。

やること
  ツールと引数を見て、該当する「過去に踏んだ地雷」を additionalContext で差し込む。
  短く。3つまで。多いと読まれない。

★止めない。ブロックしない。該当が無ければ何もしない。
"""

import os
import re
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))

# （条件, 突きつける文言）── ★全部「実際に踏んだもの」だけを書く。一般論は書かない
RULES = [
    # ── スプレッドシート ──
    (lambda t, s: 'sheets_client' in s or 'WORKBOOK_ID' in s or '_マスタ' in s or '_活動ログ' in s,
     '【この作業で踏んだ地雷】\n'
     '・**A列がキーとは限らない。** 40_活動ログのA列「ログID」は空欄運用で、'
     'A列を数えると25行が2行に見えた（2026-08-20 実測）。見出しを見てキー列を決めること\n'
     '・**行数と件数は別物。** 00_企業マスタは807行あるが416社（2026-08-20）\n'
     '・**「値が無い」と「行が無い」は別物。** 器（getMaxRows相当）を見ずに書き先を決めない\n'
     '・**書く前にバックアップ。** size が確定するまで数回読み直す（copy直後は1バイトを返す）\n'
     '・**1セルずつ update しない。** 60回/分の上限に当たって途中で落ちる。batch_update を使う'),
    # ── 台帳への発番・突合 ──
    (lambda t, s: re.search(r'発番|新規|突合|照合|重複|B-\d{4}|C-\d{4}', s) is not None,
     '【この作業で踏んだ地雷】\n'
     '・**会社名1本で突合しない。** 2026-08-19 に B-0050（小川晃代）と C-0072 を二重に作った。'
     '01_顧客詳細の 代表者名・先方担当者名・電話・メール まで見ること\n'
     '・**候補が複数のとき先頭を採らない。** 先勝ちで永続IDを固定すると誤結合が二度と疑われなくなる\n'
     '・**法人番号が違えば別法人。** 統合してはいけない（「誤ったIDは空欄より有害」）\n'
     '・**機械が「新規」と判定して書かない。** 候補を出して人の○を待つ'),
    # ── Notion ──
    (lambda t, s: 'notion' in s.lower() or 'Notion' in s,
     '【この作業で踏んだ地雷】\n'
     '・**データソースIDとデータベースIDは別物。** 取り違えて404を受け、'
     '「未接続」と誤断定した（2026-08-20）\n'
     '・**Notionにしか無い列は触らない。** メモ・協業メモ・強み・課題・各種relation。'
     '機械が書く先は「同期メモ」列\n'
     '・**Notionにバックアップは無い。** 上書きしたら戻せない。書く前に現在値を保存する\n'
     '・読み書きの前に📌【正本】Notion運用ルールを開く'),
    # ── cron・自動実行 ──
    (lambda t, s: 'crontab' in s or 'cron' in s.lower(),
     '【この作業で踏んだ地雷】\n'
     '・**未検証のものを cron に載せない。** 動作未確認のまま自動実行に載せると、'
     '壊れていることに気づけない\n'
     '・**無人実行の入口に人の操作を置かない。** ブラウザ認証へ落ちる経路があると、'
     'トークンが切れた日から毎朝無言でハングする（2026-08-20 修正）\n'
     '・**心拍を打つ。** 成功でも失敗でも。⚙️自動処理レジスタに行が無いと🔴すら立たない'),
    # ── 削除・破壊的操作 ──
    (lambda t, s: re.search(r'\brm\b|delete|trash|archive|削除', s) is not None,
     '【この作業で踏んだ地雷】\n'
     '・**正本の行削除は行わない。** 消さずに状態で表す（備考に「◯◯へ統合済み」）\n'
     '・**消してよいのは作業層のまま吸収されたものだけ。** 配った／リンクされた／'
     '参照されている が1つでもあれば消さない'),
    # ── 有璽氏へ何かを渡す ──
    (lambda t, s: 'slack' in s.lower() or 'chat.postMessage' in s,
     '【この作業で踏んだ地雷】\n'
     '・**有璽氏はチャット内のテキストをコピーできない。** 渡すものはクリックできるリンクにする\n'
     '・**チャンネルへ投げない。** 他のメンバーの邪魔になる（2026-08-20）。DMのみ\n'
     '・**報告と判断依頼を混ぜない。** 報告には「返信は要りません」を明記する\n'
     '・**押す場所まで特定してから渡す。** 「◯◯を探して」ではなく直リンクと画面名まで'),
]


# ★手書きの RULES だけだと、新しい地雷を踏んでも
#   こちらがリストへ足さなければ次回は効かない＝仕組み自体が規律に依存する
#   （2026-08-20 有璽氏「抜け漏れがあるんじゃないか」）
#   → memory から自動生成した索引も併せて読む。**memoryに書けば次から効く**
LANDMINES = os.path.join(HERE, 'landmines.json')
TOPIC_HINTS = {
    'sheets': ['sheets_client', 'WORKBOOK_ID', 'INTAKE_ID', '_マスタ', '_活動ログ',
               '_関係フォロー', 'スプレッドシート', 'spreadsheet'],
    'notion': ['notion', 'Notion'],
    'kintone': ['kintone'],
    'ledger': ['発番', '突合', '照合', '重複', 'B-0', 'C-0', '法人番号'],
    'cron': ['crontab', 'cron', 'heartbeat', '心拍'],
    'delete': ['rm ', 'delete', 'trash', 'archive', '削除'],
    'slack': ['slack', 'chat.postMessage'],
    'drive': ['drive', 'Drive', 'フォルダ'],
}


WORKING = os.path.expanduser('~/vivid-ai-hq/WORKING.md')


def already_in_progress(blob):
    """★担当を起動する直前に、WORKING.md の該当行を突きつける（2026-08-20）

    WORKING.md は毎ターン読まれている。それでも読み落とした。
    「法人番号の一括補完」が着手中と書いてあるのに、同じ作業を担当へ投げた。
    ＝ **長い文書は、届いていても読まれない。**
       memory の「1プロジェクトにつき5〜7項目まで。全部書けば全部届かない」と同じ形。

    直し：届けるのをやめて、**その作業に関係する行だけ**を起動の直前に出す。
    """
    if not os.path.exists(WORKING):
        return []
    try:
        lines = open(WORKING, encoding='utf-8').read().split('\n')
    except Exception:
        return []
    # 依頼文から特徴語を拾う（2文字以上の漢字カタカナ語と、.py などの識別子）
    words = set(re.findall(r'[一-龯]{2,}|[ァ-ヶー]{3,}|[A-Za-z_][A-Za-z0-9_]{3,}\.py', blob))
    if not words:
        return []
    hits = []
    for i, ln in enumerate(lines):
        t = ln.strip()
        if len(t) < 8:
            continue
        n = sum(1 for w in words if w in t)
        # 着手宣言・進行中の印がある行は弱いヒットでも拾う
        strong = ('着手中' in t) or ('進行中' in t) or ('★' in t and 'まだ' in t)
        if n >= 3 or (strong and n >= 2):
            hits.append(t if len(t) <= 180 else t[:180] + '…')
        if len(hits) >= 4:
            break
    if not hits:
        return []
    return ['【★WORKING.md に同じ話が載っています】\n'
            '**同じ対象が既に載っていたら、着手せず先に相談する。**\n'
            + '\n'.join('・' + h for h in hits)]


def from_memory(blob):
    """memory由来の索引から、いまの作業に関係するものを拾う"""
    if not os.path.exists(LANDMINES):
        return []
    try:
        idx = json.load(open(LANDMINES))
    except Exception:
        return []
    tops = [t for t, hints in TOPIC_HINTS.items()
            if any(h in blob for h in hints)]

    def relevant_first(entries):
        """★常設枠は本数が多い。重み順の上位だけを出すと毎回同じ2本になる。
        いまの作業に語が一致するものを先に出し、残りを重み順で埋める。"""
        def score(e):
            text = (e.get('desc', '') + ' ' + ' '.join(e.get('points') or []))
            words = [w for w in re.findall(r'[一-龯ぁ-んァ-ヶA-Za-z_]{3,}', text)]
            return sum(1 for w in set(words) if w in blob)
        return sorted(entries, key=lambda e: -score(e))

    def take(topic, n):
        got = []
        src = idx.get(topic, [])
        if topic == 'always':
            src = relevant_first(src)
        for e in src[:n]:
            pts = e.get('points') or []
            if not pts:
                continue
            got.append('【%s】\n%s' % (e['file'].replace('.md', ''),
                                       '\n'.join('・' + p for p in pts[:3])))
        return got

    # ★常設枠を必ず先に出す（2026-08-20 に発見した穴）
    #   「有璽氏に言われたこと」と汎用の地雷は always に集めてあるのに、
    #   ここがトピック枠しか読んでおらず **1度も出ていなかった**。
    #   索引を作る側を直しても、読む側を直さなければ届かない。
    out = take('always', 2)
    for t in tops[:2]:                       # トピックは2つまで
        out += take(t, 3)                    # 1トピック3本まで
    # 同じファイルが二度出ないように潰す（常設枠とトピック枠は重ならない作りだが念のため）
    seen, uniq = set(), []
    for x in out:
        if x in seen:
            continue
        seen.add(x)
        uniq.append(x)
    return uniq[:5]


def main():
    try:
        raw = sys.stdin.read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({}))
        return

    tool = str(d.get('tool_name', ''))
    inp = d.get('tool_input', {}) or {}
    try:
        blob = json.dumps(inp, ensure_ascii=False)
    except Exception:
        blob = str(inp)

    hits = []
    for cond, msg in RULES:
        try:
            if cond(tool, blob):
                hits.append(msg)
        except Exception:
            pass
    # ★memory由来を必ず先に引く（2026-08-20 に発見した、この仕組み最大の穴）
    #   以前はここが `if not hits: return` で、**ハードコードの RULES が1つも当たらないと
    #   memory を1行も見ずに終了していた**。
    #   ＝「memory に書けば次の作業から自動で突きつけられる」という、この仕組みの中心の主張が、
    #     ハードコードに載っている作業のときしか成り立っていなかった。
    #   索引を作る側・読む側・出す側の3か所とも直さないと届かない。
    # ★担当を起動する直前は、WORKING.md の該当行を最優先で出す
    #   （二重に手をつけるのを、着手する前に止める ── それがあのファイルの唯一の目的）
    if tool in ('Agent', 'Task'):
        hits = already_in_progress(blob) + hits

    hits += from_memory(blob)
    if not hits:
        print(json.dumps({}))
        return

    text = ('★これから触るものは、過去に事故を起こした場所です。'
            '**下は全部、実際に踏んだものだけ**です。\n\n' + '\n\n'.join(hits[:5]))
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'additionalContext': text,
        },
        'suppressOutput': True,
    }, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(json.dumps({}))
    sys.exit(0)
