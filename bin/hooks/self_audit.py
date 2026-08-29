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
import re
import sys
import json
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# ★2026-08-29 ビビ依頼①：パスの二重定義解消（check.sh項目8で検出・穴Aと同じ型）。
#   独自の代入文をやめ、bin/hooks/paths.py の正本を import する。
sys.path.insert(0, HERE)
from paths import REPO, WORKING_MD
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

    # ★2026-08-29 追加（ピタゴラス実装）── 「仕組みの生死」だけでなく
    #   「規範どおりに動けているか」を見る。有璽氏「なんで俺が言われてからしか
    #   この動きをせんねん。直後だけなんだよいつも」への直し。
    out['git_no_review'] = _git_commits_without_review()
    out['working_md_markers'] = _working_md_marker_ages()
    out['role_guard'] = _role_guard_summary()
    out['open_findings'] = _open_findings_summary()
    return out


def _git_commits_without_review(n=20):
    """①②観点：実装コードを含むコミットのうち、メッセージに検査役の言及が無いものを拾う。

    ★できないこと（正直に明記）：git の著者(author)は Claude Code のコミットが
      すべて有璽氏の git 設定（y_tam <y_tam@vivid-global.com>）で記録されるため、
      **「ビビが書いたか担当が書いたか」を著者情報から機械的に判別することはできない**
      （実測で確認：直近コミットは全て同一著者）。
      → 代わりに「コミットメッセージ本文に検査役への言及があるか」という
        **弱い代理指標（自己申告ベース）** を使う。申告漏れがあれば見逃す。
    """
    try:
        r = subprocess.run(
            ['git', '-C', REPO, 'log', '-n', str(n), '--format=%H|%s'],
            capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            return '（取れず）'
    except Exception as e:
        return '（取れず ： %s）' % e
    hits = []
    for line in r.stdout.strip().split('\n'):
        if '|' not in line:
            continue
        h, s = line.split('|', 1)
        try:
            names = subprocess.run(
                ['git', '-C', REPO, 'show', '--name-only', '--format=', h],
                capture_output=True, text=True, timeout=15).stdout
        except Exception:
            continue
        code_files = [f for f in names.split('\n')
                      if re.search(r'\.(py|js|ts|gs|sh)$', f)]
        if not code_files:
            continue
        try:
            body = subprocess.run(
                ['git', '-C', REPO, 'log', '-1', '--format=%B', h],
                capture_output=True, text=True, timeout=15).stdout
        except Exception:
            body = ''
        if not re.search(r'つる|ステラ|ドーベルマン|検査|載せてよい|レビュー', body):
            hits.append('%s %s（コード%d件）' % (h[:9], s[:50], len(code_files)))
    if not hits:
        return '（直近%d件、実装コードを含むコミットは全て検査役への言及あり）' % n
    return '\n'.join(hits[:10])


def _working_md_marker_ages(threshold_days=7):
    """③観点：WORKING.md の「★残」「未着手」等マーカーの経過日数（見出しの日付から算出）"""
    path = WORKING_MD
    try:
        lines = open(path, encoding='utf-8').read().split('\n')
    except Exception as e:
        return '（取れず ： %s）' % e
    import datetime as _dt
    heading_re = re.compile(r'^###.*?(\d{4})-(\d{2})-(\d{2})')
    marker_re = re.compile(r'★残|未着手|残件|判断待ち|承認待ち')
    today = _dt.date.today()
    cur = None
    hits = []
    for ln in lines:
        m = heading_re.match(ln)
        if m:
            try:
                cur = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                cur = None
            continue
        if cur and marker_re.search(ln):
            days = (today - cur).days
            if days >= threshold_days:
                hits.append((days, cur.isoformat(), ln.strip()[:70]))
    hits.sort(key=lambda x: -x[0])
    if not hits:
        return '（%d日以上経過のマーカーは無い）' % threshold_days
    return '\n'.join('%3d日経過(%s) %s' % (d, dt, t) for d, dt, t in hits[:10])


def _role_guard_summary():
    """①観点：hook_role_guard.py が実際に役割違反を止めた回数（2026-08-29 新設・稼働はこれから）

    ★2026-08-29 改修（ビビ指摘・穴A）：ここでは以前 `os.path.join(HERE, 'role_guard.log')`
    （＝ bin/hooks/role_guard.log）という誤ったパスを独自に持っていた。実物のログは
    hook_role_guard.py の LOG 定数（~/.vivid-relay/role_guard.log）にしかない。
    9,455バイト・本物の agent_id で発火し続けていたのに、パスが違うだけで
    「role_guard.log が無い＝まだ稼働していない」と毎朝言い続けていた。
    ＝ パスを2箇所に文字列で書いた時点で片方が古くなる（reference_stale_premise_daily と同型）。
    二度と起こさないよう、文字列で再定義せず hook_role_guard.py から LOG を import する。"""
    try:
        sys.path.insert(0, HERE)
        from hook_role_guard import LOG as log
    except Exception as e:
        return '（LOG定数の取得に失敗 ： %s）' % e
    # ★2026-08-29 つる ── 登録の有無を先に見る。
    #   それまでは「log が無ければ未稼働」としか判定しておらず、settings.json へ未登録の
    #   ままでも手動テストでログが出来た瞬間に「ブロック3件」と稼働中のように見えた。
    #   ＝テストするほど動いているように見える指標だった（実際にこの誤読が起きた）。
    registered = False
    try:
        s = json.load(open(os.path.expanduser('~/.claude/settings.json')))
        registered = 'hook_role_guard.py' in json.dumps(s.get('hooks', {}))
    except Exception:
        pass
    if not os.path.exists(log):
        return '（role_guard.log が無い＝まだ稼働していない。settings.json への登録が残件）'
    try:
        lines = open(log, encoding='utf-8').read().strip().split('\n')
    except Exception as e:
        return '（取れず ： %s）' % e
    blocked = sum(1 for ln in lines if '★ブロック' in ln)
    warned = sum(1 for ln in lines if '★警告' in ln)
    body = '直近ログ %d行 ／ ブロック %d件 ／ 警告 %d件' % (len(lines), blocked, warned)
    if not registered:
        return ('★未稼働（settings.json に hook_role_guard.py の登録が無い）。'
                'この件数は手動テストの痕跡であって、実際に止めた回数ではない ： ' + body)
    return body


def _open_findings_summary(min_streak=3):
    """③観点：指摘台帳（findings_tracker）で N日以上開いたままの指摘を集約"""
    try:
        sys.path.insert(0, HERE)
        from findings_tracker import open_findings
        rows = open_findings(min_streak_days=min_streak)
    except Exception as e:
        return '（取れず ： %s）' % e
    if not rows:
        return '（%d日以上開いたままの指摘は無い）' % min_streak
    return '\n'.join('%3d日連続 [%s] %s' % (
        r.get('streak_days', 0), r.get('source'), r.get('last_text')) for r in rows[:10])


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

### ★実装コードを含むコミットで検査役への言及が無いもの（弱い代理指標）
```
%s
```
★注意：git の著者情報からは「ビビが書いたか担当が書いたか」を判別できない
（Claude Code のコミットは全て有璽氏の git 設定で記録されるため、実測で確認済み）。
これは「コミットメッセージに検査役の名前が出ているか」という自己申告ベースの
弱い指標です。ここに挙がったコミットは**疑いがある**というだけで、確定ではありません。

### ★WORKING.md で7日以上放置されている「★残／未着手」マーカー
```
%s
```

### ★役割違反の検問（hook_role_guard.py）の稼働状況
```
%s
```

### ★3日以上開いたままの指摘（findings_tracker）
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

5. **★規範どおりに動けているか（2026-08-29 追加）**
   ・実装コードを含むコミットで検査役への言及が無いものは、実際に検査を経ずに
     コミットされた疑いがあるか。**git だけでは確定できないので、疑いとして報告する**
   ・WORKING.md の「★残／未着手」マーカーで7日以上放置されているものがあれば、
     「なぜ止まっているか」（判断待ちか、単に忘れられているか）を材料から推測して添える
   ・findings_tracker で3日以上開いたままの指摘があれば、それを最優先で扱う
     （[[reference_a_warning_nobody_owns]]「正しく鳴っているのに拾われない」型）

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
       d['scripts'][:2000], d['warnings'][:2500] or '（なし）',
       d['git_no_review'][:1500], d['working_md_markers'][:1500],
       d['role_guard'][:500], d['open_findings'][:1500])

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
