# 無料枠は容量でなく「回数」で尽きる

**★2026-09-15 有璽氏**
> 「他社とかこういった部分、AI会議室とかがどうやって運営してるかを調べて、
>   バーシャル（Vercel）課金して皆さんやられてるのかどうかを調べて。
>   **割ともうずっと動いてるようなものを見かけたりするんだけど、
>   そういったことっていうのができないものなの？**」

## ⛔まず自分の誤診を訂正する

会議室が止まった日、画面に出ていた文字をそのまま読んで
**「Billing State: Inactive ＝ 課金が有効でないから止まった」**と報告した。
**★これは不正確だった。**

公式ドキュメント（vercel.com/docs/vercel-blob/usage-and-pricing・2026-08-11更新）：

> Vercel Blob is **free for Hobby users** within the usage limits.
> **You will not pay for any additional usage.** However, you will not be able to
> access Vercel Blob **if limits are exceeded**. In this scenario, you will have to
> **wait until 30 days have passed** before using Blob storage again.

**★課金していないから止まったのではない。無料枠を使い切ったから止まった。**
**★30日待てば、何もしなくても自動的に戻る。**

★エラー画面の文言を、そのまま原因として報告しない。**必ず提供元の仕様書に当たる。**

## ★尽きたのは「容量」ではなく「書き込み回数」

Vercel Blob の Hobby 無料枠（2026-09 時点・出典は上記ページ）

```
Storage Size          1GB/月            ← うちは 206KB。★0.02%しか使っていない
Simple Operations     10,000回/月       ← 読み取り（cache MISS・head）
★Advanced Operations  2,000回/月        ← ★put() copy() list()＝書き込み系
Blob Data Transfer    10GB/月
```

**うちの実測（cron を数えただけ）**

```
dashboard_realtime_push   30分ごと(3,33)  48回/日 → 1,440回/月
office_realtime_push      30分ごと(3,33)  48回/日 → 1,440回/月
──────────────────────────────────────────────────
この2本だけで                            ★2,880回/月 ＝ 枠の1.44倍
＋ office_answer_apply（5分ごと）／editor_apply／担当の起動ごとの即時push
```

**★容量を見て「使いすぎではない」と判断したのが誤り。** 206KB は確かに小さい。
だが**止まる理由は大きさではなく回数だった。**

## ★型として覚えること

```
無料枠を見るときは★4つ別々に数える
  ① 容量（GB）      ← つい最初に見てしまう。たいてい余っている
  ② 書き込み回数    ← ★定期実行があると、ここが真っ先に尽きる
  ③ 読み取り回数    ← ★画面のポーリングが効く（30秒ごと＝1時間で120回）
  ④ 転送量（GB）
★「使いすぎではない」と言う前に、②③を1か月ぶん掛け算する。
★定期実行を作った瞬間に「1日◯回 × 30日」を暗算して枠と比べる。
```

- **★30秒ごとのポーリングは、読み取り枠を月10,000回として83時間ぶんで尽きる**（1人が開いた場合）。
  常時見る画面ほど、無料枠と相性が悪い。
- **★「ずっと動いている」ものが世の中にあるのは、書き込み回数が少ないか、
  そもそも回数課金の仕組みを使っていないから**（静的ファイルに同梱する等）。

関連 [[reference_two_silences_hide_a_stop]] [[project_ai_office_console]]
[[reference_vercel_free_plan_protection]] [[feedback_look_outside_before_reinventing]]

## 🔴 有璽氏は答えた。誰も動いていない（2026-09-21 つる実測）

**止まっているのは仕組みではなく、決定のあとの一手。**

```
09-15 00:42  Blob 2ストアが停止（403）
09-15 09:56  ask_hub で問う → 有璽氏「他社がどうやっているか調べて」
09-15 19:02  調査結果を問い直す → ★status=open のまま 今日まで6日 放置
09-19 08:49  ★有璽氏が回答「3 Blobを使わない作りへ変える案を出させる」
09-21 08:40  ★案は出ていない。403 は今朝も出続けている
09-25 08:4x  ★まだ出ていない（有璽氏の回答から6日）。403 は office_answer_apply.log だけで1,980回
             editor_apply.err の Traceback 672件・🔴4件とも既知=False のまま（つる 自己監査）
             ★#4394bc（Pro / Cloudflare / 現状維持）も status=open のまま10日
09-26 08:5x  ★まだ出ていない（回答から7日）。editor_apply.err 1.2MB。
             ★副作用：~/Library/Logs/vivid-kadoban-cron.log が 156MB（suspended 1,561回）
             → つるが gzip で退避（…upto20260926.gz・中身はハッシュで一致確認）
             ★cron_alive.py は4本中 editor_apply しか🔴にしない（ログ更新＝動いている扱い）
```
**★この件の持ち主がいない。**判断（#4ec39b）は済んでいて、残っているのは「案を作る」という
AIの作業だけ。誰にも割り振られていないので、毎朝検知されては流れている。

**実測2経路** ── ① `~/.vivid-relay/editor_apply.err` が 1.1MB・Traceback **672件**（全部
`HTTPError 403`）② ⚙️自動処理レジスタが **🔴失敗 4件**（editor_apply / office_answer_apply /
office_realtime_push / dashboard_realtime_push）。どれも既知=False＝誰も拾っていない。

- **★検知は正しく働いている。**9/17 につるが「落ちても失敗心拍を打つ」形へ直したので、
  レジスタは6日間ずっと🔴を出し、メッセージに 403 まで書いていた。**読む人がいなかっただけ。**
- **★実害**：①★C（lsu-editor）でブラウザから保存しても CSS へ適用されない
  ②会議室のボタンを押しても台帳へ入らない ③稼働盤・会議室の数字が更新されない。
  **有璽氏が押しても何も起きない状態が6日続いている。**
- **★「期待間隔を超えたか」だけで検査すると、この4件は1件も出ない**（毎5分きちんと起動して、
  きちんと落ちているので遅延ゼロ）。**🚦状態と最終結果を見ること。**
  → [[reference_heartbeat_proves_life_not_results]]

関連 [[reference_a_warning_nobody_owns]] [[project_ai_office_console]]
