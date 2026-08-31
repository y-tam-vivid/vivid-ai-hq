---
name: reference_pending_decision_does_not_pause_the_pipeline
description: 「人の判断待ち」にしても、既に登録済みの自動配布パイプラインは止まらない。止めるなら実行側を止める
metadata:
  node_type: memory
  type: reference
---

**2026-09-01 実地（つる・自己監査で発見）**

ピタゴラスが `intake_notify.py` の「該当なし」通知を実装し、WORKING.md へ
🔴 として **「初回の本番投稿は人の目視を挟むか、判断待ち」** と書いた。

**判断が出る前に、09-01 07:30 に自動発火して Slack へ実投稿された。**
受付シート34・36・38・39・40行目の5件（conversations.history を直接読んで実物確認）。

```
何が起きたか
  実装した人   「判断待ち」と文書に書いた        ← 人が読む場所
  実行する側   daily_jobs.conf 07:22 に登録済み  ← 機械が読む場所
               ＝ 文書の「待ち」を機械は一切見ない
```

**Why:** 「保留」は**人の読む場所**にしか存在しなかった。機械が読むのは
`daily_jobs.conf` の1行と、レジスタの `有効` チェックだけ。
片方に書いて片方に書かないと、**書いた本人だけが止まっていると思っている状態**になる。

**How to apply:**

- **判断待ちにするなら、実行側を実際に止める。** 手段は3つのどれか。
  ①`daily_jobs.conf` の行をコメントアウトする ②レジスタの `有効=False`
  ③スクリプト側にドライラン既定を残す。**どれも取らずに文書へ書くのは「止めた」ではない。**
- **逆に、止めていないなら文書へ「判断待ち」と書かない。** 次の読み手が
  「まだ動いていない」を前提に設計する。
- **★レジスタの `有効=False` は実行を止めない。** あれは監視の対象外にするだけで、
  cron / daily_jobs は独立に走る。実測：この行は `有効=False` のまま本番投稿した。

関連 [[reference_dangerous_entrypoints]] [[reference_monitor_must_exclude_parked]]
[[feedback_stop_asking_just_do_it]] [[project_intake_slack_reply]]
