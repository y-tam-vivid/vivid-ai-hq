---
name: feedback_model_usage_rule
description: モデル使い分けルール：Sonnet標準/Opus難所/Fable封印(指名時のみ)＋能動的推奨
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f50815a5-cd43-414e-9970-be39bf76a691
---

Claude/エージェントのモデル使い分けの標準ルール。

- **既定=Sonnet 5**（速い・安い、$3/$15）。日常業務・要約・下書き・調整・定例処理・アプリ量産はSonnetで完遂。
- **難所=Opus 4.8 へ昇格を"提案"**（$5/$25）。契約・複雑な設計/実装・精度が結果を左右する分析など。勝手に切り替えず「Opus 4.8を推奨（理由）」と述べて承認を仰ぐ。
- **Fable 5 は封印、明示指名時のみ**（$10/$50＝Opusの約2倍）。極めて難しい一発勝負・大規模移行・長時間自律のみ提案。
- **過剰も進言**：Opus/Fableで受けた依頼でも「Sonnetで十分」と判断したらダウングレードを提案。

**Why:** Fableは高コストゆえ封印が合理的。Opus 4.8で実力的にも十分。地力はモデル固有で指示では変わらないため、"能動的な推奨"という形で最適配分する。

**How to apply:** 全エージェント(~/.claude/agents/*.md)は `model: sonnet` を既定に持ち、本ルールを本文に明記済み。Fable Style([[feedback_language_japanese]]と同じ~/.claude/output-styles/fable-mode.md)にも「モデル使い分け(能動的推奨)」節あり。正はNotion「🤖 Claude運用ルール（モデル使い分け）」。関連：[[project_agent_naming]]
