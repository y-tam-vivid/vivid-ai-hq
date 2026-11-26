"""2026-11-26 dry-run。台帳の値は当日 00_企業マスタ から読んだ実物。事実の取り出しは mini では Haiku が行う部分を人手（クラウドの Claude）で代行した。
python3 dryrun_20261126.py  → 表を出すだけ。シートには書かない。"""
import datetime as dt

import update_proposal as up

NOW = dt.datetime(2026, 11, 26, 10, 0)

CASES = [
    dict(
        title="10/29 面談 大畑海太氏（人生の代理店）",
        ctx=up.Context("議事録の仕分け", "https://docs.google.com/document/d/1_f2sLRdGGQn_db0NC_3zBYAiGo5OYLrk/edit",
                       "B-0408", "大畑海太", "人生の代理店(個人事業主)", sensitive_flag=""),
        ledger={"会社名": "人生の代理店(個人事業主)", "URL": "", "備考": "", "事業ライン": "", "サービス種別": "",
                "都道府県": "", "関係区分_顧客": "FALSE", "関係区分_パートナー": "FALSE", "関係区分_見込み客": "TRUE"},
        facts=[
            up.Fact("URL", "https://hp.life-agencypro.com/", "AI要約「人生の代理店：https://hp.life-agencypro.com/」"),
            up.Fact("備考", "紹介制プラットフォーム「人生の代理店」を運営。利用者 約200人（2026-10時点）",
                    "「8月時点の約100人から約200人に増加した」"),
            up.Fact("関係区分_パートナー", "TRUE", "福祉施設と医師をつなぐ紹介を相互に行う関係（4名の紹介を受ける）"),
        ],
    ),
    dict(
        title="11/21 現場 MIKKE HOUSE（機微の疑いあり）",
        ctx=up.Context("議事録の仕分け", "https://docs.google.com/document/d/16sJx1adcOpftZtQ9hmasE4nEYLzzYXjq/edit",
                       "B-0415", "", "体験型 児童発達支援・放課後等デイサービス MIKKE HOUSE",
                       sensitive_flag="通報・運営指導への不安や職員の対応に関する内容が含まれる"),
        ledger={"会社名": "体験型 児童発達支援・放課後等デイサービス MIKKE HOUSE", "都道府県": "", "市区町村": "",
                "事業ライン": "福祉施設", "サービス種別": "", "備考": ""},
        facts=[
            up.Fact("都道府県", "大阪府", "「大阪市の電子申請システムが停止しており、紙での提出」＝指定権者が大阪市"),
            up.Fact("市区町村", "大阪市", "同上（所在地の区までは議事録に無い）"),
            up.Fact("サービス種別", "児童発達支援・放課後等デイサービス（多機能型）", "「自発とこでいいと…保育所等訪問」"),
            up.Fact("事業ライン", "福祉施設", "（台帳と同じ）"),
        ],
    ),
]


def show(rows):
    if not rows:
        print("  提案 0件")
        return
    fill = [r for r in rows if r[up.COL["種別"]] == up.TYPE_FILL]
    print(f"  提案 {len(rows)}件（［まとめて反映］の対象 {len(fill)}件／1件ずつ見る {len(rows) - len(fill)}件）")
    for r in rows:
        print(f"   - {r[up.COL['項目']]}｜現在「{r[up.COL['現在の値']]}」→ 提案「{r[up.COL['提案する値']]}」"
              f"｜{r[up.COL['確度']]}｜{r[up.COL['種別']]}｜根拠 {r[up.COL['根拠']][:40]}")


for c in CASES:
    print(f"\n■ {c['title']}  社内顧客ID {c['ctx'].customer_id}")
    print(" 〔いまの規則：機微の疑いがある議事録は丸ごと提案しない〕")
    show(up.build_rows(c["ctx"], c["ledger"], c["facts"], NOW))
    if c["ctx"].sensitive_flag:
        open_ctx = up.Context(**{**c["ctx"].__dict__, "sensitive_flag": ""})
        safe = [f for f in c["facts"] if f.column != "備考"]
        print(" 〔仮に：機微の議事録でも、所在地など機微でない列だけは提案する〕")
        show(up.build_rows(open_ctx, c["ledger"], safe, NOW))

print("\n■ 11/19 商談 パワーカーゴ／11/12 面談 本田：社内顧客IDが空（台帳未登録）→ 比べる相手が無く提案 0件")
