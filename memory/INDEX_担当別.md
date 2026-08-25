# 担当別 ── 誰が常設で何を読むか（★この1枚が正本）

**ビビ（中央窓口）はこの表を持って振る。各エージェントは自分の行だけを読む。**

> **★agents/*.md へ内容を写さない。** 写した瞬間に二重管理になり、必ずズレる。
> 各定義には「常設セットは `memory/INDEX_担当別.md` の自分の行」と1行だけ置く。
> 設計の全体像 → [[project_memory_layer_design]]

## 配り方は2層（2026-08-25 有璽氏）

```
常設   その担当が起動したら必ず読むもの   ← この表で決める。事前に渡しておく
都度   案件ごとに「これも見て」          ← ビビが振る。この表を見て選ぶ
```

## 常設セット

| 担当 | 定義ファイル | 常設で読む分野索引 |
|---|---|---|
| ビビ（秘書・中央窓口） | `secretary.md` | **全部**（振る側なので全分野を把握する）＋ [INDEX_担当と案件](INDEX_担当と案件.md) |
| ナミ（CFO） | `cfo.md` | [INDEX_notion](INDEX_notion.md) ／ [INDEX_担当と案件](INDEX_担当と案件.md) |
| センゴク（CLO） | `legal.md` | [INDEX_notion](INDEX_notion.md) ／ [INDEX_担当と案件](INDEX_担当と案件.md) |
| ロビン（CKO） | `cko.md` | [INDEX_notion](INDEX_notion.md) ／ [INDEX_仕組み](INDEX_仕組み.md) |
| モルガンズ（広報PR） | `pr.md` | [INDEX_発信](INDEX_発信.md) ／ [INDEX_notion](INDEX_notion.md) |
| フランキー（デザイン） | `design.md` | [INDEX_発信](INDEX_発信.md) ／ [INDEX_notion](INDEX_notion.md) |
| ステラ（開発統括） | `dev-producer.md` | [INDEX_仕組み](INDEX_仕組み.md) ／ [INDEX_担当と案件](INDEX_担当と案件.md) |
| ピタゴラス（システム） | `system-developer.md` | [INDEX_仕組み](INDEX_仕組み.md) ／ [INDEX_営業](INDEX_営業.md) |
| エジソン（アプリ） | `app-developer.md` | [INDEX_仕組み](INDEX_仕組み.md) |
| リリス（ウェブ） | `web-developer.md` | [INDEX_仕組み](INDEX_仕組み.md) ／ [INDEX_発信](INDEX_発信.md) |
| つる（データ検査役） | `data-auditor.md` | [INDEX_営業](INDEX_営業.md) ／ [INDEX_notion](INDEX_notion.md) |
| ドーベルマン（自動処理の番人） | `automation-watchdog.md` | [INDEX_仕組み](INDEX_仕組み.md) |
| クローバー博士（研究調査） | `researcher.md` | [INDEX_発信](INDEX_発信.md) |

**★全担当に共通で届くもの**（ここには書かない・自動で載る）
`fukuchi-core`（規範の正本）／`memory/MEMORY.md`（全体に効く記憶）／`WORKING.md`（進行中）

## ビビが「都度」振るときの選び方

```
議題を受ける
   ▼
何をする仕事か
   営業・顧客・台帳・kintone・名刺   → INDEX_営業
   cron・同期・監視・GAS・シェル     → INDEX_仕組み
   Notionの読み書き・DB・Drive       → INDEX_notion
   広報・SNS・デザイン・成果物        → INDEX_発信
   担当の定義・組織・個人案件         → INDEX_担当と案件
   ▼
担当へ渡すプロンプトに「着手前に memory/INDEX_◯◯.md を読んでください」と明記する
   ★エージェントは MEMORY.md を自動では読まない（実測済み）。渡さなければ届かない
```

## この表を直したとき

- **`check.sh` が「表に出てくる INDEX_* が実在するか」を見る。**行を足したら必ず通す。
- 担当を増やしたら、この表にも1行足す。**足し忘れは check.sh では検出できない**
  （定義ファイルは増えても、常設セットが空でよい担当もあり得るため）→ 増設時は手で足す。
