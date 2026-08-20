---
name: reference_manus_api_behaviors
description: Manus API の実測挙動。stoppedは完了と中断を区別しない／WebとAPIの二重操作／ドキュメントに無い口と無い口
metadata:
  type: reference
---

Manus API v2（`https://api.manus.ai`・ヘッダ `x-manus-api-key`）を実測して分かったこと。
**ドキュメントだけでは分からず、叩いて初めて出た**ものだけを書く（2026-08-20 実測）。

## ★1. `stopped` は「完了」と「人が止めた」を区別しない

`agent_status` は4値（running / waiting / stopped / error）。**このうち `stopped` が2つの意味を持つ。**
区別できるのは `status_update` の `brief` だけ。

```
brief = "Manus finished working"                    → 完了した
brief = "Manus has stopped"                          → ★人が止めた
        description = "The user stopped Manus's work"
```

**`agent_status` だけ見て「完了」と報告すると、止められたものを完了と誤報告する。**
2026-08-20、有璽氏から「止まっているから確認して」と言われて初めて気づいた。
こちらは4本すべて "stopped" を見て「完了」と読んでいた。

## ★2. Manus Web と API から、同じタスクを同時に触れる

有璽氏は Manus Web 側でも直接タスクへ指示を出している。
**API から投げたタスクに Web から別の指示が入り、Web から止められる。**
API 側からは「誰が何をしたか」は `user_message` と `brief` で見えるので、
**現在地を答える前に必ず最新メッセージまで読む。** 状態だけ見て答えない。
（vivid-ai-hq の `WORKING.md` が解いたのと同じ問題 ── 進行中の作業が別経路から見えない）

## 3. レスポンスの形（ドキュメントに無い）

- `task.listMessages` → `{ok, request_id, task_id, has_more, next_cursor, messages[]}`
  - `messages[]` は `{id, timestamp, type, <typeと同名のフィールド>}`
  - type は `user_message` / `assistant_message` / `status_update` の3つ
  - **`agent_status` はトップレベルに無い。`status_update` の中にだけある**
  - **`timestamp` はミリ秒**（秒として解釈すると年58602になる）
- **成果物は `assistant_message.attachments[]`**（`filename` / `content_type` / `url`）
  - url は署名付き。**期限があるのですぐローカルへ落とす**

## 4. 実在する口／存在しない口

```
実在   task.create  task.listMessages  task.sendMessage  task.confirmAction
       task.list    project.list       skill.list                （後3つはドキュメント外）
無い   project.get  project.info  project.listTasks  task.get  task.search
       credit.balance  usage.get  user.info  me  account.info  knowledge.list
```

- **`project.get` が無い ＝ Manus 側のプロジェクト指示・ガイドラインは API から読めない。**
  横展開したいなら Web 側で設定するか、こちらから指示文として毎回渡すしかない
- **残クレジットを取る口が無い ＝ 残量が分からないまま投げることになる**
- **`task.list` は所属プロジェクトを返さない**（`project_id` で絞ろうとしても無視される）

## 5. 引っかかった引数

- `locale: "ja-JP"` は `invalid_argument` / "invalid locale" で **400**。
  → **locale は送らない**。プロンプトが日本語なら出力も日本語で返る
  （400＝タスク未作成なので課金は発生しない）
- `task.create` の本体は `{"message": {"content": [{"type":"text","text":"..."}]}}`。
  `project_id` を付けるとそのプロジェクトに属する

## 6. 課金の勘所

- 消費するのは `task.create` と `task.sendMessage`。**読み取り系（listMessages / task.list /
  project.list）は無料**なので、状態確認はいくらでもしてよい
- 過去実績は1タスク 500〜3,500クレジット。画像生成はさらに重い

関連 → [[reference_salesbreaker_engagement_api]]（同じく「叩けば分かる」型）

## 7. Slack通知（2026-08-20 開通）

**通知の仕組みは作らない。** 議事録ラインで既に動いている `~/.vivid-relay/notify.py` の
`tell()` を呼ぶだけ。チャンネルへ投げずDMのみ、報告に「返信不要」が付くのも notify.py 側の作法。

```
実体      bin/manus.py watch
起動      launchd com.vivid.manus-watch（15分ごと・MacBook）
状態      ~/.vivid-relay/manus_watch.json
レジスタ  ⚙️自動処理レジスタ「Manus タスク監視」。心拍の着弾を実測済み
```

- **冪等**。前回状態と突き合わせ、変化した分だけ出す。同じ完了を二度鳴らさない
- **初回は通知しない**（状態を記録するだけ。でないと過去分が一斉に鳴る）
- **走り出し(running)は知らせない。** 終わり・エラー・確認待ちだけ
- `stopped` は brief を引いて「完了」と「人が止めた」を書き分ける（→ 1節）
- `task.list` は読むだけなので**課金されない**。15分ごとに叩いてよい

**★MacBookは閉じている間は動かない。** 裏側で常時動かすなら mini へ移すが、
mini には Manus APIキーも `bin/manus.py` も無い（他セッションの未コミットで pull が止まっている）。
移すときは `~/.config/manus/api_key` の配置と launchd/cron 登録が要る。

**★SLACK_BOT_TOKEN は MacBook の config.env に無かった**（miniにはあった）。
2026-08-20 に mini から移送。両機で hooks を動かす前提なら、片方にしか無い状態は事故のもと。
