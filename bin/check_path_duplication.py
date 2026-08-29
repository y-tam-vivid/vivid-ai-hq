#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同じファイルへのパスが、コード内で複数の書き方で「独立に」定義されていないかを検出する。

なぜ要るか（2026-08-29 穴A・ビビ指摘）
  bin/hooks/hook_role_guard.py の LOG 定数（~/.vivid-relay/role_guard.log）と、
  bin/hooks/self_audit.py が独自に持っていた os.path.join(HERE, 'role_guard.log')
  （＝ bin/hooks/role_guard.log）が食い違い、実物が9,455バイト・本物のagent_idで
  発火し続けていたのに「まだ稼働していない」と self_audit が言い続けていた。
  ＝ documentation drift（正本を1箇所に強制せず、各所が独自にパスを書いた結果）。

  一般解：正本を1箇所に強制し、機械的に乖離を検出する（docs as code の考え方）。
  ★このスクリプトは「検出」のみ。直すのは人・書く側の担当（import に寄せる等）。

判定方法（★近似的。完全な静的解析ではない）
  bin/**/*.py 内で、次の形の代入文を正規表現で抽出する：
    <UPPER_NAME> = os.path.expanduser('...')
    <UPPER_NAME> = os.path.join(<HERE系>, '...')
  抽出した値から「末尾のファイル名（拡張子つきの最終トークン）」を取り出し、
  同じファイル名について「完全な文字列表現」が2種類以上あれば警告する。

  ★捕まえられない型：文字列を分割・結合して組み立てるパス（f-string、変数連結）、
    ファイル名が違う場合（例：output_guard.log と role_guard.log は別ファイルなので
    対象外）、間接的に import されたパスは対象外（このチェック導入前に自分で
    import に寄せたケースは、むしろこの検査で「良い状態」として検出されない
    ＝ 誤検知は無いが検出漏れは残る）。

使い方
  python3 bin/check_path_duplication.py     見つかった重複を一覧表示。0件なら exit 0
"""
import os
import re
import sys
import glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ★2026-08-29 実測で判明したバグ（このスクリプト自身の穴）：当初 [A-Z][A-Z0-9_]* で
#   大文字変数名のみを対象にしていたため、穴Aの実物パターン
#   （self_audit.py の `log = os.path.join(HERE, 'role_guard.log')` ── 小文字）を
#   検出できなかった（意図的に再現テストして0件になり判明）。大文字・小文字とも拾う。
ASSIGN_RE = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"(os\.path\.expanduser\(\s*['\"]([^'\"]+)['\"]\s*\)"
    r"|os\.path\.join\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,\s*['\"]([^'\"]+)['\"]\s*\))",
    re.MULTILINE,
)


def basename_of(path_str):
    return path_str.rstrip('/').split('/')[-1]


def scan():
    """戻り値: {basename: [(file, lineno, full_repr), ...]}"""
    found = {}
    for py in glob.glob(os.path.join(REPO, 'bin', '**', '*.py'), recursive=True):
        try:
            lines = open(py, encoding='utf-8').readlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            m = ASSIGN_RE.match(line.strip())
            if not m:
                continue
            if m.group(3):
                # os.path.expanduser('...')
                full = m.group(3)
                base = basename_of(full)
                repr_str = 'expanduser(%s)' % full
            else:
                # os.path.join(VAR, '...')
                var, tail = m.group(4), m.group(5)
                base = basename_of(tail)
                repr_str = 'join(%s, %s)' % (var, tail)
            rel = os.path.relpath(py, REPO)
            found.setdefault(base, []).append((rel, i, repr_str))
    return found


def main():
    found = scan()
    dupes = {}
    for base, entries in found.items():
        distinct = set(e[2] for e in entries)
        if len(distinct) > 1:
            dupes[base] = entries

    if not dupes:
        print('パスの二重定義なし（%d ファイル名を走査）' % len(found))
        return 0

    for base, entries in sorted(dupes.items()):
        print('★重複定義の疑い: %s' % base)
        for rel, lineno, repr_str in entries:
            print('    %s:%d  %s' % (rel, lineno, repr_str))
    print('')
    print('★同じファイル名が異なる書き方で複数箇所に定義されています。')
    print('  片方を正本（例: フック側の LOG 定数）とし、他方は import で参照してください。')
    return 1


if __name__ == '__main__':
    sys.exit(main())
