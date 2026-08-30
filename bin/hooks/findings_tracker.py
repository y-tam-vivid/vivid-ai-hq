#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指摘が「消えた」のか「対応された」のかを区別する ── 小さな指摘台帳

なぜ要るか（2026-08-29 ドーベルマン実測・つる memory/reference_a_warning_nobody_owns.md）
  heartbeat_names_check.py の「登録漏れ： intake_notify.py」が8/25-27の3日連続で
  出ていたのに拾われなかった。notion_backfill.py の「区分待ち43件」は6日間1件も
  減らなかったのに rc=0・心拍「成功」のまま報告され続けた。
  **検査は正しく動いていた。指摘も正しかった。誰も拾わなかった。**

  ★正しく鳴っているのに拾われない問題と、鳴らなさすぎて拾われない問題は同じ根を持つ。
  「警告が消えた」ことを「直った」の証拠にしない。**消すのは以下の2通りだけ**：
    ① 別の検査が実体で直ったことを確認した
    ② 人がフラグを立てて明示的にクリアした
  それ以外（次回の実行に出てこなかった）は、台帳には残したまま "open" を false にするだけ。
  「機械が拾えなくなった」可能性を消さない。

使い方（呼び出し元のスクリプトから import）
    from findings_tracker import track
    result = track('ledger_report', alerts)   # alerts は文字列のリスト
    for r in result:
        if r['streak_days'] >= 3:
            print('★%d日連続 ： %s' % (r['streak_days'], r['text']))

  ★件数を含む文字列（「重複の要判断が16組」等）は、件数が変わるたびに別の指摘に
    見えてしまう。数字を # に正規化したキーで同一の指摘として連続日数を追う
    （生テキストは表示用にそのまま保持する）。

CLI（人が明示的にクリアする・②の経路）
    python3 findings_tracker.py --list                 いま開いている指摘を一覧
    python3 findings_tracker.py --clear "<key>" --note "対応済み"

★このファイル自体は読み書きするのは open_findings.json だけ。
  台帳（Sheets・Notion・kintone）へは一切触らない。
"""
import argparse
import datetime
import json
import os
import re
import sys

STATE = os.path.expanduser('~/.vivid-relay/open_findings.json')
NUM = re.compile(r'\d+')


def _normalize(text):
    """数字を # に伏せて、指摘の「種類」を安定的に識別するキーにする"""
    return NUM.sub('#', str(text)).strip()


def _load():
    try:
        return json.load(open(STATE, encoding='utf-8'))
    except Exception:
        return {}


def _save(d):
    """★原子的置換。並列サブエージェントからの同時書き込みでも壊れないようにする
    （hook_inject_memory.py の landmine_shown.json と同じ対処）"""
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        tmp = STATE + '.tmp.%d' % os.getpid()
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(tmp, STATE)
    except Exception:
        pass


