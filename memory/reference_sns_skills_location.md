---
name: reference_sns_skills_location
description: SNS生成スキル(vivid-sns-*)の実体はclaude.ai Project内。参照先は投稿アーカイブDBのみ(発信ネタDB非依存)
metadata: 
  node_type: memory
  type: reference
  originSessionId: f50815a5-cd43-414e-9970-be39bf76a691
---

SNSコンテンツ生成スキル群の**実体の在り処**と**参照DB**（2026-07-11 claude.aiで実地確認）。関連: [[project_ai_usage_to_content_pipeline]] / [[project_ai_log_db_consolidation]]

# 実体の場所
- **ローカル(~/.claude/skills)には無い**（MacBook・Mac mini両方確認済＝downloads-weekly-sweepのみ）。
- **実体は claude.ai の Project「SNS有璽個人投稿用プロジェクト」**（url: claude.ai/cowork/project/019d9438-6fb1-7055-84bc-85d15125e3cc）。
- コンテキスト(プロジェクトナレッジ)6+1ファイル: `vivid-sns-illust-prompt-generator_SKILL`／`visual_guideline.md`／`content_themes.md`／`qa_criteria.md`／`platform_spec.md`／`data_sources.md`／`brand_info.md`。
- スキル本体は `.skill` パッケージ（vivid-sns-orchestrator / -text-generator / -image-prompt-generator / -qa-checker、旧sns-content-generator）。法人IG・note用は別Projectに同型で存在の可能性（未確認）。

# 参照DB（data_sources.md 実物の中身）
- 個人IG用 data_sources.md が参照するのは **個人Instagram 投稿アーカイブDB のみ**（`notion.so/e44326edfbc94e68b205bd4211ec5bd7`、直近30投稿）。用途=文体/構成/トーン踏襲・重複チェック・ビジュアルトーン参照。
- **AI活用発信ネタDB(e8a19063)も学習ログ(16936917)も参照していない。**

# ★2026-08-19 前提が変わった ── 生成系が2系統になった

- **Manus AI が同じ「投稿文＋画像」を作れる**（しかも個人IGへは投稿の実行までしている）。
  vivid-sns-* と Manus で**生成系が二重**になっている → [[project_manus_outsourcing]]
- **どちらを正とするかは未決。有璽氏の判断事項。★勝手に片方へ寄せない。**
  決まるまでは 📱発信アカウント台帳の `作り手` 列に従う（アカウントごとに違ってよい）
- 下の「連携への含意」は vivid-sns-* 側の話として引き続き有効

# 連携への含意（重要）
- **AI活用発信ネタDB → 学習ログ の一元化(案A Phase2)は、SNS生成スキルに影響しない**（スキルはアーカイブ参照・アーカイブは統合対象外）。
- 発信ネタDB移行で付替えが要るのは **①モルガンズ週次routine(trig_01GtVoVWQzEKPwbDSeNRQYwL) ②ナレッジハブ④のリンクドビュー ③ドキュメント の3点のみ**。SNSスキルは対象外。
