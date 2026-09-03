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

---

## ★逆向きの事故 ── 機械の「判断待ち」は、人が答えても解除されない（2026-09-03 実地）

上は「人が止めたつもりでも機械が走る」。**今回は真裏で、機械が止まったまま人の答えが届かなかった。**

```
2026-08-20 09:34  notify.ask() が「台帳→Notion の同期を載せてよいか」を Slack へ投げ、
                  slack_pending.json を書いた
                  ★notify.pending() が None 以外を返す間、後続は一切先へ進まない設計
2026-09-03 15時台 ★14日間そのまま。この1件が findings_escalate.py の出口を塞ぎ続けていた
                  （系統Aの指摘3件＝6日連続の重複21組ほかが、1件も人へ届いていなかった）
```

**Why:** `answered` を立てられるのは `slack_inbox.py`（Slackスレッドの返信を読む）**だけ**。
有璽氏はこの日 Claude Code の会話で「載せましょう」と答えた。**答えは確かに存在したのに、
機械が見ている場所には無かった。** slack_inbox.py は 9/3 14:30 まで正常稼働していた
（＝壊れていない。見る場所が1つしか無かった）。

**★さらに悪いのは、塞がっていることが誰にも見えなかったこと。** `pending()` は
「判断待ちがある」としか言わない。**いつからか・何を塞いでいるかを誰も出していない。**

**How to apply:**

- **★`ask()` を呼ぶ設計にするなら、答えを受け取る口を2つ以上持つ。** Slackスレッドだけに
  依存しない（会話で答えられた場合に永久に届かない）。→ [[feedback_one_route_is_not_verification]] と同じ形。
- **★judgment待ちには寿命を持たせる。** `findings_escalate.py` の `PENDING_STALE_HOURS=24`
  はこの型への正しい対処だが、**それ自体が塞がれた pending の下流に居たため一度も効かなかった。**
  寿命の判定は、塞がれる側ではなく塞ぐ側（`notify.pending()`）に置く。
- **★毎朝の報告に「何日塞がっているか」を出す。** 沈黙は正常と区別がつかない
  → [[reference_a_warning_nobody_owns]] [[reference_heartbeat_proves_life_not_results]]。
- 解除は `slack_pending.json` へ `answered` / `answered_text` / `answered_at` を書く
  （ビビが手で書いてよい。バックアップを取ってから、書いた後に `notify.pending()` が
  None を返すことを実測する）。

## ★口を増やしても直らなかった ── 答えは受けたが、塞いでいる台帳に戻らない（2026-09-04 つる）

上の「答えを受け取る口を2つ以上持つ」を実行した結果が、翌日そのまま同じ形で再発した。

```
2026-09-03 20:14  ピタゴラスが ask_hub で #2df0d8 を投げた
                  ★件名も選択肢も slack_pending.json の原文をそのまま載せ、
                    「塞いでいるのはこちらです」と明示して聞いている
2026-09-03 20:14  有璽氏がボタンを押した → ask_hub_queue.json は status:answered
2026-09-04 08:30  findings_escalate が起動 →「★既に新しい判断待ち（24時間以内）の
                  Slack ask が残っています。新たには送りません」で送信0件
                  ＝系統A 3件（7日連続の重複21組ほか）は今日も誰にも届かなかった
```

**Why:** 口は2つになった。**だが答えの置き場も2つに分かれた。**
`ask_hub.py` と `slack_socket.py` は設計として
「`notify.py` の `slack_pending.json` には一切触らない」と明記している（混ぜない、が意図）。
**その分離自体は正しい。欠けていたのは「答えたという事実を、塞いでいる側へ返す1本」だけ。**

**さらに悪い形になった点** ── 24時間の寿命判定（`PENDING_STALE_HOURS`）は、
ボタンで新しい ask が立つたびに**時計が巻き戻る**。
**答えれば答えるほど「新しい判断待ち」が増えて出口が閉じ続ける**構造になっている。

**How to apply:**

- **★「答えの台帳」と「塞ぐ台帳」を分けるなら、答えたときに塞ぐ側を解除する経路を必ず1本引く。**
  分離してよいのは保存先であって、**状態の同期まで分離してはいけない。**
- **★ある台帳の原文をコピーして別の台帳で聞かない。** 聞いた先で答えが確定しても、
  引用元は「聞かれたまま」で残る。聞くなら、答えが戻る側で聞く。
- **★寿命の起点は「最後に聞いた時刻」ではなく「最初に塞がれた時刻」に置く。**
  今の実装は前者なので、催促するほど期限が延びる。
- 2026-09-04 につるが `slack_pending.json` へ `answered` を書いて解除した
  （控え `~/.vivid-relay/_backups/slack_pending.json.bak_20260904-tsuru`・
  `notify.pending()` が None を返すことを実測）。**これは応急処置で、経路は直っていない。**

## ★同じ日に踏んだ「申告と実物の食い違い」（2026-09-03）

pending を解除して `findings_escalate.py` を初めて通したら、**即座に落ちた。**

```
実測  経路1 実行     TypeError: open_findings() got an unexpected keyword argument 'category'
      経路2 ソース   findings_tracker.py に SOURCE_CATEGORY は 0 件。open_findings に category 引数なし
                     bin/hooks と .vivid-relay の2本は sha256 完全一致 ＝ 配布漏れではなく★未実装
```

**呼ぶ側（findings_escalate.py）だけができていて、呼ばれる側が無かった。**
担当は「実装・ドライラン確認済み」と報告していた。**ドライランは、塞がれた pending の手前で
早期 return していたため、壊れている行まで到達していなかった。**

- **★「ドライランが通った」は「全部の行を通った」ではない。** 途中で return する経路があると、
  その先は未実行のまま緑になる。**どこまで到達したかを出力で示させる。**
- **★呼ぶ側と呼ばれる側は別々に確かめる。** 片方だけを見て「実装済み」と読まない。

関連 [[reference_dangerous_entrypoints]] [[reference_monitor_must_exclude_parked]]
[[feedback_stop_asking_just_do_it]] [[project_intake_slack_reply]]
[[feedback_one_route_is_not_verification]] [[reference_a_warning_nobody_owns]]
[[feedback_use_the_team_not_alone]]
