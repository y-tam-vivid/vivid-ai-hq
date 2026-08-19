#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自分の設計と運用を、自分で監査して直す ── 毎日（指摘を待たない）

  python3 self_audit.py            ドライラン（何を監査するかだけ出す）
  python3 self_audit.py --run      本実行（つる＋ステラを呼んで、直せるものは直す）
  python3 self_audit.py --run --beat

なぜ要るか（2026-08-20 有璽氏）
  > 「自立して、そういったことを直らない、同じようにならないようにしていけよ。
  >   なんで俺が指摘しなきゃってやれないんだよ。自分たちで自立して回るようにして、
  >   指摘して初めて抜け漏れ6つありましたじゃねえんだろ。
  >   自分で修正、修正、修正を繰り返していけよ」

  ★これまでの形 ── 有璽氏が「抜け漏れがあるんじゃないか」と聞く → こちらが穴を探す
    ＝ **穴を探す起点が人の指摘だった。**
  ★あるべき形 ── 毎日、こちらが自分で探して直す。人は結果だけ見る

やること
  ① つる（データ検査役）に、自分たちの仕組み自体を検査させる
     ・cron に載っているものは本当に動いているか（心拍と実体の突合）
     ・レジスタに載っていないのに動いているものは無いか
     ・フックは生きているか
     ・「作ったが未検証」のまま放置されているものは無いか
  ② 出た指摘のうち **自分で直せるものはその場で直す**（可逆なものだけ）
  ③ 直せないもの（人の操作が要る／判断が要る）だけ Slack へ出す

★人へ出すのは「自分で直せなかったもの」だけ。直せたものは報告に混ぜない。
"""

import os
import sys
import json
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.expanduser('~/vivid-ai-hq')
CLAUDE = os.path.expanduser('~/.npm-global/bin/claude')
PROC_NAME = '自己監査（自分で穴を見つけて直す）'
TIMEOUT = 1500
STATE = os.path.join(HERE, 'self_audit_state.json')


def collect():
    """監査の材料。★人の手が要らないものだけ"""
    out = {}
    try:
        out['crontab'] = subprocess.run(['crontab', '-l'], capture_output=True,
                                        text=True, timeout=30).stdout
    except Exception as e:
        out['crontab'] = '（取れず ： %s）' % e
    try:
        out['selfcheck'] = subprocess.run(
            ['/usr/bin/python3', os.path.join(HERE, 'hook_selfcheck.py')],
            capture_output=True, text=True, timeout=60).stdout
    except Exception as e:
        out['selfcheck'] = '（取れず ： %s）' % e
    # ~/.vivid-relay/ の実体
    try:
        out['scripts'] = subprocess.run(
            ['ls', '-1', HERE], capture_output=True, text=True, timeout=20).stdout
    except Exception:
        out['scripts'] = ''
    # 直近のログの失敗
    warns = []
    for f in os.listdir(HERE):
        if not f.endswith('.log'):
            continue
        try:
            tail = subprocess.run(['tail', '-25', os.path.join(HERE, f)],
                                  capture_output=True, text=True, timeout=15).stdout
        except Exception:
            continue
        for line in tail.split('\n'):
            if any(k in line for k in ('Traceback', 'Error', '★失敗', 'エラー')):
                warns.append('%s ： %s' % (f, line.strip()[:150]))
    out['warnings'] = '\n'.join(warns[-25:])
    return out


def main(dry=True, beat=False):
    d = collect()
    today = datetime.date.today().isoformat()
    print('【%s】自己監査 ： %s' % ('ドライラン' if dry else '★本実行', today))
    print('■ cron ： %d行' % len([x for x in d['crontab'].split('\n')
                                 if x.strip() and not x.startswith('#')]))
    print('■ フック点検 ： %s' % d['selfcheck'].strip().split('\n')[0] if d['selfcheck'] else '（取れず）')
    print('■ ログの失敗 ： %d件' % (len(d['warnings'].split('\n')) if d['warnings'] else 0))
    print('')

    prompt = """あなたは「つる」（データ検査役）です。
