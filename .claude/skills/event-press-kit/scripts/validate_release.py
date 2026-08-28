#!/usr/bin/env python3
"""
validate_release.py - プレスリリース原稿を MARK N式8ステップで検証する

研修で示された作法を機械判定に落としたもの。人が見落としやすい点を先に潰す。

使い方:
  python3 validate_release.py release.json [--json]

入力JSONの例:
{
  "タイトル": "...",
  "自社紹介": "...",
  "世の中ごと": {"本文": "...", "出典": ["https://..."]},
  "自社ごと": {"本文": "...", "顧客の声": ["..."]},
  "詳細": "...",
  "今後の展開": "...",
  "会社概要": "...",
  "問い合わせ先": {"担当": "", "電話": "", "メール": ""},
  "画像": ["メイン画像", "会場写真", "体験の様子"],
  "配信種別": "事前告知"
}
"""
import argparse, json, re, sys

# 売り込み表現。これが入るとPRではなく広告になり、報道につながらない
SALES_WORDS = ['業界最安', '最安値', 'No.1', 'ナンバーワン', '日本初', '世界初', '唯一',
               '絶対', '最高の', '大好評', 'お得', '格安', '他社より', 'おすすめ',
               '話題の', '大人気', '今すぐ', 'ぜひご購入']
# 業界用語・硬い表現。テレビは分かりやすさを重視する
JARGON_HINT = ['ソリューション', 'スキーム', 'シナジー', 'アセット', 'コミット',
               'ステークホルダー', 'ローンチ', 'イノベーティブ']
REQUIRED = ['タイトル', '自社紹介', '世の中ごと', '自社ごと', '詳細',
            '今後の展開', '会社概要', '問い合わせ先']


def text_of(v):
    if isinstance(v, dict):
        return ' '.join(str(x) for x in v.values() if isinstance(x, str))
    if isinstance(v, list):
        return ' '.join(str(x) for x in v)
    return str(v or '')


def has_number(s):
    return bool(re.search(r'\d', s))


def validate(r):
    err, warn, ok = [], [], []
    body_all = ' '.join(text_of(r.get(k)) for k in REQUIRED)

    for k in REQUIRED:
        if not text_of(r.get(k)).strip():
            err.append(f'8ステップの構成要素が欠けています: {k}')

    # --- 1. タイトル（最重要） ---
    title = str(r.get('タイトル', ''))
    if title:
        if not has_number(title):
            warn.append('タイトルに数字が入っていません。インパクトのある数字データを入れると効果的です')
        else:
            ok.append('タイトルに数字あり')
        if len(title) > 70:
            warn.append(f'タイトルが{len(title)}字あります。2行で端的にまとめてください（目安60字前後）')
        elif len(title) < 15:
            warn.append(f'タイトルが{len(title)}字と短すぎます。何を伝えたいかが不明確になります')
        else:
            ok.append(f'タイトル{len(title)}字（適正範囲）')

    # --- 3. 世の中ごと（統計の裏付け） ---
    yononaka = r.get('世の中ごと', {})
    sources = yononaka.get('出典', []) if isinstance(yononaka, dict) else []
    if not sources:
        warn.append('世の中ごとに出典URLがありません。記者が裏取りする手間を減らすため、'
                    '統計データや官公庁の資料へのリンクを添えてください')
    else:
        ok.append(f'世の中ごとの出典 {len(sources)}件')

    # --- 4. 自社ごと（絶対数と比率、顧客の声） ---
    jisha = r.get('自社ごと', {})
    jisha_body = text_of(jisha)
    has_ratio = bool(re.search(r'\d+\s*[%％]|\d+\s*倍|昨対|前年同月比', jisha_body))
    has_abs = bool(re.search(r'\d{2,}\s*(人|組|件|名|万円|円|社|校)', jisha_body))
    if has_ratio and has_abs:
        ok.append('自社ごとに絶対数と比率の両方あり')
    elif has_ratio:
        warn.append('自社ごとに比率はありますが絶対数が見当たりません。両方を併記してください')
    elif has_abs:
        warn.append('自社ごとに絶対数はありますが比率（前年比・達成率）が見当たりません')
    else:
        warn.append('自社ごとに具体的な数字がありません。取材時に必ず確認される項目です')

    voices = jisha.get('顧客の声', []) if isinstance(jisha, dict) else []
    if not voices:
        warn.append('顧客・参加者の声がありません。メディアが視聴者の共感を得るために'
                    '必ず取材する要素なので、あらかじめ載せると取材の手間を省けます')
    else:
        ok.append(f'顧客の声 {len(voices)}件')

    # --- 5. 詳細（ファクトのみ・売り込み禁止） ---
    found_sales = sorted({w for w in SALES_WORDS if w in body_all})
    if found_sales:
        err.append(f'売り込み表現が含まれています: {", ".join(found_sales)}。'
                   'PRは公共性が命なので、事実情報のみで構成してください')
    else:
        ok.append('売り込み表現なし')

    found_jargon = sorted({w for w in JARGON_HINT if w in body_all})
    if found_jargon:
        warn.append(f'業界用語が含まれています: {", ".join(found_jargon)}。'
                    'テレビは分かりやすい表現を求めます')

    # --- 会社名・代表名の過度な露出 ---
    company = str(r.get('会社概要', ''))
    m = re.search(r'(株式会社[^\s、。］\]]+|[^\s、。］\]]+株式会社|NPO法人[^\s、。］\]]+)', company)
    if m:
        name = m.group(1)
        cnt = body_all.count(name)
        if cnt >= 5:
            warn.append(f'社名「{name}」が本文中に{cnt}回出ています。'
                        '社名や代表名の過度な押し出しは敬遠されます')

    # --- 8. 問い合わせ先 ---
    contact = r.get('問い合わせ先', {})
    if isinstance(contact, dict):
        if not str(contact.get('電話', '')).strip():
            err.append('問い合わせ先に電話番号がありません。取材依頼は急に来るため必須です')
        if not str(contact.get('担当', '')).strip():
            warn.append('問い合わせ先の担当者名がありません')

    # --- 画像 ---
    imgs = r.get('画像', [])
    if len(imgs) < 3:
        warn.append(f'画像が{len(imgs)}点です。メディアは複数枚から選ぶため3点以上を推奨します')
    else:
        ok.append(f'画像 {len(imgs)}点')

    # --- 実施報告版の追加チェック ---
    if r.get('配信種別') == '実施報告':
        if not re.search(r'\d+\s*(人|組|名)', body_all):
            err.append('実施報告なのに来場実績の数字がありません。'
                       'ニュース性が落ちるぶん、数字が唯一の武器になります')
        if '今後' not in text_of(r.get('今後の展開')):
            warn.append('実施報告では「次回開催」「継続実施」など前向きな発表があると通りやすくなります')
    return err, warn, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('release'); ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    r = json.load(open(a.release, encoding='utf-8'))
    err, warn, ok = validate(r)
    if a.json:
        print(json.dumps({'errors': err, 'warnings': warn, 'passed': ok},
                         ensure_ascii=False, indent=2))
        sys.exit(1 if err else 0)
    print(f'=== プレスリリース検証（{r.get("配信種別","種別未設定")}）===\n')
    for label, items, mark in (('要修正', err, '×'), ('確認推奨', warn, '!'), ('適合', ok, '○')):
        if items:
            print(f'■ {label}')
            for x in items: print(f'  {mark} {x}')
            print()
    print('判定:', '配信不可' if err else ('要確認' if warn else '配信可'))
    sys.exit(1 if err else 0)


if __name__ == '__main__':
    main()
