#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""レガシー17分類 → 部門軸アーカイブ の仕分け（段1=機械／段2=Haiku／段3=人）

  python3 drive_sort.py --cat 08_契約・法務              提案を作る（動かさない）
  python3 drive_sort.py --cat 08_契約・法務 --apply      提案どおりに動かす（ログを残す）

★段1（AIを使わない）で決まるものは段2へ流さない
★段2は Haiku だけ（--model haiku）。迷ったら上位へ上げず _要判断 へ
★機微（個人名・処分・診断・給与）はモデルに関係なく規則で _機微 へ寄せる
★日付は ①名前の中の日付 ②中身の日付 ③作成日(birthtime) の順。更新日は使わない
"""
import os, re, sys, json, subprocess, unicodedata as u, datetime, argparse, zipfile, hashlib

B = "/Users/yujimac/Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com/マイドライブ"
ARC = B + "/Downloads書類アーカイブ"
DEP = B + "/00_部門軸アーカイブ"
nfc = lambda s: u.normalize("NFC", s)

# ── ★`claude -p` を呼ぶときの隔離（2026-10-15 実測で分かった地雷）────────────
#   claude -p は★呼び出し元のフックと出力スタイルを子プロセスへ引き継ぐ。
#   そのため（1）UserPromptSubmit が子の入口へ文を差し込み、Haiku が仕分けではなく
#   その文（Slackの回答・書き戻しの催促）に答える （2）outputStyle: Fable Style が
#   「結論先行の説明文」を書かせ、★JSONが返らない。
#   実測 ── cwd=リポジトリ内 100.9秒でフックへの返答／cwd=/tmp 76.5秒で説明文／
#           ★下の隔離 30.9秒で `{"区分": 1, "理由": "test"}` だけ
#   ＝ フックと出力スタイルを切り、★リポジトリの外から呼ぶ。
CLAUDE_ISO_DIR = os.path.join(os.path.expanduser("~"), ".vivid-relay", "_claude_iso")
CLAUDE_ISO_SETTINGS = os.path.join(CLAUDE_ISO_DIR, "settings.json")


def _iso():
    """隔離用の settings.json を用意して (settingsのパス, 呼ぶ場所) を返す"""
    os.makedirs(CLAUDE_ISO_DIR, exist_ok=True)
    if not os.path.exists(CLAUDE_ISO_SETTINGS):
        json.dump({"hooks": {}, "outputStyle": "default"},
                  open(CLAUDE_ISO_SETTINGS, "w"), ensure_ascii=False)
    return CLAUDE_ISO_SETTINGS, CLAUDE_ISO_DIR

# ── 段1：機械で決まるもの ───────────────────────────────
BIZ = {  # 名前に出たら確定する固有名詞 → 部門
    "オレンジワークス": "15_施設運営", "SWELL": "15_施設運営", "リアンライフ": "15_施設運営",
    "LIFE STAND UP": "15_施設運営", "STAND UP": "15_施設運営", "ILIFE": "15_施設運営",
    "こどもステーション": "12_マーケティング", "かわちばなし": "12_マーケティング",
    "社畜眼鏡": "12_マーケティング", "マネーシンギュラリティ": "12_マーケティング",
    "GameBull": "13_営業", "ゲームブル": "13_営業",
}
SENSITIVE = ["是正勧告", "勧告書", "診断", "障害者手帳", "給与", "賃金台帳", "源泉", "扶養",
             "児童管理", "個人情報", "履歴書", "職務経歴", "健康診断", "返戻", "過誤",
             "退職", "懲戒", "示談", "訴訟", "被害", "通帳", "マイナンバー"]
# ★契約の原本は機微（2026-07-20 の判定表に明記・2026-10-14 有璽氏が置き場を確定）
#   正本＝14_管理/14-300_法務部/_機微。案件部門にはショートカット（権限は元を継ぐので漏れない）
#   ★「参考」「ひな形」「サンプル」が付くものは原本でない＝機微にしない
CONTRACT = ["契約書", "覚書", "念書", "合意書", "示談書"]
# ★労務・採用の個人書類は規則で寄せる（判定表に「給与明細・応募者・従業員の個人情報」と明記）
#   2026-10-14 実測：_要判断28件のうち12件がこれ。Haikuは機微を前に「確信:低」を返しがち
LABOR = ["勤怠", "勤務表", "出勤表", "シフト表", "稼働報告", "労働条件", "雇用契約",
         "標準報酬", "社会保険", "健康保険", "厚生年金", "給与明細", "賃金"]
HIRING = ["応募", "履歴書", "職務経歴", "経歴書", "採用の流れ", "誓約書", "面接", "コンピテンシー"]
CONTRACT_NOT = ["参考", "ひな形", "雛形", "サンプル", "テンプレ"]


def is_contract_original(hay):
    return any(k in hay for k in CONTRACT) and not any(k in hay for k in CONTRACT_NOT)
DATE_RE = [
    (re.compile(r"(20\d{2})[-_./年]\s*(\d{1,2})[-_./月]\s*(\d{1,2})"), lambda m: "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))),
    (re.compile(r"(20\d{2})[-_./年]\s*(\d{1,2})月?"), lambda m: "%s-%02d-01" % (m.group(1), int(m.group(2)))),
    (re.compile(r"\b(\d{2})[.年](\d{1,2})[.月](\d{1,2})"), lambda m: "20%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))),
    (re.compile(r"(20\d{2})年度"), lambda m: "%s-04-01" % m.group(1)),
]


def date_from_name(name):
    """★月00・日00 を出さない（「2026-005」で 2026-00-01 を作った実害・2026-10-14）"""
    for rx, f in DATE_RE:
        m = rx.search(name)
        if m:
            try:
                v = f(m)
                y, mo, d = int(v[:4]), int(v[5:7]), int(v[8:10])
                if 2015 <= y <= datetime.date.today().year + 1 and 1 <= mo <= 12 and 1 <= d <= 31:
                    return v
            except Exception:
                pass
    return None


def safe_name(x):
    """★ファイル名に使えない文字を直す（2026-07-20 の記録にあったのに実装し忘れ、
       「2025/09/03のBNI天竜」で移動が落ちた・2026-10-14）"""
    x = x.replace("/", "・").replace(":", "：").replace("\\", "・")
    x = re.sub(r"[\x00-\x1f]", "", x)
    return x.strip(" .")[:150]


def birth(path):
    st = os.stat(path)
    return datetime.date.fromtimestamp(getattr(st, "st_birthtime", st.st_mtime)).isoformat()


def folder_date(path):
    """フォルダは中でいちばん新しいファイルの作成日（★フォルダ自身の日付は使わない）"""
    best = None
    for root, _, fs in os.walk(path):
        for f in fs:
            if f.startswith("."):
                continue
            d = date_from_name(nfc(f)) or birth(os.path.join(root, f))
            if best is None or d > best:
                best = d
    return best or birth(path)


def extract(path, limit=1200):
    """中身の先頭を取る。取れない種類は空文字（★取れないことを隠さない）"""
    e = os.path.splitext(path)[1].lower()
    try:
        if e in (".txt", ".md", ".csv", ".rtf"):
            t = open(path, "rb").read(20000).decode("utf-8", "ignore")
            if e == ".rtf":
                t = re.sub(r"\\[a-z]+-?\d*\s?|[{}]", " ", t)
            return t[:limit]
        if e == ".pdf":
            import pypdf
            r = pypdf.PdfReader(path)
            return "".join((p.extract_text() or "") for p in r.pages[:3])[:limit]
        if e in (".docx", ".doc"):
            return subprocess.run(["textutil", "-convert", "txt", "-stdout", path],
                                  capture_output=True, text=True, timeout=30).stdout[:limit]
        if e in (".xlsx", ".xlsm"):
            with zipfile.ZipFile(path) as z:
                if "xl/sharedStrings.xml" in z.namelist():
                    x = z.read("xl/sharedStrings.xml").decode("utf-8", "ignore")
                    return " ".join(re.findall(r"<t[^>]*>([^<]+)</t>", x))[:limit]
        if e in (".pptx",):
            with zipfile.ZipFile(path) as z:
                out = []
                for n in [n for n in z.namelist() if n.startswith("ppt/slides/slide")][:4]:
                    out += re.findall(r"<a:t>([^<]+)</a:t>", z.read(n).decode("utf-8", "ignore"))
                return " ".join(out)[:limit]
    except Exception:
        return ""
    return ""


def peek(path):
    """対象（ファイル or フォルダ）の手がかりを集める"""
    name = nfc(os.path.basename(path))
    if os.path.isdir(path):
        inner = []
        for root, _, fs in os.walk(path):
            for f in fs[:40]:
                if not f.startswith("."):
                    inner.append(nfc(f))
        body = ""
        for root, _, fs in os.walk(path):
            for f in sorted(fs):
                if f.startswith("."):
                    continue
                body = extract(os.path.join(root, f))
                if body.strip():
                    break
            if body.strip():
                break
        return {"name": name, "kind": "フォルダ", "inner": inner[:25],
                "date": date_from_name(name) or folder_date(path), "body": body}
    return {"name": name, "kind": "ファイル", "inner": [],
            "date": date_from_name(name) or birth(path), "body": extract(path)}


def stage1(info):
    """機械で決まるもの＝日付・機微・★対象のヒント（固有名詞）

    ★2026-10-14 修正：固有名詞で部門を決めてはいけない。
      同じ ILIFE 宛でも、契約書は法務・請求書は経理・支援記録は施設運営。
      固有名詞は「誰の書類か（対象）」であって「どの部門の仕事か」ではない。
    """
    hay = info["name"] + " " + " ".join(info["inner"]) + " " + info["body"][:400]
    # ★2026-10-15：強制の根拠は「名前（とフォルダ直下の名前）」に限る。
    #   本文に機微語が1回出ただけで隔離すると、営業の案内資料が _機微 に埋まる
    #   （実測：「ふくち福祉BPO案内資料」が本文の“退職”で／ソフトバンクとの
    #     共催企画提案が“診断”で 13_営業/_機微 へ寄った＝★死蔵になる）。
    #   本文だけで当たったものは隔離せず「人に見てもらう印」にする
    #   → feedback_confidential_two_layer_rule「機微と決めるのはAIではない」
    nm = info["name"] + " " + " ".join(info["inner"])
    sens = [w for w in SENSITIVE if w in nm]
    sens_body = [w for w in SENSITIVE if w in hay and w not in sens]
    hints = [k for k in BIZ if k in hay]
    contract = is_contract_original(nm)
    labor = any(k in nm for k in LABOR)
    hiring = any(k in nm for k in HIRING)
    if contract:
        sens = sens + ["契約原本"]
    if labor:
        sens = sens + ["労務の個人書類"]
    if hiring:
        sens = sens + ["採用の個人書類"]
    # 本文だけに出た労務・採用・契約も「印」の側へ回す（隔離はしない）
    if not labor and any(w in hay for w in LABOR):
        sens_body.append("労務語(中身)")
    if not hiring and any(w in hay for w in HIRING):
        sens_body.append("採用語(中身)")
    if not contract and is_contract_original(hay):
        sens_body.append("契約語(中身)")
    return {"ヒント": hints, "機微": sens, "★中身に機微語": sens_body,
            "契約原本": contract, "労務": labor, "採用": hiring}


HAIKU_PROMPT = """あなたはふくち。グループの書類を仕分けます。JSONだけを返してください。

