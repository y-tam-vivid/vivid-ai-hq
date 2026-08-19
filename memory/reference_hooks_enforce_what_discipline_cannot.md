---
name: reference_hooks_enforce_what_discipline_cannot
description: 同じ失敗を繰り返さない仕組みは3つのフック。書くだけでも読むだけでも足りない
metadata:
  node_type: memory
  type: reference
---

**繰り返す理由は「知らないから」ではない。知っているのに適用しないから。**

2026-08-20 の実例 ── `reference_sheets_number_format_order.md` に
「A列がキーとは限らない」と**自分で書いた2時間後**、40_活動ログをA列で数えて
「2行」と誤報告した（実際は25行）。

```
memory     毎ターン届くのは索引1行だけ。本文は関連しそうなときだけ引かれる
           → 作業中に該当する本文が引かれない
規範       毎ターン全文届く。だが量が多く、適用点で気づかない
```

**書くだけでも読むだけでも足りない。** 有璽氏の言葉：
「作業の時に記録してても、作業の時見てなかったら全く意味ないから」（2026-08-20）

## 3つの穴と、それぞれの機械（`~/.claude/settings.json` の hooks）

| 穴 | 機械 | 実体 |
|---|---|---|
| ① 作業の瞬間に思い出さない | **PreToolUse** | `~/.vivid-relay/hook_inject_memory.py` |
| ② 指摘されるまで記録しない | **UserPromptSubmit** | `~/.vivid-relay/hook_catch_correction.py` |
| ③ 誰も棚卸ししない | 毎朝ロビンが前日を読む | `~/.vivid-relay/memory_sweep.py` |
| （付） 承認待ちが本人に見えない | **PermissionRequest** | `~/.vivid-relay/hook_permission_slack.py` |

**①が本体。** Sheets／Notion／cron／削除／Slack を触ろうとした瞬間に、
**その作業で実際に踏んだ地雷だけ**を `additionalContext` で文脈へ割り込ませる。
★一般論は書かない。実際に踏んだものだけ。書くと読まれなくなる。

**②は作り直した。** 最初の版は「怒り」を検出する作りで、
> 「怒った時だけやりますってなっとるやろうが、それが一番おかしいねん」
と指摘された。いまは「新しい事実・制約・やり方が示された合図」を拾う。
**怒っているかどうかは関係ない。**

## ★配布されないことに注意

```
~/.vivid-relay/     git管理外。フックの実体はここ
~/.claude/settings.json  git管理外・機械ローカル（絶対パスを含むため）
```

**他機（MacBook等）には自動で配られない。** 新しい機械では `bin/setup_hooks.sh` を
**1回だけ**実行する（冪等・既にあれば0件登録）。フックを増やしたらここへ追記すること。

### ★「入っている」の判定は4点そろって初めて言える（2026-08-20 実測）

ファイルが置いてあることは、効いていることの証拠にならない。

```
① ~/.vivid-relay/ に *.py が5本      置いただけ
② settings.json に3フックが登録      ここで初めて呼ばれる
③ landmines.json が生成済み          無いと①のPreToolUseが空を撃つ
④ cron 2行（08:20 selfcheck / 08:25 index再生成）  無いと静かに腐る
```

確認は `python3 ~/.vivid-relay/hook_selfcheck.py`（「3本とも正常」が出る）。

| 機械 | 状態（2026-08-20） |
|---|---|
| Mac mini | **①〜④すべて導入済み・selfcheck 正常** |
| MacBook | **未実施。** `~/vivid-ai-hq/bin/setup_hooks.sh` を1回。miniからsshで入れない |

## 承認の多さも同じ構造だった

規範は「★既定は自分で進める。承認が要るのは6つだけ」と定めているのに、
`settings.json` は「基本ぜんぶ聞く」のままだった。**規範と設定がずれていて、
規範の側だけ直しても止まらない。**
→ `defaultMode: dontAsk` ／ allow 58件 ／ ask 11件（送信・削除系だけ）／ deny 6件

関連 [[feedback_stop_asking_just_do_it]] [[feedback_one_route_is_not_verification]]
[[feedback_use_the_team_not_alone]] [[reference_sheets_number_format_order]]
