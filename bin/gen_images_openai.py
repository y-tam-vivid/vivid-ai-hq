#!/usr/bin/env python3
"""OpenAI の画像APIで、プロンプトJSONの全枠をまとめて生成する。生成→測定→不合格は作り直し。

★お金が動く。既定はドライラン（1円も使わない）。実際に生成するのは --run のときだけ。
  → fukuchi-core「承認が要る操作：お金（課金・契約・発注）」

なぜ要るか ── 2026-09-08、地域ポータル「かわちばなし」の14枠を作り直すため。
1枚ずつ画面で作ると、枠ごとに明るさがバラつく（それがそもそもの不具合だった）。
**共通指定を1か所に持ち、全枠を同じ条件で一度に作る**のがこのスクリプトの目的。

鍵の置き場
    ~/.vivid-relay/config.env に  OPENAI_API_KEY=sk-...  を1行足す（既存4件と同じ形）
    ★環境変数 OPENAI_API_KEY があればそちらを優先する
    ★両機に同じものを入れること（fukuchi-core「マシンと実行の置き場」）

使い方
    python3 bin/gen_images_openai.py scratchpad/kawachibanashi_prompts.json --out ~/kb_images
        → ★ドライラン。何枚・いくらの見込みかを出すだけ。APIを叩かない
    python3 bin/gen_images_openai.py ... --out ~/kb_images --run
        → 実際に生成する
    python3 bin/gen_images_openai.py ... --out ~/kb_images --run --only v2-hero,v2-ev-feature
        → 枠を指定して2枚だけ

出来たもの
    <out>/<id>.png            画像
    <out>/_result.json        1枠ごとの測定値と合否
"""
import argparse
import base64
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from image_tone import judge, measure  # noqa: E402

API = "https://api.openai.com/v1/images/generations"
CONFIG = pathlib.Path.home() / ".vivid-relay" / "config.env"

# ★1枚あたりの概算（USD）。2026-09-08 に第三者のまとめ1経路でしか確かめていない。
#   公式ページはトークン単価のみで1枚換算を載せていない。実額はダッシュボードで見ること。
COST_HINT = {("gpt-image-1.5", "high"): 0.133, ("gpt-image-1.5", "medium"): 0.05,
             ("gpt-image-1-mini", "medium"): 0.005, ("gpt-image-1-mini", "low"): 0.005}

# 不合格のときに足す言葉。★プロンプトを書き換えるのではなく、末尾に足すだけにする
RETRY_HINT = {
    "明るさ": "もっと明るく。真昼の順光で、全体が白っぽく見えるくらい明るくする。",
    "暗部": "黒く沈む部分をなくす。影を薄くし、暗い背景や物陰を画面に入れない。",
    "彩度": "色を少し落ち着かせる。派手な原色にせず、自然な発色にする。",
}


def load_key():
    """環境変数 → config.env の順で鍵を探す。★見つからない理由まで言う。"""
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key.strip(), "環境変数 OPENAI_API_KEY"
    if CONFIG.exists():
        for line in CONFIG.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip(), str(CONFIG)
    return None, None


