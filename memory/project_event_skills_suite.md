---
name: project_event_skills_suite
description: 対外イベント運用の6スキル群（event-*）の構成と、有璽氏が定めた5つの約束事。★2026-08-28時点で実体はどこにも無い（実測）
metadata:
  type: project
---

# イベント運用スキル群（event-*）── 構成と約束事

## いまここ（2026-08-28）

**★実体はまだ1本も存在しない。** 有璽氏は「導入した」と述べたが、実測では次のすべてで0件。

```
~/.claude/skills/            8本（cross-check〜thinking-os）。event-* は無し
~/vivid-ai-hq/.claude/skills/  同上（~/.claude/skills はここへの symlink）
origin/main（未取込20件を含む）  git ls-tree で event-* スキルは0件
Mac mini ~/.claude/skills/    event-* は無し
event-skills-for-claude-code.tar.gz   ~ 配下（Library除く）を find して0件
```

**★所在が確定（2026-08-28 有璽氏）** ── tar.gz は **claude.ai チャットの添付としてのみ存在**。
Google Drive には一度も置いていない。**＝人が1回ダウンロードするまで実体はゼロ。**
→ [[reference_two_sessions_built_the_same_thing]]「別の面で作られたファイルは、このマシンには存在しない」

**★受け取りと配布の手順（2026-08-28 決定）**

```
1  有璽氏がチャットの添付を ~/Downloads/ へ保存        ← ★人の手が要るのはここだけ
2  こちらが展開 → ~/vivid-ai-hq/.claude/skills/ へ配置
   （~/.claude/skills はここへの symlink ＝置けば全cwdで読まれる。実測済み）
3  commit & push
4  Mac mini は bin/vivid-sync.sh（15分ごと）で自動受信   ★手で scp しない＝二重管理になる
```

**★Drive経由の base64 は採らない。** バイナリは1バイト崩れると展開できず、失敗が静かに残る。
テキストへばらす案（25ファイル）も写経＝転記事故を増やす。**人が1回落とすのが最短で最も確実。**

届くまでスキル本文は読めない＝要約は書けない。**読んでいないものを「把握した」と書かないこと。**

## 6スキルの構成（有璽氏の説明。原文ベース・未検証）

| スキル | 役割 |
|---|---|
| event-comms-orchestrator | ハブ。配信カレンダー生成・フェーズ判定・各スキルへの委譲 |
| event-db-sync | Notionイベント台帳への起票・更新・照会 |
| event-plan-kit | 企画書・香盤表・役割分担・KPI設計 |
| event-press-kit | プレスリリース（MARK N式8ステップ）・メディアアプローチ |
| event-social-kit | SNS素材（カルーセル/ストーリー/リール）とキャプション |
| event-report-kit | 実施報告書・KPI実績対比・課題と改善策 |

```
event-plan-kit → event-db-sync → event-comms-orchestrator
                                    ├ event-press-kit
                                    └ event-social-kit
                                          ↓
                              event-report-kit → event-db-sync
```

**台帳が起点であり終点。** 企画書のKPI目標値と報告書の実績値は同じスキーマを共有し、
終了後に達成率が自動で成立する設計。

## ★約束事（2026-08-28 有璽氏。スキルの有無に関わらず効く）

1. **Notionには確認なしに書き込まない。** 新規・更新・ステータス変更のいずれも、応答の末尾で
   「Notionへ最新情報を反映しますか？（対象DB：イベント管理DB）」と確認して承認を得てから反映する。
   **読み取りは確認不要。書き込み前に必ず実データを検索して重複を確認する。**
2. **推測してはいけない5項目**
   ①会場の正式表記 ②参加条件（無料/有料・予約要否）③自社の立場（主催/出展/協力）
   ④併記が必要な主催者・共催者名 ⑤数値（定員・過去実績）
   **★写真や既存資料から読み取れても裏取りにはならない。必ず確認を取る。**
3. **ふくち。グループのブランド資料は fukuchi-deck-builder を使う。配色を独自に決めない。**
4. **放デイ LIFE STAND UP の療育イベントは対象外。** そちらは standup-event-notion-importer が担当。
   **event-db-sync は広報を伴う対外イベント専用。**
5. **イベント写真の肖像権処理は必須。** 自動顔検出は横顔・小さい顔を取りこぼす
   → **生成後に必ず目視確認。プレスリリースに使う写真はSNSより厳しく見る。**

## 参照資料

プレスリリースの型の正典は Google Drive「MARK N広報PR研修」フォルダの**第3回資料**。
8ステップはスキルへ落とし込み済みとのことだが、判断に迷ったら原典を確認する。

## 関連

- [[feedback_press_release_is_not_done_at_distribution]] — 配信で終わりでない（ブログ・SNSまでが1セット）
- [[project_npo_press_releases_202608]] — NPO名義リリース2本
- [[project_pr_agent]] — モルガンズ
- [[feedback_confirm_the_deliverable_form]] — 形式・本数・出口を先に確定する
