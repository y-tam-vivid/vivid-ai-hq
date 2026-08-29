#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同じ事実が複数ファイルに書かれ、片方だけ古くなっているものを見つける ── 検出専用（直さない）

なぜ要るか（2026-08-29 ピタゴラス・有璽氏依頼）
  > 「言ったことがちゃんと通ってなくて、上書きもされてなくて、っていう状態を憂いている。
  >   それが解消される術は実行して。」

  実例（ロビンの検問なし洗い出し⑳「訂正を全箇所へ伝播させる」に対応する事故）:
    2026-08-27 20:35:48  WORKING.md「prefecture/address で絞り込める」
    2026-08-27 20:36:56  memory本文「都道府県だけでは足りない。市区町村まで要る」（68秒後の訂正）
    → memory側は直ったが、WORKING.md側は2日間そのまま残った。

★これは検出専用ツール。何も書き換えない。台帳・Notion・kintoneには一切触らない。
  対象は memory/*.md ・ WORKING.md ・ .claude/skills/**/*.md（ローカルmarkdownのみ）。

★見つけられる型・見つけられない型（誤検知率は実データで測定し、報告に明記すること）
  見つけられる
    ① 数字の不一致 ── 同じ固有名詞(ファイル名等)に「62列」「61列」のように
       異なる数字+単位(列/件/行/本/名)が複数ファイルでついている
    ② 伝播漏れの疑い ── 同じ固有名詞を含む行が複数ファイルにあり、
       一方が明らかに新しく(git blame日時)、かつその新しい方の文に
       「訂正/実は/ではなく/足りない/誤り/直した/判明」等の訂正語が含まれる
  見つけられない（原理的な限界）
    ・意味は同じだが表現が違う訂正（固有名詞の共有が無いと検出できない）
    ・数字を伴わない事実の食い違い（①の対象外）
    ・訂正語を使わずに書き換えられた訂正（②で拾えない）
    ・1ファイル内で完結した訂正（複数ファイルに跨っていないので対象外）
  → **「全部見つけられる」ツールではない。人の目を代替しない。候補を絞るだけ。**

使い方
  python3 stale_copy_finder.py                 レポートを標準出力へ
  python3 stale_copy_finder.py --json out.json  同内容をJSONでも保存

出し方
  誤検知が多いと読まれなくなる（memory/reference_delivered_but_unread.md）。
  ★このツール単体では「確定」ではなく「候補」として出す。人が最終判断する。

★非決定的なツール（ステラ検査 2026-08-29 指摘1・重要）
  git blame の結果はリポジトリの状態が変わるたびに変わる。同じコードでも実行するたびに
  件数が変動する。**「N件中M件が真陽性」という実測値を固定の確定値としてmemoryへ書かない。**
  必ず実行日時とセットで書き、「その時点の実測」であることを明記すること。
  実測記録（2026-08-29）：
    ピタゴラス実行時点   数字不一致7件・伝播漏れ2件（計9件）・真陽性1件
    ステラ再検査時点     数字不一致7件・伝播漏れ3件（計10件）・真陽性1件（同一）
    ★git blameの参照先コミットが実行のたびに動くため件数が変わった（直近に関連コミット複数あり）。
    真陽性の総数（1件＝`.claude/skills/cross-check/SKILL.md:138`「フック3本」）は両者で一致。

★既知の誤検知源（ステラ検査 指摘2・ブロッカーにしないが記録する）
  CORRECTION_MARKERS の1〜2文字の短い語（特に「逆」「不要」等）が、無関係な文脈の
  部分一致で誤爆する（例:「件数はそこから逆算」の「逆」、「申請不要」の「不要」）。
  改修するなら、短いマーカーは前後の文字種（助詞等）で境界を取るか、3文字以上の
  マーカーを優先するなどの精度向上余地がある。今回は誤検知率が実測10%程度と分かった
  うえで「手動確認の候補リスト」という位置づけに留めているため、未対応のまま残す。
