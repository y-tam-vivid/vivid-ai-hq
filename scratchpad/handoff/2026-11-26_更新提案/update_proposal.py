"""顧客情報の「更新提案」── 判定と書き込みの共通部品（mini の meeting_sort.py / intake_register.py から import する）

設計の正本: Notion「顧客情報の更新提案（AIが台帳を更新する仕組み）の設計」4237b1568b5781098f2bd876d3f41e63
置き場: 受付シート 1XCqGDG1kUMg6Mh0xUfWzudqvG_PyLcNpJNJKuszyJe0 の「更新提案」タブ（A〜Q・見出し1行目）

★この部品はシートへの読み書きを自分で持たない。呼び出し側の sheets クライアントを
  `SheetIO`（get / update / append の3つ）として渡す。mini の sheets_client に合わせて薄い包みを書くこと。

守るルール（設計4章）
  1. 確定の値を推定で上書きしない ── 「書き換え×推定」は 種別=要確認のみ・提案する値=空（候補は根拠へ）
  2. 同じ顧客・同じ項目に未処理の提案があれば、新しい行を作らず根拠を追記する
  3. 「書き換え」は必ず1件ずつ確認 ──［まとめて反映］が○にするのは「空欄を埋める」だけ
  4. 機微（健康・家族・決済）は提案に含めない ── 議事録の「機微の疑い」が空でなければ1件も作らない＋値の語彙でも弾く
  5. 台帳へ書くのは 確認=○ かつ 反映=未 の行だけ。書く直前に現在値が提案時と同じかを確かめる（違えば失敗にして書かない）
"""
from __future__ import annotations

import datetime as _dt
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable, Protocol

SHEET = "更新提案"
HEADERS = ["提案日時", "提案元", "出典URL", "社内顧客ID", "相手のお名前", "会社・団体名", "対象シート",
           "項目", "現在の値", "提案する値", "根拠", "確度", "種別", "確認", "反映", "反映日時", "社内メモ"]
COL = {h: i for i, h in enumerate(HEADERS)}

# 第1段階の対象（設計2章）。01_顧客詳細・02_個人マスタは列の確認後に足す（★未確認のまま足さない）
ALLOWED = {
    "00_企業マスタ": ["会社名かな", "法人番号", "電話番号", "都道府県", "市区町村", "住所", "URL",
                      "事業ライン", "サービス種別", "備考"],
}
# 選択肢がある列（90_選択肢マスタ 2026-11-26 実測）。ここに無い値は「要確認のみ」に落とす（値の散らばりを作らない）
OPTIONS = {
    "事業ライン": {"福祉施設", "補助金・助成金", "toC"},
    "サービス種別": {"放課後等デイサービス", "児童発達支援", "就労継続支援A型", "就労継続支援B型", "就労移行支援", "その他"},
}
# 人が決める列。提案は「要確認のみ」でしか出さない（値は台帳へ入れない）
CONFIRM_ONLY = {"関係区分_顧客", "関係区分_パートナー", "関係区分_見込み客"}
# 何があっても提案しない列
NEVER = {"社内顧客ID", "最新ステータス", "担当", "kintone登録状況", "kintoneレコード番号", "kintone突合方法",
         "カスタマーID", "作成日", "更新日", "電話番号_正規化"}

SENSITIVE_RE = re.compile(r"病|障害者手帳|通院|服薬|診断|妊娠|離婚|家族|子ども|子供|夫|妻|借金|債務|破産|"
                          r"口座|クレジット|カード番号|暗証|給与|年収")

OK_MARK = "○ 反映する"
NG_MARK = "× 反映しない"
HOLD_MARK = "保留"
TYPE_FILL, TYPE_REWRITE, TYPE_CONFIRM = "空欄を埋める", "書き換え", "要確認のみ"
SURE, GUESS = "確定", "推定"


