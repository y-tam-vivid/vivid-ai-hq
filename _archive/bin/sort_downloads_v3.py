#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Downloads → マイドライブ書類アーカイブ 週次自動振り分け
- 使い捨て一時ファイル(~$ , .DS_Store)を除去
- ファイル/フォルダ名のキーワードで17分類へ「確信できるものだけ」移動
- 判定できないものは Downloads に残す（誤仕分け防止）
- ログとmacOS通知で結果を報告
安全設計: Driveが未マウントなら何も動かさず終了。ドライラン対応(--dry-run)。
"""
import os, sys, shutil, csv, datetime, subprocess

HOME = os.path.expanduser("~")
DOWNLOADS = os.path.join(HOME, "Downloads")
ARCHIVE = os.path.join(HOME, "Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com/マイドライブ/Downloads書類アーカイブ")
LOGDIR = os.path.join(ARCHIVE, "_整理ログ")
DRY = "--dry-run" in sys.argv

# (カテゴリ, キーワード) 上から優先。ファイル/フォルダ名(小文字)に含まれれば一致
RULES = [
 ("13_個人・プライベート",["免許証","マイナンバー","健康保険証","医療保険の資格","価値観マップ","パーソナルトレーニング","自己史","推し活","富裕層","結婚し豊","ライフプランニング","ファスティング","脳大成","ホロスコープ","診断結果","潜在意識","田村佑司","ボクシング","春休み","トレーニング"]),
 ("12_福祉事業運営",["児童管理","児童指導員","重要事項説明","実地指導","障害児","放課後等デイ","放デイ","就労継続","就労支援","返戻","過誤","是正勧告","処遇改善","加算","減算","支援プログラム","mikke house","羽曳野","苅田","福祉サービス","福祉リスト","syougai","sien","jidou","syajitumu","オレンジワークス","サビ管","重要事項","法改正","実績報告"]),
 ("09_採用・人事・給与",["面接シート","労働条件通知","労働条件","勤怠","シフト表","給料体系","給与","賞与","退職者","源泉徴収","キャリアパス","人員配置","稼働報告","活動報告書","誓約書","採用","被保険者","標準報酬","年度更新","異動届","職員"]),
 ("03_財務・経理・税務",["請求書","請求","領収","明細","仕訳","借方","貸方","交通費精算","経費","立替","家計","節税","即時償却","電気代削減","会費ペイ","加盟店","invoice","receipt","creditdebit","料金表","決算","確定申告","口座","振替","楽天銀行","americanexpress","会計","予実","収支","tranbi","adobe","workspace","通信費","支払"]),
 ("04_補助金・助成金・行政",["補助金","助成金","奨励金","委任状","証明書","届出","it導入","省力化","畜産","農福","カスタマーハラスメント","広域交付","戸籍","給付","交付申請","リスキリング","賃上げ","業務改善助成"]),
 ("08_契約・法務",["契約書","譲渡契約","委託受託","監督署","労働基準","貸付","覚書","協議書","誓約","破産","債権","弁護士","解約","委任契約","倫理審査"]),
 ("10_広報・SNS・PR",["instagram","x投稿","sns","広報","pr研修","公式line","掲載","情報発信","オウンドメディア","youtube","プレスリリース","ゲートキーパー","組織図","org_chart","名札","チラシ","ポスター","紙面","meo"]),
 ("14_学習・リサーチ・読み物",["論文","リサーチ","要約","福田恆存","オルテガ","ちゃぶ台","不都合な","ゼロ秒","giversgain","アート思考","シンギュラリティ","心得","理論","コングロマリット","基礎資料","学習障害","ガイドブック","立ち上げガイド","セミナー","ウェビナー","講座","ワークショップ","攻略法","マニュアル","極意"]),
 ("05_事業・組織",["事業計画","事業戦略","事業構想","事業展開","kpi","kgi","ビビッド","スタンドアップ","stand up","standup","fukuchi","ふくち","経営理念","行動指針","事業承継","会社案内","会社情報","キックオフ","定例","進行スクリプト","ロードマップ","ファネル","bpo","天佑","ilife"]),
 ("07_議事録・面談・商談",["議事録","打ち合わせ","お打合せ","商談","面談","顔合わせ","近況共有","gmail -","案件管理","進捗管理","営業案件","提案書","ご提案","ヒアリング","1on1","壁打ち","notta","会食","bni","週報","週次報告"]),
 ("06_イベント・講座",["こどもマルシェ","マルシェ","イベント","こどもステーション","親子","撮影会","フォーラム","むすびえ","当日","タイムスケジュール"]),
 ("01_AI・開発",["claude","chatgpt","gemini","生成ai","ai活用","aiスクール","プロンプト","skill","notion","todotion","家系図","議事録自動","システム","アプリ","ツール","portal","さくらサーバー","shopify","レビューシート","要件","handover","引き継ぎ","運用ルール",".drawio",".json",".html","fp-analysis"]),
 ("02_デザイン・制作",["design","ロゴ","logo","vi制作","ci名刺","名刺","イラスト","北欧","デザイン","canva",".fig",".psd",".ai","3つ折り","巻3","プロフィール例","監修者"]),
 ("11_取引先・人物別",["自己紹介","名刺"]),
 ("16_音声・動画メモ",[]),   # 拡張子で判定
 ("15_画像・スクショ素材",[]),# 拡張子で判定
 ("17_メモ・下書き",[]),      # 名称パターンで判定
]
MEDIA = {"mov","mp4","m4a","mp3","webm","wav","aac","aiff"}
IMG   = {"png","jpg","jpeg","heic","webp","gif","bmp","tif","tiff","avif"}

def classify(name, is_dir):
    n = name.lower()
    ext = "" if is_dir else (name.rsplit(".",1)[-1].lower() if "." in name else "")
    # メモ・下書き
    if not is_dir and (n.startswith("名称未設定") or "メモ.rtf" in n or "自分の考察" in n or n.startswith("たたき")):
        return "17_メモ・下書き"
    for cat, kws in RULES:
        for kw in kws:
            if kw and kw in n:
                return cat
    if not is_dir:
        if ext in MEDIA: return "16_音声・動画メモ"
        if ext in IMG:   return "15_画像・スクショ素材"
        if "スクリーンショット" in n or "screenshot" in n or "camscanner" in n:
            return "15_画像・スクショ素材"
    return None  # 不確実 → 残す

def uniq_dest(dst):
    if not os.path.exists(dst): return dst
    base, ext = os.path.splitext(dst)
    i = 2
    while os.path.exists(f"{base}_{i}{ext}"):
        i += 1
    return f"{base}_{i}{ext}"

def main():
    ts = subprocess.run(["date","+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
    # Drive未マウントなら中断
    if not os.path.isdir(ARCHIVE):
        note(f"Drive未接続のため中止 ({ts})")
        print("ARCHIVE not found. abort."); return
    junk = moved = kept = 0
    rows = []
    entries = [e for e in os.listdir(DOWNLOADS) if not e.startswith(".") and not e.startswith("_")]
    for e in entries:
        src = os.path.join(DOWNLOADS, e)
        # 一時ファイル除去
        if e.startswith("~$"):
            if not DRY: os.remove(src)
            junk += 1; continue
        is_dir = os.path.isdir(src)
        cat = classify(e, is_dir)
        if cat is None:
            kept += 1; rows.append((e, "残置(要手動)", "")); continue
        dstdir = os.path.join(ARCHIVE, cat)
        os.makedirs(dstdir, exist_ok=True)
        dst = uniq_dest(os.path.join(dstdir, e))
        if not DRY: shutil.move(src, dst)
        moved += 1; rows.append((e, cat, "移動"))
    # .DS_Store掃除
    if not DRY:
        for root,_,files in os.walk(DOWNLOADS):
            for f in files:
                if f == ".DS_Store":
                    try: os.remove(os.path.join(root,f)); junk += 1
                    except: pass
    # ログ
    os.makedirs(LOGDIR, exist_ok=True)
    logf = os.path.join(LOGDIR, f"週次整理_{ts[:10]}.csv")
    try:
        with open(logf, "w", newline="", encoding="utf-8-sig") as fp:
            w = csv.writer(fp); w.writerow(["対象","結果/カテゴリ","動作"])
            for r in rows: w.writerow(r)
    except Exception as ex:
        print("log write err:", ex)
    msg = f"整理完了: {moved}件を本棚へ / 残置{kept}件 / 不要{junk}件除去"
    print(f"[{ts}] {msg}")
    note(msg + (" (DRYRUN)" if DRY else ""))

def note(text):
    try:
        subprocess.run(["osascript","-e",
            f'display notification "{text}" with title "Downloads週次整理"'], timeout=10)
    except: pass

if __name__ == "__main__":
    main()
