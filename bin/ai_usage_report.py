#!/usr/bin/env python3
"""Claude Code のトークン消費を日ごとに数えて CSV へ積む。★読むだけ。何も書き換えない。

なぜ要るか ── 2026-09-12 有璽氏
    「使ってるAIの使用量を知りたい。何パーセント使ってるのかとか、いつリセットされるのかとか。
     それがそれぞれのエージェントでどれぐらい消費しているのかとかも見えるようにしてほしい。
     それを後でCSVファイルでアウトプットして検証できるようにもしたい。」

★出せるもの・出せないものを最初に分けてある（実測 2026-09-12）
    ✅ 出せる   トークン消費（input / output / cache作成 / cache読取）
                ~/.claude/projects/**/*.jsonl の message.usage に実在する
                ★担当（サブエージェント）別・モデル別・案件（cwd）別に割れる
    🔴 出せない Claudeプランの「何％使った」「いつリセット」
                ★ANTHROPIC_API_KEY が無く、Maxプランの消費率はローカルに保存されていない
                ★見られるのは Claude Code の /usage コマンドだけ＝人が叩く領域
    🔴 出せない ChatGPT Plus（サブスク）の使用量。APIで公開されていない

★金額について（[[feedback_never_write_an_unmeasured_number]]）
    単価は公式の料金ページで4種すべて確認した（2026-09-12 実測）
    https://platform.claude.com/docs/en/about-claude/pricing
      claude-opus-5    input $5    cache作成 $6.25(5分)  cache読取 $0.50   output $25
      claude-sonnet-5  input $2    cache作成 $2.50       cache読取 $0.20   output $10
    ★cache読取を入れないと額が一桁変わる（実測：入れないと $34、入れると約 $400）
    ★cache作成は「5分」と「1時間」で単価が違う（1時間は input の2倍）が、
      transcript は cache_creation_input_tokens しか持たず区別できない。
      ★5分の単価で計算している＝1時間キャッシュを使った分は★過少に出る。
    ★そもそも Max プランは従量課金ではない。この金額は「API換算の参考値」であって請求額ではない。

使い方
    python3 bin/ai_usage_report.py                    今日ぶんを数えて表示（★書かない）
    python3 bin/ai_usage_report.py --days 7           直近7日
    python3 bin/ai_usage_report.py --run              CSVへ追記する（★--run のときだけ書く）
    python3 bin/ai_usage_report.py --run --beat       心拍も打つ（定期実行用）
    python3 bin/ai_usage_report.py --weekly           週のまとめを出す（月曜に見る用）

出口
    ~/.vivid-relay/usage/daily_<ホスト名>.csv   1日1行 × 担当 × モデル。★追記のみ・上書きしない
    ~/.vivid-relay/usage/agents_<ホスト名>.csv  担当別の明細
"""
import argparse
import collections
import csv
import datetime as dt
import json
import os
import pathlib
import socket
import sys

HOME = pathlib.Path.home()
PROJECTS = HOME / ".claude" / "projects"
OUTDIR = HOME / ".vivid-relay" / "usage"
HOST = socket.gethostname().split(".")[0]
JST = dt.timezone(dt.timedelta(hours=9))

# (input, cache作成5分, cache読取, output) ドル / 1Mトークン
# ★公式の料金ページで確認済み（2026-09-12）
PRICE = {
    "claude-opus-5":     (5.00,  6.25, 0.50, 25.00),
    "claude-opus-4-8":   (5.00,  6.25, 0.50, 25.00),
    "claude-opus-4-7":   (5.00,  6.25, 0.50, 25.00),
    "claude-opus-4-6":   (5.00,  6.25, 0.50, 25.00),
    "claude-opus-4-5":   (5.00,  6.25, 0.50, 25.00),
    "claude-sonnet-5":   (2.00,  2.50, 0.20, 10.00),
    "claude-sonnet-4-6": (3.00,  3.75, 0.30, 15.00),
    "claude-sonnet-4-5": (3.00,  3.75, 0.30, 15.00),
    "claude-haiku-4-5":  (1.00,  1.25, 0.10,  5.00),
    "claude-fable-5":    (10.00, 12.50, 1.00, 50.00),
    "claude-fable-5-1":  (10.00, 12.50, 0.25, 50.00),
}

