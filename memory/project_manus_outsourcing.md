---
name: project_manus_outsourcing
description: Manus AI を社外の手足として接続（MCP5本）。個人IGは投稿実行までManusへ委任済＝承認規範の例外。生成系がvivid-sns-*と二重で未決
metadata: 
  node_type: memory
  type: project
---

**Manus AI が Claude Code に MCP ツールとして繋がった**（2026-08-19）。自律でブラウザを触る
**社外の手足**。使うのはモルガンズ（広報PR）。関連: [[project_pr_agent]] /
[[reference_sns_skills_location]] / [[project_ai_usage_to_content_pipeline]]

# 現在地（2026-08-20 時点）

```
実体      bin/manus.py   1ファイルでMCPサーバ(--mcp)とCLIを兼ねる。依存なし・Python3.9互換
          API v2  task.create / listMessages / sendMessage / confirmAction
ツール    manus_ask / manus_status / manus_wait / manus_reply / manus_confirm
規範      .claude/agents/pr.md の「Manus AI への外注」「発信ラインの運用」節が正本
接続      MacBook = ✔Connected ／ mini = 未登録
残①      APIキー未発行（有璽氏の操作。Manus Web → 設定 → API Integration）
          置き場 ~/.config/manus/api_key（キーだけ1行・chmod 600）★API本体は未実測
残②      vivid-sns-* と Manus のどちらを正とするかが未決
```

# ★忘れると設計を壊す4つ

- **★個人Instagram は「投稿の実行」まで Manus が行っている**（2026-08-20 実測。
  `@yuji_tam3.0_2026` へのカルーセル投稿）。＝**「対外発信は必ず人が押す」を一律に適用しない。**
  有璽氏がそのアカウントについて恒久的に委任している、と読む。
  **ただし個人アカウントの委任は法人アカウントの委任ではない。**
  判断は 📱発信アカウント台帳の `投稿の実行` 列（Manusが投稿する／人が投稿する／未定）。
  **未定なら投稿させない。** 台帳 https://app.notion.com/p/067a2cb73d974f9f837b3b680ee6a121

- **★Manus 側に品質ゲートが既にある。重ねて検査しない**（2026-08-20 実測。Manus 自身が
  「投稿は保留しました」と止め、判定表を返してきた。「申請しないと損！」を不安を煽る表現として不合格）。
  モルガンズが見るのは**Manus には構造的に見えないもの**だけ ── ①アカウント間の混線
  ②解禁日・エンバーゴ ③台帳との整合 ④発信タイミングの全体設計。
  **Manus の「不合格」は事故ではなく正常動作。押し切らせない。**

- **★Manus は社外。** 未公表の発表・解禁前のネタ・内部の数値目標・顧客名・個人情報・
  交渉中の相手は渡さない。渡すなら**公開情報だけで完結する形に指示文を書き換えてから**投げる
  → 情報ファイアウォール（fukuchi-core）の適用先が1つ増えた

- **★`manus_ask` / `manus_reply` はクレジットを消費する＝「お金」。** 投げる前に
  **指示文そのものを有璽氏に見せて承認を得る**。読むだけの `manus_status` / `manus_wait` は承認不要

# 使い方の要点

- 投げてよいのは**時間はかかるが判断が要らない仕事**（掲載モニタリング・媒体/記者の下調べ・
  競合巡回・公的データ収集）。**判断そのもの**（発表文の起草・ニュースバリュー評価・危機対応）は投げない
- 指示文には必ず **④使った事実の出典** を出させる。**出典が無いと検品できない**
  （Manus が調べて足した事実＝こちらの資料に無い＝裏が取れていない）
- 台帳に**空欄があるアカウントへは投げない**。埋めてもらってから動く
  （空欄のまま投げると、こちらの推測がそのアカウントの声として世に出る）
- 記録 → Notion⑥ https://app.notion.com/p/3c17b1568b5781d1a7c6e17e6053bec2
