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

★保留（park）── 2026-09-05 有璽氏の判断で新設。「クリア」とは別物
  クリア（clear）  もう出なくてよい。直った／対応した
  保留（park）     ★問題は残っている。人が「いまは対応しない」と決めただけ
                   → 警告からは外す。★台帳からは消さない・連続日数も伸ばさない
                   → 誰が・いつ・なぜ・どうすれば再開するか を必ず一緒に持つ

  なぜ clear で済ませないか ── clear は「対応した」の意味で使われており、
  cleared_by_human=True は「再発したら streak を1から数え直す」挙動を持つ。
  保留は対応していないので、clear で消すと **記録が「対応済み」に化ける**。
  ★消さずに状態で表す（fukuchi-core）。だから別のフラグにした。

    python3 findings_tracker.py --list-parked
    python3 findings_tracker.py --park "<key>" --reason "..." --by "有璽氏" --resume "..."
    python3 findings_tracker.py --unpark "<key>"      ★これ1回で毎朝の警告へ戻る

  ★期限（自動復活）は入れていない。2026-09-05 に有璽氏が3案から
    「期限なしで保留にする」を選んだため（受付番号 #5bbcb0・17:26）。
    日付での自動復活が要るなら、その決定を取り直してから足すこと。

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

# ★2026-09-03 ピタゴラス追加（ビビ依頼・findings_escalate.py が要求する系統分離）。
#   系統A ＝ 業務データの指摘（人の判断が要る＝有璽氏のDMへ上げてよい）
#   系統B ＝ 仕組みの自己点検の指摘（self_audit.py の役割内。DMへは上げない）
#   ★未登録の source は 'B'（＝findings_escalate.py が拾わない側）へ倒す（category_of() 参照）。
#   ★2026-09-03 ステラ検査・条件③：この「B」は"安全側"ではなく"サイレント側"と呼ぶのが正確。
#     "安全"と呼べるのは findings_escalate.py（系統Aだけを人へ自動エスカレーションする
#     スクリプト）が実際に稼働している前提のときだけ。その前提はいま崩れている
#     （findings_escalate.py は daily_jobs/cron に未登録＝走っていない。WORKING.mdの
#     該当ブロック参照）。前提が崩れていてもいなくても、Bへ落ちた指摘は
#     findings_escalate.py に拾われない＝有璽氏へは自動では届かない、という事実は変わらない。
#   ★新しい source を SOURCE_CATEGORY へ足すときは、必ずこの辞書へ明示的に登録すること。
#     登録を忘れると、その source の指摘は黙って 'B'（サイレント側）へ落ち、
#     誰にも自動では届かなくなる（本人はエスカレーションされていることを期待していても）。
SOURCE_CATEGORY = {
    'ledger_report': 'A',
    'action_catalog': 'B',
    'inspector_miss': 'B',
    'single_route_claim': 'B',
}


def category_of(source):
    """source の系統を返す。未登録の source は 'B'（＝findings_escalate.py が
    拾わない・人へは自動で届かないサイレント側）に倒す。上のSOURCE_CATEGORY直前の
    コメント参照。新しい source を足すときはSOURCE_CATEGORYへの登録を忘れないこと。"""
    return SOURCE_CATEGORY.get(source, 'B')


def _normalize(text):
    """数字を # に伏せて、指摘の「種類」を安定的に識別するキーにする"""
    return NUM.sub('#', str(text)).strip()


PARK_FIELD = 'parked'   # rec['parked'] = {'reason','by','at','resume'}


def _key_of(source, text):
    """呼び出し元が生テキストしか持っていなくても台帳のキーを引けるようにする"""
    return '%s::%s' % (source, _normalize(text))


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
            if rec.get(PARK_FIELD):
                # ★保留中（park）── まだ出ているという事実だけを更新する。
                #   ・streak_days は伸ばさない（人が「いまは対応しない」と決めただけで、
                #     放置日数を積み上げても意味が無い）
                #   ・open へ戻さない（＝毎朝の警告にも findings_escalate にも乗らない）
                #   ・last_seen は更新する（★更新しないと「今日は出なかった」に見え、
                #     保留と「直った」の区別がつかなくなる）
                #   戻すのは unpark() だけ。
                rec['last_seen'] = today
                rec['last_text'] = text
            else:
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
            'parked': rec.get(PARK_FIELD),
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


def parked_info(source, text):
    """その指摘が保留中なら {'reason','by','at','resume'} を返す。でなければ None。
    ★呼び出し元は生テキストのまま渡してよい（内部で _normalize する）。"""
    rec = _load().get(_key_of(source, text))
    if not rec:
        return None
    return rec.get(PARK_FIELD) or None


def is_parked(source, text):
    return parked_info(source, text) is not None