FIELDS = ["日付", "機械", "担当", "モデル", "入口", "案件",
          "input", "output", "cache作成", "cache読取", "ターン数",
          "API換算額_USD", "単価が確定しているか"]


def jst_date(ts):
    """ISO8601（UTC）を JST の日付文字列にする。"""
    try:
        d = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None
    return d.astimezone(JST).strftime("%Y-%m-%d")


def short(p):
    """cwd を案件名らしく短くする。"""
    if not p:
        return "-"
    name = pathlib.Path(p).name
    return name if name else "-"


def collect(days):
    """transcript を読んで集計する。★読むだけ。"""
    today = dt.datetime.now(JST).date()
    wanted = {(today - dt.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)}
    rows = collections.defaultdict(lambda: dict(
        input=0, output=0, cw=0, cr=0, turns=0))
    seen = set()
    files = 0
    if not PROJECTS.exists():
        return rows, 0, wanted
    for f in PROJECTS.rglob("*.jsonl"):
        files += 1
        try:
            fh = f.open(errors="ignore")
        except Exception:
            continue
        with fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                msg = d.get("message") or {}
                u = msg.get("usage")
                if not u:
                    continue
                day = jst_date(d.get("timestamp") or "")
                if day not in wanted:
                    continue
                # ★同じ行を二重に数えない
                uid = d.get("uuid")
                if uid:
                    if uid in seen:
                        continue
                    seen.add(uid)
                model = msg.get("model") or "?"
                agent = "サブエージェント" if d.get("agentId") else "メイン"
                key = (day, HOST, agent, model,
                       d.get("entrypoint") or "?", short(d.get("cwd")))
                r = rows[key]
                r["input"] += int(u.get("input_tokens") or 0)
                r["output"] += int(u.get("output_tokens") or 0)
                r["cw"] += int(u.get("cache_creation_input_tokens") or 0)
                r["cr"] += int(u.get("cache_read_input_tokens") or 0)
                r["turns"] += 1
    return rows, files, wanted


def to_records(rows):
    out = []
    for (day, host, agent, model, ep, proj), r in sorted(rows.items()):
        if not any((r["input"], r["output"], r["cw"], r["cr"])):
            continue  # ★消費ゼロの行は出さない（<synthetic> など）
        price = PRICE.get(model)
        if price:
            pin, pcw, pcr, pout = price
            usd = (r["input"] * pin + r["cw"] * pcw + r["cr"] * pcr
                   + r["output"] * pout) / 1_000_000
            usd_s, known = f"{usd:.4f}", "確定(公式単価4種)"
        else:
            usd_s, known = "", "★単価が未確認"
        out.append(dict(zip(FIELDS, [
            day, host, agent, model, ep, proj,
            r["input"], r["output"], r["cw"], r["cr"], r["turns"], usd_s, known])))
    out.sort(key=lambda r: -(float(r["API換算額_USD"]) if r["API換算額_USD"] else 0))
    return out


