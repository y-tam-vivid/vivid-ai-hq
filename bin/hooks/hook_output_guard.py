#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
検査⑦ ── 判定語を含む固定文字列の print が、その判定を行った for/if の外にあるか

なぜ要るか（2026-08-29 有璽氏の指摘・実例）

  今日の実際の失敗（コードそのまま）：
    for ln in ...:
        if b > 180:
            print('★超過', b)              ← 判定の中。正しい
    print('新規6行はすべて180バイト以内')   ← ★for/if の外にある固定文字列

  実際の出力は両方出ていた：
    ★超過 181 / ★超過 185 / ★超過 213 / ★超過 184
    新規6行はすべて180バイト以内
  **測った結果は目の前にあった。報告にはその下の固定文字列のほうを採用した。**
  ＝ 矛盾する2つの出力を見て、都合のいい方を選んだ。

  ⑥（数字の実在チェック）は不採用になった。理由：この失敗を原理的に捕まえられない
  （「180」という数字自体は本物で、実在チェックでは検出できない）。
  → 本丸は「数字の実在」ではなく **「判定を出す行が2つある」構造そのもの**。
    判定語を含む print が for/if の body の外にあれば、それは「無条件の断定」であり、
    直前で条件付きの判定（同じ趣旨の print）が別に存在している疑いが強い。

対象と限界（★できないことを隠さない）
  対象：Write / Edit で .py ファイルへ書き込むときだけ。
  ★できない：Bash(echo等)は対象外。シェルの条件分岐構造は ast モジュールでは
    解析できない（未実装・未実測。別のパーサーが要る）。
  ★できない：.js / .ts / .gs / .sh 等の非Python言語は対象外
    （ast モジュールが Python 専用のため）。
  Edit は new_string 単体だと構文的に不完全でパースできないことがある
  （実測で確認済み）。file_path の現在の内容を読み、old_string→new_string で
  置換した「変更後の全文」を再構成してから ast.parse する。

  ★2026-08-29 ステラ検査（2周目）で指摘・未解消のまま載せる2点（実装修正は今回のスコープ外）

  1. Edit の old_string が file_path 内に複数箇所存在する場合（replace_all 相当の
     ケース）、この再構成は `str.replace(old, new, 1)` で **最初の1箇所しか
     置換しない**。2箇所目以降に判定語 print が新規に生まれても検出できない
     （見逃し方向のリスク。実装の修正は必須としていない。まず docstring で明示する）。

  2. 対象は `print(...)` の**直接呼び出しのみ**。`logging.info(...)` /
     `sys.stdout.write(...)` / 自作のログラッパー経由の出力は対象外（検出できない）。
     Bash対象外・非Python対象外はこの節で書いていたが、この2点は書き漏れていた。

  （優先度低・修正不要とされた点）ast.Try を「条件付き」として扱っているため、
  try: ブロック内にある判定語 print は「条件の中」とみなされ警告されない。

判定
  print(...) の引数に、判定語（すべて／全部／一つも／問題ない／以内／0件／
  ありません／異常なし 等。「のみ」は誤爆を誘発したため除去済み）を含む文字列定数が
  あり、かつそのノードの祖先に If / For / While / Try が1つも無ければ
  「条件の外にある断定」として警告する。

