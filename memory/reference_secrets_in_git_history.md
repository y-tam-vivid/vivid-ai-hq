---
name: reference_secrets_in_git_history
description: gitへ一度入れた機微は作業ツリーから消しても履歴に残る。commitして配られた時点で不可逆に近い。入れる前に検査し、作業場所をリポジトリの外へ置く
metadata:
  type: reference
---

**★git は「消す」を持っていない。** `git rm` も `.gitignore` も、**これから先**を変えるだけ。
**一度 commit した中身は履歴に残り、push した時点で他機と GitHub へ配られている。**

## 2026-09-04 実際に起きたこと（予実の作業中）

```
ファイル   may_rows.pkl（22,860バイト・5月分の取引データ）
中身       ★口座番号2件（りそな個人・楽天ビビッド）が平文
入った経路 ★`git add -A` が拾った → [[reference_git_add_all_swallows_others]]
配布状況   ★origin/main に含まれる ＝ GitHub と Mac mini へ既に配られていた
```

**★担当の自己申告は「add する前に気づいて削除済み。履歴には一切残っていない」だった。**
**鵜呑みにせず履歴を自分で検索したから見つかった** → [[feedback_never_write_an_unmeasured_number]]。

## 気づいた後にできること／できないこと

```
できる（可逆）   git rm --cached ＋ 実ファイル削除 → 作業ツリーと追跡から消える
                 .gitignore へ拡張子を足す（★再発の入口を塞ぐ。今回は *.pkl / *.csv）
★できない        履歴から消すこと。filter-repo 等での書き換え＋ force push が要り、
                 ★他機の同期が壊れる ＝ 不可逆に近い ＝ fukuchi-core「不可逆な操作は要承認」
```

- **★private リポジトリでも「見えないから良い」にはしない。** 配布先が増えるほど回収できない。
- **★履歴の書き換えは自分で判断しない。** 有璽氏へ出す（2026-09-04 時点で判断待ち）。

## 再発を止める（★順番が大事）

```
✕ 「git add -A を使わない」だけ        今回もそれで踏んだ。規律に依存する対策は切れる回に効かない
◎ ★作業場所をリポジトリの外に置く      機微を扱う中間ファイルを repo 配下で作らせない
                                       （今回、担当は vivid-ai-hq/scratchpad/ へ機微CSVを作っていた。
                                        ★scratchpad は .gitignore に入っていない＝commitすれば配られる
                                        → [[reference_fix_where_git_reaches]]）
◎ ★.gitignore で入口を塞ぐ            拡張子単位（*.pkl / *.csv）。人の記憶に頼らない
◎ ★外へ出す前に1回検査する            push・公開・共有の前に、口座番号・鍵・メール・DB名を数える
```

**★「外へ出す」に git push も含まれる。** 同じ 2026-09-04、LIFE STAND UP を GitHub へ
上げる前には検査を先に行い（DB名1件・メール65件を検出して private を必須と判断した）、
**そちらでは事故が起きていない。同じ日に、検査した方は防げて、しなかった方は流出した。**

関連 → [[reference_tool_results_cache_keeps_secrets]]（機微は MCP の読取キャッシュにも残る）
／ [[feedback_confidential_two_layer_rule]]（機微は `_機微` で本人限定へ隔離する）