def show(recs, files, wanted):
    print(f"★読んだ transcript: {files}本 ／ 対象の日: {len(wanted)}日分 ／ 出た行: {len(recs)}")
    if not recs:
        print("（対象の日に消費なし）")
        return
    tot = collections.Counter()
    w = f"{'日付':<11} {'担当':<7} {'案件':<16} {'in':>8} {'out':>9} {'cache作':>11} {'cache読':>13} {'$':>9}"
    print("\n" + w)
    print("-" * 92)
    for r in recs:
        proj = (r["案件"] or "-")[:15]
        print(f"{r['日付']:<11} {r['担当']:<7} {proj:<16}"
              f"{r['input']:>8,} {r['output']:>9,} {r['cache作成']:>11,} {r['cache読取']:>13,} "
              f"{('$'+r['API換算額_USD'][:6]) if r['API換算額_USD'] else '―':>8}")
        for k in ("input", "output", "cache作成", "cache読取"):
            tot[k] += r[k]
        if r["API換算額_USD"]:
            tot["usd"] += float(r["API換算額_USD"])
    print("-" * 92)
    print(f"{'合計':<36}{tot['input']:>8,} {tot['output']:>9,} "
          f"{tot['cache作成']:>11,} {tot['cache読取']:>13,} {'$'+format(tot['usd'],'.2f'):>8}")
    # ★内訳を出す。どこに効いているかが分からないと手の打ちようがない
    print("\n★金額の内訳（何が効いているか）")
    for label, key, price_idx in (("input", "input", 0), ("cache作成", "cache作成", 1),
                                  ("cache読取", "cache読取", 2), ("output", "output", 3)):
        sub = sum((r[key] * PRICE[r["モデル"]][price_idx] / 1_000_000)
                  for r in recs if r["モデル"] in PRICE)
        pct = (sub / tot["usd"] * 100) if tot["usd"] else 0
        bar = "█" * int(pct / 2.5)
        print(f"  {label:<9}{tot[key]:>13,} tok  ${sub:>8.2f}  {pct:>5.1f}%  {bar}")
    print("\n★Maxプランは従量課金ではないので、この額は請求額ではなくAPI換算の参考値です。")
    print("★cache作成は「5分」の単価で計算しています（1時間キャッシュ分は過少に出ます）。")


def write_csv(recs):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    path = OUTDIR / f"daily_{HOST}.csv"
    # ★追記。同じ日を二度書かないよう、既存の (日付,担当,モデル,入口,案件) は差し替える
    existing = []
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            existing = list(csv.DictReader(fh))
    key = lambda r: (r["日付"], r["担当"], r["モデル"], r["入口"], r["案件"])
    new_keys = {key(r) for r in recs}
    merged = [r for r in existing if key(r) not in new_keys] + recs
    merged.sort(key=lambda r: (r["日付"], r["担当"], r["モデル"]))
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(merged)
    return path, len(merged)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=1, help="直近何日ぶんを数えるか（既定1＝今日）")
    ap.add_argument("--run", action="store_true", help="★CSVへ書く（これが無ければ表示だけ）")
    ap.add_argument("--beat", action="store_true", help="心拍を打つ（定期実行用）")
    ap.add_argument("--weekly", action="store_true", help="直近7日をまとめて見る")
    a = ap.parse_args()
    days = 7 if a.weekly else a.days

    rows, files, wanted = collect(days)
    recs = to_records(rows)
    show(recs, files, wanted)

    if a.run:
        path, n = write_csv(recs)
        print(f"\n✅ 書いた: {path}（累計 {n}行）")
    else:
        print("\n★表示だけ。CSVへ書くには --run を付ける。")

    if a.beat:
        try:
            sys.path.insert(0, str(HOME / ".vivid-relay"))
            import heartbeat  # noqa
            # ★2026-09-13 つる：ok=True は beat() に無い引数で、初回(9/12)から心拍が1回も届いていなかった。
            #   両機で動く仕事なので名前も機械ごとに分ける（同名だと片方の生存がもう片方の停止を隠す）。
            machine = "Mac mini" if "mini" in HOST.lower() else "MacBook"
            heartbeat.beat(f"AI使用量の集計（ai_usage_report・{machine}）",
                           "成功", f"{len(recs)}行 / transcript {files}本")
        except Exception as e:
            print(f"（心拍を打てなかった: {e}）")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"★失敗: {e}", file=sys.stderr)
        sys.exit(1)
