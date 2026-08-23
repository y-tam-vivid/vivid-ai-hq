---
name: reference-slack-tokens-and-socket-mode
description: Slackのトークンは2種類あり役割が違う。app-level(xapp-)はSocket Mode専用で、bot(xoxb-)の代わりにはならない。miniに両方あるが消費するコードは0本
metadata:
  type: reference
---

# Slackのトークンは2種類ある ── 「鍵はあるが、それを使う口が無い」

**2026-08-23 実測。** 有璽氏から `xapp-1-...` を受領 → 既に mini の
`~/.vivid-relay/config.env` に**同じ値が入っていた**（12:58 に誰かが投入済み）。
受け取ったから入れる、の前に**入っているかを実測する**。上書きは事故になる。

```
xoxb- (SLACK_BOT_TOKEN)   58文字   Web APIを叩く鍵
                                   chat.postMessage / auth.test など「こちらから送る」
                                   ★議事録botの通知(#09_事務-議事録管理bot)はこれで動いている

xapp- (SLACK_APP_TOKEN)   98文字   Socket Mode専用の鍵
                                   apps.connections.open で WSS の口を開き
                                   「Slack側からイベントを受け取る」ためだけに使う
                                   ★chat.postMessage には使えない。互いの代用にならない
```

## 生死の確かめ方（値を画面に出さずに測る）

```
bot   curl -s -X POST https://slack.com/api/auth.test               -H "Authorization: Bearer $SLACK_BOT_TOKEN"
app   curl -s -X POST https://slack.com/api/apps.connections.open   -H "Authorization: Bearer $SLACK_APP_TOKEN"
      → ok:true と url が返れば有効（2026-08-23 実測 ok=true）
```

`ok:false` を見ずに空の結果を「無い」と読むと権限があるのに無いと報告する
（→ [[feedback_never_write_an_unmeasured_number]]）。**必ず `ok` を見る。**

## ★いまの状態 ── 鍵は有効。だが使う側が存在しない

`SLACK_APP_TOKEN` を読むコードは **vivid-ai-hq にも ~/.vivid-relay にも 0 本**（grep 実測）。
Socket Mode の常駐プロセスは未実装。**入れた＝動く、ではない。**
「Slackから話しかけて動かす」をやるなら、ここから受け口を作る必要がある。

## ★MacBook には無い

`~/.vivid-relay/config.env` は **git 管理外**なので自動で届かない
（→ [[reference_fix_where_git_reaches]]）。両機統一の原則に対して、Slackの鍵は
**mini にしか無い状態が続いている**（2026-08-20 に SLACK_BOT_TOKEN で同じ事故）。
手で運ぶしかない。運んだら **MacBook 側でも実際に叩いて**確かめる
（→ [[feedback_batch_the_checks]]）。

## 平文で渡ってきた鍵は、渡った経路に残る

今回の xapp- は Slack DM に平文で流れた＝Slackの履歴に残る。
危険度は「Socket Modeの口を開ける」だけだが、**不要になったら Slack API 管理画面で
revoke する**のが素直。ローテーションは有璽氏の操作。
