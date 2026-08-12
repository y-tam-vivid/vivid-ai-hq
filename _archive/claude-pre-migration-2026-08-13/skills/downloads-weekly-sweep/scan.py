#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
downloads-weekly-sweep / scan.py

Downloads を走査し、Stage 1（①junk隔離 → ②重複除去 → ③ファイル名正規化 → ④17分類格納）の
「提案CSV」を出力する。**この段階では一切ファイルを移動・改名・削除しない**（提案のみ）。

- 判定は確信度3層：格納A(自動確定) / 格納B(要レビュー) / 隔離C(junk)。迷いは 保留。
- 改名も保守的：A層は安全なクリーンアップのみ（重複サフィックス除去・日付prefix付与）。
  実質的な内容ベースの改名は空欄にして、Claude/人がレビュー時に埋める（＝全自動改名しない）。
- Googleネイティブ形式(.gdoc/.gsheet 等)はローカル改名不可 → ネイティブ=yes を立て新名案は空。

出力：<ARCHIVE>/_整理ログ/週次整理_提案_YYYY-MM-DD.csv
"""
import csv
import os
import re
import sys
from datetime import datetime

HOME = os.path.expanduser("~")
DOWNLOADS = os.path.join(HOME, "Downloads")
ARCHIVE = os.path.join(
    HOME,
    "Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com",
    "マイドライブ", "Downloads書類アーカイブ",
)
LOGDIR = os.path.join(ARCHIVE, "_整理ログ")
QUARANTINE_NAME = "_不要候補_確認用"  # Downloads内にローカル隔離（Driveへjunkを上げない）

# 17分類（フォルダ名そのまま）
CATS = {
    "01": "01_AI・開発",
    "02": "02_デザイン・制作",
    "03": "03_財務・経理・税務",
    "04": "04_補助金・助成金・行政",
    "05": "05_事業・組織",
    "06": "06_イベント・講座",
    "07": "07_議事録・面談・商談",
    "08": "08_契約・法務",
    "09": "09_採用・人事・給与",
    "10": "10_広報・SNS・PR",
    "11": "11_取引先・人物別",
    "12": "12_福祉事業運営",
    "13": "13_個人・プライベート",
    "14": "14_学習・リサーチ・読み物",
    "15": "15_画像・スクショ素材",
    "16": "16_音声・動画メモ",
    "17": "17_メモ・下書き",
}

# 強キーワード（一致すれば格納A）。上から順に優先。
STRONG_RULES = [
    ("03", ["請求書", "見積書", "領収", "確定申告", "決算", "税務", "仕訳", "給与明細", "通帳", "振込", "楽天銀行", "invoice"]),
    ("04", ["補助金", "助成金", "it導入", "省力化投資", "奨励金", "交付決定", "実績報告", "届出"]),
    ("08", ["契約書", "覚書", "nda", "秘密保持", "破産", "債権", "倫理審査", "利用規約"]),
    ("09", ["履歴書", "職務経歴", "在籍証明", "人員配置", "給与評価", "雇用契約", "シフト表", "勤怠"]),
    ("07", ["議事録", "面談", "商談", "1on1", "壁打ち", "notta", "打ち合わせ", "台本", "minutes"]),
    ("12", ["放課後", "デイサービス", "送迎", "受給者証", "個別支援計画", "モニタリング", "児発管", "加算", "避難訓練", "life stand up", "オレンジワークス", "利用者負担上限", "hug"]),
    ("10", ["instagram", "インスタ", "x投稿", "twitter", "threads", "プレスリリース", "公式line", "sns", "掲載"]),
    ("06", ["セミナー", "ウェビナー", "マルシェ", "撮影会", "講座", "イベント企画", "参加者"]),
    ("02", ["ロゴ", "vi・ci", "デザインシステム", "figma", "canva", "バナー", "サムネ", "イラスト", "北欧デザイン"]),
    ("01", ["claude", "gpt", "gas", "apps script", "プロンプト", "自動化", "スキル化", "システム要件", "要件定義", "notion", "家系図"]),
    ("05", ["事業計画", "事業構想", "組織図", "経営", "kpi", "ビジョン", "ふくち", "ilife", "ビビッド", "swellsociety", "stand up"]),
    ("13", ["トリセツ", "健康診断", "プライベート", "私用", "個人的"]),
    ("14", ["リサーチ", "調査研究", "参考記事", "読み物", "論文", "書籍まとめ"]),
]

MEDIA_IMG = {".png", ".jpg", ".jpeg", ".gif", ".heic", ".webp", ".bmp", ".tiff", ".svg"}
MEDIA_AV = {".mov", ".mp4", ".m4a", ".mp3", ".wav", ".aac", ".avi", ".mkv", ".m4v"}
NATIVE_EXT = {".gdoc", ".gsheet", ".gslides", ".gform", ".gdraw", ".gvid", ".gmap", ".gsite"}
INSTALLER_EXT = {".dmg", ".pkg", ".exe", ".iso"}

DEDUP_SUFFIX = re.compile(r"\s*(\(\d+\)|copy|のコピー)$", re.IGNORECASE)
# 名前のどこかに日付らしきトークンがあれば prefix を付けない（重複防止）
DATE_ANY = re.compile(r"\d{8}|\d{4}[-_.]\d{2}[-_.]\d{2}|\d{6}")


def is_junk(name):
    if name == ".DS_Store" or name.startswith("~$") or name.endswith(".tmp"):
        return "Office一時/システム生成ファイル"
    if name == ".localized" or name == "Icon\r":
        return "システムファイル"
    return None


def classify(name, ext_l, low):
    """(層, カテゴリ名, 根拠) を返す。層 in {格納A,格納B,隔離C}."""
    # 強キーワード
    for cat, kws in STRONG_RULES:
        for kw in kws:
            if kw in low:
                return "格納A", CATS[cat], "強KW:%s" % kw
    # メディア拡張子
    if ext_l in MEDIA_IMG:
        # スクショ系はより確実
        if "screenshot" in low or "スクリーンショット" in low or "スクショ" in low or low.startswith("img_"):
            return "格納A", CATS["15"], "スクショ/画像"
        return "格納B", CATS["15"], "画像拡張子(用途要確認:素材か制作物か)"
    if ext_l in MEDIA_AV:
        return "格納A", CATS["16"], "音声/動画拡張子"
    # 弱い手がかり → 保留寄りのB
    if any(k in low for k in ["無題", "untitled", "draft", "下書き", "メモ", "test", "テスト", "temp"]):
        return "格納B", CATS["17"], "下書き/無題(内容要確認)"
    return "格納B", "", "自動判定不可(要レビュー)"


def propose_rename(name, is_dir, native, mtime):
    """安全なクリーンアップのみA改名として提案。実質的改名は空欄(レビューで埋める)。"""
    if is_dir or native:
        return ""  # フォルダ・ネイティブは自動改名しない
    base, ext = os.path.splitext(name)
    new = base
    # 重複サフィックス除去
    while True:
        m = DEDUP_SUFFIX.search(new)
        if not m:
            break
        new = new[: m.start()].rstrip()
    # 空白・アンダースコアの整理
    new = re.sub(r"\s+", " ", new).strip()
    # 名前のどこにも日付が無ければ mtime から prefix を付与（全社規則§10：YYYY-MM-DD_ 統一）
    if not DATE_ANY.search(new):
        new = mtime.strftime("%Y-%m-%d") + "_" + new
    candidate = new + ext
    return candidate if candidate != name else ""


def main():
    ts = datetime.now()
    rows = []
    idx = 0
    for name in sorted(os.listdir(DOWNLOADS)):
        if name == QUARANTINE_NAME:
            continue
        # 隠しファイル/ディレクトリ(.DS_Store・.claude・アプリ状態ファイル等)は触らない
        if name.startswith("."):
            continue
        path = os.path.join(DOWNLOADS, name)
        try:
            st = os.stat(path)
        except OSError:
            continue
        is_dir = os.path.isdir(path)
        ext_l = os.path.splitext(name)[1].lower()
        low = name.lower()
        mtime = datetime.fromtimestamp(st.st_mtime)
        size_mb = round(st.st_size / (1024 * 1024), 1) if not is_dir else ""
        native = "yes" if ext_l in NATIVE_EXT else "no"
        idx += 1

        # ① junk
        junk = is_junk(name)
        if junk:
            rows.append([idx, "dir" if is_dir else "file", name, path, size_mb,
                         "隔離C", QUARANTINE_NAME, "", native, junk, "y"])
            continue
        if ext_l in INSTALLER_EXT:
            rows.append([idx, "file", name, path, size_mb,
                         "隔離C", QUARANTINE_NAME, "", native,
                         "インストーラ(再DL可能:通常不要)", ""])
            continue

        # ②③④
        tier, cat, reason = classify(name, ext_l, low)
        newname = propose_rename(name, is_dir, native == "yes", mtime)
        if native == "yes" and reason == "自動判定不可(要レビュー)":
            reason += " / ネイティブ形式はDrive側で改名"
        approve = "y" if tier == "格納A" and cat else ""
        rows.append([idx, "dir" if is_dir else "file", name, path, size_mb,
                     tier, cat, newname, native, reason, approve])

    os.makedirs(LOGDIR, exist_ok=True)
    out = os.path.join(LOGDIR, "週次整理_提案_%s.csv" % ts.strftime("%Y-%m-%d"))
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "種別", "現在名", "元パス", "サイズMB",
                    "判定", "提案カテゴリ", "新名案", "ネイティブ", "根拠", "承認(y/n)"])
        w.writerows(rows)

    a = sum(1 for r in rows if r[5] == "格納A")
    b = sum(1 for r in rows if r[5] == "格納B")
    c = sum(1 for r in rows if r[5] == "隔離C")
    print("提案CSVを出力しました: %s" % out)
    print("  対象 %d 件  (格納A:%d 自動 / 格納B:%d 要レビュー / 隔離C:%d junk)" % (len(rows), a, b, c))
    print("  → 格納B の空欄カテゴリ・新名案をレビューで埋め、承認(y)列を確定してから apply.py を実行してください。")


if __name__ == "__main__":
    main()
