#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""記録の巡回 ── メモリ本文と索引のズレを検出する（読むだけ・何も書かない）

担当: ドーベルマン（automation-watchdog）。毎週の巡回で走らせる。
規範: memory/project_memory_layer_design.md ／ memory/feedback_memory_index_hygiene.md

見るのは4つ。★どれも「実測できるもの」だけを見る（推測で判定しない）。
  1  本文を更新したのに索引を更新していない commit
  2  frontmatter の name とファイル名の不一致
  3  どの索引にも載っていない（＝孤児。check.sh と同じ検査を別経路で）
  4  MEMORY.md のバイト数と長すぎる索引行
"""
import os, re, subprocess, sys, datetime

ROOT = os.path.expanduser('~/vivid-ai-hq')
MEM  = os.path.join(ROOT, 'memory')
DAYS = int(os.environ.get('MEMORY_AUDIT_DAYS', '30'))
LIMIT_BYTES = 24986
LIMIT_LINE  = 180

def git(*a):
    return subprocess.run(['git', '-C', ROOT] + list(a),
                          capture_output=True, text=True).stdout

def is_index(path):
    b = os.path.basename(path)
    return b == 'MEMORY.md' or b.startswith('INDEX_')

def main():
    problems = []
    notes = []

    # --- 1. 本文だけ更新して索引を直していない commit -------------------
    since = (datetime.date.today() - datetime.timedelta(days=DAYS)).isoformat()
    shas = [s for s in git('log', '--since', since, '--format=%H', '--', 'memory/').split() if s]
    forgot = []
    for sha in shas:
        files = [f for f in git('show', '--name-only', '--format=', sha).split('\n')
                 if f.startswith('memory/') and f.endswith('.md')]
        if not files:
            continue
        bodies  = [f for f in files if not is_index(f) and '_archive/' not in f]
        indexes = [f for f in files if is_index(f)]
        # 新規追加は索引を足す義務があるので同じ扱い。削除だけの commit は対象外
        if bodies and not indexes:
            subject = git('log', '-1', '--format=%s', sha).strip()
            forgot.append((sha[:7], subject, bodies))
    if forgot:
        problems.append(
            "本文を更新したのに索引（MEMORY.md / INDEX_*.md）を直していない commit が "
            f"{len(forgot)} 件（直近{DAYS}日）")
        for sha, subject, bodies in forgot[:10]:
            notes.append(f"    {sha} {subject}")
            for b in bodies[:4]:
                notes.append(f"        {b}")
        if len(forgot) > 10:
            notes.append(f"    …ほか {len(forgot)-10} 件")

    # --- 2. frontmatter の name とファイル名 -----------------------------
    mismatch = []
    for f in sorted(os.listdir(MEM)):
        if not f.endswith('.md') or is_index(f):
            continue
        head = open(os.path.join(MEM, f), encoding='utf-8').read(1200)
        m = re.search(r'^name:\s*(\S+)', head, re.M)
        if not m:
            mismatch.append((f, '(name: が無い)'))
        elif m.group(1).replace('-', '_') != f[:-3].replace('-', '_'):
            mismatch.append((f, m.group(1)))
    if mismatch:
        problems.append(f"frontmatter の name とファイル名が違う: {len(mismatch)} 本")
        for f, n in mismatch[:10]:
            notes.append(f"    {f}  →  name: {n}")

    # --- 3. どの索引にも載っていない -------------------------------------
    idx_text = ''
    for f in os.listdir(MEM):
        if is_index(f):
            idx_text += open(os.path.join(MEM, f), encoding='utf-8').read()
    orphans = [f for f in sorted(os.listdir(MEM))
               if f.endswith('.md') and not is_index(f) and ('(%s)' % f) not in idx_text]
    if orphans:
        problems.append(f"どの索引にも載っていないメモリ: {len(orphans)} 本")
        for f in orphans[:10]:
            notes.append(f"    {f}")

    # --- 4. MEMORY.md の大きさ -------------------------------------------
    mp = os.path.join(MEM, 'MEMORY.md')
    raw = open(mp, 'rb').read()
    size = len(raw)
    longs = [l for l in raw.decode('utf-8').split('\n')
             if l.startswith('- [') and len(l.encode('utf-8')) > LIMIT_LINE]
    if size > LIMIT_BYTES:
        problems.append(f"MEMORY.md が上限超過: {size} バイト（上限 {LIMIT_BYTES}）")
    elif size > 20000:
        notes.append(f"    △ MEMORY.md {size} バイト（上限 {LIMIT_BYTES} に接近）")
    if longs:
        notes.append(f"    △ {LIMIT_LINE}バイト超の索引行 {len(longs)} 本（MEMORY.md）")

    # --- 出力 -------------------------------------------------------------
    n_files = len([f for f in os.listdir(MEM) if f.endswith('.md') and not is_index(f)])
    n_index = len([f for f in os.listdir(MEM) if is_index(f)])
    print(f"記録の巡回 ── メモリ {n_files} 本 / 索引 {n_index} 枚 / MEMORY.md {size} バイト")
    if not problems:
        print("OK  ズレは見つかりませんでした")
        for n in notes:
            print(n)
        return 0
    for p in problems:
        print(f"NG  {p}")
    for n in notes:
        print(n)
    print()
    print("直し方: 本文を直したら、同じ commit で索引の現在地も1行だけ差し替える。")
    print("        → memory/feedback_memory_index_hygiene.md")
    return 1


def beat(result, message):
    """⚙️自動処理レジスタへ心拍を打つ。★処理名は完全一致（1文字違うと黙って失敗する）"""
    hb = os.path.expanduser('~/.vivid-relay/heartbeat.py')
    if not os.path.exists(hb):
        print('（心拍は打てない: heartbeat.py が無い）')
        return
    subprocess.run(['/usr/bin/python3', hb, '記録の巡回（memory_audit.py）', result, message])

if __name__ == '__main__':
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main()
    body = buf.getvalue()
    print(body, end='')
    if '--beat' in sys.argv:
        first = [l for l in body.split('\n') if l.startswith(('OK', 'NG'))]
        beat('成功' if rc == 0 else '警告',
             (first[0] if first else '結果不明')[:180])
    sys.exit(rc)