def track(source, current_texts):
    """
    source          呼び出し元の名前（例 'ledger_report' 'self_audit'）
    current_texts   今回出ている指摘（alerts）の生テキストのリスト

    戻り値: [{"key","text","first_seen","last_seen","streak_days","is_new"}, ...]
      current_texts と同じ順序・同じ件数で返す。
    ★このターン出てこなかった過去の指摘は消さず、台帳の中で open=false にするだけ。
    """
    today = datetime.date.today().isoformat()
    state = _load()
    seen_keys = set()
    out = []

    for text in current_texts or []:
        norm = _normalize(text)
        key = '%s::%s' % (source, norm)
        seen_keys.add(key)
        rec = state.get(key)
        if rec is None:
            rec = {
                'source': source,
                'key': norm,
                'first_seen': today,
                'last_seen': today,
                'last_text': text,
                'streak_days': 1,
                'open': True,
                'cleared_by_human': False,
                'cleared_note': '',
            }
            is_new = True
        else:
            is_new = False
            # ★人がクリア済みなのに同じ指摘がまた出た＝再発。streak をリセットして再度追う
            if rec.get('cleared_by_human'):
                rec['first_seen'] = today
                rec['streak_days'] = 1
                rec['cleared_by_human'] = False
                rec['cleared_note'] = ''
            elif rec.get('last_seen') != today:
                # 連続日数の判定：前回記録の翌日以降なら継続とみなす（cron頻度に依存しない
                # 簡易ロジック。1日以上空いていても「まだ続いている」として数える。
                # ★逆に厳密な「毎日連続」を要求すると、cronが1回スキップしただけで
                #   streak が切れて「慢性化した警告」を見失う → 緩め側に倒す）
                rec['streak_days'] = rec.get('streak_days', 1) + 1
            rec['last_seen'] = today
            rec['last_text'] = text
            rec['open'] = True
        state[key] = rec
        out.append({
            'key': key,
            'text': text,
            'first_seen': rec['first_seen'],
            'last_seen': rec['last_seen'],
            'streak_days': rec['streak_days'],
            'is_new': is_new,
        })

    # 今回出てこなかった、同じ source の過去の指摘は open=false にするだけ（消さない）
    for k, rec in state.items():
        if rec.get('source') != source:
            continue
        if k in seen_keys:
            continue
        if rec.get('open'):
            rec['open'] = False
            rec['closed_seen_last'] = today

    _save(state)
    return out


def clear(key, note=''):
    """★人が明示的にクリアする経路（②）。self_audit.py 等が勝手に呼んではいけない。"""
    state = _load()
    if key not in state:
        return False
    state[key]['cleared_by_human'] = True
    state[key]['cleared_note'] = note
    state[key]['open'] = False
    _save(state)
    return True


def open_findings(min_streak_days=0):
    """いま open な指摘（streak_days >= min_streak_days）を新しい順で返す

    ★2026-08-31 修正（ビビが実物のopen_findings.jsonを読んで発見した欠陥）：
      track() の戻り値は 'text' というキー名を使うが（docstring 19-24行目の使用例参照）、
      保存データ（この関数が返す各行の実体）は 'last_text' というキー名しか持っていなかった。
      ＝ track() の戻り値の形式を期待して 'text' キーで読むと、保存データ側には存在しない
      ため常に None になる（"中身が空"に見える）。呼び出し側（ledger_report.py 等）も
      track() 側の保存（_save 内の rec['last_text'] = text）も、どちらも正しく動作していた
      ── 2経路で実測して裏取り済み：
        経路1: ~/.vivid-relay/open_findings.json を直接読み last_text に中身があることを確認
        経路2: findings_tracker.py --list（CLI）で中身が正しく表示されることを確認
      欠陥は「保存」ではなく「2つの異なるキー名を持つインターフェースが並立していたこと」。
    ★対処：ここで 'text' キー（'last_text' の複製）を動的に追加し、どちらのキー名でも
      読めるようにする。保存データ自体（open_findings.json）は変更しない（二重管理を避け、
      正本は last_text のまま・text は読み出し時に複製するだけ）。
      dict(v) でコピーしてから追加する（元の state 辞書を書き換えない）。
    """
    state = _load()
    rows = [dict(v) for v in state.values()
            if v.get('open') and v.get('streak_days', 0) >= min_streak_days]
    rows.sort(key=lambda r: -r.get('streak_days', 0))
    for r in rows:
        r['text'] = r.get('last_text', '')
    return rows


def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--clear')
    ap.add_argument('--note', default='')
    args = ap.parse_args()

    if args.clear:
        ok = clear(args.clear, args.note)
        print('クリアしました' if ok else '★該当キーが見つかりません： %s' % args.clear)
        return

    rows = open_findings()
    if not rows:
        print('開いている指摘はありません')
        return
    for r in rows:
        print('%3d日連続  [%s] %s' % (r.get('streak_days', 0), r.get('source'), r.get('last_text')))


if __name__ == '__main__':
    _main()
