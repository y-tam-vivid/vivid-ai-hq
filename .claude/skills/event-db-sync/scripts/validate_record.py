#!/usr/bin/env python3
"""
validate_record.py - Notion起票前のレコード検証

イベントレコード（JSON）を受け取り、以下を機械的に判定する。
  1. 必須項目の充足
  2. 「推測してはいけない項目」の空欄検出
  3. 日付の整合性（初日 <= 最終日、過去日付の警告）
  4. 重複照合に使うべき固有キーワードの抽出

使い方:
  python3 validate_record.py record.json
  python3 validate_record.py record.json --json   # 機械可読な結果を返す

入力JSONの例:
{
  "イベント名": "◯◯フェア2026",
  "開催初日": "2026-09-12",
  "最終日": "2026-09-13",
  "開催時間": "10:00-17:00",
  "会場": "◯◯センター 北館1F ホールA",
  "所在地": "大阪市北区",
  "自社の立場": "主催",
  "参加費": "無料",
  "予約": "不要",
  "主催者・共催者": "株式会社◯◯",
  "ターゲット": ["親子"],
  "投稿先アカウント": ["公式"],
  "ステータス": "開催決定"
}
"""
import argparse, json, re, sys
from datetime import date, datetime

REQUIRED = ['イベント名', '開催初日', 'ステータス']

# 埋まっていなければ必ずユーザーに確認する項目（推測で埋めてはいけない）
MUST_CONFIRM = {
    '会場': '正式表記を階層・区画まで確認する',
    '参加費': '無料/有料は告知の信頼性に直結する',
    '予約': '要否を誤ると当日トラブルになる',
    '自社の立場': '主催/共催/出展/協力/後援を誤ると関係先に失礼',
    '主催者・共催者': '併記が必要な名称と表記を確認する',
}

VALID_STATUS = ['企画中', '開催決定', '告知中', '開催中', '終了', '振り返り済']
VALID_STANCE = ['主催', '共催', '出展', '協力', '後援', '視察']

# 重複照合クエリに使うべきでない汎用語（複数イベントに登場しやすい）
GENERIC = {'イベント', 'フェア', '祭', 'まつり', '体験', '見学', '相談会', '説明会',
           '教室', 'ワークショップ', 'セミナー', '展示', '発表', '会', '春', '夏', '秋', '冬'}


def parse_d(s):
    try:
        return datetime.strptime(str(s)[:10], '%Y-%m-%d').date()
    except Exception:
        return None


def distinctive_terms(rec):
    """重複照合に有効な固有キーワードを抽出する。
    同名イベントの別年度と衝突しないよう、固有名詞寄りの語を優先する。"""
    src = ' '.join(str(rec.get(k, '')) for k in ('イベント名', '会場', '主催者・共催者'))
    src = re.sub(r'[（）()【】\[\]「」、。,./|]', ' ', src)
    terms = []
    for w in src.split():
        w = w.strip()
        if len(w) < 2 or w in GENERIC:
            continue
        if re.fullmatch(r'[0-9]{2,4}年?', w):  # 年号単体は除外
            continue
        terms.append(w)
    seen, out = set(), []
    for t in terms:
        if t not in seen:
            seen.add(t); out.append(t)
    return out[:4]


def validate(rec):
    errors, warns, confirms = [], [], []

    for k in REQUIRED:
        if not str(rec.get(k, '')).strip():
            errors.append(f'必須項目が空です: {k}')

    st = rec.get('ステータス')
    if st and st not in VALID_STATUS:
        errors.append(f'ステータスの値が不正です: {st}（許容: {" / ".join(VALID_STATUS)}）')
    sc = rec.get('自社の立場')
    if sc and sc not in VALID_STANCE:
        errors.append(f'自社の立場の値が不正です: {sc}（許容: {" / ".join(VALID_STANCE)}）')

    for k, why in MUST_CONFIRM.items():
        if not str(rec.get(k, '')).strip():
            confirms.append(f'{k} … {why}')

    s, e = parse_d(rec.get('開催初日')), parse_d(rec.get('最終日'))
    if rec.get('開催初日') and not s:
        errors.append('開催初日が YYYY-MM-DD 形式ではありません')
    if rec.get('最終日') and not e:
        errors.append('最終日が YYYY-MM-DD 形式ではありません')
    if s and e and e < s:
        errors.append('最終日が開催初日より前です')
    if s:
        d = (s - date.today()).days
        if d < 0 and st in ('企画中', '開催決定', '告知中'):
            warns.append(f'開催初日が過去です（{-d}日前）。ステータスが「{st}」のままです')
        elif 0 <= d < 14 and st in ('企画中', '開催決定'):
            warns.append(f'開催まで{d}日です。プレスリリースの推奨リードタイム（2週間以上前）を割っています')

    if len(distinctive_terms(rec)) < 2:
        warns.append('重複照合に使える固有語が少ないです。日本語は空白で区切られないため自動抽出に限界があります。'
                     '会場名・主催者名・開催年など固有の語を手動で足して検索してください')

    tm = str(rec.get('開催時間', ''))
    if tm and not re.fullmatch(r'\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}', tm):
        warns.append(f'開催時間の形式が想定外です: {tm}（例 10:00-17:00）')

    return errors, warns, confirms


def main():
    p = argparse.ArgumentParser()
    p.add_argument('record')
    p.add_argument('--json', action='store_true')
    a = p.parse_args()
    rec = json.load(open(a.record, encoding='utf-8'))
    errors, warns, confirms = validate(rec)
    terms = distinctive_terms(rec)

    if a.json:
        print(json.dumps({'errors': errors, 'warnings': warns,
                          'confirm_required': confirms, 'dedup_terms': terms},
                         ensure_ascii=False, indent=2))
        sys.exit(1 if errors else 0)

    print(f'=== 検証: {rec.get("イベント名", "(名称未設定)")} ===\n')
    if errors:
        print('■ エラー（起票不可）')
        for x in errors: print(f'  × {x}')
        print()
    if confirms:
        print('■ ユーザー確認が必要（推測で埋めない）')
        for x in confirms: print(f'  ? {x}')
        print()
    if warns:
        print('■ 警告')
        for x in warns: print(f'  ! {x}')
        print()
    print('■ 重複照合クエリ候補（この語でイベントDBを検索してから起票する）')
    print(f'  {" ".join(terms) if terms else "(固有語を抽出できず。手動で指定すること)"}')
    print()
    print('判定:', '起票不可' if errors else ('確認後に起票可' if confirms else '起票可'))
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
