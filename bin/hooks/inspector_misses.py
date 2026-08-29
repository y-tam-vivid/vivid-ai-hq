#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""検査役の見落とし記録 ── findings_tracker の薄いラップ（2026-08-29 ステラ設計・優先度3）

なぜ要るか
  検査役（ステラ・つる・センゴク・ナミ）が「載せてよい」と判定した対象に、
  後から欠陥が見つかることがある。これは検査役個人の能力の話ではなく、
  「この検査役はこの型を構造的に見落とす」というパターンを可視化するための道具。
  週次で 検査役×型 に集計し、同じ組み合わせが2回出たらそれを明示して回す。

★新しい保存形式は作らない。findings_tracker.py の open_findings.json をそのまま使う
  （source='inspector_miss'。キーは「検査役:型」を軸にした短い文字列にする）。

使い方
  記録   python3 inspector_misses.py --record --inspector ステラ --type "誤検知率の未実測" --detail "..."
  一覧   python3 inspector_misses.py --list
  週次   python3 inspector_misses.py --weekly

★cross-check/SKILL.md への追記が要る場面（今回のスコープでは発生していない）
  もし将来この道具の運用ルールを cross-check/SKILL.md へ足す必要が出たら、
  .claude/skills/ 配下は Edit/Write が拒否される壁がある
  （memory/reference_permissions_are_part_of_the_environment.md 参照）。
  その場合は bin/apply_targets_md_replacement.sh と同じ型
  （① バックアップ ② _pending_*.md を用意 ③ 有璽氏が1回スクリプトを叩く）で畳むこと。
  この inspector_misses.py 自体は bin/hooks/ 配下なのでその壁には当たらない。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from findings_tracker import track, open_findings  # noqa: E402


def record(inspector, miss_type, detail):
    """1件記録する。戻り値は findings_tracker.track() の結果（1件目）。"""
    key_hint = '%s:%s' % (inspector, miss_type)
    text = '%s（%s）' % (key_hint, detail) if detail else key_hint
    result = track('inspector_miss', [text])
    return result[0] if result else None


def weekly_report(min_streak=2):
    """検査役×型 が min_streak 日以上にわたって記録され続けている組み合わせを
    『構造的な見落とし』として返す。

    ★2026-08-29 実測で設計ミスを発見・修正した経緯（隠さず記録する）：
    当初は open_findings() の重複排除済みデータを『検査役:型』文字列でカウントする
    設計だったが、findings_tracker.track() は同じキーを同日に何度呼んでも
    レコードが1件に集約される（streak_daysは日次カウントのため）ため、
    「2回以上」が原理的に検出できなかった（意図的に2回recordして実測し、
    weekly_reportが0件を返すバグを確認した）。
    ★正しい軸は「累計呼び出し回数」ではなく「streak_days（何日にわたって
    繰り返し発生しているか）」。findings_tracker本来の設計（日をまたいで
    同じキーが再度trackされたらstreak_daysが伸びる）をそのまま使う。
    """
    rows = [r for r in open_findings(min_streak_days=min_streak)
            if r.get('source') == 'inspector_miss']
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--record', action='store_true')
    ap.add_argument('--inspector', help='検査役の名前（例: ステラ）')
    ap.add_argument('--type', dest='miss_type', help='見落としの型（例: 誤検知率の未実測）')
    ap.add_argument('--detail', default='', help='詳細（任意）')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--weekly', action='store_true')
    args = ap.parse_args()

    if args.record:
        if not args.inspector or not args.miss_type:
            print('★--inspector と --type は必須です')
            sys.exit(1)
        r = record(args.inspector, args.miss_type, args.detail)
        print('記録しました:', r)
        return

    if args.list:
        rows = [r for r in open_findings(min_streak_days=0) if r.get('source') == 'inspector_miss']
        if not rows:
            print('inspector_miss の記録はまだありません')
            return
        for r in rows:
            print('%3d日連続 | %s' % (r.get('streak_days', 0), r.get('last_text')))
        return

    if args.weekly:
        all_rows = [r for r in open_findings(min_streak_days=0) if r.get('source') == 'inspector_miss']
        structural = weekly_report(min_streak=2)
        print('inspector_miss 累計 %d件（open状態）' % len(all_rows))
        if structural:
            print('★構造的な見落とし（2日以上にわたって繰り返し記録された組み合わせ）:')
            for r in structural:
                print('  %3d日連続 | %s' % (r.get('streak_days', 0), r.get('last_text')))
        else:
            print('構造的な見落としパターンは無い（2日以上の連続記録なし）')
        return

    ap.print_help()


if __name__ == '__main__':
    main()
