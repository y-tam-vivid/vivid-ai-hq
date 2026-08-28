---
name: reference_norms_outnumber_their_enforcement
description: 規範632KBに対し実際にブロックする機械ゲートは1つだけ。最も重い「規範の変更」が技術的に最も無防備だった
metadata:
  type: reference
---

**★「破っても何も起きないルール」が量産される構造を、数字で確認した**（2026-08-29 つる実測）。
有璽氏「なんで俺が言われてからしかこの動きをせんねん。直後だけなんだよいつも。ですぐ忘れる」。

## 量と強制力が釣り合っていない

```
規範の量
  毎ターン必ず届く   CLAUDE.md 613B ＋ fukuchi-core 40,549B
                     ＋ MEMORY.md 12,903B ＋ WORKING.md 61,214B
                     ＝ 115,279バイト（原稿用紙 約95枚）★毎ターン
  索引経由でしか届かない  feedback 42本＋reference 85本 ＝ 632,353バイト（約526枚）

実際にブロックする機械ゲート
  ★全体で 1つだけ ── hook_session_writeback.py の検査2（2026-08-29 新設）
  hook_inject_memory.py は exit(0) のみ ＝ 見せるだけ・強制力なし
  hook_catch_correction.py は自ら「★止めない。ブロックしない」と明記
```

**★毎ターン95枚を届けて、止めるのは1点。** これが「届いているのに守らない」の正体。

## 承認が要る6種のうち、機械で効いているのは2.5種

```
外へ出る（送信・公開）    Gmail / Slack は ask に入っている        効いている
お金（課金・契約・発注）  ★settings.json の ask に無い
正本の削除（kintone）     kintone ツール自体が未登録＝到達不能     （事実上不可）
★規範の変更              ★ask に無い。Edit/Write が無条件 allow
人に配るもの              機械の判定なし
大きな分岐                機械の判定なし
```

**★いちばん重い「規範の変更」が、技術的にいちばん無防備だった。**
fukuchi-core/SKILL.md を誰でも無条件に書き換えられる状態で「規範の変更は要承認」と
書いてある ＝ 規範が規範自身を守れていない。

## ★唯一のゲートが、指摘した本人の失敗を拾えなかった

検査2の「探した証拠」の判定語は `memory/` `INDEX_` `drive.files` `notion-search` 等。
**`find` `ls` `grep` `cat` が入っていない。**

2026-08-29、つる自身が `~/.vivid-relay/daily_jobs.conf` を `find` で探して0件 →
別の場所で発見、という行為をした。**この最も基本的な探索が「探していない」と判定される構造**
だった（同一ターン内で自己修正したため発火はしなかったが、条件は揃っていた）。

**★ゲートを作ったら、実際に踏んだ失敗の再現でテストする。** 想定した経路だけで試すと、
作った本人が思いつかなかった経路がそのまま穴になる（[[feedback_use_the_team_not_alone]]）。

## 規範どうしの矛盾も実在する

- fukuchi-core は「既定は自分で進める」を**6箇所**で明言
- 一方 `WORKING.md` には「判断待ち／承認待ち／要承認」が**9件**実在
  （`WORKING.md:91,157,205,299,349,398,465,581,584`）
- 可逆かどうかの判定を各セッションが個別に下すため、**本来は自分で進めてよい案件が
  待機列に紛れている**（[[feedback_stop_asking_just_do_it]]「判断待ちに積むと停滞が人のせいに見える」）

## 1プロジェクト5〜7項目の規範も守られていない

WORKING.md 18ブロック中3件が逸脱。**うち1件（SalesBreaker申し送り）は136項目**。
この規範を検査する仕組みは存在しない（`memory_audit.py` に該当コードなし）。

## 次にやること（順序つき）

1. `settings.json` の ask へ **fukuchi-core/SKILL.md の編集** を足す（★規範の変更＝要承認）
2. 検査2の探索判定へ **Read / Grep / Glob / find / ls / grep** を足す
3. `memory_audit.py` へ「1プロジェクト5〜7項目」「WORKING.md のバイト数」検査を足す
4. WORKING.md の「判断待ち」に**経過日数**を機械的に付す

関連: [[reference_hooks_enforce_what_discipline_cannot]] [[reference_no_gate_on_asking_the_human]]
[[reference_what_actually_reaches_the_next_turn]] [[feedback_use_the_team_not_alone]]
[[reference_delivered_but_unread]]
