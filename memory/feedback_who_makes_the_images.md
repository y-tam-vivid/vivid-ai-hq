---
name: feedback_who_makes_the_images
description: SNS画像は「写真の切り出し」と「デザイン物」で作り手を分ける。デザインはManus等の外、写真の判断はこちら
metadata:
  type: feedback
---

**SNSの画像加工はManus（または同等の生成系）に任せる**（2026-08-25 有璽氏）。
**あわせて、アカウントごとにデザインを使い分ける。** 同じ写真を使ってもよいが、
見た目は分ける。

**Why:** こちらがPILで組む画像は「読める」止まりで、アカウントの顔にならない。
発信先が増えるほど、全部が同じ見た目になる方が損になる。

## ★画像を2つに割る。全部を外へ出さない

```
写真の切り出し・トリミング      ← こちら（Claude Code）
  規約と肖像の判断が要るため。2026-08-25、会場ポスターとイーゼル看板が
  大きく写る2カットを Roblox の表記規約に沿って画角から外した。
  この判断は規範（[[reference_roblox_event_naming_rules]]）を読んでいる側でないとできない

表紙カード・数字カード・バナー  ← Manus／生成系（外）
  アカウントごとの世界観をつくる仕事。こちらの守備範囲ではない
```

**渡すときは「素材＋制約」で渡す。**「いい感じに」では規約判断が外へ流出する。
出してよい数字・注記（n=37 等）・使ってはいけないロゴを、指示文に必ず書く
→ [[project_manus_outsourcing]]（Manusは社外＝情報ファイアウォールの適用先）。

## 使い分けの正本は 📱発信アカウント台帳。新しい器を作らない

**既に3列ある。**`視覚トーン` ／ `デザイン正本`（Driveへのリンク）／ `作り手`。
アカウント別のデザインを決めたら、**ここを埋める**。別表を作ると二重管理になる。
collection://3f0202d1-2352-4695-a399-626705eb9014

## 着手できる条件（2026-08-25 実測。どれか1つが要る）

```
Manus            MCPは ✔Connected。★APIキーが失効（HTTP 401 "api key has been
                 deleted or does not exist"）。保守明けを待つ話ではない。
                 ★人が要る：Manus Web → 設定 → API Integration で再発行し
                 ~/.config/manus/api_key を差し替える ── これが最短
ChatGPT / OpenAI ★連携はゼロ。MCP登録なし・~/.config になし・環境変数なし
Canva            ✔Connected。ただし★無料プラン。
                 ブランドキットもブランドテンプレートも有料機能で叩けない
                 （list-brand-kits は空配列、search-brand-templates は
                  "requires a Canva paid plan" を返す＝2経路で確認）
Figma / Gamma    ✔Connected。画像量産の用途では未検証
```

**★道具の可否はここに書き溜めない**（腐る）→ [[reference_tool_access_map]]。
上は「この日そうだった」という実測の記録であって、次に使うときは必ず取りに行く。
