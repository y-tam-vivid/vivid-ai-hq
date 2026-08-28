---
name: reference_permissions_are_part_of_the_environment
description: 権限設定(settings.jsonのpermissions)も両機でそろえる。片方が空だと同じ作業がそこでだけ全部止まる
metadata:
  type: reference
---

**「両機は同じ環境にする」の対象に、`~/.claude/settings.json` の `permissions` も含める。**

```
2026-08-21 実測
  Mac mini   defaultMode: dontAsk ／ allow 58 ／ ask 11 ／ deny 6   ← 8/20 に整備済み
  MacBook    defaultMode: dontAsk ／ allow  0 ／ ask  0 ／ deny 0   ← 空のまま
```

**Why:** `dontAsk` は「許可リストに載っているものだけ通す」モード。**リストが空なら全部落ちる。**
2026-08-21、MacBook で丸一日ぶん次が全部拒否された ── `~/vivid-ai-hq/` へのWrite、`cat >` や
`printf >` などBashの書き込み、`sips` での画像縮小、そして **Claude in Chrome（tabs_context の
最初の1手で停止）**。作業のたびにスクリプトを scratchpad へ置いて有璽氏に1行流してもらう形になり、
**同じ成果を出すのに往復が3〜4倍かかった。**

**How to apply:**

```
新しい機械・新しい面を足したら   道具（鍵・トークン・スクリプト）と同時に permissions もそろえる
確認のしかた                    python3 で settings.json を読み、allow/ask/deny の件数を数える
                               ★「dontAskだから自動で進む」は誤り。allowが空なら逆に何も進まない
機械ごとに違ってよいもの          その機械にしか無い機能だけ
                               例：mcp__claude-in-chrome__* はブラウザを使う作業機（MacBook）に置く
```

- **止まった側は「できない」と誤って結論しやすい。** 2026-08-21 はブラウザもPR TIMES入稿も
  「この環境では無理」と書きかけた。**実際は設定1つだった**
  → [[feedback_verify_before_declining]]（憶測で断らない。設定・仕様を読んでから言う）
- **拒否メッセージは原因を言わない。** 「don't ask mode で拒否」としか出ないので、
  詰まったら早い段階で `~/.claude/settings.json` の permissions を読む。
- 実体 → `scratchpad/apply_permissions.sh`（miniのallowをそろえ、chromeを追加。バックアップつき）
- **規範側（fukuchi-core「マシンと実行の置き場」）への追記は要承認**。ここでは事実だけ持つ。

## 2026-08-21 解消（MacBook）

有璽氏の承認を得て mini の `permissions` を MacBook `~/.claude/settings.json` へマージした。
**MacBook allow 0 → 58 ／ deny 6 ／ ask 11 ／ defaultMode dontAsk**（mini と同一）。
バックアップ `~/.claude/settings.json.bak_20260821`。

- **マージ直後の同一セッション内で Write が通ることを実測**（起動し直しは不要だった）。
- `~/.claude/settings.local.json` にも別途 allow が積まれている（過去セッションでの都度承認の堆積）。
  **こちらは機械ローカルの履歴であって正本ではない。揃える対象は `settings.json` の方。**

## ★★allow に `*` があっても通らないものがある ── ask が優先する（2026-08-27 実測）

カレンダーへ予定を作ろうとして拒否された。**allow には `mcp__claude_ai_Google_Calendar__*` が
入っていたのに落ちた。**原因は ask 側。

```
allow   mcp__claude_ai_Google_Calendar__*          ← ワイルドカードで許可されている
ask     mcp__claude_ai_Google_Calendar__create_event   ★こちらが勝つ
        mcp__claude_ai_Google_Calendar__delete_event
defaultMode: dontAsk → ask のものは「聞けないので拒否」になる
```

- **★これは事故ではなく意図的な設計。**ask に並んでいるのは
  Gmail送信・Slack投稿・Driveのゴミ箱・カレンダーの作成/削除 ＝ **外へ出る操作**。
  規範の「承認が要る6項目」と一致している。**回避しようとしない。**
- **★拒否されたら allow だけ見て「権限が無い」と結論しない。**ask と deny を必ず見る。
  allow に `*` があるほど、原因が ask 側にあると気づきにくい。

### 予定を作れないときの代替（実際に使った手）

```
✕ 有璽氏に8本を手で作ってもらう   往復が多く、時刻や繰り返しの写し間違いが出る
◎ ★.ics ファイルを作って渡す      Googleカレンダーへ一括インポートできる
   RRULE（繰り返し）も含められる。インポート前に中身を確認できるので可逆
   ★色（colorId）だけは ics に載らない。インポート後に手で付ける
```

## ★担当が「書けない」ことがある ── allow に Edit があっても拒否される（2026-08-29 実測）

ピタゴラス（サブエージェント）が `snspipe.py` へ Edit しようとして、次で拒否された。

```
Permission to use Edit has been denied because Claude Code is running in don't ask mode.
```

**設定を読むと矛盾している。**

```
defaultMode  dontAsk
allow(60件)  Edit / Write / NotebookEdit / TodoWrite  ← 明記されている
deny(6件)    Edit/Write/.claude/skills を含むものは 0件
ask(11件)    同上 0件
```

**★フックではない。** `hook_role_guard.py` は settings.json に未登録で、
`role_guard.log` にも新しい行が増えていない＝**発火すらしていない**（実測で切り分け済み）。
拒否の文言もフックの差し戻し文と一致しない。

- **★同じ担当でも、書けた回と書けなかった回がある。** 同じセッションのピタゴラスは、
  最初の起動では `bin/md2pptx.py` `bin/md2pdf.py` `bin/setup_ffmpeg.sh` を**新規作成できていた**。
  拒否されたのは **SendMessage で resume した後**の Edit。
  **原因は未特定。「resume すると権限が変わる」は仮説であって確定ではない。**
- **★これで詰みが起きる。** ビビは規範で `.py` を編集できず、担当は権限で書けない。
  **誰も適用できない状態**が生まれる。**規範側の制限と環境側の制限が別々に効くと、
  重なった部分が誰の手も届かない領域になる。**
- **対処（試す順）** ① **resume ではなく新しく担当を起動して渡す**（実測でこれは通った）
  ② それも駄目なら有璽氏へ差し戻す。**★「できない」で止めず、経路を変えて1回試す。**
  → [[feedback_verify_before_declining]]
- **★担当の「不可」報告は、原因まで書かせる。** 最初の報告は「構造的に不可（変わらず）」の
  一行だけで、**理由も、その判断が新しく生じたことも書かれていなかった**。
  エラー全文を求めて初めて権限層と判明した。**結論だけの不可報告を受け取らない。**
