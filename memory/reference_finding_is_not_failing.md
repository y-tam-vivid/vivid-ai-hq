---
name: reference_finding_is_not_failing
description: 検査スクリプトの終了コードは「完走したか」で決める。「見つけたか」で決めると監視が逆向きになる
metadata:
  node_type: memory
  type: reference
---

**検査が異常を見つけるほど「検査が壊れた」ことになる、逆向きの監視の型。**

## 実測（2026-08-26 つる）

`bin/memory_audit.py` は索引ズレを検出すると `sys.exit(1)` を返していた。
呼び出し元 `bin/daily_jobs.sh` は rc≠0 を**ジョブの失敗**として扱う。結果:

```
検出あり → rc=1 → daily_jobs.sh が「恒久エラー」と判定
                  ① その日の残り枠を即諦める（.gaveup を立てる）
                  ② 「日次ジョブが失敗しました」を有璽氏へ通知（1日5回）
                  ③ daily_jobs 自身の心拍を「失敗」にする
```

2026-08-25 は5枠すべてが1回目で `.gaveup`。**巡回自体は正常に完走し、
心拍も🟡警告で正しく着弾していた。**壊れていたのは終了コードの意味づけだけ。

**Why:** 終了コードは1本しかないのに、2つの別々のことを載せていた ──
「検査が完走したか」と「検査結果が綺麗か」。呼び出し元が読めるのは前者だけ。
後者を載せると、**汚れが多い日ほど「システムが壊れている」と報告される**。
慢性の赤は本物の赤を埋もれさせる（fukuchi-core「慢性化した赤はゲートにならない」）。

**How to apply:**

| 何を伝えるか | どこに載せるか |
|---|---|
| 検査が完走したか（例外・認証切れ・対象が無い） | **終了コード**。落ちたときだけ非0 |
| 検査結果が綺麗か（ズレN件・要対応M件） | **心拍の 成功/警告/失敗** と標準出力 |

- **新しい検査スクリプトを daily_jobs.conf / cron へ載せる前に、
  「所見ありのとき rc は何か」を1回実測する。** 名前と既定値からは読めない
  → [[reference_dangerous_entrypoints]]
- 直したら `.gaveup` / `.attempts` の残骸も消す。残っているとその日は走らない。

関連 [[project_memory_layer_design]] [[feedback_memory_index_hygiene]]
[[project_automation_register]] [[feedback_find_holes_without_being_told]]
