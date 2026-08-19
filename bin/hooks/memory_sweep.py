#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
記録の取りこぼしを毎朝ひろう ── ロビン（CKO）が前日を棚卸しする

  python3 memory_sweep.py            ドライラン（読むだけ）
  python3 memory_sweep.py --run      本実行（ロビンを呼んで記録させる）
  python3 memory_sweep.py --run --beat

なぜ要るか（2026-08-20 有璽氏）
  > 「怒った時だけやりますってなっとるやろうが、それが一番おかしいねん」
  > 「そこまで私がこうやって言わなくてもいけるような状態にしろって言ってんの」

  最初に作った UserPromptSubmit フックは「指摘された瞬間」に反応する作りだった。
  ★それでは指摘されるまで記録しない。指摘が要らない状態にはならない。

  記録を**モデルの規律**にも**有璽氏の指摘**にも依存させない。
  毎朝、別の主体（ロビン）が前日の実績を読んで、記録されていない学びを拾う。

拾う材料（どれも人の手が要らない）
  ① git log            前日の commit（何を変えたか）
  ② corrections.log    フックが拾った有璽氏の発言
  ③ 各種ログ           ~/.vivid-relay/*.log の前日ぶん（失敗・警告）
  ④ memory の更新有無   前日に memory が1本も増えていなければ★異常として扱う

★ロビンは「記録されていない学び」だけを書く。既にあるものは触らない。
"""

import os
import re
import sys
import glob
import json
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.expanduser('~/vivid-ai-hq')
CLAUDE = os.path.expanduser('~/.npm-global/bin/claude')
PROC_NAME = '記録の取りこぼしを拾う（ロビンの朝の棚卸し）'
TIMEOUT = 900


def yesterday():
    return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


def gather():
    y = yesterday()
    out = {}
    # ① 前日の commit
    try:
        r = subprocess.run(
            ['git', 'log', '--since=%s 00:00' % y, '--until=%s 23:59' % y,
             '--pretty=format:%h %s%n%b'],
            cwd=REPO, capture_output=True, text=True, timeout=60)
        out['commits'] = (r.stdout or '').strip()
    except Exception as e:
        out['commits'] = '（取れず ： %s）' % e
    # ② 有璽氏の発言（フックが拾ったもの）
    lines = []
    p = os.path.join(HERE, 'corrections.log')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            if line.startswith(y):
                lines.append(line.rstrip())
    out['corrections'] = '\n'.join(lines[-40:])
    # ③ ログの失敗・警告
    warns = []
    for f in glob.glob(os.path.join(HERE, '*.log')):
        if f.endswith('corrections.log'):
            continue
        try:
            tail = subprocess.run(['tail', '-40', f], capture_output=True,
                                  text=True, timeout=20).stdout
        except Exception:
            continue
        for line in tail.split('\n'):
            if re.search(r'★|失敗|エラー|Error|Traceback|警告', line):
                warns.append('%s ： %s' % (os.path.basename(f), line.strip()[:160]))
    out['warnings'] = '\n'.join(warns[-30:])
    # ④ 前日に memory が増えたか
    try:
        r = subprocess.run(
            ['git', 'log', '--since=%s 00:00' % y, '--until=%s 23:59' % y,
             '--name-only', '--pretty=format:', '--', 'memory/'],
            cwd=REPO, capture_output=True, text=True, timeout=60)
        touched = sorted(set(x for x in (r.stdout or '').split('\n') if x.strip()))
        out['memory_touched'] = touched
    except Exception:
        out['memory_touched'] = []
    return out


def main(dry=True, beat=False):
    y = yesterday()
    d = gather()
    print('【%s】記録の取りこぼしを拾う ： %s' % ('ドライラン' if dry else '★本実行', y))
    print('')
    print('■ 前日の commit ： %d行' % len(d['commits'].split('\n')) if d['commits'] else '■ commit なし')
    print('■ 有璽氏の発言（フックが拾った）： %d件'
          % (len(d['corrections'].split('\n')) if d['corrections'] else 0))
    print('■ ログの失敗・警告 ： %d件'
          % (len(d['warnings'].split('\n')) if d['warnings'] else 0))
    print('■ 前日に触った memory ： %d本' % len(d['memory_touched']))
    for m in d['memory_touched'][:10]:
        print('     %s' % m)
    print('')

    if not d['commits'] and not d['corrections'] and not d['warnings']:
        print('---- 前日に動きが無い。何もしない ----')
        if beat and not dry:
            try:
                from heartbeat import beat as hb
                hb(PROC_NAME, '成功', '前日に動きなし')
            except Exception:
                pass
        return 0

    prompt = """あなたはロビン（CKO）。ふくち。グループのナレッジ統括です。
`~/vivid-ai-hq/.claude/agents/cko.md` を読んでロビンとして振る舞ってください。

**前日（%s）の実績を読んで、記録されていない学びを拾い、memory へ落としてください。**

## なぜこの仕事があるか
有璽氏から「怒った時だけ記録するのはおかしい。指摘しなくても回る状態にしろ」と
言われました（2026-08-20）。記録をモデルの規律にも有璽氏の指摘にも依存させないため、
毎朝あなたが棚卸しします。

## 材料

### 前日の commit
%s

### 有璽氏の発言（フックが拾ったもの・タブ区切り：時刻／型／発言）
%s

### ログに出た失敗・警告
%s

### 前日に触った memory
%s

## やること

1. 上の材料から「**次に同じことをする人が得をする事実**」を拾う。
   特に次を優先：
   - 想定と違ったこと（実測して初めて分かったこと）
   - 有璽氏が示した事実・制約・やり方（★怒っているかどうかは関係ない）
   - 踏んだ地雷（同じ形で再発しうるもの）
2. `~/vivid-ai-hq/memory/` に**既に同じ内容があるか必ず探す**。
   あれば追記して更新する。無ければ新規に作る（frontmatter の書式は既存に合わせる）
3. `~/vivid-ai-hq/memory/MEMORY.md` に1行の索引を足す。
   ★索引はラベルではなく**現在地**を運ぶこと
4. `./check.sh` を通す（memory索引の孤児が出ないこと）

## 守ること
- **既にあるものは触らない。** 重複を増やさない
- **拾うものが無ければ「無い」と言って終わる。** 無理に書かない
- commit はしない（こちらで行う）
- 報告は800文字以内。何を書いたか／何を書かなかったかを簡潔に
""" % (y, d['commits'][:6000] or '（なし）',
       d['corrections'][:6000] or '（なし）',
       d['warnings'][:3000] or '（なし）',
       '\n'.join(d['memory_touched']) or '（前日は memory を1本も触っていない）')

    if dry:
        print('---- ドライランなのでロビンを呼ばない ----')
        print('   プロンプト長 ： %d文字' % len(prompt))
        return 0

    try:
        r = subprocess.run([CLAUDE, '-p', prompt], cwd=REPO,
                           capture_output=True, text=True, timeout=TIMEOUT)
        out = (r.stdout or '').strip()
        ok = (r.returncode == 0)
    except Exception as e:
        out, ok = '★失敗 ： %s' % e, False
    print(out[:2000])

    # Slackへ知らせる（報告なので返信不要と明記される）
    try:
        sys.path.insert(0, HERE)
        from notify import tell
        tell('前日の記録を棚卸ししました（%s）' % y, out[:2500])
    except Exception as e:
        sys.stderr.write('[Slack] 送れず ： %s\n' % e)

    if beat:
        try:
            from heartbeat import beat as hb
            hb(PROC_NAME, '成功' if ok else '失敗', out[:180])
        except Exception:
            pass
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(dry=('--run' not in sys.argv), beat=('--beat' in sys.argv)))
