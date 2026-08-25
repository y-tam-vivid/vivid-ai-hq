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

## ★ただし「受け口が無い」は誤り ── ポーリング版が既に稼働中（2026-08-23 ロビン実測）

**「Slackから話しかけて動かす」は、用途としては既に動いている。** Socket Mode が
無いだけで、受け口そのものは在る。**無い前提で新規に作ると二重になる。**

```
crontab（mini・実測）
  */5  slack_inbox.py --run --beat     有璽氏とのDM(D0AT4NQ6X7D)を5分ごとに読み
                                       claude CLI へ渡して実行し結果をDMへ返す（296行）
                                       不可逆操作はSTOP_WORDSで止めて聞き返す／flockで多重起動を防ぐ
  */5  inbox_runner.py --run --beat
  状態 slack_inbox_state.json が 13:05 更新 ＝ 生きている
```

したがって Socket Mode 化は**新規機能ではなく置き換え**。判断すべきは「作るか」ではなく
**①ポーリングを止めて置き換えるのか ②並走させるのか（＝同じDMを2経路が拾い二重実行する）**。
並走させるなら重複排除のキー（`ts`）をどちらが持つかを先に決める。
既存の安全弁（STOP_WORDS・flock・DMのみ・心拍）は**新経路にも同じものが要る**。
→ [[reference_relay_piles_up_and_blames_the_user]] [[feedback_stop_asking_just_do_it]]

**常駐の置き場も未解決。** crontab は書き込み不能のまま（[[reference_cron_write_blocked_in_session.md]]）。
launchd は `com.vivid.chatwork-relay.plist` が唯一の前例だが**パスが `/Users/yujimac/`＝MacBook用**で
mini では動かず、`launchctl list` に vivid は0件（未ロード・実測）。
launchd 経由はファイル権限が消える型もある → [[reference_launchd_loses_file_access]]。

## ★2026-08-23 追記 ── 「Slackから話しかけて動かす」は**もう動いている**（Socket Modeではない）

上の「受け口を作る必要がある」は**半分誤り**だった。Socket Mode は確かに未実装だが、
**同じ用途の経路は稼働中**。作る前に、既にある経路を実測すること。

```
実体   ~/.vivid-relay/slack_inbox.py（12KB・pidロックあり）
起動   mini crontab  */5 * * * *  --run --beat      ★常駐ではなく5分ポーリング
鍵     xoxb-（conversations.history）。xapp- は使っていない
中身   DMの新着を拾う → 承認が要る語なら保留 → それ以外は claude CLI（-p）へ丸ごと渡す
```

**★DMへ書いたものは、何であれ「指示」として claude CLI に渡る。** 13:02 のログに、
有璽氏が貼った **xapp- トークンの本文そのものが指示として実行され「完了」と記録されている**。
鍵・顧客名・個人情報をDMへ貼ると、そのまま実行プロンプトへ流れる。
Socket Mode 化すると遅延が消える＝**貼った瞬間に実行される**ので、この穴は先に塞ぐ。

**Socket Mode に移すなら、変わるのは遅延だけ（5分→即時）。** 代わりに以下を新たに背負う。
`slack_sdk` も `websocket` も**未インストール**（Python 3.9.6・実測 ModuleNotFoundError）／
常駐プロセスの生死監視／再接続／**crontab が書けない状態は 8/23 も未解消**
（→ [[reference_cron_write_blocked_in_session]]）＝登録先は launchd だが
[[reference_launchd_loses_file_access]] の型を踏む。

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

### ★DMへ貼った鍵は「実行ログ」にも平文で焼き付く（2026-08-23 つる実測）

Slackの履歴だけではない。**受け口が指示として実行するので、その本文がログへ残る。**

```
config.env                600  正規の置き場（これは適正）
slack_inbox.log:2038      644  ★鍵の本文が平文。実行ログとして残った
slack_inbox_partial.txt   644  ★同上（途中経過の退避ファイル）
memory/ の記述            git  伏せ字 `xapp-1-...` のみ＝漏れていない（HEADにも無し）
```

- **鍵を revoke するだけでは終わらない。644 の2ファイルを消すまでが後始末。**
- **★入力の検疫が無い受け口は、秘密情報を受け取った瞬間に自分で二次コピーを作る。**
  Socket Mode 化（＝遅延ゼロ化）は、この二次コピーが**貼った瞬間**にできることを意味する。
  検疫（鍵・顧客名の混入を検出して実行前に落とす）を先に入れないと、速くするほど傷が増える。

### 多重起動の防ぎ方は flock ではない（申告と実物が違った）

`slack_inbox.py:186-194` は **pidファイル方式**（`os.path.exists(LOCK)` → pid を読む →
`kill -0` 相当で生死を見る）。`flock(2)` は使っていない。
**「flock で多重起動を防ぐ」という申告は実物と合わない。**
ログには「先の実行（PID 79445）がまだ走っているので今回は何もしない」が連続で残る
＝**ポーリング側でも既に「生きたまま黙る」が起きている**（→ [[reference_ran_is_not_succeeded]]）。
