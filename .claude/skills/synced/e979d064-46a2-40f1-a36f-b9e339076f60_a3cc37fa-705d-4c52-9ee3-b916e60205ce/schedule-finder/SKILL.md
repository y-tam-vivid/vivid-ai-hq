---
name: schedule-finder
description: Googleカレンダー（仕事・個人の複数カレンダー対応）を読み込み、指定された日程・時間枠の空き時間を1時間単位でピックアップし、LINE・メール・Slackなど指定フォーマットで出力するスキル。「空き時間を調べて」「日程候補を出して」「来週の空きを教えて」「○曜日から△曜日の間で空いてる時間は？」「アポイントの候補を出して」など、日程調整・スケジュール確認・MTG設定に関わるあらゆるフレーズで必ず使用すること。ユーザーが時間帯や出力先を指定している場合でも、していない場合でも、このスキルを積極的に活用すること。
---

# Schedule Finder Skill

A skill that reads multiple Google Calendars (work + personal), merges their events, identifies free 1-hour slots within a user-specified date and time range, and formats the output for the user's chosen communication channel (LINE, email, Slack, etc.).

---

## Calendar Configuration

The following two calendars are always checked simultaneously:

| Label | Calendar ID | Notes |
|---|---|---|
| 仕事 | `y_tam@vivid-global.com` | Primary work calendar (ビビッド) |
| 個人 | `yuji38132000@gmail.com` | Personal calendar (プライベート) |

A time slot is only marked FREE if it is free in **both** calendars.

---

## Step 1: Parse User Request

Extract the following parameters from the user's message. If any are missing or ambiguous, ask before proceeding.

| Parameter | Example input | Notes |
|---|---|---|
| **Date range** | 「来週月〜水」「4/13〜4/15」「今週金曜」 | Resolve relative terms using current date |
| **Time range** | 「午前中」「9時〜13時」「終日」 | "午前中" = 09:00–12:00, "終日" = 09:00–18:00 |

**Do NOT proceed to Step 2 until both parameters are confirmed.**

---

## Step 2: Fetch Current Time and Calendar Events

1. Use `user_time_v0` to get the current date and timezone (Asia/Tokyo assumed default).
2. Resolve relative date expressions (e.g., "来週月曜" → concrete date).
3. Call `gcal_list_events` **twice in parallel** — once per calendar:
   - **Call A** — `calendarId`: `y_tam@vivid-global.com` (仕事)
   - **Call B** — `calendarId`: `yuji38132000@gmail.com` (個人)
   - Both calls use: `timeMin` = start of date range at 00:00:00, `timeMax` = end of date range at user's specified end time, `timeZone` = `Asia/Tokyo`, `condenseEventDetails` = `true`
4. Merge all events from both calendars into a single unified busy list before computing free slots.

---

## Step 3: Identify Free 1-Hour Slots

Apply the following filtering rules to determine which calendar blocks are **busy**:

### BUSY (block the slot):
- `eventType: "default"` AND `transparency` is NOT `"transparent"` AND `myResponseStatus` is NOT `"declined"` AND `status` is NOT `"cancelled"`

### FREE (ignore the block):
- `eventType: "workingLocation"` → location marker only, not a real block
- `transparency: "transparent"` → marked as free by the user
- `myResponseStatus: "declined"` → user has declined the invite
- `status: "cancelled"` → event was cancelled
- `allDay: true` with no explicit time → treat as free unless it is a confirmed, non-transparent event

### Slot Generation Logic:

```
for each day in date_range:
  for each 1-hour slot in time_range (e.g., 09:00, 10:00, 11:00, ...):
    slot_start = HH:00
    slot_end   = HH+1:00
    if NO busy event overlaps [slot_start, slot_end):
      mark slot as ✅ FREE
    else:
      mark slot as ❌ BUSY (skip)
```

**Partial overlaps count as busy.** If any busy event touches a slot, that slot is marked unavailable.

---

## Step 4: Ask for Output Format

Before generating the output, ask the user:

> 📤 出力フォーマットを選んでください：
> 1. **LINE** — コピペしやすいシンプル枠付き
> 2. **メール** — 件名 + 本文形式
> 3. **Slack** — マークダウン対応形式
> 4. **その他** — 要件を教えてください

Wait for the user's selection before proceeding to Step 5.

---

## Step 5: Format and Output

Use the appropriate template below based on the user's selection.

---

### 📱 LINE Format

```
━━━━━━━━━━━━━━
📅 [期間ラベル]の空き時間（[時間帯]）
━━━━━━━━━━━━━━

【M/DD（曜）】
✅ HH:00〜HH:00
✅ HH:00〜HH:00

【M/DD（曜）】
✅ HH:00〜HH:00
...

━━━━━━━━━━━━━━
上記よりご都合のよいお時間を
お知らせいただけますでしょうか🙏
━━━━━━━━━━━━━━
```

---

### 📧 Email Format

```
件名：【日程調整のお願い】[用件名 or ご面談のご案内]

[相手の名前] 様

お世話になっております。[送信者名]でございます。

ご面談のお時間をいただきたく、候補日程をご案内いたします。
ご都合のよいお日時をお知らせいただけますと幸いです。

■ 候補日程（[期間ラベル] / [時間帯]）

・M/DD（曜） HH:00〜HH:00
・M/DD（曜） HH:00〜HH:00
・M/DD（曜） HH:00〜HH:00
（以下、候補があれば続ける）

上記以外をご希望の場合も、お気軽にお申し付けください。

どうぞよろしくお願いいたします。

[署名]
```

---

### 💬 Slack Format

```
📅 *[期間ラベル]の空き時間（[時間帯]）*

*M/DD（曜）*
✅ `HH:00〜HH:00`
✅ `HH:00〜HH:00`

*M/DD（曜）*
✅ `HH:00〜HH:00`

ご都合のよいお時間をリアクションまたは返信でお知らせください 🙏
```

---

### 🔧 その他フォーマット

If the user selects "その他", ask:
> どのような形式が必要ですか？（例：Notion貼り付け用、コピペ用テキストのみ、など）

Then generate the most appropriate format based on their description.

---

## Notes and Edge Cases

- **Empty result**: If no free slots exist in the requested range, respond:
  > 指定された期間・時間帯に空き枠が見つかりませんでした。別の日程や時間帯をお試しください。

- **Ambiguous time expressions**:
  - 「午前中」→ 09:00〜12:00
  - 「昼前まで」→ 09:00〜12:00
  - 「午後」→ 13:00〜18:00
  - 「夕方まで」→ 09:00〜17:00
  - 「終日」→ 09:00〜18:00
  - Explicit range (e.g., 「10時〜15時」) → use as-is

- **Weekday label**: Use Japanese short form — 月・火・水・木・金・土・日

- **Caller note**: The `[期間ラベル]` in templates should be a natural Japanese phrase derived from the date range, e.g.,「来週月〜水」「4/13（月）〜4/15（水）」.