部門は次のどれか1つ。★その部門が何を扱うかは下のとおり：
10_経営企画室    会社全体の方針・組織・KGI・社外共有の制作物・補助金の申請
11_事業開発      新規事業・デザイン制作・Web制作・プロダクト開発・社内のAI活用
12_マーケティング 広報・SNS・プレスリリース・イベント・調査研究
13_営業          商談・提案資料・顧客や取引先の資料・パートナー・案件の進行
14_管理          労務(勤怠・給与)／経理(請求・支払・口座)／法務(契約・弁護士・訴訟)／
                 採用(応募・履歴書・面接)／総務(サブスク・社内の契約事務)
15_施設運営      LIFE STAND UP・オレンジワークス・リアンライフ等、福祉の現場運営
                 (支援記録・加算・実地指導・利用者・保護者)
_個人(本人限定)   有璽氏個人の学び・健康・家計・私的な記録（会社の仕事でないもの）
                 ★取引先・顧客の破産や債権債務、紹介された人の資料は「会社の仕事」＝個人ではない
                 ★個人に入れるのは、会社の誰にも関係しない本人だけのもの
不明             ★上のどれにも当てはめられないとき

★よくあるものの行き先
   他社の会社案内・サービス資料・業界の参考資料   → 13_営業（相手を知るための資料）
   書籍の要約・講座・セミナー・思想や自己啓発     → _個人(本人限定)
   催しの名簿・申込者一覧                      → その催しを持つ部門（多くは12_マーケティング）
   研究・調査・論文                           → 12_マーケティング（調査・リサーチ部）
   AIやツールの使い方・プロンプト集             → 11_事業開発（社内のAI活用）

