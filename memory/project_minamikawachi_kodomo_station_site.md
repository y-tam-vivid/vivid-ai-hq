---
name: project_minamikawachi_kodomo_station_site
description: NPO法人 南河内こどもステーション 公式サイト素案v1 ── Claude Designの書き出しをVercelへデモ公開済み（2026-09-28）
metadata:
  type: project
---

**現在地（2026-09-28）**：Claude Design の書き出し（素案v1・4ページ＋スタイルガイド）を
そのまま Vercel へデモ公開した。**https://minamikawachi-kodomo-demo.vercel.app/**
（合言葉なし・noindex＋robots.txt で検索よけ）。本実装（静的HTML/WP等への作り直し）は未着手。

- 入力 `~/Downloads/南河内こどもステーション WEBサイト構築_design_handoff_minamikawachi_kodomo_station/`（読むだけ・無変更）
- 公開用コピー `~/kodomo-station-demo/`（Vercelプロジェクト `minamikawachi-kodomo-demo`・チーム fuku-chi-vivid）
- ページ：index（トップ）／about／activities／join／styleguide
- **★`.dc.html` は README に「単体では動かない」とあるが、HTTP配信すれば動く**
  （support.js が unpkg から React/Babel を読む）。file:// では動かない
- **★日本語ファイル名は Vercel で404になった**（macOSの濁点分解NFD。NFC化しても解消せず）
  → 英字名へ付け替えてリンクを書き換えた。次回も最初から英字にする
- 除外：`README.md`・`assets/pamphlet/`（16MB・どのページからも参照されていない）
- 【要差替】付箋・「素案（検討用）」ラベルは残したまま（デモなので意図どおり）
- 要差替12項目は README「未確定・要差替 一覧」が正本

関連：[[reference_vercel_free_plan_protection]]
