---
name: project_fukushi_platform_claude_operated
description: 放デイ版の運営支援＋医療連携などを束ねる福祉プラットフォーム（現場はClaudeから操作）の構想。11/18 有璽氏の前提
metadata:
  type: project
---

# 福祉の運営プラットフォーム（Claudeから操作する）── 構想（2026-11-18〜）

**きっかけ**：有璽氏が D-Luca ポータル（https://care-luca-sooty.vercel.app/）を見せ「放デイ版でこういう仕組みを作りたい」（11/18）。
D-Luca の画面の中身は [[project_kaigo_proposal_pack]] の11/18の行。

**有璽氏の前提（11/18・原文の要旨）**
- 個々のアプリはバラバラでよい（医療連携システム＝[[project_iryo_renkei_system]] とも繋ぎたい）
- 最後にそれらを紐付けるプラットフォーム／ポータルを置く
- そのプラットフォーム自体を Claude 等から操作できる → ★現場は Claude を操作するだけで済む形

**Why:** アプリごとに画面を覚えさせない。入口を Claude 1つにする。
**How to apply:** 各アプリは「APIを持つ部品」として作る。ポータルは共通のログイン・事業所・利用者の名寄せと、Claude向けの窓口（MCPサーバー）を持つ。
安全・専門判断（個別支援計画など）は Claude からも「案を出す」まで（fukuchi-core §1）。

**未決（11/18 時点）**
- 自社用か／外販か／D-Lucaとの共同か（提携先と競合しうる）── 有璽氏へ問い済み・未回答
- 最初に作る部品（推し：加算チェック＋運営自主点検）
