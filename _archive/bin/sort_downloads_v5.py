#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Downloads → 部門軸アーカイブ 週次自動振り分け  v5 (2026-07 部門軸再設計版)
========================================================================
設計: Notion組織マスター(部門10-15 × 部署 × 大型PJ)のコード付き部門軸フォルダを
      Driveの「実体」とし、Downloadsの新規ファイルをキーワードで該当部署へ振り分ける。
      機微(給与/契約/応募/口座 等)は各部署配下の「_機微」サブフォルダへ自動隔離。
      個人・プライベートは会社ツリー外の「_個人(本人限定)」へ。
      確信できないものは Downloads に残す(誤仕分け防止)。法人はrelationタグ/ショートカットで
      表現するため本スクリプトはフォルダ実体(部門軸)にのみ振り分ける。

安全設計:
  - Drive未マウントなら何もせず終了
  - 既定はキーワード確信分のみ移動、不明は残置
  - --dry-run  判定のみ(移動しない)
  - --init     部門軸スケルトン(空フォルダ)を作成して終了(振り分けはしない)
  - 全操作は move ベース＝_整理ログ/ のCSVで復元可能
注意: ROOT は下記定数。マイドライブ直下 00_部門軸アーカイブ を既定とする(変更可)。
"""
import os, sys, shutil, csv, subprocess

HOME = os.path.expanduser("~")
DOWNLOADS = os.path.join(HOME, "Downloads")
DRIVE = os.path.join(HOME, "Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com/マイドライブ")
ROOT = os.path.join(DRIVE, "00_部門軸アーカイブ")   # ← 部門軸ツリーのルート(要確認・変更可)
LOGDIR = os.path.join(ROOT, "_整理ログ")
KININ = "_機微"                     # 機微サブフォルダ固定名(先頭_で最上部固定)
PERSONAL = "_個人(本人限定)"         # 会社ツリー外・本人限定
RESIDUAL = None                     # 不確実は Downloads 残置

DRY  = "--dry-run" in sys.argv
INIT = "--init" in sys.argv

# ── 部門軸フォルダ・スケルトン(Notion組織マスター 2026-07-20 準拠) ──────────────
#   "部門フォルダ": ["部署フォルダ", ...]
DEPT_TREE = {
 "10_経営企画室":   ["10-100_経営戦略", "10-200_代表秘書"],
 "11_事業開発":     ["11-100_事業開発部", "11-200_システム開発部", "11-300_デザイン制作部",
                     "11-400_コンテンツ開発部", "11-500_EC事業部"],
 "12_マーケティング":["12-100_広報部", "12-200_イベント事業部", "12-300_WEBマーケティング部",
                     "12-400_調査・リサーチ部", "12-500_マーケティング戦略部"],
 "13_営業":         ["13-100_法人コンサル部", "13-200_FPコンサル部", "13-300_営業事務部"],
 "14_管理":         ["14-100_労務部", "14-200_経理部", "14-300_法務部", "14-400_採用部", "14-500_総務部"],
 "15_施設運営":     ["15-100_自社施設BPO部", "15-200_施設マネジメント部",
                     "15-300_LIFE STAND UP", "15-400_オレンジワークス藤井寺"],
}

def dept_path(dept, bu):
    return os.path.join(ROOT, dept, bu)

# コード接頭辞 "NN-M" → 部署パス の逆引き(DEPT_TREEから自動生成)
#   部署コード NN-M00 / PJコード NN-Mxx はいずれも先頭4文字 "NN-M" で同一部署へ寄せる
import re
CODE2DEPT = {}
for _dept, _bus in DEPT_TREE.items():
    for _bu in _bus:
        _m = re.match(r"^(\d\d-\d)\d\d_", _bu)
        if _m:
            CODE2DEPT[_m.group(1)] = (_dept, _bu)

def code_route(name):
    """ファイル名/フォルダ名の先頭が 部署/PJ コード(NN-Mxx)なら該当部署パスを返す"""
    m = re.match(r"^(\d\d-\d)\d\d[_\-\s]", name)
    if m and m.group(1) in CODE2DEPT:
        dept, bu = CODE2DEPT[m.group(1)]
        return dept_path(dept, bu)
    return None

# ── 機微ルール: キーワード → (部署パス, _機微へ) ─────────────────────────────
#   ここに当たったら該当部署の _機微 サブフォルダへ隔離する
KININ_RULES = [
 (("14_管理","14-100_労務部"), ["給与","給料","賞与","源泉徴収","標準報酬","被保険者","労働条件",
                               "勤怠","シフト","退職者","誓約書","雇用契約","社会保険"]),
 (("14_管理","14-300_法務部"), ["契約書","譲渡契約","委任契約","覚書","秘密保持","nda","協議書",
                               "債権","破産","解約","貸付"]),
 (("14_管理","14-400_採用部"), ["履歴書","職務経歴","応募","面接シート","採用選考","内定"]),
 (("14_管理","14-200_経理部"), ["口座","振替","確定申告","決算","仕訳","源泉","楽天銀行",
                               "americanexpress","口座振替"]),
]
KININ_KWS = [kw for _, kws in KININ_RULES for kw in kws]  # 機微判定用フラット集合
# ── 個人・プライベート(会社ツリー外) ───────────────────────────────────────
PERSONAL_KWS = ["免許証","マイナンバー","健康保険証","医療保険の資格","価値観マップ",
                "パーソナルトレーニング","自己史","推し活","ホロスコープ","診断結果",
                "潜在意識","田村佑司","ボクシング","ファスティング","春休み"]

# ── 部署振り分けルール: 上から優先。キーワード(小文字)一致で該当部署へ ───────────
#   (部門, 部署, [キーワード])
RULES = [
 # 12 マーケティング
 ("12_マーケティング","12-100_広報部",      ["instagram","x投稿","sns","広報","pr","公式line","掲載","プレスリリース",
                                            "オウンドメディア","note","meo","情報発信","ゲートキーパー"]),
 ("12_マーケティング","12-200_イベント事業部",["こどもマルシェ","マルシェ","こどもステーション","親子","撮影会",
                                            "フォーラム","むすびえ","タイムスケジュール","当日運営"]),
 ("12_マーケティング","12-300_WEBマーケティング部",["webサイト","lp","ランディング","seo","広告運用","web集客"]),
 ("12_マーケティング","12-400_調査・リサーチ部",["リサーチ","調査","論文","発達障害","トラブル調査","基礎資料"]),
 ("12_マーケティング","12-500_マーケティング戦略部",["マーケ戦略","統合マーケ","ブランディング","ファネル"]),
 # 11 事業開発
 ("11_事業開発","11-200_システム開発部",   ["fukuchi","ふくち","システム","アプリ","api","データ連携","要件定義",
                                            "portal","shopify","さくらサーバー",".json",".drawio",".html"]),
 ("11_事業開発","11-300_デザイン制作部",     ["design","ロゴ","logo","名刺","イラスト","canva",".fig",".psd",".ai",
                                            "デザイン","3つ折り","素材サイト","芽育"]),
 ("11_事業開発","11-400_コンテンツ開発部",   ["figma動画","動画教材","お金の教養","コンテンツ開発","講座教材","教材"]),
 ("11_事業開発","11-500_EC事業部",          ["ネットショップ","ec運営","古着","アパレルec","出品","物販"]),
 ("11_事業開発","11-100_事業開発部",        ["事業開発","新規事業","事業構想","事業計画","kpi","kgi","ロードマップ"]),
 # 13 営業
 ("13_営業","13-200_FPコンサル部",          ["fp","ライフプラン","保険見直し","資産形成","senet","heritage",
                                            "リーディングキャピタル","変額","nisa","fp-analysis"]),
 ("13_営業","13-100_法人コンサル部",        ["福祉施設コンサル","法人コンサル","補助金コーディネート","処遇改善",
                                            "加算","放課後等デイ","放デイ","就労支援","就労継続","サビ管"]),
 ("13_営業","13-300_営業事務部",            ["補助金申請","助成金申請","it導入","省力化","業務改善助成","交付申請"]),
 # 15 施設運営
 ("15_施設運営","15-300_LIFE STAND UP",     ["life stand up","lsu","スタンドアップ","英語クラス"]),
 ("15_施設運営","15-400_オレンジワークス藤井寺",["オレンジワークス","羽曳野","藤井寺"]),
 ("15_施設運営","15-200_施設マネジメント部", ["施設マネジメント","施設運営マニュアル","児童指導員","児童管理",
                                            "重要事項説明","実地指導","支援プログラム"]),
 ("15_施設運営","15-100_自社施設BPO部",      ["bpo","施設本部","本部機能"]),
 # 10 経営企画
 ("10_経営企画室","10-100_経営戦略",         ["経営戦略","経営理念","行動指針","事業承継","会社案内","キックオフ",
                                            "定例","ビビッド","ilife","天佑"]),
 ("10_経営企画室","10-200_代表秘書",         ["代表秘書","秘書","スケジュール調整"]),
 # 14 管理(機微でない通常業務)
 ("14_管理","14-500_総務部",                ["総務","備品","庶務","社内規程"]),
 ("14_管理","14-100_労務部",                ["人員配置","キャリアパス","稼働報告","活動報告書","異動届","職員"]),
]

MEDIA = {"mov","mp4","m4a","mp3","webm","wav","aac","aiff"}
IMG   = {"png","jpg","jpeg","heic","webp","gif","bmp","tif","tiff","avif"}

def classify(name, is_dir):
    """戻り値: 絶対パス(移動先ディレクトリ) または None(残置)"""
    n = name.lower()
    ext = "" if is_dir else (name.rsplit(".",1)[-1].lower() if "." in name else "")
    # 0) コード接頭辞で確定振り分け(最優先・命名規約準拠)。中身が機微なら _機微 へ
    cr = code_route(name)
    if cr:
        if any(kw in n for kw in KININ_KWS):
            return os.path.join(cr, KININ)
        return cr
    # 1) 個人・プライベート → 会社ツリー外
    for kw in PERSONAL_KWS:
        if kw in n:
            return os.path.join(ROOT, PERSONAL)
    # 2) 機微 → 該当部署/_機微
    for (dept, bu), kws in KININ_RULES:
        for kw in kws:
            if kw in n:
                return os.path.join(dept_path(dept, bu), KININ)
    # 3) 部署振り分け
    for dept, bu, kws in RULES:
        for kw in kws:
            if kw and kw in n:
                return dept_path(dept, bu)
    # 4) メディア/画像は中身不明のため残置(部門が定まらない)
    #    ※部門が判る名前のメディアは上のRULESで拾われる
    return RESIDUAL  # None = 残置

def uniq_dest(dst):
    if not os.path.exists(dst): return dst
    base, ext = os.path.splitext(dst)
    i = 2
    while os.path.exists(f"{base}_{i}{ext}"):
        i += 1
    return f"{base}_{i}{ext}"

def init_skeleton():
    made = 0
    for dept, bus in DEPT_TREE.items():
        for bu in bus:
            p = dept_path(dept, bu)
            if not os.path.isdir(p):
                if not DRY: os.makedirs(p, exist_ok=True)
                made += 1
    for p in (os.path.join(ROOT, PERSONAL), LOGDIR):
        if not os.path.isdir(p):
            if not DRY: os.makedirs(p, exist_ok=True)
            made += 1
    print(f"[init] 部門軸スケルトン作成: 新規{made}フォルダ  root={ROOT}" + (" (DRYRUN)" if DRY else ""))

def main():
    ts = subprocess.run(["date","+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
    if not os.path.isdir(DRIVE):
        note(f"Drive未接続のため中止 ({ts})"); print("DRIVE not found. abort."); return
    if INIT:
        init_skeleton(); return
    if not os.path.isdir(ROOT):
        print(f"ROOT未作成: 先に --init でスケルトンを作成してください  ({ROOT})"); return
    junk = moved = kept = 0
    rows = []
    entries = [e for e in os.listdir(DOWNLOADS) if not e.startswith(".") and not e.startswith("_")]
    for e in entries:
        src = os.path.join(DOWNLOADS, e)
        if e.startswith("~$"):
            if not DRY: os.remove(src)
            junk += 1; continue
        is_dir = os.path.isdir(src)
        dstdir = classify(e, is_dir)
        if dstdir is None:
            kept += 1; rows.append((e, "残置(要手動)", "")); continue
        os.makedirs(dstdir, exist_ok=True)
        dst = uniq_dest(os.path.join(dstdir, e))
        rel = os.path.relpath(dstdir, ROOT)
        if not DRY: shutil.move(src, dst)
        moved += 1; rows.append((e, rel, "移動"))
    if not DRY:
        for root,_,files in os.walk(DOWNLOADS):
            for f in files:
                if f == ".DS_Store":
                    try: os.remove(os.path.join(root,f)); junk += 1
                    except: pass
    os.makedirs(LOGDIR, exist_ok=True)
    logf = os.path.join(LOGDIR, f"週次整理_{ts[:10]}.csv")
    try:
        with open(logf, "w", newline="", encoding="utf-8-sig") as fp:
            w = csv.writer(fp); w.writerow(["対象","振り分け先(部門軸)","動作"])
            for r in rows: w.writerow(r)
    except Exception as ex:
        print("log write err:", ex)
    msg = f"整理完了: {moved}件を部門軸へ / 残置{kept}件 / 不要{junk}件除去"
    print(f"[{ts}] {msg}")
    note(msg + (" (DRYRUN)" if DRY else ""))
    if not DRY:
        _beat("成功", msg)

def _beat(result, message):
    """⚙️自動処理レジスタへ心拍を送る。心拍の失敗で本体は止めない"""
    try:
        sys.path.insert(0, os.path.expanduser("~/.vivid-relay"))
        from heartbeat import beat
        beat("Downloads整理（→ Drive 17分類）", result, message)
    except Exception as e:
        print("heartbeat skipped:", repr(e))

def note(text):
    try:
        subprocess.run(["osascript","-e",
            f'display notification "{text}" with title "Downloads週次整理 v5"'], timeout=10)
    except: pass

if __name__ == "__main__":
    main()
