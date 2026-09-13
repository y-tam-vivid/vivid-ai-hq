---
name: project_ai_usage_tracking
description: Claude Codeのトークン消費を日次でCSVへ積み、週1で見る。cache読取が額の7割を占めると実測。Claudeプランの残%とChatGPT Plusは取れない
metadata:
  type: project
---

## 有璽氏の要件（2026-09-12）

> 「使ってるAIの全部見れたらいいなと思うんだけど、クロードのアカウント、ChatGPTとかもそうだし、
>  あと僕だと**Manus**とかもあるんだけど、それの**それぞれの使用量**を知りたいです。
>  **何パーセント使ってるのか**とか、**いつリセットされるのか**とか。
>  それが**それぞれのエージェントでどれぐらい消費しているのか**とかも見えるようにしてほしい。
>  それを後で**CSVファイル**でアウトプットして**検証できるように**もしたい。」

決定（同日）── 「**取れるものから取ろう。Claudeからまずは使っていきましょう。Manusはまだ、
おいおいでいい。今日から実測してCSVで出すように。それもルーティンに入れて。**」

## ★粒度 ── 取るのは毎日、見るのは週1

```
取る   ★毎日1回（22:30）。上書きせず、同じ日の行だけ差し替えて積む
見る   ★週1（月曜）にまとめて
```

**★なぜ取るのを毎日にするか** ── transcript は整理されて消えることがあり、
消えた日は二度と割れない（[[reference_overwriting_containers_have_no_past]]
「定期化する前に『遡れるか』を決める」）。毎日CSVへ落としておけば元が消えても残る。

## How to apply

```
道具   bin/ai_usage_report.py（git管理下・★両機に配布済み）
       既定はドライラン（表示だけ）。★--run のときだけCSVへ書く
       --days N ／ --weekly（直近7日）／ --beat（心拍）
出口   ~/.vivid-relay/usage/daily_<ホスト名>.csv
       列＝日付・機械・担当・モデル・入口・案件・input・output・cache作成・cache読取・
           ターン数・API換算額_USD・単価が確定しているか
cron   ★両機とも 22:30（MacBook 15→16行 ／ mini 50→51行。他の行は無傷を diff で確認）
       ★これは「そのマシンの中身を扱う仕事」なので両機で動かすのが正しい
       （fukuchi-core「定期実行は片方だけ」の例外。Downloads整理と同じ型）
```

**★担当・案件の割り方**（transcript の実測 2026-09-12）

```
担当     d["agentId"] があれば「サブエージェント」、無ければ「メイン」
案件     d["cwd"] の末尾ディレクトリ名（vivid-ai-hq / lifestandup-wp など）
入口     d["entrypoint"]（cli ／ claude-desktop）
モデル   d["message"]["model"]
消費     d["message"]["usage"] の input_tokens / output_tokens /
         cache_creation_input_tokens / cache_read_input_tokens
★二重計上を防ぐ  d["uuid"] で一意にする
★時刻     timestamp は UTC。JSTへ直してから日付にする
```

## 🔴実測でいちばん効いたこと ── cache読取が額の7割

2026-09-12 の1日（MacBook）

```
cache読取   602,657,016 tok   $301.33   ★73.9%   ← ここが本体
cache作成    11,468,509 tok   $ 71.68     17.6%
output        1,390,980 tok   $ 34.77      8.5%
input             2,090 tok   $  0.01      0.0%
合計                          $407.79   （mini は別に $33.18）
```

- **★最初は input/output だけで計算し $33.89 と出した。一桁違った。**
  「cache の単価は確認できていない」で止めずに、公式ページを取りに行って直した
  → [[feedback_one_route_is_not_verification]]／[[feedback_stop_asking_just_do_it]]
- **★金額は必ず内訳（どこに効いているか）と一緒に出す。**合計だけでは手の打ちようがない

## 単価（公式・2026-09-12 実測）

https://platform.claude.com/docs/en/about-claude/pricing

| モデル | input | cache作成(5分) | cache作成(1時間) | cache読取 | output |
|---|---|---|---|---|---|
| Opus 5 / 4.8 / 4.7 / 4.6 | $5 | $6.25 | $10 | **$0.50** | $25 |
| Sonnet 5 | $2 | $2.50 | $4 | **$0.20** | $10 |
| Sonnet 4.6 / 4.5 | $3 | $3.75 | $6 | $0.30 | $15 |
| Haiku 4.5 | $1 | $1.25 | $2 | $0.10 | $5 |
| Fable 5 | $10 | $12.50 | $20 | $1 | $50 |
| Fable 5.1 | $10 | $12.50 | $20 | **$0.25** | $50 |

