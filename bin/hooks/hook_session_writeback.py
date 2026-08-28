#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stop フック ── 書き戻さずにターンを終えようとしたら1回だけ差し戻す

なぜ要るか（2026-08-25 有璽氏）
  > 「これでオペレーション上は問題ないと思ってるけど、落ちへんの。
  >   ★途中で止まったりするんだよね、このオペレーションがね。確実に回るようにしてほしい」

  「離席宣言」「区切り」で書き戻す手順は **AIの規律に依存している**。
  規律に依存する対策は、規律が切れた回にだけ効かない（reference_hooks_enforce_what_discipline_cannot）。
  ★だから合図を増やすのではなく、**ターンが終わるたび**に機械で見る。

何を見るか（★誤爆しないための線引き）
  対象   memory/ ・ WORKING.md ・ .claude/ ・ bin/ の未コミット
  条件   ★最終更新から10分以上たっているものだけ
         ＝ いま書いている最中のもの・他セッションが書き込んだ直後のものでは鳴らない
  無限ループ対策  stop_hook_active が true（＝すでに1度差し戻した）なら黙って通す

出力の作法
  exit 2 ＋ stderr  → Claude に差し戻される（stderr の中身がそのまま指示になる）
  exit 0            → そのまま終了
  ★何があっても exit 1 で落とさない。フック自身の失敗でセッションを止めない
"""
import json, os, subprocess, sys, time

REPO = os.path.expanduser('~/vivid-ai-hq')
WATCH = ('memory/', 'WORKING.md', '.claude/', 'bin/')
STALE_MIN = 10
LOG = os.path.expanduser('~/.vivid-relay/hook_writeback.log')


def log(verdict, detail=''):
    """★毎回1行残す。「鳴っていない」と「動いていない」を区別するため（2026-08-28 有璽氏）

    このフックは exit 2 の中身が Claude にしか返らず、有璽氏の画面には出ない。
    ログが無いと「消えてる気がする」を実測で否定できない。★何があっても例外を外に出さない。
    """
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a') as f:
            f.write('%s\t%s\t%s\n' % (time.strftime('%Y-%m-%dT%H:%M:%S'), verdict, detail))
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    # すでに1度差し戻している。2度目は通す（無限ループにしない）
    if payload.get('stop_hook_active'):
        log('通した', '2度目（stop_hook_active）')
        return 0

    if not os.path.isdir(os.path.join(REPO, '.git')):
        log('通した', 'リポジトリが無い')
        return 0

    r = subprocess.run(['git', '-C', REPO, 'status', '--porcelain', '-z'],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout:
        log('通した', '未コミット0件')
        return 0

    entries = [e for e in r.stdout.split('\0') if e]
    targets = []
    i = 0
    while i < len(entries):
        e = entries[i]
        code, path = e[:2], e[3:]
        i += 1
        if code[0] in ('R', 'C'):
            i += 1
        if not path.startswith(WATCH):
            continue
        full = os.path.join(REPO, path)
        if 'D' in code:
            targets.append((path, '削除'))
            continue
        if not os.path.isfile(full):
            continue
        if (time.time() - os.path.getmtime(full)) / 60.0 < STALE_MIN:
            continue          # いま書いている最中。触らない
        targets.append((path, '変更' if code.strip() != '??' else '新規'))

    if not targets:
        log('通した', '%d分超の対象なし（未コミット%d件）' % (STALE_MIN, len(entries)))
        return 0

    lines = [
        '★書き戻しが終わっていません。ターンを終える前に片づけてください。',
        '',
        f'{STALE_MIN}分以上さわっていない未コミットが {len(targets)} 件あります：',
    ]
    for p, kind in targets[:15]:
        lines.append(f'  [{kind}] {p}')
    if len(targets) > 15:
        lines.append(f'  …ほか {len(targets)-15} 件')
    lines += [
        '',
        '順番も固定です（memory/feedback_write_back_before_you_go.md）：',
        '  1  この会話で分かった事実を memory/ の該当ファイルへ書く（無ければ作る）',
        '  2  索引（MEMORY.md か INDEX_*.md）の現在地を1行だけ差し替える',
        '  3  WORKING.md の自分のブロックを実態に合わせる（終わったものは消す）',
        '  4  ./check.sh を通す',
        '  5  ★触ったファイルを明示して commit（git add -A は使わない）',
        '',
        '他セッションの書きかけで自分は触っていない、あるいは意図して置いている場合は、',
        'その旨を1行述べてそのまま終えて構いません（2度目はこのフックは鳴りません）。',
    ]
    sys.stderr.write('\n'.join(lines) + '\n')
    log('★差し戻した', '%d件: %s' % (len(targets), ' '.join(p for p, _ in targets[:5])))
    return 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:               # フック自身の失敗でセッションを止めない
        sys.stderr.write(f'(hook_session_writeback: {e})\n')
        sys.exit(0)
