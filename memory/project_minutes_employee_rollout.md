---
name: project_minutes_employee_rollout
description: 議事録の社員展開（パイロット5名）。受付フォルダ・共有区分・機微判定まで稼働、全社への自動昇格は未実装
metadata:
  node_type: memory
  type: project
---

**「まず自分の型を固めてから社員へ」の後半。** 個人側が回る状態になったので、2026-08-19に入口を開いた。

## 入口（受付フォルダ）

```
[Y05]議事録 関連/[00]議事録_受付/     親 1X2rRn7NP3yah5oX9Q7ezSZJT_FXHpblB は共有しない
   柴田純世  1dQx84E73NuUcL4Jx1AMMJ5s81HpHmgzc
   松本秋紀  1qqEmwQgp7PTNwC_JlB7759hmkB0cEjvB
   鈴木亜弓  1g3s5J3Bk6rUp1iVm6CjyH1p4JhAVoISu
   佐藤真央  1hCM_AWWjNLvzbTy4cHuQgmLh5JxuZj1V   ※jinji_soumu@ は部門アドレス
   高橋峻    12xdktQWl8yKgyvZsuB_PMhdI_ynk8eGK
```

**社員ごとに1フォルダ。** 全員で1つにすると処理までの最大1時間、他人の議事録が見える。
個人フォルダならその窓が閉じる。**この形が選べるのは、ソースフォルダのキーを
手段ラベル→フォルダIDに変えたから**（従来は5名足した瞬間に全部衝突した）。

設定シート「ソースフォルダ」に5行（手段ラベル=その他／共有区分=社員）。
**手段ラベルを「その他」にしたのは、nottaとMeetのどちらが来るか分からないため**＝AIに本文から判断させる。

## いまの流れ（全社へはまだ行かない）

```
社員が置く → 毎時08分ごろ処理 → 🔒個人議事録DB（オーナー区分=社員）
                              → 機微判定が付く
                              → ★ここで止まる。昇格の自動経路は未実装（意図的）
```

**1〜2週間の実データを見てから自動昇格を設計する。** 置き方のばらつきと機微判定の当たり方を先に見る。

## 決まっていること

| 論点 | 決定 |
|---|---|
| 規模 | パイロット5〜6名。**全員展開はしない**（有璽氏 2026-08-19） |
| 機微 | 基本は全社共有。**AIが機微と判定したものだけ自動で止める**。人が見て判断 |
| 止め方 | Notionで止めるだけ。**Driveのファイルは動かさない**（見せないことが目的で、片付けることが目的ではない） |
| 見せ方 | 社員はSlack通知とタスクだけ。コアメンバーのみNotion |
| 案内 | 「📝 会議の記録の残し方（全社共通）」`3c17b1568b57811784a2c8f2cec07501` |

## 残り

- 昇格の自動経路（オーナー区分=社員 かつ 機微が空 → 全社へ）
- 差し戻し／アーカイブの手続き
- 案内ページの配り方（社員はNotionを持たない前提。Slack貼付かPDFが本命）
- 承認カードと重複退避の競合（退避してもカード承認で戻る）

関連 [[project_giji_automation_gas]] [[project_minutes_quarantine]] [[reference_link_sharing_inherits_everywhere]] [[project_calendar_template_autofill]]