class SheetIO(Protocol):
    def get(self, rng: str) -> list[list[str]]: ...
    def update(self, rng: str, values: list[list[str]]) -> None: ...
    def append(self, rng: str, values: list[list[str]]) -> None: ...


@dataclass
class Fact:
    """議事録などから取り出した1項目。certainty は 確定（名刺・登記・公式サイト）／推定（本人申告・紹介者談・AI調査）"""
    column: str
    value: str
    evidence: str          # 出典の抜粋（50字程度に切る）
    certainty: str = GUESS


@dataclass
class Context:
    source: str            # 提案元（議事録の仕分け／紹介面談スキル／名刺読み取り／手入力）
    source_url: str
    customer_id: str
    person: str = ""
    company: str = ""
    sheet: str = "00_企業マスタ"
    sensitive_flag: str = ""   # 議事録DBの「機微の疑い」。空でなければ何も提案しない


def norm(s: str) -> str:
    """比較用。全角半角・空白・電話のハイフン・URL末尾スラッシュの違いを同じ値とみなす"""
    s = unicodedata.normalize("NFKC", str(s or "")).strip()
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[-‐－―ー]", "-", s) if re.fullmatch(r"[\d\-‐－―ー()]+", s) else s
    if re.fullmatch(r"[\d\-()]+", s):
        s = re.sub(r"\D", "", s)
    if s.startswith("http"):
        s = s.rstrip("/").replace("http://", "https://")
    return s.lower()


def classify(column: str, current: str, fact: Fact) -> tuple[str, str] | None:
    """(種別, 提案する値) を返す。提案不要なら None"""
    if column in NEVER:
        return None
    if norm(current) == norm(fact.value):
        return None
    if column in CONFIRM_ONLY:
        return TYPE_CONFIRM, ""
    if column in OPTIONS and fact.value not in OPTIONS[column]:
        return TYPE_CONFIRM, ""
    if not str(current or "").strip():
        return TYPE_FILL, fact.value
    if fact.certainty == SURE:
        return TYPE_REWRITE, fact.value
    return TYPE_CONFIRM, ""            # ルール1：書き換え×推定は値を入れない


def build_rows(ctx: Context, ledger_row: dict[str, str], facts: Iterable[Fact],
               now: _dt.datetime | None = None) -> list[list[str]]:
    """台帳の現在値（列名→値）と取り出した事実を比べ、追記すべき行を作る（重複の吸収は merge_pending で）"""
    if ctx.sensitive_flag.strip():
        return []
    allowed = set(ALLOWED.get(ctx.sheet, [])) | CONFIRM_ONLY
    stamp = (now or _dt.datetime.now()).strftime("%Y/%m/%d %H:%M")
    rows = []
    for f in facts:
        if f.column not in allowed or not str(f.value or "").strip() and f.column not in CONFIRM_ONLY:
            continue
        if SENSITIVE_RE.search(f"{f.value} {f.evidence}"):
            continue
        current = ledger_row.get(f.column, "")
        got = classify(f.column, current, f)
        if not got:
            continue
        kind, value = got
        evidence = f.evidence[:60]
        if kind == TYPE_CONFIRM and f.value and f.column not in CONFIRM_ONLY:
            why = "選択肢に無い値" if f.column in OPTIONS and f.value not in OPTIONS[f.column] else "推定での書き換え"
            evidence = f"候補「{f.value}」（{why}のため値は入れない）／{evidence}"
        row = [""] * len(HEADERS)
        row[COL["提案日時"]] = stamp
        row[COL["提案元"]] = ctx.source
        row[COL["出典URL"]] = ctx.source_url
        row[COL["社内顧客ID"]] = ctx.customer_id
        row[COL["相手のお名前"]] = ctx.person
        row[COL["会社・団体名"]] = ctx.company
        row[COL["対象シート"]] = ctx.sheet
        row[COL["項目"]] = f.column
        row[COL["現在の値"]] = str(current or "")
        row[COL["提案する値"]] = value
        row[COL["根拠"]] = evidence
        row[COL["確度"]] = f.certainty
        row[COL["種別"]] = kind
        row[COL["反映"]] = "未"
        rows.append(row)
    return rows


