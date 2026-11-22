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
出し直し  ★push しただけでは出ない。Vercel API の gitSource（ブランチ＋sha）で本番デプロイ（rootDirectory=blog-review/vercel）
          画像を含むので、ファイルを直接送るより git 経由が確実（10/23 2回目から）
```

**★既存の仮公開 lifestandup-preview には足せなかった。** 書き出し一式（static-preview/）は MacBook にしか無く、
クラウドから本番デプロイすると既存ページが全部消える。→ 別プロジェクトで同じ合言葉にした。

**★解析タグを必ず外す。** 公開中ページを型にすると GA4・SalesBreaker・Jetpack統計まで付いてきて、
確認用の閲覧が本番の計測に混ざる。build_review_site.py は外れていないと止まる。

## 本文とサムネイル（10/23 2回目）

- 本文は実施報告を参照して加筆（約1.7倍）。★報告に書かれていることだけで足す（推測の情景描写を入れない）
- サムネイルは既存「Summer Vacation at Stand Up Part 1」の飾りを土台に文字だけ描き直し（make_thumbs.py・League Spartan Black）
- ★報告とお便りの食い違い2件目：7/31 プラネタリウムの番組はお便り「星空」／報告はアニメ番組 → 本文は「映像」でぼかした

## 未決（03/Notion 個人タスクに行あり）

- 写真の元データ（STANDUP LINEアルバム）を Drive へ
- 顔の処理：モザイク か 既存と同じ笑顔スタンプ か
- 7/22 の順番：お便り「31アイス→映画」／実施報告の予定表「映画→31アイス」

## 公開中サイト（固定ページ）の子どもの顔 ── 10/23 差し替え済み

- 集計：固定ページ32本・表示画像77枚を2経路（HTML／実ブラウザ表示）で数え、表示の切り抜きのまま目視。ブログ134本は有璽氏の判断で対象外
- 有璽氏の判断：A1〜A5・B1 を差し替え、Instagram欄など他はそのまま。★モザイク案は取りやめ「丸ごと別の写真」へ
- 実ファイル5枚（A2とA3は重ねて表示される同じ1枚）：voice-3←iv-x-photo／prog-jhs-list←iv-fv-2／iv-k-photo←voice-2／recruit-values-fv←su-fv-main／prog-hs-body←iv-fv-1
- 反映：有璽氏がXサーバーのファイル管理で上書き。本番のハッシュ一致＋実ブラウザ表示で5/5確認（10/23）。元画像は lifestandup-wp 4b6ca3f の親
- ★GitHubのテーマは9/10版で本番(9/14〜)と不一致＝zipを作り直して上げると直しが戻る。写真だけの上書きにした
- ★旧サイトのページ（/trial・/company・/beginners-guide 等）がまだ200で見える。残すかは未判断

## 写真（11/18 受領・反映）

- 現場から58枚（Drive 1J9Pl2omW7iI8PGxJUekwJqGm1gXgyzx7 の part1/part2・ファイル名が〔写真〕枠の名前）。本文は現場OK
- ★顔は既存ブログと同じ「笑顔スタンプ」（有璽氏 11/18。モザイクでは揃わない）。道具 lifestandup-wp/blog-review/stamp_faces.py
- ★顔検出だけでは漏れる（横顔・マスク・眼鏡で8か所）＝全枚を目で見て手で足す。ポスターの絵に誤検出も出る

## テーマとナビ（11/18 本番反映）

- ★本番テーマの元は Drive の 9/14 版ZIP（GitHub の theme/ は 9/10 の古い版＝使わない）。11/18 に 0.2.3→0.2.5-20261118 まで上げた
- コラム（スラッグ column）は名前を「お役立ち情報」に変え、/useful にも並ぶ（ブログ一覧にも残る）。バッジは lsu_flow_cat の 'column'→useful
- ★一覧の列数は 外観→カスタマイズ→「一覧の列数（LIFE STAND UP）」で1〜3列（お役立ち情報＝既定2・お知らせ一覧＝既定1）。PC 861px以上だけ効く。/活動風景/ のカテゴリーページは対象外
- ナビの お知らせ▾ に「お役立ち情報」（/useful）を追加＝Code Snippets #6。正本 bin/web_tracking/lsu_navdrop.html
- ★STAND UP は放課後等デイサービスのみ（児童発達支援は現在行っていない・有璽氏 11/18）。記事で「児発・放デイの事業所」と書かない。11/18 お役立ち情報2本を修正済み（何歳から何歳まで に注釈「小学生以上を対象に放デイ」）
- 2026-11-22 ハロウィン2026を1本版で公開（WP 5845・写真38枚・お子さまは笑顔スタンプ）。2本版（Part.1/2）は確認用サイトに残置。入れる道具 blog-review/wp/post_halloween.py（既定は下書き・--publish で公開）
