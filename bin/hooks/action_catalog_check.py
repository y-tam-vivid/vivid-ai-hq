#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""行為カタログの3点突合（Layer2・2026-08-29 ビビ依頼②）

なぜ要るか
  action_catalog.json（Layer1）に載せただけでは「実在するか」「動いているか」は分からない。
  穴A（self_audit.pyがログの実在を誤って『まだ稼働していない』と言い続けた）と同じ事故を、
  この検問自身が起こさないよう、判定コードのパスは各実装ファイルから import して取る
  （文字列で再定義しない）。

3点
  ① カタログの各行 → settings.json（またはcrontab／daily_jobs.conf）に実在するか
  ② 実在するなら → ログ実体が直近24hに動いているか（mtime基準）
  ③ ログパスは実装ファイルの LOG 定数を import して取得する（穴Aの型を作らない）
     ★ log_module が null のエントリ（LOG定数が無い／未確認）は「判定不能」として扱う。
     ★ cron 系（log_file_hint）は crontab のリダイレクト出力であり、対象スクリプト自身は
       LOG定数を持たない。ここだけは import で取れないため、カタログJSON内の文字列を
       正本として扱う（二重管理リスクとして明記。crontabの記述を変えたらここも直すこと）。

★このスクリプトは cron / daily_jobs へ登録しない（ビビの依頼どおり実装と実測まで）。

使い方
  python3 bin/hooks/action_catalog_check.py            一覧表示
  python3 bin/hooks/action_catalog_check.py --json      JSON出力（findings_tracker連携用）
"""
import argparse
import datetime
import importlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CATALOG = os.path.join(HERE, 'action_catalog.json')
STALE_HOURS = 24


def load_catalog():
    return json.load(open(CATALOG, encoding='utf-8'))


def _settings():
    try:
        return json.load(open(os.path.expanduser('~/.claude/settings.json'), encoding='utf-8'))
    except Exception:
        return None


def _crontab_text():
    try:
        r = subprocess.run(['crontab', '-l'], capture_output=True, text=True, timeout=10)
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''


def _daily_jobs_text():
    p = os.path.join(os.path.dirname(HERE), 'daily_jobs.conf')
    try:
        return open(p, encoding='utf-8').read()
    except Exception:
        return ''


def check_registration(action, settings, crontab_text, daily_jobs_text):
    """① 実在確認。戻り値: (bool, detail_str)"""
    reg = action.get('registration', {})
    typ = reg.get('type')

    if typ == 'settings_hook':
        if settings is None:
            return False, 'settings.jsonを読めない'
        event = reg.get('event')
        substr = reg.get('command_substr')
        hooks_for_event = settings.get('hooks', {}).get(event, [])
        blob = json.dumps(hooks_for_event, ensure_ascii=False)
        found = substr in blob
        return found, ('settings.json hooks.%s に実在' % event) if found else \
            ('settings.json hooks.%s に無い' % event)

    if typ == 'cron':
        substr = reg.get('command_substr')
        found = substr in crontab_text
        return found, 'crontabに実在' if found else 'crontabに無い'

    if typ == 'daily_jobs_conf':
        substr = reg.get('command_substr')
        found = substr in daily_jobs_text
        return found, 'daily_jobs.confに実在' if found else 'daily_jobs.confに無い'

    if typ == 'settings_permission':
        if settings is None:
            return False, 'settings.jsonを読めない'
        path = reg.get('path', '')
        substr = reg.get('pattern_substr', '')
        node = settings
        for key in path.split('.'):
            node = node.get(key, {}) if isinstance(node, dict) else {}
        blob = json.dumps(node, ensure_ascii=False)
        found = substr in blob
        return found, ('%s に実在' % path) if found else ('%s に無い' % path)

    if typ == 'code_path':
        # ★実在確認の自動化はスコープ外（呼び出し関係の静的解析が要る）。判定不能として扱う。
        return None, '判定方法未実装（code_pathタイプ）'

    return None, '未知のregistration.type: %s' % typ


def check_log_activity(action):
    """② ログが直近24hに動いているか。③ パスはimportで取る（cron系のみ文字列を正本にする）。
    戻り値: (bool_or_None, detail_str)
    """
    log_module = action.get('log_module')
    log_attr = action.get('log_attr')
    log_file_hint = action.get('log_file_hint')

    log_path = None
    source = None
    if log_module and log_attr:
        try:
            mod = importlib.import_module(log_module)
            log_path = getattr(mod, log_attr)
            source = 'import %s.%s' % (log_module, log_attr)
        except Exception as e:
            return None, 'import失敗: %s' % e
    elif log_file_hint:
        log_path = os.path.expanduser(log_file_hint)
        source = 'catalog記載の文字列（cron系・importで取れない既知の限界）'
    else:
        return None, 'ログパス不明（log_module/log_file_hintとも無い）'

    if not os.path.exists(log_path):
        return False, '%s（%s）が存在しない' % (log_path, source)

    age_h = (datetime.datetime.now().timestamp() - os.path.getmtime(log_path)) / 3600.0
    active = age_h <= STALE_HOURS
    return active, '%s（%s）最終更新 %.1f時間前' % (log_path, source, age_h)


def run_all():
    catalog = load_catalog()
    settings = _settings()
    crontab_text = _crontab_text()
    daily_jobs_text = _daily_jobs_text()

    results = []
    for action in catalog['actions']:
        reg_ok, reg_detail = check_registration(action, settings, crontab_text, daily_jobs_text)
        if reg_ok:
            log_ok, log_detail = check_log_activity(action)
        else:
            log_ok, log_detail = None, '登録が無いため未確認'
        results.append({
            'id': action['id'],
            'name': action['name'],
            'registered': reg_ok,
            'registration_detail': reg_detail,
            'log_active': log_ok,
            'log_detail': log_detail,
        })
    return results


def track_problems(results):
    """Layer3：登録なし／ログ非活性のものを findings_tracker へ渡して streak 化する。
    ★判定不能（None）は問題として扱わない（誤検知を避ける。分からないものを『壊れている』
    と報告しない、の原則どおり）。"""
    sys.path.insert(0, HERE)
    from findings_tracker import track
    texts = []
    for r in results:
        if r['registered'] is False:
            texts.append('%s（%s）が未登録：%s' % (r['id'], r['name'], r['registration_detail']))
        elif r['registered'] is True and r['log_active'] is False:
            texts.append('%s（%s）は登録済みだがログが停止：%s' % (r['id'], r['name'], r['log_detail']))
    return track('action_catalog', texts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--track', action='store_true',
                     help='Layer3: 問題をfindings_trackerへ記録する（cron専用ではない・手動実行可）')
    args = ap.parse_args()

    results = run_all()

    if args.track:
        tracked = track_problems(results)
        if not tracked:
            print('★問題なし（記録対象0件）')
        else:
            for t in tracked:
                print('記録: %s（streak %d日）' % (t['text'], t['streak_days']))
        return

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    for r in results:
        reg_mark = {True: '✓', False: '✗', None: '？'}[r['registered']]
        log_mark = {True: '✓', False: '✗', None: '？'}[r['log_active']]
        print('[%s登録 %sログ] %s ： %s' % (reg_mark, log_mark, r['id'], r['name']))
        print('    登録: %s' % r['registration_detail'])
        print('    ログ: %s' % r['log_detail'])


if __name__ == '__main__':
    main()