def generate(key, model, prompt, size, quality, timeout=300):
    """1枚だけ生成する。戻り値は PNG のバイト列。"""
    body = json.dumps({"model": model, "prompt": prompt, "size": size,
                       "quality": quality, "n": 1}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    item = d["data"][0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    with urllib.request.urlopen(item["url"], timeout=timeout) as r:  # 旧形式への保険
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompts_json")
    ap.add_argument("--out", required=True, help="画像の保存先ディレクトリ")
    ap.add_argument("--run", action="store_true", help="★実際に生成する（課金される）")
    ap.add_argument("--model", default="gpt-image-1.5")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--only", default="", help="枠idをカンマ区切りで指定")
    ap.add_argument("--max-retry", type=int, default=2, help="不合格のとき作り直す回数")
    a = ap.parse_args()

    spec = json.loads(pathlib.Path(a.prompts_json).read_text(encoding="utf-8"))
    common, slots = spec["common"], spec["slots"]
    if a.only:
        want = {s.strip() for s in a.only.split(",") if s.strip()}
        slots = [s for s in slots if s["id"] in want]
        missing = want - {s["id"] for s in slots}
        if missing:
            print(f"★--only に指定されたが見つからない枠: {sorted(missing)}", file=sys.stderr)

    per = COST_HINT.get((a.model, a.quality))
    n_max = len(slots) * (1 + a.max_retry)
    print(f"枠 {len(slots)}件 ／ モデル {a.model} ／ 品質 {a.quality}")
    if per:
        print(f"概算 ${per * len(slots):.2f}（作り直しが最大まで走ると ${per * n_max:.2f}）"
              f"  ★1経路でしか確かめていない概算。実額はダッシュボードで見ること")
    else:
        print("★この モデル×品質 の1枚単価は手元に無い。実額はダッシュボードで見ること")

    if not a.run:
        print("\n★ドライラン。APIを叩いていない。実行するには --run を付ける。")
        for s in slots:
            print(f"  {s['id']:<16} {s.get('枠', ''):<28} {s['size']}")
        return 0

    key, where = load_key()
    if not key:
        print(f"★鍵が無い。{CONFIG} に OPENAI_API_KEY=sk-... を1行足すか、"
              "環境変数 OPENAI_API_KEY に入れること。", file=sys.stderr)
        return 1
    print(f"鍵の在り処: {where}\n")

    out = pathlib.Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    results, calls = [], 0

    for s in slots:
        prompt = common + "\n\n" + s["prompt"]
        path = out / f"{s['id']}.png"
        row = None
        for attempt in range(a.max_retry + 1):
            try:
                png = generate(key, a.model, prompt, s["size"], a.quality)
                calls += 1
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")[:300]
                print(f"× {s['id']}  HTTP {e.code}  {detail}")
                row = {"id": s["id"], "error": f"HTTP {e.code}: {detail}"}
                break
            except Exception as e:
                print(f"× {s['id']}  {type(e).__name__}: {e}")
                row = {"id": s["id"], "error": f"{type(e).__name__}: {e}"}
                break
            path.write_bytes(png)
            m = measure(path)
            ng = judge(m)
            row = {"id": s["id"], "枠": s.get("枠", ""), "path": str(path),
                   "試行": attempt + 1, **{k: m[k] for k in
                   ("lightness", "saturation", "dark_ratio")}, "ng": ng}
            mark = "○" if not ng else "×"
            print(f"{mark} {s['id']:<16} 試行{attempt + 1}  明るさ{m['lightness']:5.1f} "
                  f"彩度{m['saturation']:5.1f} 暗部{m['dark_ratio']:5.1f}%"
                  + ("   " + " / ".join(ng) if ng else ""))
            if not ng:
                break
            if attempt < a.max_retry:      # 不合格の理由に応じた一言を足して作り直す
                add = {RETRY_HINT[k] for k in RETRY_HINT if any(k in x for x in ng)}
                prompt = common + "\n\n" + s["prompt"] + "\n\n" + " ".join(sorted(add))
                time.sleep(1)
        results.append(row)

    ok = sum(1 for r in results if r and not r.get("ng") and not r.get("error"))
    ls = [r["lightness"] for r in results if r and "lightness" in r]
    spread = round(max(ls) - min(ls), 1) if ls else None
    (out / "_result.json").write_text(json.dumps(
        {"model": a.model, "quality": a.quality, "api_calls": calls,
         "spread": spread, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n合格 {ok}/{len(results)}   枚数間のひらき {spread}   API呼び出し {calls}回")
    print(f"結果 {out / '_result.json'}")
    print("★数値が通っても、必ず実物を目で見てから採用すること（数値は1経路目）。")
    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    sys.exit(main())
