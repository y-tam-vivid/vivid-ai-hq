---
name: reference_prtimes_editor_behaviors
description: PR TIMES入稿エディタの実測挙動。行頭の「1.」で本文全体が番号リスト化し、解除できない
metadata:
  type: reference
---

**PR TIMES の下書きエディタ（`my_c3/action.php?run=mypage&page=pressreleaseedit&release_id=N`）の実測。**
2026-08-25、Claude in Chrome から2本を入稿して確認した。

```
★行頭の「1.」で本文が丸ごと番号リストになる
   「1. こたえる」と入力した瞬間にオートフォーマットが働き、
   ★以降に入力した全行（44行）がリスト項目に巻き込まれた
   ツールバーの番号リストボタンでは解除できない
   （選択して押すと、逆に番号が振り直されて 44→61 に増えた）
   直し方＝本文を全選択して削除し、「STEP1」「①②③」表記で入れ直す
   ※タイトル・サブタイトルは本文と別枠なので巻き込まれない
```

- **本文中に `・` の箇条書きは安全。** 数字＋ピリオドだけが危ない。
- 文字数の上限＝タイトル100／サブタイトル100／本文8000。画像は30枚まで。
- 「保存」は下書き保存で、押しても配信申請にはならない。**配信は「次へ」から先の別画面**。
- 新規作成は毎回 `release_id` が1つ増える（2026-08-25 時点で 4 と 5 を使用）。
- 入稿の元原稿は [[project_npo_press_releases_202608]] のArtifact内「PR TIMES 入稿用テキスト」。

**★拡張が動かないときの切り分け**（同日に4回踏んだ）

```
navigateは通るのに screenshot / get_page_text だけタイムアウトする
  → サイト許可ではなく、拡張自身が claude.ai にサインインしていない
     右パネルに「Sign in to Claude」が出ていないか見る
  → 権限側は ~/.claude/settings.json の allow に mcp__claude-in-chrome__* が要る
     → [[reference_permissions_are_part_of_the_environment]]
```

## 🔴 2026-10-05 ★5回目を踏んだ。しかも★この節を読まずに誤った原因を報告した

有璽氏「実際にプレスリリース、PRタイムズの方に掲載するところ、下書きまで作成してください」

**症状は上の節とまったく同じだった。**

```
navigate ✅通る（タブも作れる・URLも移る）
screenshot / read_page / get_page_text 🔴落ちる
  文言は3種に揺れた  「Script injection timed out after 5000ms」
                     「Page script returned empty result」
                     「Page still loading (waited 45000ms for document_idle)」
  ★example.com でも同じ＝サイト固有ではない（2経路で確認済み）
```

**🔴こちらの誤り。**この節に答え（★拡張が claude.ai にサインインしていない）が書いてあるのに、
**読まずに「Chrome拡張が壊れている・Chromeの再起動が要る」と報告した。**
有璽氏は別のブラウザを立ち上げてくださった ── **こちらの誤報のために1手を無駄にさせた。**

```
★先に memory を探す。この案件は「PR TIMES」で grep すれば1本で出た
   ls memory | grep -i prtimes  →  reference_prtimes_editor_behaviors.md
★「ブラウザが壊れている」は原因ではなく症状。層を切り分けてから言う
   ①拡張のサインイン ②サイト権限 ③settings.json の permissions ④OS層
   ★①は接続一覧では分からない（list_connected_browsers は inUse:true を返す）
★新しいブラウザを立ち上げても、接続一覧の deviceId・connectedAt が変わらなければ
   ★拡張につながっていない（＝別ブラウザを足しても解決しない）
```

→ [[feedback_check_the_archive_first]]（まず保管庫を見る）／[[feedback_verify_before_declining]]
