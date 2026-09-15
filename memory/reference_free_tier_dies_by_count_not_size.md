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
