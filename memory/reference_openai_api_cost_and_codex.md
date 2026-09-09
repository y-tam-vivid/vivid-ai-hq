---
name: reference_openai_api_cost_and_codex
description: OpenAI API は画像生成にだけ使っている。コストの下げ方と、Codex では画像生成できない事実
metadata:
  type: reference
---

## ★APIを使っているのは「画像生成」だけ（2026-09-09 実測）

有璽氏「このChatGPTとの連携はAPIを毎回使う必要があるんですか？ そうじゃなくて、あくまで
画像生成に使うのですか？ **多分前者だよね**」── **★後者が正しい。訂正した。**

```
実測（bin/*.py を grep）
  api.openai.com を叩いている箇所      1つだけ
  bin/gen_images_openai.py:41          /v1/images/generations
  ★chat/completions や responses を叩いている箇所   0件
```

**会話・コード生成・要約には1円も使っていない。** ここは Claude Code のまま。
**画像を作るときだけ、その回数ぶんだけ課金される。**

## コストの下げ方（実測値つき）

```
モデル×品質                1枚      18枚
gpt-image-1.5 high        $0.133   $2.39   ← 2026-09-08 に使った
gpt-image-1.5 medium      約$0.05  約$0.90
gpt-image-1-mini          約$0.005 約$0.09  ★27分の1
```

- **★実際にかかったのは 33回・約$4.4**（作り直しを含む）。
- **★下げ方は3つ**：①`--quality medium` ②`--model gpt-image-1-mini`
  ③**作り直しを減らす**（`--max-retry 1`。合否線を厳しくしすぎると作り直しで倍かかる）。
- **★まず mini で18枚($0.09)出して構図を確かめ、採用する枠だけ high で作り直す**のが安い。

## ★Codex では画像生成できない（1経路・要再確認）

有璽氏「単なるChatGPTじゃなくて、あちらにある **CodeX** とかと連携する形に作りたい」。

```
Codex          ★コーディングのエージェント（CLI / IDE / クラウド）
               ChatGPT Plus・Pro・Business に含まれ、プランごとの利用上限で使える
               ＝ API課金とは別枠で使える
               ★ただし画像生成の機能は持たない
ChatGPT Plus   API クレジットは1円も付かない。★課金系統が完全に別
               画面の中では画像生成できるが、外から叩く口ではない
```

**→ 画像生成のコストを Codex に寄せることはできない。**
安くするなら上の「モデルと品質を落とす」しかない。
**★これは2026-09-09 に Web検索1経路で確認しただけ。** 実際に Codex を入れて試してはいない。

## この環境の現状（2026-09-09）

```
OPENAI_API_KEY   ~/.vivid-relay/config.env（★MacBook・mini の両機に配布済み）
Codex CLI        ★入っていない（gh / netlify / wrangler / surge も無い）
```
