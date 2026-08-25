---
name: project_ops_dashboard_artifact
description: 稼働盤（Artifact 98acdc66）が8/23で止まっている。真因は公開経路が無いこと。★公開中の版と機械生成の版が別物で寄せる先が未決
metadata:
  type: project
---

**有璽氏の依頼（2026-08-25）**

> AIエージェントの動きをまとめたURLについて**定期的に更新**してください。結局途中で更新が止まってる。
> **例えば2時間に一度**の頻度などで。 https://claude.ai/code/artifact/98acdc66-a511-45e0-8fb0-523a41728fe4

## 実測 ── 止まっているのは「生成」ではなく「公開」（2026-08-25）

```
dashboard_data.py   mini。動く。2026-08-25 21:55 に実行して最新値を取得できた
dashboard_build.py  mini。動く。dashboard.html を 61,820バイトで書き出した
Artifact への公開   ★ここが無い。最終更新 2026-08-23 のまま
```

**★Artifact の公開は `Artifact` ツールからしかできない。**cron からも GAS からも叩けない。
publish できるのは Claude Code のセッションだけ ―― つまり**人かAIがその場に居ないと更新されない**。
`dashboard.html` は 8/24 10:40 にも生成されていた。**作っていたが、誰も公開していなかった。**

## ★止めた理由 ── 公開中の版と機械生成の版が別物（決着が要る）

上書き公開しようとして中身を突き合わせ、**同じものではない**と分かったので止めた。

| | 公開中（Artifact 98acdc66・8/23） | 機械生成（dashboard_build.py） |
|---|---|---|
| 作り方 | **手で書いた**（`.sec-head` `.pill` `.tablewrap` 等の独自CSS） | 自動生成（`.tile` `.st` `.filters`） |
| 章 | 4章 | 3章 |
| **営業の台帳はいまどうなっているか** | **ある**（443社・法人番号なし171件の3分類まで） | **無い** |
| 自動処理の一覧 | 要約 | 53件・絞り込み・行を開くと備考 |
| エージェント13体 | あり | あり（起動のされ方・最終稼働つき） |
| 更新 | **手でしか作れない＝定期化できない** | **機械で作れる＝定期化できる** |

**★そのまま上書きすると、台帳の章と今の見た目が消える。**
規範「採用されたものを作り直さない」に反するので**publish しなかった**。
→ [[feedback_dont_remake_what_was_approved]] [[feedback_one_route_is_not_verification]]

## 有璽氏に決めてもらうこと（1つだけ）

```
案A  機械生成を正本にする（推奨）
     dashboard_build.py へ「営業の台帳」の章を足す（数字は dashboard_data.json に既にある）
     → 見た目は今の機械版に変わる。★2時間おきの自動更新ができるようになる
案B  手書きの見た目を正本にする
     dashboard_build.py の出力テンプレを手書き版の見た目へ寄せる（工数が増える）
     → 見た目は変わらない。定期化はできるが実装が重い
```

## 定期更新の経路（★どれも未実測。決まってから着手）

```
① mini の cron から claude CLI をヘッドレス起動し Artifact ツールを使わせる
   ~/.npm-global/bin/claude は mini に実在（2026-08-25 実測）。★publish が通るかは未実測
② クラウド routine から publish   ★ローカルの dashboard.html を読めない。データ受け渡しが要る
③ 人がセッションで叩く            いまの状態。★止まる（現に2日止まった）
```

## 済ませてあること

- `bin/dashboard_to_artifact.py` を新設。`dashboard.html` から Artifact 用（骨組みを外した形）へ変換する。
  **★見た目・配色・スクリプトには手を入れない。**`document.body.dataset.generated` が
  `<body>` ごと消える問題だけ `.wrap` へ移して対処。実測で変換できることを確認済み。
- レジスタには「稼働ダッシュボード データ収集 / 生成」の2行が既にあるが**どちらも止めてある**
  （有効オフ）。定期化するならここを有効にし、ドーベルマンの検査を通す。

関連: [[project_automation_register]] [[reference_ran_is_not_succeeded]]