"""
import argparse
import json
import os
import re
import subprocess
import sys

REPO = os.path.expanduser('~/vivid-ai-hq')

TARGET_GLOBS = [
    'memory',            # *.md（_archive は除外）
    '.',                 # WORKING.md 単体
    '.claude/skills',    # **/*.md
]

FILENAME_RE = re.compile(
    r'[A-Za-z0-9_ぁ-んァ-ヶ一-龠][A-Za-z0-9_ぁ-んァ-ヶ一-龠\-]{2,60}'
    r'\.(?:py|md|sh|gs|json|csv|xlsx|ts|js|html|txt)')

NUM_UNIT_RE = re.compile(r'(\d{1,6})\s*(列|件|行|本|名|日|社|人)')

CORRECTION_MARKERS = [
    '訂正', '実は', 'ではなく', '足りない', '不要', '廃止', '誤り', '誤って',
    '直した', '変わった', '判明', '更新済み', '古い', '★訂正', '違った',
    '間違い', 'だけでは', '逆', '覆った', '取り消',
]

# 汎用すぎて誤検知源になるもの（自己言及的に全ファイルへ現れる基盤ファイル名）
# ★実測（2026-08-29）：初版はこれらを除外せず、単純な「同一行内の共起」で数字を拾った結果、
#   51件中ほぼ全件が誤検知だった（同じ文中の無関係な数字を同じ主語に紐づけていたため）。
STOPWORDS = {
    'README.md', 'CLAUDE.md', 'MEMORY.md', 'WORKING.md', 'SKILL.md',
    'settings.json', 'settings.local.json',
}

PROXIMITY_CHARS = 20  # 数字+単位トークンがファイル名トークンの前後この文字数以内なら「同じ主語」とみなす
MIN_BASENAME_LEN = 5  # 短すぎる基底名（誤爆源）を除外


def _collect_files():
    files = []
    # memory/*.md（_archive を除く）
    memdir = os.path.join(REPO, 'memory')
    for name in os.listdir(memdir):
        if name.endswith('.md') and not name.startswith('_'):
            files.append(os.path.join(memdir, name))
    # WORKING.md
    wf = os.path.join(REPO, 'WORKING.md')
    if os.path.exists(wf):
        files.append(wf)
    # .claude/skills/**/*.md
    skdir = os.path.join(REPO, '.claude', 'skills')
    for root, _dirs, names in os.walk(skdir):
        for name in names:
            if name.endswith('.md'):
                files.append(os.path.join(root, name))
    return sorted(set(files))


def _read_lines(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.readlines()
    except Exception:
        return []


def _blame_date(path, lineno):
    """git blame で該当行の最終更新日時を取る（取れなければ None）"""
    try:
        rel = os.path.relpath(path, REPO)
        out = subprocess.run(
            ['git', 'blame', '-L', '%d,%d' % (lineno, lineno),
             '--date=iso-strict', '--', rel],
            cwd=REPO, capture_output=True, text=True, timeout=15).stdout
        m = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', out)
        return m.group(1) if m else None
    except Exception:
        return None


def _basename_ok(fname):
    base = fname.rsplit('.', 1)[0]
    return len(base) >= MIN_BASENAME_LEN


def _extract(files):
    """file -> [(lineno, text, fname_spans, numunit_spans)]
    fname_spans  = [(name, start, end), ...]
    numunit_spans = [(num, unit, start, end), ...]
    """
    per_file = {}
    for path in files:
        lines = _read_lines(path)
        rows = []
        for i, raw in enumerate(lines, start=1):
            text = raw.rstrip('\n')
            fname_spans = [
                (m.group(0), m.start(), m.end())
                for m in FILENAME_RE.finditer(text)
                if m.group(0) not in STOPWORDS and _basename_ok(m.group(0))
            ]
            numunit_spans = [
                (m.group(1), m.group(2), m.start(), m.end())
                for m in NUM_UNIT_RE.finditer(text)
            ]
            if fname_spans or numunit_spans:
                rows.append((i, text, fname_spans, numunit_spans))
        per_file[path] = rows
    return per_file


def find_numeric_mismatches(per_file):
    """同じファイル名トークン＋同じ単位で、数字が食い違う候補。
    ★数字は「ファイル名トークンの近傍（PROXIMITY_CHARS文字以内）」にあるものだけを
      その主語の数字とみなす（同じ文中の無関係な数字を拾わないため。実測で必須と判明）。
    ★ 2つ以上の異なるファイルに跨って出てくるものだけを候補にする
      （同一ファイル内の言及だけなら「伝播漏れ」ではなく単なる筆者の書き間違いの領域）。
    """
    # key = (filename_token, unit) -> set of (number, path, lineno, text)
    index = {}
    for path, rows in per_file.items():
        for lineno, text, fname_spans, numunit_spans in rows:
            for fname, fs, fe in fname_spans:
                for num, unit, ns, ne in numunit_spans:
                    gap = max(fs - ne, ns - fe, 0)
                    if gap > PROXIMITY_CHARS:
                        continue
                    index.setdefault((fname, unit), set()).add(
                        (num, path, lineno, text))
    out = []
    for (fname, unit), occ in index.items():
        nums = {o[0] for o in occ}
        files_involved = {o[1] for o in occ}
        if len(nums) > 1 and len(files_involved) >= 2:
            out.append({
                'subject': fname,
                'unit': unit,
                'occurrences': [
                    {'number': o[0], 'file': os.path.relpath(o[1], REPO),
                     'line': o[2], 'text': o[3]}
                    for o in sorted(occ, key=lambda x: (x[1], x[2]))
                ],
            })
    return sorted(out, key=lambda x: x['subject'])


def find_propagation_gaps(per_file, min_gap_days=1):
    """同じファイル名トークンが複数ファイルにあり、新しい方に訂正語があるが
    古い方には無い候補"""
    # key = filename_token -> list of (path, lineno, text)
    index = {}
    for path, rows in per_file.items():
        for lineno, text, fname_spans, _numunit_spans in rows:
            for fname, _fs, _fe in fname_spans:
                index.setdefault(fname, []).append((path, lineno, text))

    out = []
    for fname, occ in index.items():
        if len(occ) < 2:
            continue
        dated = []
        for path, lineno, text in occ:
            d = _blame_date(path, lineno)
            dated.append({'path': path, 'lineno': lineno, 'text': text, 'date': d})
        dated = [d for d in dated if d['date']]
        if len(dated) < 2:
            continue
        dated.sort(key=lambda x: x['date'])
        newest = dated[-1]
        has_marker = any(m in newest['text'] for m in CORRECTION_MARKERS)
        if not has_marker:
            continue
        matched = 0
        for older in dated[:-1]:
            if matched >= 3:
                break  # ★同じ主語に対する大量の旧言及で埋もれないよう上位3件まで
            if older['path'] == newest['path']:
                continue  # 同一ファイル内の自己言及（訂正の地の文）は対象外
            if older['date'] >= newest['date']:
                continue
            gap_days = (_iso_to_epoch(newest['date']) - _iso_to_epoch(older['date'])) / 86400.0
            if gap_days < min_gap_days:
                continue
            if any(m in older['text'] for m in CORRECTION_MARKERS):
                continue  # 古い方にも訂正語があるなら伝播漏れではなく単なる言及
            matched += 1
            out.append({
                'subject': fname,
                'gap_days': round(gap_days, 1),
                'newer': {
                    'file': os.path.relpath(newest['path'], REPO),
                    'line': newest['lineno'], 'text': newest['text'],
                    'date': newest['date'],
                },
                'older_possibly_stale': {
                    'file': os.path.relpath(older['path'], REPO),
                    'line': older['lineno'], 'text': older['text'],
                    'date': older['date'],
                },
            })
    return sorted(out, key=lambda x: -x['gap_days'])


def _iso_to_epoch(iso):
    import datetime
    return datetime.datetime.fromisoformat(iso).timestamp()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', help='JSON出力先パス（任意）')
    ap.add_argument('--min-gap-days', type=float, default=1.0)
    args = ap.parse_args()

    files = _collect_files()
    per_file = _extract(files)
    numeric = find_numeric_mismatches(per_file)
    prop = find_propagation_gaps(per_file, min_gap_days=args.min_gap_days)

    print('=== ① 数字の不一致候補（同じ固有名詞に異なる数字+単位） ===')
    print('%d 件' % len(numeric))
    for item in numeric:
        print('- %s（%s）' % (item['subject'], item['unit']))
        for o in item['occurrences']:
            print('    %s:%d  %s%s  「%s」' % (
                o['file'], o['line'], o['number'], item['unit'], o['text'].strip()[:80]))

    print()
    print('=== ② 伝播漏れの疑い（新しい方に訂正語があり、古い方には無い） ===')
    print('%d 件' % len(prop))
    for item in prop:
        print('- %s（差 %.1f日）' % (item['subject'], item['gap_days']))
        n = item['newer']
        o = item['older_possibly_stale']
        print('    新: %s:%d [%s]  「%s」' % (n['file'], n['line'], n['date'], n['text'].strip()[:80]))
        print('    旧(要確認): %s:%d [%s]  「%s」' % (o['file'], o['line'], o['date'], o['text'].strip()[:80]))

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump({'numeric_mismatches': numeric, 'propagation_gaps': prop},
                       f, ensure_ascii=False, indent=2)
        print('\nJSON: %s' % args.json)

    return 0


if __name__ == '__main__':
    sys.exit(main())
