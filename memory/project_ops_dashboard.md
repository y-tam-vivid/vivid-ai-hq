---
name: project_ops_dashboard
description: AIエージェントと自動処理の稼働を1枚のブラウザ画面で見る稼働ダッシュボード。有璽氏が自分で見に行ける形が要件。
metadata:
  type: project
---

**有璽氏の要件（2026-08-23）** ──
「各エージェントがどうやって動いているのか、claudeやaiがどう動いているのかを**一元で管理**したい。
それも**私が見に行ける状態**で。エージェントは動いていて、稼働していて、それを私側が見に行ける
ような、**ウェブブラウザーみたいなもの**で確認できるようなもの」

**Why:** 稼働の実体は crontab・daily_jobs・各ログ・⚙️自動処理レジスタ・agents/*.md に散っており、
どれもAIに聞かないと分からなかった。**有璽氏が自分の目で見に行ける面が1つも無かった。**
Slack通知は流れて消える／Notionレジスタは行が48ある。「いま全体としてどうなのか」に答える面が要る。

**How to apply:**

```
データを集める   ~/.vivid-relay/dashboard_data.py    リリス作成・読むだけ
画面にする       ~/.vivid-relay/dashboard_build.py   ビビ作成 → dashboard.html
開く             python3 ~/.vivid-relay/dashboard_build.py     （生成してブラウザで開く）
                 --no-open で開かない ／ --beat で心拍を打つ（定期実行用）
```

- **★静的HTMLは黙って古くなる。** 生成時刻を焼くだけでは「古い版を最新と思って読む」事故
  （[[reference_silent_sync_failure]] と同型）になる。**ページ自身が経過時間を毎分測り直し**、
  30分超で🟡・3時間超で🔴＋「これは過去の状態です」と名乗る作りにしてある。ここを外さない。
- **★数はレジスタと画面の2箇所で数え、食い違ったら画面に出す。** 片方を黙って採らない
  → [[reference_monitor_must_exclude_parked]]（2026-08-23 に検査役2体が違う数字を出した件）。
- **止めてある（enabled=false）は異常に混ぜない。** 既定の表示は「要対応」フィルタ。
- 読むだけ。台帳・Notion・kintone へは書かない。外部CDNも使わない（社外へ何も出ない）。
- **★置き場は `~/.vivid-relay/`（git管理外）＝MacBookへ自動で届かない。** 両機で見るなら
  2本をコピーする → [[reference_fix_where_git_reaches]]。
- **定期生成はまだ載せていない**（2026-08-23 時点）。載せるなら daily_jobs.conf ＋
  ⚙️レジスタ登録＋ドーベルマン検査をセットで。
