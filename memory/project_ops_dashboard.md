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

## ★2026-09-07 10分おきへ（有璽氏「リアルタイムは無理なん？」・案A）

**daily_jobs.conf の kadoban_0810〜2210（2時間おき8本）→ crontab 直接 `*/10` へ移行。**
理由：daily_jobs.conf は「1日1回・状態ファイルで管理」の設計で10分おきに合わない。
**crontab への書き込みは2026-08-20時点で無応答だったが、今回実測したところ直っていた**
（RC=0・10秒以内に返る。既存crontabを無変更で書き戻しdiff一致で確認）。

- **詰まりの手当てを先に入れた**（有璽氏「今日1回vercel deployが53分応答なし」への対応）。
  `bin/run_with_timeout.py`（新設・`os.setsid()`+`os.killpg()`でプロセスグループごとkill。
  macOSのbash/zshに`timeout`コマンドが無いため）で deploy・env ls とも既定300秒×2回まで、
  2回連続タイムアウトでSlack通知して`exit 1`（黙って死なない）。
  二重起動防止はmkdir方式のロック（stale lock自動奪取つき）。
  **実測（隔離環境・タイムアウト値を短縮して検証）**：詰まり時rc=1・7秒で終了・通知送信・
  ロック解放を確認／二重起動時は後発がrc=0でスキップしログに残す／stale lock奪取も確認／
  正常系（詰まらない場合）もrc=0・URL取得・401確認まで通ることを確認。
- **★実装中に踏んだ罠**：コマンド置換 `$(deploy)` の中で `exit 1` を呼んでも
  サブシェルしか終わらず、スクリプト全体はrc=0で完走してしまう不具合を1回作った
  → [[reference_bash_subshell_exit_pitfall]]。戻り値＋グローバル変数方式に直した。
- **★依頼は`vercel deploy`のみを想定していたが、`vercel env ls`（環境変数チェック部分）も
  同様に詰まりうることが実測で判明**（隔離テストで本物のnpxがVercel未認証のデバイス
  認証フローに入ってハングした）。ここもタイムアウトで保護した。
- 案B（数字だけを外部ストアへ出し30秒おきに読む・真のリアルタイム化）は**設計のみ提示**。
  実装していない。`~/.vivid-relay/kadoban_realtime_案B.md`（git管理外）。
  置き場（Supabase／Vercel Edge Config／Blob）と機微の線引き（案件名を出すか番号化するか）は
  有璽氏の判断待ち。

## ★2026-09-08 案Bを実装（有璽氏「案Bはそのまま出す。Aで問題ない」＝③-A採用）

**置き場は Vercel Blob（private store）に決めた。実測で選んだ理由：**

```
Supabase       見送り。新しい外部アカウント・認証を増やす（両機に同じ環境を、に逆行）
Edge Config    見送り。CLIに専用サブコマンドが無くREST API実装が要る／1件あたりの
               サイズ上限が小さく今回のデータ(約23KB)には合わない可能性が高い（未実測のまま除外）
★Vercel Blob   採用。`vercel blob create-store <name> --access private` で private store が
               作れることを実測（想定外＝publicしか無いと思っていた）。同一Vercelプロジェクトに
               繋がる（外部サービスが増えない）。トークン無しの直接GETは403（実測・閉域が保てる）。
               CLI経由のPUTは1回1.3〜1.5秒（実測3回平均）。cronの最小PATH環境でも動作確認済み
```

**構成**

```
mini: dashboard_data.py（既存・無改修）
mini: dashboard_realtime_push.py（新規・git管理外）
        dashboard_data.json から summary/agent_activity/projects_major だけ抜いて
        （約23KB）Vercel Blob（pathname=kadoban/realtime.json）へ全置換pushする。
        失敗しても案A本体を止めない設計で crontab へ `|| true` 付きで追記
web/kadoban/api/data.js（新規・git管理下）
        Vercel Serverless Function。BLOB_READ_WRITE_TOKEN でBlobから読んで返すだけ
        （@vercel/blob SDK不使用・依存追加なし）。失敗時も必ずHTTP200＋{ok:false,stale:true}
        を返す設計＝呼び出し元JSがエラー分岐しやすい。★のBasic認証(middleware.js)の
        matcherは/api/を除外していないので、このFunctionにも閉域がそのまま掛かる（実測）
mini: dashboard_build.py（改修）
        agent-chip に data-agent-key、proj-row に data-proj-name を付与。
        30秒おきに /api/data.json を fetch する rtPoll() を追加。取得失敗時は
        直前の表示を壊さず、rt-fresh の文言と色だけを変える（DOM要素は残す）
bin/kadoban_deploy.sh（改修・1点のみ）
        $SITE/api/ へ web/kadoban/api/data.js を運ぶ処理を追加。無くても本体は壊れない
```

**🔴重要な発見：Vercel無料プランには1日あたりのデプロイ回数上限（約100回）がある。**
実装当日に本番デプロイ・Preview デプロイとも `"code":"api-deployments-free-per-day"` で
拒否された（`vercel deploy`・`vercel deploy --prod` の両方で再現・24時間はリトライ不可）。
**10分おきの案Aは1日144回デプロイを試みる設計で、この上限に構造的に近い（または既に超えている）。**
案Bへ移行する動機（「出し直しを無くす」）が、この実測によって裏付けられた形。
**★この制限により、今回の実装は「本番での通し確認（画面を開いたまま数字が実際に切り替わる
瞬間）」が未確認のまま。** 単体レベル（data.jsのhandlerを直接呼び出し・成功/トークン無し/
不正トークンの3ケース）・crontabへの安全な追記（`|| true`で案A本体を止めない・cron最小
PATH環境での動作確認済み）・Basic認証の閉域維持（旧デプロイでも `/api/data.json` が
合言葉なしで401）は実測済み。**次に10分おきのcronがデプロイに成功した回（デプロイ上限が
明けた後）で、実際に30秒ごとに画面の数字が動くことを1回目視確認すること。**

- **★機微の線引きは有璽氏の決定で③-A（案件名・担当名をそのまま出す）に確定。** 番号化（③-B）は
  不採用。稼働盤の中身が丸ごとBlobへ乗る点は本体（index.html）と変わらず、リスクの性質は
  「保存場所が外部インフラへ増える」点のみ（Basic認証と同じ閉域の内側にとどめてある）。
