#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
memory から「地雷インデックス」を作る ── フックが読む元

  python3 build_landmine_index.py          作って中身を出す
  python3 build_landmine_index.py --quiet  静かに作る（フックやcronから）

なぜ要るか（2026-08-20 有璽氏「抜け漏れがあるんじゃないか」）
  最初に作った PreToolUse フックは、突きつける文言を**コードに手で書いていた**。
  ＝ 新しい地雷を踏んでも、こちらがリストへ足さなければ次回は効かない。
  **仕組み自体が規律に依存していた。** これが最大の穴だった。

  直し：`~/vivid-ai-hq/memory/` を走査して自動で作る。
  **memory に書けば、次の作業から自動で突きつけられる。**

作り方
  memory の各ファイルから
    ・description（frontmatter）
    ・本文のうち ★ で始まる行、太字の行
  を拾い、ファイル名と本文からトリガー語を決める。

出力
  ~/.vivid-relay/landmines.json
"""

import os
import re
import sys
import json
import glob
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MEM = os.path.expanduser('~/vivid-ai-hq/memory')
OUT = os.path.join(HERE, 'landmines.json')
PROC_NAME = '地雷インデックスの再生成'   # ★⚙️レジスタの行名と1文字ずつ一致させること

# ファイル名／本文のどの語が出たら、どの作業のときに出すか
TOPIC_WORDS = {
    'sheets': ['sheet', 'スプレッドシート', '企業マスタ', '個人マスタ', '活動ログ',
               '関係フォロー', '選択肢マスタ', 'ワークブック', 'gviz', 'gas', 'apps script'],
    'notion': ['notion', 'ノーション', 'データソース', 'relation', '顧客db'],
    'kintone': ['kintone', 'キントーン'],
    'ledger': ['突合', '発番', '重複', '社内顧客id', '法人番号', '名寄せ', '台帳'],
    'cron': ['cron', 'launchd', '心拍', '自動処理', 'レジスタ', '定期実行'],
    'delete': ['削除', 'アーカイブ', '破壊', '消さ'],
    'slack': ['slack', 'チャットワーク', 'chatwork', '通知'],
    'drive': ['drive', 'ドライブ', 'フォルダ', '共有'],
}


def topics_of(name, body):
    s = (name + ' ' + body).lower()
    hits = set()
    for topic, words in TOPIC_WORDS.items():
        for w in words:
            if w in s:
                hits.add(topic)
                break
    return sorted(hits)


def key_lines(body):
    """★で始まる行と、太字だけの短い行を拾う。多すぎると読まれないので絞る

    ★戻り値は (行のリスト, ★行の本数)。★行の本数は「地雷らしさ」の重みに使う。
    """
    # ★中身のない見出しを弾く（2026-08-20 実測）
    #   memory の書式には「**Why:**」「**How to apply:**」という見出し太字がある。
    #   これを拾うと、フックが `・**How to apply:**` だけを表示する
    #   ＝ 出ているのに何も伝えていない状態になる。**出た本数では検証できない。**
    EMPTY_HEAD = re.compile(r'^\*\*(Why|How to apply|なぜ|使い方|適用)\s*[:：]?\*\*[:：]?$')
    starred, bold = [], []
    for line in body.split('\n'):
        t = line.strip().lstrip('-・ ').strip()
        if not t or t.startswith('#') or t.startswith('|') or t.startswith('```'):
            continue
        if EMPTY_HEAD.match(t):
            continue
        if t.startswith('★') or t.startswith('**★'):
            starred.append(t)
        elif re.match(r'^\*\*[^*]{6,70}\*\*[。、]?$', t):
            bold.append(t)
    # ★行を先に置く。太字だけの行は補充にまわす（地雷とは限らないため）
    seen, uniq = set(), []
    for x in starred + bold:
        k = re.sub(r'[^\w一-龯ぁ-んァ-ヶ]', '', x)[:30]
        if k in seen:
            continue
        seen.add(k)
        uniq.append(x if len(x) <= 150 else x[:150] + '…')
    return uniq[:4], len(starred)


def weight(name, n_star, n_lines, mtime, newest):
    """どれを残すか。★ファイル名順（先着）で切ると、新しい地雷ほど落ちる

    2026-08-20 実測 ── 8トピック全部が上限6本ちょうどに当たっており、
    memory 106本のうち48本しか届いていなかった。しかも残っていたのは
    `ai-asset-catalog.md` のような **地雷ですらないもの**（ファイル名がaで始まるだけ）。
    「memoryに書けば次から効く」と言っていた仕組みが、書いても効いていなかった。
    """
    # ★を付けるかどうかは書き手の癖で決まる。★だけを重みにすると、
    #   ★を付け忘れた重要な地雷が沈む（2026-08-20 実測：`\u`エスケープの記憶が★0本で落ちた）。
    #   突きつける行そのものの本数も数え、書き方の癖に依存させない。
    w = n_star * 5 + n_lines * 2
    if name.startswith('feedback_'):
        w += 6                          # 有璽氏に言われたこと。最優先
    elif name.startswith('reference_'):
        w += 4                          # 実測して分かった型
    days = max(0.0, (newest - mtime) / 86400.0)
    w += max(0, 4 - days)               # ごく最近のものだけ少し優先（★古い地雷を押し出さない程度に）
    return w


MAX_CHARS = 1400      # 1トピックあたりの上限。★本数ではなく文字数で切る（読まれる量が問題なので）
FRESH_DAYS = 7        # ★この日数以内に書かれたものは上限で落とさない（いちばん踏みやすいので）


def main(quiet=False):
    paths = [p for p in sorted(glob.glob(os.path.join(MEM, '*.md')))
             if os.path.basename(p) != 'MEMORY.md']
    newest = max([os.path.getmtime(p) for p in paths] or [0])

    idx = {}
    n_files = 0
    for p in paths:
        name = os.path.basename(p)
        try:
            raw = open(p, encoding='utf-8').read()
        except Exception:
            continue
        n_files += 1
        m = re.search(r'^description:\s*(.+)$', raw, re.M)
        desc = m.group(1).strip() if m else ''
        body = raw.split('---', 2)[-1]
        tops = topics_of(name, desc + ' ' + body[:1500])
        # ★有璽氏に言われたこと（feedback_*）は、トピック語に当たらなくても常設枠へ入れる。
        #   2026-08-20 実測 ── 「書く前にdiffを見せる」が丸ごと落ちていた。
        #   本文に sheets / notion といった語が無いというだけの理由で、どの作業でも
        #   効くはずの規範が1度も突きつけられていなかった。
        if not tops and not name.startswith('feedback_'):
            continue
        lines, n_star = key_lines(body)
        # ★本文から拾えないときは description を使う。**落とさない。**
        #   見出しだけを弾いた結果、規範そのもの（「書く前にdiffを見せる」等）が
        #   丸ごと消えては本末転倒。description は必ず1行の要旨を持っている。
        if not lines:
            if not desc:
                continue
            lines = [desc if len(desc) <= 150 else desc[:150] + '…']
        mt = os.path.getmtime(p)
        entry = {'file': name, 'desc': desc, 'points': lines,
                 'w': round(weight(name, n_star, len(lines), mt, newest), 1),
                 # ★書いたばかりのものは上限で落とさない（下の詰め方を参照）
                 'fresh': (time.time() - mt) / 86400.0 <= FRESH_DAYS}
        # ★どこへ入れるか（2026-08-20 実測で3回作り直した）
        #   ・feedback_*  ── 有璽氏に言われたこと。**どの作業でも効くので必ず常設枠**。
        #     トピック語を含むかどうかで振り分けると、文字数の運で落ちる。
        #     実際「書く前にdiffを見せる」が本文に sheets/notion の語が無いだけで丸ごと
        #     落ちていた（1度も突きつけられていなかった）
        #   ・3トピック以上に当たるもの ── 汎用の地雷（\u エスケープ等）。同じく常設枠。
        #     トピック枠へ入れると、トピック固有の地雷（IDを勝手に発番しない等）を押し出す
        always = name.startswith('feedback_') or len(tops) >= 3
        for t in (['always'] if always else tops):
            idx.setdefault(t, []).append(entry)

    # ★重い順に、文字数の上限まで詰める。落としたものは黙って落とさない
    #
    # ★2026-08-29 実測 ── 常設枠で **188本中100本が落ちていた**。
    #   しかも落ちていたのが `reference_hooks_enforce_what_discipline_cannot`
    #   `reference_delivered_but_unread` ── **「書いても届かない」を止めるための記憶そのもの**。
    #   重い順で切ると、書いたばかりの地雷（＝いちばん踏みやすい）が真っ先に落ちる。
    #   だから **直近 FRESH_DAYS 以内のものは上限に関わらず先に確保する**。
    dropped = {}
    for t in idx:
        idx[t].sort(key=lambda e: -e['w'])
        # ★常設枠は広めに取る。どの作業でも効くものなので、押し出す方が損が大きい
        cap = MAX_CHARS * 3 if t == 'always' else MAX_CHARS
        fresh = [e for e in idx[t] if e.get('fresh')]
        kept = list(fresh)
        used = sum(len(e['desc']) + sum(len(x) for x in e['points']) for e in kept)
        for e in idx[t]:
            if e in kept:
                continue
            cost = len(e['desc']) + sum(len(x) for x in e['points'])
            if used + cost > cap and kept:
                continue
            kept.append(e)
            used += cost
        if len(kept) < len(idx[t]):
            dropped[t] = [e['file'] for e in idx[t] if e not in kept]
        idx[t] = kept

    json.dump(idx, open(OUT, 'w'), ensure_ascii=False, indent=1)
    if dropped and not quiet:
        sys.stderr.write('[landmine] ★上限で落としたもの（黙って落とさない）\n')
        for t, files in sorted(dropped.items()):
            sys.stderr.write('   %-8s %d本 ： %s\n' % (t, len(files), ' / '.join(files[:4])))
    if not quiet:
        print('memory %d本を走査 → %s' % (n_files, OUT))
        for t, entries in sorted(idx.items()):
            print('  %-8s %d本' % (t, len(entries)))
            for e in entries[:3]:
                print('       %5.1f  %s' % (e['w'], e['file']))

    # ★心拍（2026-08-27 つる）── これが無かったせいで、毎朝08:25に確かに動いて
    #   landmines.json を作り直しているのに、⚙️レジスタは永久に🟡遅延を出していた。
    #   「動いているものを止まっていると誤判定する」型。--quiet でも必ず打つ
    #   （cron行は --quiet だけなので、フラグ制にすると今日と同じ穴が残る）。
    try:
        sys.path.insert(0, HERE)
        from heartbeat import beat as hb
        hb(PROC_NAME, '成功',
           'memory %d本を走査 → 地雷 %d本' % (n_files, sum(len(v) for v in idx.values())))
    except Exception as e:
        sys.stderr.write('[心拍] 打てず ： %s\n' % e)
    return 0


if __name__ == '__main__':
    # ★2026-08-29 実測 ── `import time` の抜けで NameError を出しながら **exit=0** を返し、
    #   古い landmines.json をそのまま残していた。呼び出し側（cron・フック）からは
    #   「動いた」ようにしか見えず、**新しい記憶が1本も載らないまま気づけない**。
    #   → 落ちたら 1 を返し、心拍も「失敗」で打つ（reference_ran_is_not_succeeded）。
    try:
        sys.exit(main(quiet='--quiet' in sys.argv))
    except Exception as e:
        sys.stderr.write('[landmine] ★失敗 ： %r\n' % (e,))
        try:
            sys.path.insert(0, HERE)
            from heartbeat import beat as hb
            hb(PROC_NAME, '失敗', repr(e)[:300])
        except Exception:
            pass
        sys.exit(1)
