"""data/*.json（掲載の正本）を index.html の DATA 区間へ書き込む。

掲載するのは _meta.show が true のものだけ。kind は3つ：
  sample＝架空の見本／draft＝実在・本人の確認前（画面に「掲載内容は確認中」）／real＝実在・承諾済み（_meta.consent が無いと止める）
画面には sample と pending（確認中か）だけを渡し、社内の紐付け（meikan_id など）は出さない。
使い方：python3 scratchpad/f119-portal/render_data.py  → そのあと build_public.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEGIN, END = "/*DATA:BEGIN*/", "/*DATA:END*/"
SETS = [("C", "partners"), ("V", "voices"), ("M", "facilities")]


def load(name):
    rows = json.loads((HERE / "data" / f"{name}.json").read_text(encoding="utf-8"))
    out = []
    for r in rows:
        meta = r.get("_meta", {})
        if not meta.get("show"):
            continue
        kind = meta.get("kind")
        if kind not in ("sample", "draft", "real"):
            raise SystemExit(f"{name}/{r.get('id')}: kind が不明（{kind}）")
        if kind == "real" and not meta.get("consent"):
            raise SystemExit(f"{name}/{r.get('id')}: 実在の掲載なのに承諾（_meta.consent）が空")
        rec = {k: v for k, v in r.items() if k != "_meta"}
        rec["sample"] = kind == "sample"
        rec["pending"] = kind == "draft"
        out.append(rec)
    return out


def main():
    p = HERE / "index.html"
    s = p.read_text(encoding="utf-8")
    i, j = s.index(BEGIN), s.index(END) + len(END)
    body = "\n".join(f"const {var}={json.dumps(load(name), ensure_ascii=False)};" for var, name in SETS)
    p.write_text(s[:i] + BEGIN + "\n" + body + "\n" + END + s[j:], encoding="utf-8")
    print("DATA 区間を更新:", ", ".join(f"{n} {len(load(n))}件" for _, n in SETS))


if __name__ == "__main__":
    main()