- **★cache作成は5分と1時間で単価が違う**（1時間は input の2倍）。
  **transcript は `cache_creation_input_tokens` しか持たず区別できない。**
  → 5分の単価で計算している＝**1時間キャッシュを使った分は過少に出る**
- **★Maxプランは従量課金ではない。**この額は**API換算の参考値**であって請求額ではない

## ★取れないもの（最初に切り分けた）

```
🔴 Claudeプランの「何％使った・いつリセット」
   ★ANTHROPIC_API_KEY が無い（config.env に0件）＝Admin/Usage API を叩けない
   ★そもそも Max プランの消費率はローカルに保存されていない
   ★見られるのは Claude Code の /usage コマンドだけ ＝ ★有璽氏が自分で叩く領域
🔴 ChatGPT Plus（サブスク）の使用量 ── APIで公開されていない
   ★APIキー経由の従量課金分とは別物。混ぜて出すと嘘になる
```

**★「％」を目的に置くと全部できないことになる。**トークン実数と概算額を正とする。

## 残（有璽氏の判断・おいおい）

- **Manus のクレジット** ── 鍵は `~/.config/manus/api_key` に実在。★残量が返るかは未確認
  （有璽氏「Manusに関してはまだですね。おいおいでいいです」）
- **OpenAI の使用量** ── `OPENAI_API_KEY` は `config.env` に実在。usage API は未実装
- ⚙️自動処理レジスタへの行と心拍名の登録（★未実施。次に触る人がやる）
- 週次まとめのSlack通知（`--weekly` は動くが、自動では出していない）

## 関連

[[project_ai_office_console]] 会議室（ここへ使用量のタブを足す先）／
[[feedback_never_write_an_unmeasured_number]]／[[reference_overwriting_containers_have_no_past]]

## 🔴2026-09-13 初回発火で止まった。原因は2つとも「止まる仕組みを選んでいた」

有璽氏「**自動で更新が継続的にかかる形でないと、この設計そのものが意味ない。
なんで止まってんのって話やし、止まらんように設計して**」

```
① MacBook の22:30が飛んだ
   真因 ★cron はスリープ中の回を捨てる。MacBookは持ち運ぶので夜は必ず閉じている
        実測：CSVが 9/12 17:29 のまま＝22:30の回が存在しない
   直し ★launchd へ移した（StartCalendarInterval は寝ていた回を復帰後に実行する）
        bin/launchd/com.vivid.ai-usage-report.plist ＋ bin/install_launchd.sh（★冪等・既定はドライラン）
        crontab の重複行は外した（MacBook 16→15 ／ mini 51→50。★他の行は diff で無傷）
   ★答えは既に「ブラウザ衛生」の備考に書いてあった
     ── 「cronではなくlaunchdで動かす（cronはスリープ中の回を捨てるため）」
     Downloads整理が7回中2回（29%）飛んでいた実測つき。★読んでから作らなかった。

② 心拍が2回続けて着弾しなかった。★原因は毎回違う
   1回目  ok=True で呼んで TypeError（正しくは result=）
          → ★道具は要約でなく実物のシグネチャを見る（inspect.signature）
   2回目  機械名なしの名前で打っていたが、レジスタの行は機械名つきだった
          （2026-09-13 につるが「両機で動く」ことに気づいて2行へ分けてくれていた）
          → heartbeat.beat は title の★完全一致で探す。1文字違えば黙って届かない
   直し ★PROC_NAME を HOST から機械名つきで組む。
        ★heartbeat.beat の戻り値も画面へ出す（「打てた」と「着いた」は別）
```

- **★「心拍: 成功」と画面に出ても、着いたかは別。**必ずレジスタ側で読み返してから
  `有効=True` にする。今回は 2026-09-13 00:30/00:31 UTC の着弾を実測してから有効化した。
- **★scp と git で二重に配らない。**`ai_usage_report.py` を scp で配ってから git でも配り、
  両機に別々の版ができて衝突した → [[reference_fix_where_git_reaches]]
- **★`git pull --ff-only` を手で打たない。**両機が同時に動くので枝分かれは日常的に起きる。
  `git merge --no-edit origin/main` を使う（vivid-sync.sh が cron でやっているのと同じこと）。

### ★止まる仕組みの見分け方（この件で確定した3つ）

```
1  人の会話からしか起動できない        Artifact・チャット・手元のコマンド
2  閉じる機械に置いた cron             MacBookは夜必ず飛ぶ。★launchd を使う
3  心拍の行が無い／名前が1文字違う      止まっても🔴が立たない＝止まったことすら分からない
```
