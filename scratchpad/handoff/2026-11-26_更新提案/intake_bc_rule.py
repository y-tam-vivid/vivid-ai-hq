"""受付シート→台帳の登録で「B（法人）／C（個人）のどちらで発番するか」を決める規則（intake_register.py から import する）

2026-11-26 有璽氏「Aでやろうかな」＝ 商材が空・「まだ分からない」でも、会社名に法人格があれば B で発番する。
  ・商材から決まるときは今までどおり商材で決める（この部品は「決まらないとき」だけ口を出す）
  ・法人格が無ければ今までどおり止める。★止めた理由は受付シートの社内メモへ書く（いまは心拍の件数にしか出ていない）
  ・人の入力欄（商材）には何も書き足さない（B-0473 で「商材欄に印を足して通した」やり方はやめる）
"""
from __future__ import annotations

import re
import unicodedata

UNDECIDED = {"", "まだ分からない", "その他"}

LEGAL_FORMS = [
    "株式会社", "有限会社", "合同会社", "合資会社", "合名会社",
    "一般社団法人", "公益社団法人", "一般財団法人", "公益財団法人",
    "特定非営利活動法人", "NPO法人", "社会福祉法人", "医療法人", "学校法人", "宗教法人",
    "税理士法人", "弁護士法人", "行政書士法人", "社会保険労務士法人", "司法書士法人", "監査法人",
    "事業協同組合", "協同組合",
]
LEGAL_ABBR = re.compile(r"\((株|有|合|同)\)|㈱|㈲|\b(inc|llc|ltd|co\.,?\s*ltd)\b\.?", re.I)

# 相手として拾ってはいけない名前（自社・仮の名前）。この名前の行は B でも C でも発番しない
NOT_A_COUNTERPART = re.compile(r"^(未登録|不明|社内)$|ビビッド|有璽")


def _n(s: str) -> str:
    return unicodedata.normalize("NFKC", str(s or "")).strip()


def legal_form(company: str) -> str:
    c = _n(company)
    for w in LEGAL_FORMS:
        if w in c:
            return w
    m = LEGAL_ABBR.search(c)
    return m.group(0) if m else ""


def decide_by_company(company: str, person: str, shohin: str) -> tuple[str | None, str]:
    """商材で決まらない行について (B / None, 理由) を返す。商材で決まる行には None と空の理由を返す（呼び出し側の既存処理に任せる）"""
    s = _n(shohin)
    if re.sub(r"\(to[BC]\)", "", s, flags=re.I).strip() not in UNDECIDED:
        return None, ""
    c = _n(company)
    if not c:
        return None, "【登録を止めた】商材が決まっておらず、会社名も空のため B/C を決められない。商材か会社名を埋めてください"
    if NOT_A_COUNTERPART.search(c):
        return None, f"【登録を止めた】会社名「{c}」は相手の名前ではない（自社・仮の名前）。相手を直してください"
    form = legal_form(c)
    if form:
        return "B", f"商材が未定のため、会社名の法人格「{form}」から B で発番（2026-11-26 規則A）"
    return None, (f"【登録を止めた】商材が「{s or '空'}」で、会社名「{c}」に法人格が無いため B/C を決められない。"
                  "商材を選ぶか、法人なら会社名に法人格を入れてください")
