---
name: reference_overwriting_containers_have_no_past
description: 毎回上書きする器は、作った瞬間から履歴を失っている。定期化する前に「遡れるか」を決める
metadata:
  type: reference
---

**「定期的に更新する」と決めた瞬間、同時に決めなければいけないことがある ── 過去をどこに残すか。**

2026-08-25、有璽氏「**過去のやつは消えますか？ 今のものも、今後含めて遡れますか？**」
実測すると、稼働盤の経路には**履歴を残す処理が1行も無かった**。

```
dashboard_data.json   毎回まるごと上書き   grep "history|snapshot|archive" → 0件
dashboard.html        毎回まるごと上書き   同上 → 0件
＝ 8/23 の数字も 8/24 の数字も、もうどこにも無い
```

**Why:** 「現在地を示す画面」は、性質上いつも最新だけを持つ。**それでよい**。
壊れるのは**定期実行に載せたとき**で、上書きの回数が増えるほど失う過去も増える。
しかも**失ったことに誰も気づかない**（画面はいつも正しく見える）。

**How to apply:**

```
定期実行に載せる前に、必ず2つを分けて決める
  いまを見せる器     上書きでよい（dashboard.html / Artifact の最新版）
  過去を残す器       ★別に要る。上書きの経路とは分ける
```

- **★残す単位は「日ごと最新1本」。**回数で残さない
  → [[reference_retention_by_count_deletes_the_wrong_ones]]（本数で切ると希少な版が消える）。
  2時間おきなら1日12版。全部残すと嵩むうえ、**どれが「その日の姿」か分からなくなる**。
- **★残すのは画面ではなく数字。**HTMLは見た目が変われば比較できなくなる。
  比較できるのは JSON（`{"value","how","as_of"}` の3点セット）。
- **置き場は git 配下にする。**機械ローカル（`~/.vivid-relay/`）に置くと
  もう一方のマシンから見えず、消えても気づかない → [[reference_fix_where_git_reaches]]。
- **Artifact のバージョン履歴は「画面の履歴」であって「数字の履歴」ではない。**
  publish のたびに版が積まれ、`label` が版の名前になる。**画面は遡れるが集計はできない。**
  数字を並べたいなら JSON の履歴が要る。

実装 ── `bin/dashboard_history.py`（2026-08-25 新設）
`dashboard_data.json` を読み、`data/dashboard_history/YYYY-MM-DD.json.gz` へ保存する。
同じ日は上書き（＝その日の最新）。**過去の日は消さない。**1本 約16KB（gzip）＝年間 約5.8MB。

関連: [[project_ops_dashboard_artifact]] [[feedback_artifact_accumulate_dont_replace]]
[[reference_log_needs_an_exit]]（器を作ったら出口を書き出す）
