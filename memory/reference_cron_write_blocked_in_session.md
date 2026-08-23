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

## ★ 5番目の経路がある ── 別マシンから ssh 越しなら書ける（2026-08-20 実測）

**詰まるのは「そのマシンのセッションの中から書くとき」だけ。**

```
mini のセッション内     crontab file          ★返らない（上の4通り）
MacBook から ssh 越し   ssh mini 'crontab f'   ✅ 書けた。照合も一致
```

実測手順（安全な形＝同じ内容の書き戻し）:

```
ssh mini 'BK=/tmp/cron_bk_$(date +%Y%m%d-%H%M%S).txt
          crontab -l > $BK
          crontab $BK          # ← ここが通る
          crontab -l | diff - $BK'
```

→ 26行を書き戻して「成功／一致」。**sshd 配下の別プロセスなので、
セッション側のサンドボックス／TCC の制約に掛からない**とみられる（原因は未確定のまま）。

**How to apply:**

- **「AI側に解決策なし」と結論する前に、別マシンからの ssh を試す。**
  2026-08-20、mini 側は4経路で詰まり「AI側に先がない」と判定したが、
  **MacBook から ssh 越しに書けた。** 経路を1つ数え落としていた
- ただし **cron 投函口（`bin/cron_apply.sh`）は捨てない。** ssh はもう一方のマシンが
  起きている必要があり、mini が単独で自分に登録する手段としては投函口が要る
- **書く前に必ず `crontab -l` をファイルへ退避する。** crontab に「元に戻す」は無い
- ★**未検証のものを cron に載せない。** 2026-08-20 時点で `notion_customer_upsert.py` は
  mini 側の決定により「`--restore` の実地検証が済むまで投函しない」条件。
  **書ける経路が見つかったからといって、載せてよいことにはならない**

**Why:** ここで詰まると「AIは自動実行を作れるのに、自動実行に登録できない」という壊れ方をする。
作ったスクリプトが毎朝走らないまま、レジスタにも載らず、誰も気づかない。
人へ「この1行を貼ってください」と渡すのは筋が悪い ── 有璽氏は mini の画面からコピーできない
（[[feedback_cannot_copy_from_terminal]]）。

## ★★ 日次ジョブの正本は crontab ではない ── `daily_jobs.conf` へ一本化済み（2026-08-20）

**「mini の crontab へ載せる」という問いの立て方自体が、もう古い。**
書き込み障害が直る見込みが立たないため、日次ジョブの正本は移してある。

```
毎日1回のジョブ    ~/vivid-ai-hq/bin/daily_jobs.conf   ★ここが正本。いま動いている経路
                     vivid-sync.sh(*/15) → daily_jobs.sh が読んで実行する
                     定刻を過ぎても次の15分サイクルで拾う（catch-up）
それ以外            bin/cron/mini.cron                  crontab が直った日に入れる投函口
                     ★同じジョブを両方に置かない。移したら投函口側から消す
                       （直った瞬間に2経路で二重に走る）
```

- **障害は 2026-08-23 も未解消**（ドーベルマンが同一内容の書き戻しで再実測。23秒後も
  プロセスは S 状態で生存＝無応答。crontab 本体は無傷）。**3日経っても直っていない。**
- したがって **「cron に載せますか」と聞かれたら、答えは daily_jobs.conf への1行追加**。
  crontab が書けるかどうかを毎回調べ直す必要はない。**塞がっている前提で設計する。**
- ★ただし **crontab 本体の既存25本は今も走っている**。読みは通る。止まったのは書き込みだけ。

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