def is_pending(r: list[str]) -> bool:
    r = r + [""] * (len(HEADERS) - len(r))
    return r[COL["反映"]] == "未" and not r[COL["確認"]].startswith("×")


def merge_pending(existing: list[list[str]], new_rows: list[list[str]]):
    """ルール2。戻り値 (追記する行, [(既存の行番号(1始まり), 新しい根拠)])"""
    index = {}
    for i, r in enumerate(existing, start=2):   # existing は見出しを除いた2行目から
        r = r + [""] * (len(HEADERS) - len(r))
        if is_pending(r):
            index[(r[COL["社内顧客ID"]], r[COL["対象シート"]], r[COL["項目"]])] = (i, r)
    to_append, to_annotate = [], []
    for n in new_rows:
        key = (n[COL["社内顧客ID"]], n[COL["対象シート"]], n[COL["項目"]])
        if key in index:
            i, old = index[key]
            add = f"{n[COL['提案日時']]} {n[COL['根拠']]}（{n[COL['出典URL']]}）"
            if add not in old[COL["根拠"]]:
                to_annotate.append((i, f"{old[COL['根拠']]}\n＋{add}"))
        else:
            to_append.append(n)
    return to_append, to_annotate


def bulk_ok_targets(rows: list[tuple[int, list[str]]]) -> list[int]:
    """［まとめて反映］で ○ にしてよい行番号。ルール3：空欄を埋める だけ"""
    out = []
    for i, r in rows:
        r = r + [""] * (len(HEADERS) - len(r))
        if is_pending(r) and not r[COL["確認"]] and r[COL["種別"]] == TYPE_FILL:
            out.append(i)
    return out


def answer_to_mark(answer: str) -> str:
    """Slack の答え → 「確認」列の値"""
    return {"ok": OK_MARK, "ng": NG_MARK, "hold": HOLD_MARK}[answer]


@dataclass
class ApplyResult:
    written: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def plan_apply(proposals: list[list[str]], ledger: dict[str, dict[str, str]]):
    """intake_register 用。確認=○ かつ 反映=未 の行ごとに (行番号, 動作, 値, メモ) を返す。書き込みは呼び出し側。
    動作: write（台帳へ書く）／done_no_write（要確認のみ＝台帳へは書かず済にする）／fail（書かない）"""
    plans = []
    for i, r in enumerate(proposals, start=2):
        r = r + [""] * (len(HEADERS) - len(r))
        if not (r[COL["確認"]].startswith("○") and r[COL["反映"]] == "未"):
            continue
        cid, col, kind = r[COL["社内顧客ID"]], r[COL["項目"]], r[COL["種別"]]
        if kind == TYPE_CONFIRM:
            plans.append((i, "done_no_write", "", "要確認のみ＝台帳へは書いていない（人が値を決めて手で直す）"))
            continue
        if col in NEVER or col in CONFIRM_ONLY or col not in ALLOWED.get(r[COL["対象シート"]], []):
            plans.append((i, "fail", "", f"対象外の項目「{col}」"))
            continue
        row = ledger.get(cid)
        if row is None:
            plans.append((i, "fail", "", f"台帳に {cid} が無い"))
            continue
        if norm(row.get(col, "")) != norm(r[COL["現在の値"]]):
            plans.append((i, "fail", "", f"提案後に台帳の値が変わった（今：{row.get(col, '')}）。提案を作り直す"))
            continue
        if kind == TYPE_REWRITE and r[COL["確度"]] != SURE:
            plans.append((i, "fail", "", "書き換え×推定は台帳へ入れない（ルール1）"))
            continue
        plans.append((i, "write", r[COL["提案する値"]], ""))
    return plans
