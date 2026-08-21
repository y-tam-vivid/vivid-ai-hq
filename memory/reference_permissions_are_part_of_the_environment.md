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
