---
name: reference_cron_write_blocked_in_session
description: AIのセッションからは crontab を書けない（無応答で返らない）。cron 自身に入れさせる投函口がある
metadata:
  node_type: memory
  type: reference
---

**Claude のセッションから `crontab` へ書き込むと、無応答のまま返らない**（2026-08-20 実測・Mac mini）。

```
crontab -l          通る（読むだけ）
crontab file        ★返らない。プロセスは S 状態で眠り続ける
(…) | crontab -     ★同じ
sandbox を切っても  ★同じ
```

2経路（パイプ／ファイル）× sandbox 有無の4通りで同じ。20秒でも2分でも返らない。
`lsof` も `sample` も取れず、原因は特定できていない（TCC の疑いが濃いが未確定）。

**Why:** ここで詰まると「AIは自動実行を作れるのに、自動実行に登録できない」という壊れ方をする。
作ったスクリプトが毎朝走らないまま、レジスタにも載らず、誰も気づかない。
人へ「この1行を貼ってください」と渡すのは筋が悪い ── 有璽氏は mini の画面からコピーできない
（[[feedback_cannot_copy_from_terminal]]）。

**How to apply:**

```
入れたい行を  ~/vivid-ai-hq/bin/cron/<機械>.cron へ書く（mini.cron / macbook.cron）
   ▼
bin/cron_apply.sh が crontab に無い行だけを入れる（★追加のみ・冪等・消さない）
   ▼
bin/vivid-sync.sh（cron */15）が毎回呼ぶ ＝ **cron から起動された処理なら書ける**
   ▼
確認は ~/Library/Logs/vivid-cron-apply.log と crontab -l の2経路
```

- **投函しただけでは入っていない。** 反映は次の同期（最大15分）。**入ったことを必ず実測で確かめる**
- 番人つき（20秒で諦めてログへ）。同期本体は止めない。**セッションから直接叩くと必ず番人が働く**
- **未検証のものを置かない。** ドライラン／本実行を1回通してから投函する
- 予定時刻は ⚙️自動処理レジスタの「予定」列に合わせる（二重管理を作らない）

関連 [[project_automation_register]] [[reference_mac_mini_execution_env]]
[[reference_launchd_loses_file_access]] [[feedback_verify_before_declining]]
