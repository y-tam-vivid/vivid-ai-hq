#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""放置された未コミットを自動で確定させる（vivid-sync.sh から15分ごとに呼ばれる）

なぜ要るか（2026-08-25 有璽氏）
  「僕が離席するタイミングで自動的に上書きしてほしい。もしくは私からの指示が
   一定期間ない時は自動で現状をMDファイルなりメモリなりに共有する設計にできないか」

  commit されていない変更は他機へ1バイトも届かない。2026-08-25 に MacBook が50件遅れ、
  同じ棚卸しを2機が別々にやる事故が起きた。原因は「書いたが commit していない」だった。

設計の線引き（★ここを間違えると他体の書きかけを飲む）
  対象にする   変更(M) と 新規(??) のうち、★最終更新から N 分以上たったもの
               ＝ いま書いている最中のものは触らない
  対象にしない  削除(D)。消すのは不可逆なので必ず人が commit する
               .gitignore 済み・サブモジュール・conflict 中のファイル
  add は必ずパス指定  ★git add -A は使わない → memory/reference_git_add_all_swallows_others.md

環境変数
  VIVID_REPO              既定 ~/vivid-ai-hq
  VIVID_AUTOCOMMIT_MIN    既定 60（分）
  VIVID_AUTOCOMMIT_DRYRUN 1 なら実行せず対象だけ出す
"""
import os, subprocess, sys, time

REPO = os.environ.get('VIVID_REPO', os.path.expanduser('~/vivid-ai-hq'))
MIN  = int(os.environ.get('VIVID_AUTOCOMMIT_MIN', '60'))
DRY  = os.environ.get('VIVID_AUTOCOMMIT_DRYRUN', '0') == '1'


def git(*a, **kw):
    return subprocess.run(['git', '-C', REPO] + list(a),
                          capture_output=True, text=True, **kw)


def main():
    # conflict 中は絶対に触らない
    if git('ls-files', '-u').stdout.strip():
        print('skip: マージ衝突の解決中')
        return 0

    out = git('status', '--porcelain', '-z').stdout
    if not out:
        print('skip: 未コミットなし')
        return 0

    entries = [e for e in out.split('\0') if e]
    targets, skipped_del, too_fresh = [], 0, 0
    i = 0
    while i < len(entries):
        e = entries[i]
        code, path = e[:2], e[3:]
        i += 1
        if code[0] in ('R', 'C'):   # rename/copy は次要素が元パス
            i += 1
        if 'D' in code:
            skipped_del += 1
            continue
        full = os.path.join(REPO, path)
        if not os.path.isfile(full):
            continue
        age_min = (time.time() - os.path.getmtime(full)) / 60.0
        if age_min < MIN:
            too_fresh += 1
            continue
        targets.append(path)

    print('対象 %d / 書きかけ(新しい) %d / 削除のため見送り %d'
          % (len(targets), too_fresh, skipped_del))
    if not targets:
        return 0
    for p in targets:
        print('    ' + p)
    if DRY:
        print('dry-run: 実行していません')
        return 0

    add = git('add', '--', *targets)
    if add.returncode != 0:
        print('NG  git add に失敗: ' + add.stderr.strip())
        return 1
    if not git('diff', '--cached', '--name-only').stdout.strip():
        print('skip: ステージに何も乗らなかった')
        return 0

    msg = ('自動確定（%d分以上更新が無かったもの・%d件）\n\n'
           '離席や無操作で commit されずに残った変更を、他機へ届けるために確定させる。\n'
           '★中身は編集していない。対象はパス指定で、削除は含めていない。\n'
           '経緯 → memory/feedback_write_back_before_you_go.md\n\n'
           'Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>' % (MIN, len(targets)))
    c = git('commit', '-m', msg)
    if c.returncode != 0:
        print('NG  commit に失敗: ' + (c.stderr or c.stdout).strip())
        return 1
    print('OK  %d件を確定した（push は vivid-sync.sh が behind=0 のときに行う）' % len(targets))
    return 0


if __name__ == '__main__':
    sys.exit(main())
