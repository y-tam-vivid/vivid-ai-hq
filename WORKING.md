# いま手をつけているもの

> **毎ターン自動で読まれる。** 目的は1つ ── **二重に手をつけるのを、着手する前に止めること。**
> ここには「いま誰が何を触っているか」だけを置く（1ブロック＝何を／どこまで／次に何を待つか／★同じ対象に手をつけないでください）。
> **ずっと変わらない決まり（使い方・衝突の決め方・判断はSlackのボタン・触ってはいけないもの・呼称）は
> Obsidian `00_System/16_同時作業の決まりと触ってはいけないもの.md` が正本。** 着手前に一度読む。
> 経緯は memory の本文か ⑥ログへ。上限15KB・棚卸しは `00_System/15_毎ターン届くMDの作り方と更新方法.md`。
> 降ろした全文：`_archive/WORKING_完了ログ_{20261011,20261008,20261003,20260825}.md`

---

## Mac mini セッション

### 【リリス / mini 2026-10-06】かわちばなし：kb_live.sh の未反映3件 ── ★有璽氏のデプロイ判断待ち
- 実装済み・本番未反映：①イベント静的ページ ②合言葉を外す前の片付け ③Clarity ytbpus9k6u（結果 `~/.vivid-relay/kawachi_{eventpages,cleanup,clarity}_result.md`）
- **★同じ対象に手をつけないでください**: `~/.vivid-relay/kb_live.sh`

### 【ピタゴラス / mini 2026-10-06】かわちばなし：週次見張り `kb_watch.py` ── ★cron前（レジスタ行の相談→ドーベルマン点検 待ち）
- **★同じ対象に手をつけないでください**: `~/.vivid-relay/kb_watch.py`

## MacBook セッション

- **【ビビ / 10/02〜】家計台帳 ⇄ 営業台帳** ── 開発用で送信経路は通った（経緯 `memory/project_kakei_daicho.md`）。▶相手待ち：本番の窓口と鍵／商標の確認。★有璽氏の判断待ち：`#5dedca` Se20の持分の割合。
  **★同じ対象に手をつけないでください**: 営業ワークブック `02_個人マスタ`（総合ステータス列・検討時期列V）／`90_選択肢マスタ` 末尾2列／`~/.vivid-relay/{crm_dev.env,crm_key_check.sh,kakei_payload_20261007.*}`／`memory/{project_kakei_daicho,project_toc_customer_ledger,reference_dropdowns_prevent_value_sprawl}.md`
- **【ビビ / 10/10〜】医療連携システムの自社開発（運営者版）** ── 実装 段階1＋検査の直し済み（テスト138件）。▶ステラの再検査が未実施。次の段は有璽氏の判断（安全の設定の上限値・検証者・代理・PostgreSQL）とお金の流れ10問の回答待ち。経緯 `memory/project_iryo_renkei_system.md`。
  **★同じ対象に手をつけないでください**: `scratchpad/iryo-renkei/`・`scratchpad/_restricted_iryo/`（設計/実装担当に渡さない）・`~/iryo-renkei-app`
- **【ビビ / 10/05〜】かわちばなし** ── 本番＝17版＋`kawachibanashi.osaka.jp`（合言葉中）。▶2件が止まっている（10/11 mini へ届かない原因は解消＝Tailscale経由で再開できる）：①10/10 団体回答の反映 ②18版（承認済み・出す前に写真7枚の src と日本語名の href を直す。手順書 Drive `04_ClaudeCodeへの引き継ぎ/引き継ぎ_18版を本番へ反映_20261011.md`）。🔴残：@media 未対応／申込締切後の見せ方／Search Console→合言葉を外す。手順 `memory/project_kawachibanashi_portal.md`。
  **★同じ対象に手をつけないでください**: シート `1mRp6Cx…`（「イベント」タブ・kb-0051/0053〜0058）／`kb_live.sh`／`~/.vivid-relay/kb_collect.py`／`bin/web_tracking/sites.json` のかわちばなしの行／`~/kb_build`／`~/kb_live`
- **【ビビ / 10/03〜】こどもステーション団体サイト** ── 本番 v54・Ad Grants 承認済み。▶キャンペーン作成は本人確認で停止中＝**再開 10/14**。公開は必ず最新番号から（直しの正本 `~/kodomo-photo-work/*_fixes.py`）。
  **★同じ対象に手をつけないでください**: さくらの DNS（ko-station.org）／Vercel のドメイン設定／`~/kodomo-photo-work/{oct3_fixes,apply_oct3}.py`
- **【ビビ / 10/08〜】119番 医療連携LP（児童/就労×A/B/C）とSBフォーム営業の準備** ── 書く：公開用LPフォルダ・SBの文面下書き（保存は要承認）。
  **★同じ対象に手をつけないでください**: 医療連携LPの公開用フォルダ／SB template（医療連携）
- **【ビビ / 10/08〜】全公開サイトへSBタグ＋クリックログ** ── 7サイト反映済み。▶残はビビッド1サイト＝WPのログインURL待ち。共用 GTM-PQX3L4TQ。
  **★同じ対象に手をつけないでください**: `~/.vivid-relay/sbtag/`
- **【リリス / 10/05〜】公開中サイトへ Clarity＋SEO標準装備** ── 4サイト設置済み。▶ビビッドのみ保留（WPログインURL不明）／SKILL.md 追記は承認待ち／10/12 週次初回／11/1 月次初回→旧クラウド月次 trig_01Y9 停止。
  **★同じ対象に手をつけないでください**: 上記サイトの head／`bin/web_tracking/{clarity_daily,weekly_seo_report,monthly_seo_report,ai_analysis}.py`／mini crontab の SEO 3行
- **【ビビ+チョッパー / 10/06】Web制作の出戻り対策** ── ★有璽氏の判断待ち4件（本番の入口／resize or reload／8750固定を外すか／重なりの目視精査）。
  **★同じ対象に手をつけないでください**: mini `~/lifestandup-wp/{sweep_widths_fast.py,sweep_widths.py,tools/lsu_env.py}`／ポート8750
- **【ビビ / 10/08〜】日々のメモの振り分け** ── 試作・検査済み（mini `memo_sort.py`・cron未登録）。▶デイリーノートが数日分たまったら dry-run。
  **★同じ対象に手をつけないでください**: mini `~/.vivid-relay/memo_sort.py`
- **【ビビ / 10/09〜】定期タスクの自動起票** ── 稼働中（mini cron 毎朝7:05・10/11 07:05 成功をレジスタで確認）。
  **★同じ対象に手をつけないでください**: mini `~/.vivid-relay/recurring_tasks.py`／Notion「🔁 定期タスク台帳」

## Claude Desktop セッション

> SalesBreaker 関連のやり取りはここで行われている（2026-08-13 有璽氏）。こちらからは書かない。

---

*最終更新: 2026-10-11 / MacBook ビビ（有璽氏「Obsidian導入後の思考で整理して」＝変わらない決まりを 00_System/16 へ移し、各ブロックを進行中だけに）*