def park(key, reason='', by='', resume=''):
    """★人が「いまは対応しない」と決めた指摘を、警告から外す（台帳からは消さない）。

    clear() との違いは docstring 冒頭の表のとおり。★cleared_by_human は立てない
    ── 立てると記録が「対応済み」に化け、再発時の streak リセット挙動まで付いてくる。
    戻り値 True/False（キーが台帳に無ければ False）。"""
    state = _load()
    if key not in state:
        return False
    state[key][PARK_FIELD] = {
        'reason': reason,
        'by': by,
        'at': datetime.date.today().isoformat(),
        'resume': resume or ('python3 findings_tracker.py --unpark "%s"' % key),
    }
    # ★open を落とすのは「自動エスカレーション（findings_escalate.py）の入口から外す」ため。
    #   open_findings() は open=True しか返さない。表示は parked_findings() で別に取る。
    state[key]['open'] = False
    _save(state)
    return True


def unpark(key):
    """保留を解除する。★これ1回で毎朝の警告へ戻る（他に触る場所は無い）。
    open はここでは True に戻さない ── 次回 track() が実際にその指摘を再検出したときに
    True へ戻る。ここで戻すと、既に直っているものまで警告へ復活させてしまう。"""
    state = _load()
    if key not in state or not state[key].get(PARK_FIELD):
        return False
    state[key].pop(PARK_FIELD, None)
    _save(state)
    return True


def parked_findings():
    """いま保留中の指摘（連続日数の多い順）。★画面に出すためのもの。黙って消さない。"""
    rows = [dict(v) for v in _load().values() if v.get(PARK_FIELD)]
    rows.sort(key=lambda r: -r.get('streak_days', 0))
    for r in rows:
        r['text'] = r.get('last_text', '')
    return rows


def open_findings(min_streak_days=0, category=None, include_parked=False):
    """いま open な指摘（streak_days >= min_streak_days）を新しい順で返す

    ★2026-09-03 ピタゴラス追加：category 引数（'A' / 'B' / None）。
      None（既定）なら従来どおり全件を返す＝★後方互換を壊さない
      （dashboard_data.py・dashboard_build.py・ledger_report.py・inspector_misses.py・
      self_audit.py はいずれも category を渡さずに呼んでおり、挙動は変わらない）。
      'A' か 'B' を渡すと category_of(r['source']) がそれと一致する行だけに絞る。

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

    ★2026-09-05 追加：include_parked（既定 False）。保留（park）にした指摘は返さない。
      park() 側で open=False にしているので既に返らないが、**二重に落とす**（片方の実装が
      将来変わっても、保留が黙って警告へ復活しないようにするため）。
      保留中のものを見たいときは parked_findings() を使う。
    """
    state = _load()
    rows = [dict(v) for v in state.values()
            if v.get('open') and v.get('streak_days', 0) >= min_streak_days]
    if not include_parked:
        rows = [r for r in rows if not r.get(PARK_FIELD)]
    if category is not None:
        rows = [r for r in rows if category_of(r.get('source')) == category]
    rows.sort(key=lambda r: -r.get('streak_days', 0))
    for r in rows:
        r['text'] = r.get('last_text', '')
    return rows


def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--clear')
    ap.add_argument('--note', default='')
    ap.add_argument('--category', choices=['A', 'B'], default=None,
                     help='系統で絞り込む（A=業務データ／B=仕組みの自己点検）。'
                          '省略時は従来どおり全件')
    ap.add_argument('--list-parked', action='store_true')
    ap.add_argument('--park')
    ap.add_argument('--unpark')
    ap.add_argument('--reason', default='')
    ap.add_argument('--by', default='')
    ap.add_argument('--resume', default='')
    args = ap.parse_args()

    if args.park:
        ok = park(args.park, reason=args.reason, by=args.by, resume=args.resume)
        print('保留にしました（★台帳からは消していません）' if ok
              else '★該当キーが見つかりません： %s' % args.park)
        return

    if args.unpark:
        ok = unpark(args.unpark)
        print('保留を解除しました。次回の検出から警告へ戻ります' if ok
              else '★保留中ではありません： %s' % args.unpark)
        return

    if args.list_parked:
        rows = parked_findings()
        if not rows:
            print('保留中の指摘はありません')
            return
        for r in rows:
            pk = r.get(PARK_FIELD) or {}
            print('⏸ %3d日連続  [%s] %s' % (r.get('streak_days', 0), r.get('source'),
                                             r.get('last_text')))
            print('    理由 %s ／ 決めた人 %s ／ %s' % (pk.get('reason', ''), pk.get('by', ''),
                                                        pk.get('at', '')))
            print('    戻すには %s' % pk.get('resume', ''))
        return

    if args.clear:
        ok = clear(args.clear, args.note)
        print('クリアしました' if ok else '★該当キーが見つかりません： %s' % args.clear)
        return

    rows = open_findings(category=args.category)
    if not rows:
        print('開いている指摘はありません')
        return
    for r in rows:
        print('%3d日連続  [%s] %s' % (r.get('streak_days', 0), r.get('source'), r.get('last_text')))


if __name__ == '__main__':
    _main()
