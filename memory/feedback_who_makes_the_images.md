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

## 作る場所（2026-08-26 実測）

```
Canva     ★これが本命。generate-design で instagram_post が実際に生成できた
          接続先は有璽氏本人のアカウント（「ふくち。グループ 事業計画」等が見える）
          ★1回で4案の候補が返る。保存は create-design-from-candidate を呼んだ時だけ
            ＝候補を出すところまでは可逆
          ★そのままでは使えない。4案のうち使えたのは1案で、英字のプレースホルダ
            （"Warm & Inviting Children's Event Brand"）が残っていた。
            ＝1案選んで edit-design で直す工程が要る。「投げて終わり」にはならない
Manus     MCPは ✔Connected。★APIキーが失効（HTTP 401 "api key has been
          deleted or does not exist"）。保守明けを待つ話ではない。
          Manus Web → 設定 → API Integration で再発行 → ~/.config/manus/api_key
OpenAI    ★APIキーは無い（MCP登録なし・~/.config になし・環境変数なし）。
          ★ChatGPT の有料契約とAPIキーは別物。Plusを持っていてもAPIは使えず、
            platform.openai.com で別に発行し従量課金を登録する必要がある
```

**★ブランドテンプレート機能は使えない**（`search-brand-templates` が
"requires a Canva paid plan" を返す＝Teams以上の機能）。**だが要らない。**
アカウントごとの雛形は、Canvaで1枚ずつ作って `copy-design` で複製すれば同じことができる。

## ★この節で1度間違えた（2026-08-25 → 08-26 訂正）

**エラー文1本で「Canvaは無料プラン」と断定し、有璽氏の訂正で覆った。**
実際は有料アカウントで、生成は通った。

```
見たもの   search-brand-templates → "requires a Canva paid plan"
やった判断  ＝このアカウントは無料プラン
正しい読み  ＝この機能が Teams 以上。プランの有無とは別の話
やるべきだった  生成そのものを1回叩く（それが目的の機能なのだから）
```

**★エラー文は「その機能が使えない理由」しか語らない。アカウント全体の能力を語らない。**
→ [[feedback_one_route_is_not_verification]] ／ 能力を書き溜めない話は [[reference_tool_access_map]]
