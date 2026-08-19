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

HERE = os.path.dirname(os.path.abspath(__file__))
MEM = os.path.expanduser('~/vivid-ai-hq/memory')
OUT = os.path.join(HERE, 'landmines.json')

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
    """★で始まる行と、太字だけの短い行を拾う。多すぎると読まれないので絞る"""
    out = []
    for line in body.split('\n'):
        t = line.strip().lstrip('-・ ').strip()
        if not t or t.startswith('#') or t.startswith('|') or t.startswith('```'):
            continue
        if t.startswith('★') or t.startswith('**★'):
            out.append(t)
        elif re.match(r'^\*\*[^*]{6,70}\*\*[。、]?$', t):
            out.append(t)
    # 重複を潰して短い順に
    seen, uniq = set(), []
    for x in out:
        k = re.sub(r'[^\w一-龯ぁ-んァ-ヶ]', '', x)[:30]
        if k in seen:
            continue
        seen.add(k)
        uniq.append(x if len(x) <= 150 else x[:150] + '…')
    return uniq[:4]


def main(quiet=False):
    idx = {}
    n_files = 0
    for p in sorted(glob.glob(os.path.join(MEM, '*.md'))):
        name = os.path.basename(p)
        if name == 'MEMORY.md':
            continue
        try:
            raw = open(p, encoding='utf-8').read()
        except Exception:
            continue
        n_files += 1
        m = re.search(r'^description:\s*(.+)$', raw, re.M)
        desc = m.group(1).strip() if m else ''
        body = raw.split('---', 2)[-1]
        tops = topics_of(name, desc + ' ' + body[:1500])
        if not tops:
            continue
        lines = key_lines(body)
        if not lines and not desc:
            continue
        entry = {'file': name, 'desc': desc, 'points': lines}
        for t in tops:
            idx.setdefault(t, []).append(entry)

    # トピックごとに多すぎないよう絞る（読まれなくなるため）
    for t in idx:
        idx[t] = idx[t][:6]

    json.dump(idx, open(OUT, 'w'), ensure_ascii=False, indent=1)
    if not quiet:
        print('memory %d本を走査 → %s' % (n_files, OUT))
        for t, entries in sorted(idx.items()):
            print('  %-8s %d本' % (t, len(entries)))
            for e in entries[:2]:
                print('       %s' % e['file'])
    return 0


if __name__ == '__main__':
    sys.exit(main(quiet='--quiet' in sys.argv))
