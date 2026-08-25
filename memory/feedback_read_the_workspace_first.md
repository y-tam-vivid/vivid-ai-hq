---
name: feedback_read_the_workspace_first
description: 作業を始める前に cwd の START_HERE/AGENTS/README/.env を読む。読まずに「できない」と3回言い、有璽氏に2度指摘させた
metadata:
  type: feedback
---

**着手前に、いまいるディレクトリに置かれているものを読む。**
`START_HERE.md` `AGENTS.md` `README.md` `.env`（キー名だけ）`docs/` の一覧。これだけ。

## 2026-08-23 に起きたこと

cwd は `~/Downloads/JapanGtmAgentWorkspace`。**セッションの最初から最後までこの中にいた。**
中身は ── **「JAPAN GTM Agent Workspace powered by SalesBreaker」**
＝ SalesBreaker を AI エージェントが操作するための公式パック。

```
.env                              SALESBREAKER_API_KEY  ★鍵はここに在った
START_HERE.md                     操作境界・認証・使えるルート一覧（9KB）
AGENTS.md                         エージェント向けの作法（5KB）
docs/salesbreaker-*.md            API仕様13本（リスト品質・CRM出力・権限・制限とエラー…）
saved-lists / campaigns /
analytics / reports / templates    作業用の器
```

**一度も開かずに、こう答えていた。**

| 当方の発言 | 実際 |
|---|---|
| 「APIキーが無いので送信の口は叩けない」 | `.env` に在った |
| 「管理画面への投入と送信は人の手」（3回） | NGリスト一括登録もテンプレ保存もAPIで可能 |
| 「Apps Scriptのスコープが無いので無理」 | GASは要らない。直接叩ける |

**有璽氏に2度言わせた** ── 「こちらの追加はそちらで設定できますか？」「いや、前はやったからできるよ。」

## なぜ起きたか

**`~/vivid-ai-hq` の規範と memory は毎ターン届くので、それを読めば十分だと思い込んだ。**
届く経路ばかり見て、**足元に置かれたものを見なかった**。
`START_HERE.md` は「ここから始めよ」という名前で、cwd の直下にあった。

「読むもの一覧は地図でない・起点1枚から辿る」（[[feedback_reading_list_is_not_a_map]]）を
守っているつもりで、**その起点が cwd に置いてあることに気づいていなかった**。

## How to apply

```
セッションの最初に1回      ls -a して、START_HERE / AGENTS / README / .env / docs を探す
                          あれば読む。無ければ無いと分かる。★30秒で終わる
「できない」と言う前に      その判断の根拠に、cwd の中身を数えたか
道具の在り処              グローバル（~/.vivid-relay・~/vivid-ai-hq）だけでなく
                          ★プロジェクト直下にも置かれる。両方見る
```

**「経路を数える」と言いながら、自分が立っている場所を数えていなかった。**
→ [[feedback_verify_before_declining]] ／ [[feedback_one_route_is_not_verification]]
