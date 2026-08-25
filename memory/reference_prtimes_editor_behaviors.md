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