`~/vivid-ai-hq/.claude/agents/data-auditor.md` を読んで、つるとして振る舞ってください。

**今日の仕事は、顧客データではなく「私たち自身の仕組み」の検査です。**

## なぜこの仕事があるか
有璽氏から「なんで俺が指摘しなきゃ穴を探さないんだ。自分で修正を繰り返していけ」と
言われました（2026-08-20）。これまでは**穴を探す起点が人の指摘**でした。
今日から毎日、あなたが自分で探します。

## 材料（実測値）

### crontab
```
%s
```

### フックの生存点検
```
%s
```

### ~/.vivid-relay/ にあるもの
```
%s
```

### 直近のログに出た失敗
```
%s
```

## 検査してほしいこと

1. **cron に載っているのに動いていないもの**
   Notion ⚙️自動処理レジスタ（`b4e9609d99d14626a71226c84f9c6d76`、
   トークンは `~/.vivid-relay/config.env` の NOTION_TOKEN。★値は出力しない）を読み、
   「最終実行」が期待間隔を大きく超えているものを挙げる

2. **動いているのにレジスタに載っていないもの**
   crontab の実体とレジスタを突き合わせる。★心拍では絶対に見つからない穴

3. **「作ったが未検証」のまま放置されているもの**
   スクリプトは在るのに cron にも無く、レジスタにも無いもの

4. **仕組み自体の穴**
   ・フックは3本とも生きているか
   ・記録の経路（memory / landmines.json / corrections.log）は更新されているか
   ・「有効」なのに一度も心拍が来ていないものは無いか

## ★重要 ── 出したら終わりにしない

指摘を **「自分で直せるもの」と「人の操作・判断が要るもの」に分けて**ください。

- **自分で直せるもの**（可逆・設定・登録漏れ・ログの整理など）は、**その場で直してください**。
  ★あなたは普段データを書き換えませんが、今日の対象は自分たちの仕組みです。
  ただし台帳・顧客DB・kintone には一切触らないこと。
- **人の操作が要るもの**（API申請・フォルダ設置・権限追加）と
  **判断が要るもの**（設計の分岐）は、直さずリストにしてください。

## 出し方
```
■ 直した ： N件
   ・何をどう直したか（1行ずつ）
■ ★人が要る ： N件
   ・何を／なぜAIではできないか（1行ずつ）
■ 異常なし
```
1000文字以内。日本語。**問題が無ければ「無い」と明言する。**
""" % (d['crontab'][:3000], d['selfcheck'][:1500],
       d['scripts'][:2000], d['warnings'][:2500] or '（なし）')

    if dry:
        print('---- ドライランなので、つるを呼ばない ----')
        print('   プロンプト長 ： %d文字' % len(prompt))
        return 0

    try:
        r = subprocess.run([CLAUDE, '-p', prompt], cwd=REPO,
                           capture_output=True, text=True, timeout=TIMEOUT)
        out = (r.stdout or '').strip()
        ok = (r.returncode == 0)
    except Exception as e:
        out, ok = '★失敗 ： %s' % e, False
    print(out[:2500])

    # ★人が要るものが出たときだけ Slack へ出す（直せたものは出さない＝報告を増やさない）
    need_human = '人が要る' in out and '★人が要る ： 0件' not in out
    try:
        sys.path.insert(0, HERE)
        if need_human:
            from notify import tell
            tell('自己監査 ： 人の手が要るものが出ました（%s）' % today, out[:2500])
    except Exception as e:
        sys.stderr.write('[Slack] 送れず ： %s\n' % e)

    try:
        json.dump({'date': today, 'need_human': need_human}, open(STATE, 'w'))
    except Exception:
        pass

    if beat:
        try:
            from heartbeat import beat as hb
            hb(PROC_NAME, '警告' if need_human else ('成功' if ok else '失敗'), out[:180])
        except Exception:
            pass
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(dry=('--run' not in sys.argv), beat=('--beat' in sys.argv)))