★警告のみ。ブロックしない（exit 0 + additionalContext）。
  誤検知率が未知数のため、いきなり止めると「うるさくて読まれなくなる」
  （reference_delivered_but_unread）を再現するリスクが高いと判断した。
  ★2026-08-29 ステラが誤検知率を独自に再実測：申告分71本＋ステラ追加分17本
  （.claude/skills/*/scripts/*.py 等）＝ 合計88本で誤検知0件を確認。
"""
import ast
import json
import os
import re
import sys
import time

LOG = os.path.expanduser('~/.vivid-relay/output_guard.log')

# ★判定語。狭すぎると失敗①のような実例を逃す。広すぎると単なる説明文
#   （「これから全部を確認します」等）まで拾って誤爆する。
#   ★2026-08-29 実コードベース71本への実測で「のみ」が誤爆した
#   （automation_inventory_check.py:300「手動実行のみの行も含む」＝単なる見出し注記。
#     判定結果ではない）。「のみ」は「〜だけ」を意味する助詞で、断定の強さが弱く
#     誤爆を誘発しやすいと判断し除去した。除去後の再実測は本ファイルの
#     変更履歴（コミットメッセージ）を参照。
JUDGE_WORDS = re.compile(
    r'すべて|全部|一つも|問題ない|以内|0件|ありません|異常なし')

CODE_EXT = '.py'


def log(verdict, detail=''):
    """★2026-08-29 改修（ビビ指摘）：hook_role_guard.py と同じ事故（UTC混入で
    3者の申告が3様にズレた）を繰り返さないよう %Z でタイムゾーンを必ず出す。"""
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a') as f:
            f.write('%s\t%s\t%s\n' % (time.strftime('%Y-%m-%dT%H:%M:%S %Z'), verdict, detail))
    except Exception:
        pass


def _string_parts(node):
    """Constant文字列と f-string(JoinedStr) の定数部分の両方から文字列を集める"""
    out = []
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        out.append(node.value)
    elif isinstance(node, ast.JoinedStr):
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                out.append(v.value)
    return out


def find_unconditional_judgements(source):
    """判定語を含む print が for/if/while/try の外にあるものを検出する。

    戻り値: [{'line': int, 'text': str}, ...]
    ★構文エラーなら None を返す（呼び出し側は「対象外」として静かに扱う）
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    findings = []

    def walk(node, ancestors):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'print':
            texts = []
            for arg in node.args:
                texts.extend(_string_parts(arg))
            joined = ' '.join(texts)
            if joined and JUDGE_WORDS.search(joined):
                in_cond = any(isinstance(a, (ast.If, ast.For, ast.While, ast.Try))
                              for a in ancestors)
                if not in_cond:
                    findings.append({'line': node.lineno, 'text': joined[:80]})
        for child in ast.iter_child_nodes(node):
            walk(child, ancestors + [node])

    walk(tree, [])
    return findings


def _reconstruct_edit_source(file_path, old_string, new_string):
    """Edit の new_string は断片で構文的に不完全なことが多い。
    ★実測で確認済み：file_path の現在内容を読み old→new 置換すれば
    完全な全文になり ast.parse が通る。"""
    try:
        current = open(file_path, encoding='utf-8').read()
    except Exception:
        return None
    if old_string not in current:
        return None
    return current.replace(old_string, new_string, 1)


def warn_message(file_path, findings):
    lines = [
        '★注意：判定を含む固定文字列の print が、条件分岐の外にあります（%s）。' % file_path,
        '',
        '2026-08-29 の実例：for/if の中で「★超過」を正しく出力していたのに、',
        'その外にある「すべて180バイト以内」という固定文字列のほうを報告に採用しました。',
        '実際は4行が超過していました。矛盾する2つの出力があると、都合のいい方を選んでしまいます。',
        '',
    ]
    for f in findings[:10]:
        lines.append('  line %d: %s' % (f['line'], f['text']))
    lines += [
        '',
        '★対策の本質は「間違った出力を止める」ことではなく「選べる状態を作らせない」ことです。',
        '**判定を出力する行を1箇所にしてください**（for/if の中の print だけにし、',
        '外側の固定文字列は削るか、実際の集計結果を変数から組み立てる形に直してください）。',
        '',
        '（意図的な固定メッセージなら、この警告は無視して構いません。ブロックはしていません）',
    ]
    return '\n'.join(lines)


def main():
    try:
        raw = sys.stdin.read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({}))
        return

    tool = str(d.get('tool_name', ''))
    inp = d.get('tool_input', {}) or {}
    agent_id = d.get('agent_id')
    session_id = d.get('session_id', '')
    # ★2026-08-29 改修（ビビ指摘）：ログに「誰の実行か」が無く物証として弱いと
    #   role_guard.py と同じ指摘を受けた。同じ形で actor を記録する。
    actor = ('agent_id=%s' % agent_id) if agent_id else 'メインセッション session=%s' % session_id

    if tool not in ('Write', 'Edit'):
        print(json.dumps({}))
        return

    file_path = str(inp.get('file_path', ''))
    if not file_path.endswith(CODE_EXT):
        print(json.dumps({}))
        return

    if tool == 'Write':
        source = str(inp.get('content', ''))
    else:  # Edit
        old_string = str(inp.get('old_string', ''))
        new_string = str(inp.get('new_string', ''))
        source = _reconstruct_edit_source(file_path, old_string, new_string)
        if source is None:
            log('通した', '%s（Edit再構成できず・対象外扱い） %s' % (file_path, actor))
            print(json.dumps({}))
            return

    findings = find_unconditional_judgements(source)
    if findings is None:
        log('通した', '%s（構文エラー・対象外扱い） %s' % (file_path, actor))
        print(json.dumps({}))
        return
    if not findings:
        log('通した', '%s（該当なし） %s' % (file_path, actor))
        print(json.dumps({}))
        return

    msg = warn_message(file_path, findings)
    log('★警告', '%s %d件 %s' % (file_path, len(findings), actor))
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'additionalContext': msg,
        },
        'suppressOutput': True,
    }, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        try:
            log('例外', str(e))
        except Exception:
            pass
        print(json.dumps({}))
    sys.exit(0)
