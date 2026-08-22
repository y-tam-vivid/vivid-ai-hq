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

- **`project.get` が無い ＝ プロジェクト指示は API からは読めない。**
  **★ただし「読めない」で止めてはいけない（2026-08-20 実地）。**
  当方は API に口が無いことを確認して「読めない」と結論し、**そこで止めた**。
  実際は有璽氏に「Manus Web で開いて貼ってください」と頼めば手に入る。
  **API で取れない ≠ 取得手段が無い。** 人に頼む経路を先に潰さない。
  → この見落としのせいで、**プロジェクト指示文を知らないまま独自の設計を Manus へ送り、
    指示が二重になった**（プロジェクト側の「5本柱・カルーセル5枚1:1」と、
    当方が送った「A/B/D併用・火木土ルーティン」が競合）
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
実体      bin/manus.py watch                          ★両機に入っている
状態      ~/.vivid-relay/manus_watch.json             機ごとに別（共有していない）
定期実行  ★Mac mini のみ  cron */15
          MacBook は ~/Library/LaunchAgents/com.vivid.manus-watch.plist.disabled
          （消さずに残してある。主を入れ替えるときは拡張子を戻すだけ）
レジスタ  ⚙️自動処理レジスタ「Manus タスク監視」・実行機=Mac mini。心拍の着弾を両機で実測済み
```

**★両機で定期実行してはいけない。** 状態ファイルが機ごとに別なので、
両方が独立に「変化した」と判断し、**同じ完了が2回 Slack に届く**。
手で `manus.py watch` を叩くのはどちらからでもよい（規範「両機を同じ環境にする」）。

- **冪等**。前回状態と突き合わせ、変化した分だけ出す。同じ完了を二度鳴らさない
- **初回は通知しない**（状態を記録するだけ。でないと過去分が一斉に鳴る）
- **走り出し(running)は知らせない。** 終わり・エラー・確認待ちだけ
- `stopped` は brief を引いて「完了」と「人が止めた」を書き分ける（→ 1節）
- `task.list` は読むだけなので**課金されない**。15分ごとに叩いてよい

**2026-08-20 に mini へ移設済み。** MacBook は閉じている間は動かないため。
移設で必要だったもの: `~/.config/manus/api_key` の配置／`bin/manus.py` の pull／cron 登録。
**cron 相当の最小環境（`env -i PATH=/usr/bin:/bin`）で実測してから載せた。**

**★SLACK_BOT_TOKEN は MacBook の config.env に無かった**（miniにはあった）。
2026-08-20 に mini から移送。両機で hooks を動かす前提なら、片方にしか無い状態は事故のもと。

---

## ★添付機能が無い。参照素材は Drive へ置いてリンクで渡す（2026-08-22 実測）

`task.sendMessage` はテキストだけ。**画像・PDFを直接添付する口が API に無い。**
`task.create` にも無い。したがって参考画像を渡す手段は1つ。

```
① 該当アカウントの Drive フォルダへ置く（03_ブランド・テンプレート素材 配下など）
② Drive の共有リンクを本文に書く
③ ★用途の制限を毎回本文へ明記する
```

**Manus は Drive を直接読める**（実績あり → [[feedback_check_the_archive_first]]）ので、これで通る。
Drive はマウント経由で `cp` するだけでよいが、**同期を待ってから**リンクを取ること
（`mcp__claude_ai_Google_Drive__search_files` でフォルダIDが引ければ同期済み）。

**★人物写真を渡すときに本文へ必ず書く3点**（Manus は社外 → [[project_manus_outsourcing]]）

```
1  実在の人物であること・本人の指示で渡していること
2  写真そのものを成果物へ貼り込まないこと（画風の中で描き起こす参照に限る）
3  このタスク以外の用途に使わないこと
```

2026-08-22、有璽氏本人のプロフィール写真7枚を119番の人物イラスト参照として渡した実例。

## ★棚卸しの「対象アカウント」を額面で受け取らない（2026-08-22 実測）

4アカウント分の棚卸しをタスク別に投げたところ、**ビビッド法人IG のタスクが
`@yuji_tam3.0_2026`（有璽氏の個人IG）を棚卸しして報告してきた。**
報告書の体裁は完璧で、件数も詳細も揃っている。**中を開くまで気づけない。**

- 原因は Manus 側が**そのアカウントへ接続できていない**こと。
  接続が無いと「0件でした」ではなく、**繋がっている別アカウントを見て報告する**
- 検算は件数ではなく**中身**を見る。格納先の実ファイルを数え、
  台帳MDの `対象アカウント：` 行と**Drive実数の両方**を突き合わせる
- ビビッドは実測 **5件・0B（すべて棚卸し文書・画像0件）** だった

## ★「アカウント不明」はファイル名でなく画像を開いて判定する（2026-08-22）

API から回収した133件はタスクIDしか手掛かりが無く、タスク名
（「プロジェクト指示文と共有ファイルの設定方法」等）はアカウントを示さない。
**画像を数枚開いたら一発で分かった** ―― ロゴ「福祉施設の110番」が入っていた（90件）。
タスク名から推測せず、**代表を数枚めくる**。1タスク1枚で足りる。