★「誰宛か」ではなく「★どの仕事の書類か」で決める。
   例：ILIFE宛でも、契約書なら14_管理（法務）、請求書なら14_管理（経理）、支援記録なら15_施設運営

種類は次のどれか1つ：
契約書 / 請求書 / 提案書 / 議事録 / 資料 / 様式 / 報告書 / 申請 / データ / 記録 / 素材 / 不明

返す形（JSONのみ・説明文を付けない）：
{"部門":"13_営業","種類":"資料","対象":"相手や案件の名前","要点":"短く","確信":"高|中|低"}

★迷ったら 確信:"低" にして 部門:"不明" を返すこと。無理に当てない。
★「対象」は人名・社名・案件名。分からなければ空文字。

--- 名前
%s
--- 種別
%s
--- 中の主なファイル
%s
--- 中身の先頭
%s
--- 名前に出てくる関係先（★部門の決め手にはしない。対象の手がかり）
%s
"""


def stage2(info, hints=()):
    p = HAIKU_PROMPT % (info["name"], info["kind"], " / ".join(info["inner"][:12]),
                        info["body"][:1200], "・".join(hints) or "なし")
    s, wd = _iso()
    try:
        r = subprocess.run(["claude", "-p", "--model", "haiku", "--settings", s, p],
                           capture_output=True, text=True, timeout=180, cwd=wd)
        t = r.stdout.strip()
        m = re.search(r"\{.*\}", t, re.S)
        if m:
            return json.loads(m.group(0))
        # ★JSONが無い＝判定できていない。「不明」と区別する（不明は判定した結果）
        return {"部門": "不明", "確信": "低", "err": "JSONなし", "生": t[:120]}
    except Exception as e:
        return {"部門": "不明", "確信": "低", "err": type(e).__name__}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cat")
    ap.add_argument("--dir", help="任意のフォルダを対象にする（_要判断 の再判定など）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if a.dir:
        src = a.dir if os.path.isabs(a.dir) else os.path.join(DEP, a.dir)
        a.cat = os.path.basename(src)
    else:
        src = None
        for x in os.listdir(ARC):
            if nfc(x) == nfc(a.cat or ""):
                src = os.path.join(ARC, x)
    if not src or not os.path.isdir(src):
        print("対象が無い:", a.cat or a.dir); sys.exit(1)

    items = [x for x in sorted(os.listdir(src)) if not x.startswith(".")]
    if a.limit:
        items = items[:a.limit]
    print("対象 %d 個（%s）\n" % (len(items), a.cat))

    # ★着手の前に段2を1回だけ試す（2026-10-15）。返らない・JSONが来ない状態で流すと
    #   全件が「不明」＝_要判断 に落ちたまま、終了コード0で完走してしまう
    _t = stage2({"name": "検証.pdf", "kind": "ファイル", "inner": [],
                 "body": "これは段2が生きているかを確かめるための検証です。"})
    if _t.get("err"):
        print("★段2（Haiku）が使えない：%s %s" % (_t["err"], _t.get("生", "")))
        print("★全件が『不明』に落ちるので着手しません。直してから流してください")
        sys.exit(2)
    print("段2の動作確認 OK（部門=%s）\n" % _t.get("部門"))
    plan = []
    MEDIA = (".mov", ".mp4", ".m4a", ".mp3", ".wav", ".png", ".jpg", ".jpeg", ".heic", ".gif", ".psd", ".ai")
    skipped = 0
    for x in items:
        p = os.path.join(src, x)
        # ★中身を読めないもの（音声・動画・画像）はAIへ投げない。名前だけで動かす価値が薄い
        #   2026-10-14 実測：16_音声・動画メモ 15件がすべて「要判断」に落ちた
        if os.path.isfile(p) and os.path.splitext(x)[1].lower() in MEDIA:
            skipped += 1
            continue
        info = peek(p)
        s1 = stage1(info)
        tgt = stage2(info, s1["ヒント"])
        conf = tgt.get("確信", "低")
        why = "段2：Haiku" + ("（手がかり %s）" % "・".join(s1["ヒント"]) if s1["ヒント"] else "")
        if s1["機微"]:
            why += " ／★名前に機微語 " + "・".join(s1["機微"][:3])
        if s1["★中身に機微語"]:
            # ★隔離はしない。有璽氏に「置いてよいか・隔離するか」を聞くための印
            why += " ／▲中身に機微語 " + "・".join(s1["★中身に機微語"][:3]) + "（隔離せず印だけ）"
        dep = tgt.get("部門", "不明")
        # ★2026-10-15 修正：機微語に当たったものは「どれも」規則で寄せる。
        #   それまで forced は契約原本・労務・採用の3つだけで、SENSITIVE（マイナンバー・
        #   診断・給与ほか）は why に書くだけで何もしていなかった。実測で
        #   「マイナンバー(表)_田村佑司.pdf」「鈴川聖子さん診断結果.pdf」が
        #   人が開ける _要判断 に素のまま置かれていた（3件）。
        forced = (s1.get("契約原本") or s1.get("労務") or s1.get("採用")
                  or bool(s1["機微"]))
        if (dep == "不明" or conf == "低") and not forced:
            dest = "_要判断_20261014"
            newname = info["name"]
        else:
            # ★契約の原本は、Haikuが何と答えても法務部の _機微 へ寄せる（規則が優先）
            if s1.get("契約原本"):
                dest = "14_管理/14-300_法務部/_機微"
                why += " ／★契約原本は規則で法務へ"
            elif s1.get("労務"):
                dest = "14_管理/14-100_労務部/_機微"
                why += " ／★労務の個人書類は規則で労務へ"
            elif s1.get("採用"):
                dest = "14_管理/14-400_採用部/_機微"
                why += " ／★採用の個人書類は規則で採用へ"
            elif s1["機微"] and dep == "不明":
                # ★部門が決まらない機微は、人が開ける素の _要判断 に置かない。
                #   同じ _要判断 の中の _機微 サブフォルダへ入れる（権限を限定できる形）
                dest = "_要判断_20261014/_機微"
                why += " ／★部門が不明な機微は _要判断/_機微 へ"
            else:
                dest = dep + ("/_機微" if s1["機微"] else "")
            tai = (tgt.get("対象") or "").strip()
            you = (tgt.get("要点") or "").strip()[:24]
            if not (tai or you):   # ★Haikuが何も返さなければ元の名前を掃除して使う
                raw = os.path.splitext(info["name"])[0]
                raw = re.sub(r"^\s*20\d{2}[-_./年]\s*\d{1,2}[-_./月]?\s*\d{0,2}日?\s*", "", raw)
                raw = re.sub(r"【[^】]*】", "", raw).strip(" _-")
                # ★2026-10-15：名前が【】だけのファイルは、掃除で中身が消えて
                #   「2026-04-21【資料】_v1.docx」という名無しになる
                #   （実測：「【ビジネスメンバー採用の流れ】.docx」）。空なら元の名前を使う
                if not raw:
                    raw = os.path.splitext(info["name"])[0].strip("【】 _-")
                tai = raw[:34]
            base = "【%s】%s" % (tgt.get("種類", "資料"), "_".join([t for t in (tai, you) if t])[:46])
            ext = os.path.splitext(info["name"])[1] if info["kind"] == "ファイル" else ""
            newname = safe_name("%s%s_v1%s" % (info["date"], base, ext))
        plan.append({"元": info["name"], "先": dest, "新": newname, "根拠": why,
                     "確信": conf, "▲中身に機微語": s1["★中身に機微語"]})
        print("%-40s → %-28s %s" % (info["name"][:40], dest, conf))
        if dest != "_要判断_20261014":
            print("     %s" % newname[:76])
        print("     %s" % why)

    print("\n合計 %d ／ 要判断 %d ／ ★素材で飛ばした %d" % (
        len(plan), sum(1 for x in plan if x["先"].startswith("_要判断")), skipped))
    out = "/tmp/drive_sort_%s.json" % re.sub(r"\W", "_", a.cat)
    json.dump(plan, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("提案:", out)
    if not a.apply:
        print("★動かしていません。--apply で実行します")
        return
    import shutil
    ok = 0
    for r in plan:
        s = os.path.join(src, r["元"])
        d = os.path.join(DEP, r["先"])
        os.makedirs(d, exist_ok=True)
        t = os.path.join(d, r["新"])
        if not os.path.exists(s) or os.path.exists(t):
            print("  ★飛ばす:", r["元"][:40]); continue
        shutil.move(s, t); ok += 1
    print("移した:", ok)
    log = os.path.join(DEP, "_整理ログ", "レガシー移行_20261014.json")
    old = json.load(open(log, encoding="utf-8")) if os.path.exists(log) else []
    old.append({"日時": datetime.datetime.now().isoformat(timespec="seconds"),
                "元": "Downloads書類アーカイブ/" + a.cat, "件数": ok,
                "明細": [{"旧": r["元"], "新": r["新"], "先": r["先"]} for r in plan]})
    json.dump(old, open(log, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ログ:", log)


if __name__ == "__main__":
    main()
