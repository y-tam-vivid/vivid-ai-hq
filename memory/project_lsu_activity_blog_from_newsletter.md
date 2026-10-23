---
name: project_lsu_activity_blog_from_newsletter
description: LIFE STAND UP の活動ブログを月々のお便り＋Driveの実施報告から書く。確認用ページは lsu-blog-review.vercel.app（Basic認証）。実施報告には実名・個別の様子・金額があり記事に入れない
metadata:
  type: project
---

# LSU 活動ブログ ── お便りから記事を作る（2026-10-23〜）

**有璽氏 10/23「月々のお便りをもとにブログ記事を作れるか」→ 夏休み分で着手。**

```
元資料    掲示用のお便り（写真で受領）＋ Drive 実施報告 12nILnByteX08kLK0wTl6BW9MojXE8T5F（docx 8本）
          ★実施報告は内部記録＝児童/スタッフの実名・特定児童の様子・収支が入っている → 記事には入れない
          ★写真は実施報告に無い。在処は「STANDUP LINEアルバム」＝元データを施設から貰う必要あり
記事の型  公開中ブログ（i-life-fukushi.com/blog）の既存流儀に合わせる
          「Summer Vacation at Stand Up Part.1/2」＝期間ごとに数行事まとめ・冒頭「こんにちは、STAND UPです！」
顔の処理  既存記事は 子ども＝笑顔スタンプ／周囲＝ぼかし。有璽氏の指示は「モザイク」→ どちらで統一するか回答待ち
```

## 確認用ページ（現場に見せる器）

```
URL       https://lsu-blog-review.vercel.app/  （Vercel lsu-blog-review／チーム fuku-chi-vivid）
保護      middleware の Basic 認証。合言葉は環境変数（仮公開サイト lifestandup-preview と同じ値）
実測      10/23 合言葉なし401／あり200（/・part1・part2）。ソース(layout.html等)は404。
          ★curl で <title> まで本物を確認（Security Checkpoint ではなかった）
ソース    ~/lifestandup-wp/blog-review/（vercel/ が出している中身・drafts/ が下書きの正本）
```

**★既存の仮公開 lifestandup-preview には足せなかった。** 書き出し一式（static-preview/）は MacBook にしか無く、
クラウドから本番デプロイすると既存ページが全部消える。→ 別プロジェクトで同じ合言葉にした。

**★解析タグを必ず外す。** 公開中ページを型にすると GA4・SalesBreaker・Jetpack統計まで付いてきて、
確認用の閲覧が本番の計測に混ざる。build_review_site.py は外れていないと止まる。

## 未決（03/Notion 個人タスクに行あり）

- 写真の元データ（STANDUP LINEアルバム）を Drive へ
- 顔の処理：モザイク か 既存と同じ笑顔スタンプ か
- 7/22 の順番：お便り「31アイス→映画」／実施報告の予定表「映画→31アイス」
