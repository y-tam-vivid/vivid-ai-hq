---
name: vivid-sns-illust-prompt-generator
description: 田村有璽の個人Instagramアカウント向けに、Nano Banana（Gemini 2.5 Flash Image）で生成する「3Dレンダリング寄り温かみ系イラスト」のプロンプトを生成するスキル。福祉×IT・DX、福祉×お金、パーソナル：思想の3テーマで使用される。投稿文と投稿テーマカテゴリを入力として、ブランドガイドラインに沿ったシーン記述型プロンプト（日本語版・英語版）を出力する。「イラストプロンプトを作って」「Nano Bananaのイラストプロンプトが欲しい」「投稿に合わせたイラストを生成したい」などのフレーズで必ず使用する。`vivid-sns-image-prompt-generator`の後継スキルとして独立構築されており、当面は本スキル単独で動作する。オーケストレーター統合は別途対応予定。
---

# vivid-sns-illust-prompt-generator

田村有璽の個人Instagramアカウント向けイラスト画像生成プロンプトを、Nano Banana（Gemini 2.5 Flash Image）に最適化された形式で生成するスキル。

---

## 1. スキル概要

### 1.1 責務

本スキルは、投稿文と投稿テーマを入力として、以下を満たすイラスト生成プロンプトを出力する。

- **3Dレンダリング寄り温かみ系**の単一スタイル（過去投稿260304系を参照モデルとする）
- ブランドガイドライン（`visual_guideline.md`）への準拠
- テーマ別アクセントカラーの適切な織り込み
- 日本語版・英語版の両言語プロンプトを併記

### 1.2 適用範囲

| 対象テーマ | 説明 |
|---|---|
| **福祉×IT・DX** | 福祉施設のDX事例、AI活用、データ可視化を題材としたイラスト |
| **福祉×お金** | 補助金・融資・節税の知見を視覚化するイラスト（写真主体ではない場合） |
| **パーソナル：思想** | 価値観・信条を抽象的に表現するイラスト |

### 1.3 適用範囲外

以下のテーマには本スキルを使用しない（別スキルが対応）。

- パーソナル：日常業務・ボランティア（写真スキルが対応）
- パーソナル：プライベート（写真スキルが対応）
- パーソナル：寺社仏閣（写真スキルが対応）
- 漫画形式の投稿（漫画風スキルが対応）
- テキスト主体の告知・宣言型投稿（バナースキルが対応）

### 1.4 トリガー条件

以下のいずれかに該当する場合に本スキルを起動する。

- ユーザーが「イラストプロンプトを作って」「Nano Bananaのイラストプロンプトが欲しい」「投稿に合わせたイラストを生成したい」等の依頼を行った場合
- 投稿文生成スキル（`vivid-sns-text-generator`）の後段として呼ばれた場合で、投稿テーマが上記「適用範囲」に該当する場合
- ユーザーが投稿カテゴリを「福祉×IT・DX」「福祉×お金」「パーソナル：思想」のいずれかに指定し、画像種類を明示しないか「イラスト」と指定した場合

オーケストレータースキル（`vivid-sns-orchestrator`）からの呼び出しは、現時点では未対応。各画像種類スキルの完成後に統合作業を行う。

---

## 2. 入力仕様

### 2.1 必須入力

| 項目 | 説明 | 例 |
|---|---|---|
| `post_text` | 投稿本文（フック・本文・CTAを含む全文） | 「施設にいる間、元気ですか？〜」 |
| `theme_category` | 大テーマ名 | `福祉×IT・DX` / `福祉×お金` / `パーソナル：思想` |

### 2.2 任意入力

| 項目 | 説明 | デフォルト |
|---|---|---|
| `aspect_ratio` | アスペクト比 | `4:5`（縦長フィード推奨） |
| `text_overlay` | 画像内テキスト（10文字以内） | なし |
| `text_position` | テキスト配置 | `画像上部` |
| `additional_requirements` | 追加要件（特定の要素・避けたい要素など） | なし |
| `past_post_reference` | 過去投稿のスタイル参照（過去投稿アーカイブから自動取得） | 自動 |

### 2.3 入力検証

以下に該当する場合、プロンプト生成前にユーザーに確認する。

- `theme_category` が「適用範囲外」（写真・漫画・バナー向けテーマ）の場合 → 別スキルの利用を案内
- `post_text` が空または極端に短い（50字未満）場合 → 投稿文の補足を依頼
- `text_overlay` が10文字を超える場合 → 短縮を依頼

---

## 3. 参照ファイル

本スキルは以下のプロジェクトファイルを参照する。

| ファイル | 参照する情報 |
|---|---|
| `visual_guideline.md` | カラー設計、避けるべき表現、画像内テキスト方針、アスペクト比 |
| `content_themes.md` | テーマ別の狙い、訴求軸、テーマ候補 |
| `brand_info.md` | 発信者情報、ブランドボイス、NGワード |
| `qa_criteria.md` | 画像プロンプトの判定項目（自己チェック用） |
| `data_sources.md` | 過去投稿アーカイブのURL（スタイル参照用） |

参照は必須であり、各ファイルが存在しない場合はユーザーに通知する。

---

## 4. プロンプト生成プロセス

本スキルは以下の5ステップで動作する。

### Step 1：投稿文の意図解析

`post_text` から以下を抽出する。

- **核となるメッセージ**（読者に伝えたい主旨）
- **感情トーン**（共感／希望／信頼／真摯さ／温かさ／挑戦 など）
- **登場する具体物**（施設・タブレット・スタッフ・利用者・補助金書類等）
- **訴求軸**（情熱／共感／知識／未来／人間性のいずれか）

### Step 2：テーマ別ガイドラインの適用

`theme_category` に応じて以下を決定する。

| テーマ | アクセントカラー | 主な被写体傾向 | 推奨シンボル |
|---|---|---|---|
| 福祉×IT・DX | オレンジ#FFA500（情熱） | スタッフ・利用者・タブレット・データ可視化 | 繋がるノード、データの流れ、温かい光のライン |
| 福祉×お金 | オレンジ#FFA500（信頼性） | スタッフ・経営者・書類・グラフ | 伸びるグラフ、土台のある建物、芽吹く植物 |
| パーソナル：思想 | オレンジ#FFA500（芯のある発信） | 抽象的人物・象徴物・自然要素 | 灯り、橋、並んで歩く、絵筆 |

### Step 3：構図・要素の選定

Step 1・2の結果から、以下を決定する。

- **被写体の数と配置**（中央配置／三分割／左右対称 等）
- **背景設定**（施設内／屋外／抽象空間）
- **登場人物の人数と属性**（スタッフ・利用者・経営者・抽象人物）
- **シンボル要素**（推奨シンボルから1〜2点選定）

### Step 4：プロンプト組立

第5章のテンプレートに沿って、5要素（被写体／構図／ライティング／スタイル／色調）を満たすプロンプトを組み立てる。

### Step 5：自己チェックと出力

`qa_criteria.md` の画像プロンプト判定項目（必須・推奨・NG）に対して、内部的にセルフチェックを行う。

- 必須項目：`visual_guideline.md`準拠／シーン記述型／5要素網羅／アスペクト比指定
- 推奨項目：投稿文との整合／両言語対応／シンボル選定／過去投稿画像とのトーン一貫性
- NG項目：札束・現金描写／実在キャラ・有名人連想／ステレオタイプ表現／10文字超の画像内テキスト

問題がなければ、日本語版・英語版の両プロンプトを出力する。

---

## 5. プロンプトテンプレート

### 5.1 基本テンプレート（日本語版）

以下の構造でプロンプトを組み立てる。

```
[被写体記述]
[構図記述]
[ライティング記述]
[スタイル記述]
[色調・カラーパレット記述]
[画像内テキスト指定（任意）]
[アスペクト比指定]
[避けるべき要素のネガティブ指示]
```

### 5.2 雛形（日本語）

```
3Dレンダリング寄り温かみのあるイラストで、[被写体・シーン]を描く。
[構図方針：中心構図/三分割/左右対称]で、[人物の数と属性、配置]を配置する。
ライティングは朝〜昼の自然光で、コントラストは控えめに、柔らかな光が[特定の要素]を照らす。
画風は[260304系参照：施設の日常を描く温かみのあるイラスト]、線は柔らかく、人物の頬にはほんのり赤み、表情は穏やかで自信がある。
背景はオフホワイト〜ベージュ系（#FAFAFA基調）、アクセントとしてネイビー#003366を[文字・小要素・タイトル装飾]に、テーマアクセントの[#FFA500オレンジ等]を[データの流れ・光のライン・小要素]として控えめに配置する。
[画像内テキスト：「キーワード（10文字以内）」を画像上部に配置（任意）]
アスペクト比：4:5（Instagram縦長フィード推奨）。
避けるべき要素：札束・現金の直接描写、ギラギラ・メタリックな質感、実在キャラクター・ブランドロゴ、ステレオタイプ的な人物表現、過度に冷たいテクノロジー感。
```

### 5.3 雛形（英語）

```
A warm, slightly 3D-rendered illustration depicting [subject/scene].
Composition: [center-focused/rule-of-thirds/symmetrical], with [number and type of figures] arranged [position description].
Lighting: soft natural morning-to-midday light, low contrast, gentle illumination on [key element].
Style: warm and approachable illustration in the manner of welfare-facility daily-life imagery, with soft lines, subtle blush on figures' cheeks, calm and confident expressions.
Color palette: off-white to beige background (#FAFAFA base), navy #003366 as accent for [text/small elements/title decoration], theme accent [orange #FFA500 etc.] used sparingly for [data flow/light streams/small elements].
[Optional: in-image Japanese text "[keyword (≤10 chars)]" placed at the top of the frame]
Aspect ratio: 4:5 (Instagram vertical feed).
Avoid: direct depictions of cash or currency, glossy or metallic textures, recognizable real-world characters or brand logos, stereotypical figure portrayals, overly cold or sterile technology aesthetics.
```

### 5.4 テンプレートの変数置換ルール

- `[被写体・シーン]`：Step 1で抽出した「核となるメッセージ」と「登場する具体物」から記述を構築
- `[構図方針]`：Step 3で選定した構図を記述
- `[人物の数と属性、配置]`：Step 3で選定した内容を具体的に記述
- `[特定の要素]`：シーンの中で最も重要なオブジェクト（例：タブレット、書類、握手）
- `[データの流れ・光のライン・小要素]`：テーマアクセントカラーを織り込む箇所を具体化

---

## 6. スタイル定義（3Dレンダリング寄り温かみ系）

過去投稿260304系（5枚）を参照モデルとする。以下の特徴を全プロンプトで踏襲する。

### 6.1 描画スタイル

| 要素 | 仕様 |
|---|---|
| 線質 | 柔らかい線、はっきりとした輪郭線（漫画風の硬質な線ではない） |
| 陰影 | やわらかいグラデーション、3Dレンダリング的な立体感（フラットすぎない） |
| 質感 | マットで温かみのあるトーン、ギラギラ・メタリックは禁止 |
| 全体の雰囲気 | 「施設の日常」を温かく描く絵本的・親しみやすい質感 |

### 6.2 人物表現

| 要素 | 仕様 |
|---|---|
| 顔の描き方 | 簡略化された表情、目は黒目を強調（リアルすぎない） |
| 頬 | ほんのり赤みを差す（生気を感じる温かさ） |
| 表情 | 穏やかで自信がある／時に内省的／笑顔は控えめで自然 |
| 体型 | 全身バランスはリアル寄り、誇張なし |
| 服装 | スタッフは制服（ポロシャツ・エプロン）、利用者は普段着、経営者はビジネスカジュアル |

### 6.3 背景・空間表現

| 要素 | 仕様 |
|---|---|
| 場所 | 福祉施設内（リビング・居室・キッチン）／屋外（庭・公園）／抽象空間 |
| 床・家具 | 木目調を多用、観葉植物を配置 |
| 空気感 | 余白を活かす、過度に詰め込まない |
| 奥行き | 軽い透視図法、ボケは入れすぎない |

### 6.4 シンボル・装飾要素

`visual_guideline.md` に定義された推奨シンボルから、テーマに応じて1〜2点選定。

- **成長**：芽吹く植物、伸びるグラフ
- **信頼**：握手、肩を並べる人物
- **情熱**：灯り、穏やかな炎
- **伴走**：並んで歩く、橋
- **創造**：絵筆、色が広がる
- **テクノロジー**：シンプルなデバイス、繋がるノード（控えめに）

### 6.5 「データの流れ」表現（DX系特有）

福祉×IT・DXテーマ特有の表現として、以下を採用する。

- **有機的な光のライン**：ライトブルー・ミントグリーン系の柔らかな光が、人物・タブレット・センサー間を繋ぐように流れる
- **ハート・睡眠アイコン等の温かいピクトグラム**：データを冷たい数字ではなく「人を見守る情報」として表現
- **タブレット・センサーの描き方**：機械的すぎず、人の手に馴染むようなサイズ・デザイン

これにより、福祉×ITが「冷たいテクノロジー」ではなく「温かい寄り添い」として表現される。

---

（続きは次ターンで作成：色彩運用ルール／出力仕様／NG事項チェックリスト／QA連携／使用例／メタデータ）
---

## 7. 色彩運用ルール

### 7.1 基本原則（B-2方針）

論点B（B-2案）で確定した方針に基づき、本スキルでは以下のカラー運用を採用する。

> ネイビー#003366は「主要面積」ではなく、「アクセント・タイトル文字・小要素」として使用する。主要面積はオフホワイト〜ベージュ系（#FAFAFA基調）で構成する。

これは過去投稿260304系の参照モデルに沿った運用であり、温かみのある親しみやすい雰囲気を保つために必要である。

### 7.2 各カラーの用途と画面占有率の目安

| カラー | コード | 用途 | 画面占有率の目安 |
|---|---|---|---|
| オフホワイト | #FAFAFA | 背景・主要面積 | 50〜70% |
| ベージュ・アイボリー系 | #F5EFE0 等 | 背景補助・木目床 | 10〜20% |
| ネイビー | #003366 | タイトル文字・主要テキスト・線・服装の一部 | 5〜15% |
| テーマアクセント | #FFA500 等 | 光のライン・小要素・強調点 | 5〜10% |
| 補助光カラー | ライトブルー・ミントグリーン・ピンク等 | データの流れ・温かい光（DX系） | 5〜10% |
| ウォームグレー | #9E9E9E | 影・アウトライン補助 | 5%以内 |

### 7.3 テーマ別の具体例

#### 福祉×IT・DX

主要面積は施設内のオフホワイト壁・木目床・観葉植物。スタッフの制服に**ネイビー#003366**を反映（ポロシャツの紺色など）。タブレット周辺にライトブルー・ミントグリーンの**有機的な光のライン**を流し、テーマアクセントの**オレンジ#FFA500**は温かい光のハイライトや、画面上部のタイトル装飾に使用する。

#### 福祉×お金

主要面積は穏やかな室内またはオフホワイト背景。**ネイビー#003366**は経営者の服装・グラフの線・タイトル文字に使用。テーマアクセントの**オレンジ#FFA500**は伸びるグラフの光、芽吹く植物のハイライト、書類の重要箇所のマーカーに控えめに配置する。

#### パーソナル：思想

主要面積はオフホワイトの抽象空間、または朝の柔らかい光に満ちた屋外。**ネイビー#003366**は人物の服装・タイトル文字・象徴物の輪郭に使用。テーマアクセントの**オレンジ#FFA500**は灯りの光、橋の欄干、絵筆の色など、芯となる要素に控えめに配置する。

### 7.4 ガイドラインとの整合に関する注意

`visual_guideline.md` の「メインカラー（ネイビー）は主要面積として使用」という記述は、本スキル運用と若干の摩擦がある。これは画像種類（イラスト／写真／漫画／バナー）によって主要面積の構成が異なるためであり、`visual_guideline.md` 側に「画像種類による占有率の柔軟運用」を明記する更新が必要となる。

この更新は4スキルすべてが完成した後にまとめて実施する。本スキル単独運用時は、本セクション（7.1〜7.3）が優先される。

---

## 8. 出力仕様

### 8.1 出力フォーマット

本スキルは以下の構造で出力する。

```markdown
## 生成プロンプト

### 日本語版
[日本語プロンプト本文]

### 英語版
[英語プロンプト本文]

### 補足情報
- アスペクト比：[指定]
- 推奨ツール：Nano Banana（Gemini 2.5 Flash Image）
- 想定テーマ：[テーマカテゴリ]
- 画像内テキスト：[指定有無と内容]

### セルフチェック結果
- 必須項目：[全項目クリア/未クリア項目あり]
- 推奨項目：[クリア率 ◯/◯ 項目]
- NG項目：[該当なし/該当あり]
```

### 8.2 両言語の運用ガイド

| 言語 | 主な用途 | 推奨される使い方 |
|---|---|---|
| **英語版** | 主：実際のNano Banana入力 | Nano Bananaは英語プロンプトの方が安定する傾向があるため、実運用は英語版を主軸とする |
| **日本語版** | 補助：人間によるレビュー用 | プロンプトの意図を有璽さん・編集者が確認する目的。Nano Bananaへの入力には基本的に使わない |

ただし、画像内テキスト（日本語のキーフレーズ）は両言語版とも日本語表記で指定する。Nano Bananaの日本語テキスト描画機能を使うため。

### 8.3 過去投稿アーカイブの参照運用

`data_sources.md` に記載された過去投稿アーカイブ（Notion）への参照は、以下の運用とする。

- **デフォルト**：参照しない（プロジェクトファイルの記述で十分カバーできる）
- **参照する条件**：
  - ユーザーが明示的に「過去投稿のスタイルを踏襲して」と指示した場合
  - 同一テーマで連続投稿する際の差別化チェックが必要な場合
  - スキル本体の改修・更新時の傾向再分析

参照負荷を抑えるため、毎回の起動時に自動参照することは避ける。

### 8.4 アスペクト比の選定ルール

| アスペクト比 | 使用ケース | 優先度 |
|---|---|---|
| 4:5 | Instagramフィード（縦長推奨） | デフォルト |
| 1:1 | Instagramフィード（正方形） | ユーザー指定時 |
| 9:16 | Instagramストーリーズ | ストーリーズ用と明示された場合のみ |

ユーザーから指定がない場合は4:5を採用する。

---

## 9. NG事項チェックリスト

プロンプト生成時、以下の要素は**絶対に含めない**。出力前に必ずセルフチェックする。

### 9.1 描写内容のNG

- [ ] 札束・現金・コインの直接描写（`brand_info.md`・`visual_guideline.md`準拠）
- [ ] 過度にゴージャス・ラグジュアリーな演出
- [ ] 暗い・陰鬱・冷たい色調
- [ ] 障害者・高齢者のステレオタイプ表現（弱々しい・哀れみを誘う等）
- [ ] 実在のキャラクター・有名人・著名ブランドロゴを想起させる描写
- [ ] 過度にテクノロジー寄りの冷たいビジュアル(機械的すぎる・人間味のないSF的描写）
- [ ] ギラギラ・メタリックな質感

### 9.2 テキスト関連のNG

- [ ] 画像内テキストが10文字を超える
- [ ] 画像内テキストの配置が画像中央下部・上部以外
- [ ] 画像内テキストが日本語以外の言語

### 9.3 構造的なNG

- [ ] キーワード羅列型のプロンプト（必ずシーン記述型で記述する）
- [ ] 5要素（被写体／構図／ライティング／スタイル／色調）のいずれかが欠ける
- [ ] アスペクト比の指定が欠ける
- [ ] テーマ別アクセントカラーの指定が欠ける

### 9.4 ブランド整合のNG

- [ ] 田村有璽以外の特定個人を強く想起させる人物描写
- [ ] ビビッドグループ事業内容と矛盾する設定（医療従事者・看護師の描写を強調するなど）
- [ ] 「絶対に儲かる」「必ず採択される」等の断定的誇大表現を視覚化したもの

これらのNG項目に該当した場合、プロンプトを生成し直すか、ユーザーに確認を求める。

---

## 10. QA連携

### 10.1 連携先スキル

本スキルの出力は、後段で `vivid-sns-qa-checker` スキルに引き渡される運用を想定する。ただし、現時点では本スキル単独運用も許容する。

### 10.2 QAスキルへの引き渡し情報

QAスキルが本スキルの出力を評価できるよう、以下の情報を併せて出力する。

```markdown
## QA連携情報
- テーマカテゴリ：[福祉×IT・DX / 福祉×お金 / パーソナル：思想]
- 投稿文との整合：[投稿文の核メッセージとプロンプトの被写体の対応関係を簡潔に記述]
- 採用シンボル：[推奨シンボルから選定したものを列挙]
- アクセントカラーの織り込み箇所：[具体的に記述]
- セルフチェック結果：[8.1の構造に準拠]
```

### 10.3 QAで不合格となった場合の挙動

QAスキルから「不合格」判定と修正指示を受け取った場合、本スキルは以下の手順で再生成する。

1. 修正指示の内容を確認する
2. 該当箇所のみを修正したプロンプトを再生成する（全面再生成は避ける）
3. 再生成後、再びセルフチェックを実施する
4. 最大3回の再生成サイクルを許容する。3回後も不合格の場合はユーザーに確認を求める

`vivid-sns-orchestrator` 統合時には、この再生成ループは自動化される予定。

---

## 11. 使用例

以下は3テーマそれぞれに対する具体的なプロンプト生成例である。

### 11.1 例：福祉×IT・DX

**入力**：
- `post_text`：「センサーで利用者を見守る時代。データの力で、職員の不安を安心に変えていく。」（260304系の文脈に近い）
- `theme_category`：福祉×IT・DX
- `text_overlay`：「見守るテクノロジー」（10文字）

**出力（英語版）**：

```
A warm, slightly 3D-rendered illustration depicting a young female caregiver in a teal polo shirt holding a tablet, standing beside an elderly woman wearing a soft pink cardigan in a homely Japanese welfare facility living room. The two are smiling gently at each other.
Composition: center-focused, medium shot, with both figures occupying the central two-thirds of the frame.
Lighting: soft natural morning light streaming from a window on the left, low contrast, gentle illumination on both faces.
Style: warm and approachable illustration in the manner of welfare-facility daily-life imagery, with soft lines, subtle blush on figures' cheeks, calm and confident expressions, slight 3D rendering depth without heavy shading.
Color palette: off-white walls and warm wood-grain flooring (#FAFAFA base), navy #003366 used for the caregiver's polo shirt and small text accents, theme accent orange #FFA500 used sparingly for warm light highlights and a small data-flow line emanating from the tablet, supplementary light-blue and mint-green organic light streams flowing between the tablet and the elderly woman to symbolize gentle data observation. A small heart pictogram and a sleep icon float subtly near the connection.
In-image Japanese text "見守るテクノロジー" placed at the top center of the frame in a strong gothic font.
Aspect ratio: 4:5 (Instagram vertical feed).
Avoid: direct depictions of cash or currency, glossy or metallic textures, recognizable real-world characters or brand logos, stereotypical elderly portrayals, overly cold or sterile technology aesthetics.
```

### 11.2 例：福祉×お金

**入力**：
- `post_text`：「補助金は手段。目的は事業者が前に進むこと。」
- `theme_category`：福祉×お金
- `text_overlay`：なし

**出力（英語版）**：

```
A warm, slightly 3D-rendered illustration depicting a male business owner in a navy blazer and white shirt standing beside a small, freshly-sprouting green plant rising from rich soil, his hand gently extended toward the plant in encouragement.
Composition: rule-of-thirds, with the figure on the left third and the sprouting plant centered slightly right, ample upward negative space symbolizing growth potential.
Lighting: soft natural morning light from upper right, low contrast, illuminating both the figure's face and the new leaves of the plant.
Style: warm and approachable illustration with soft lines, subtle blush on the figure's cheek, calm and quietly confident expression, slight 3D rendering depth.
Color palette: off-white background with subtle warm gradient (#FAFAFA base), navy #003366 used for the figure's blazer and the title text accent, theme accent orange #FFA500 used sparingly for warm sunlight highlights on the plant's new leaves and a small upward-trending graph element in the upper-right corner.
Aspect ratio: 4:5 (Instagram vertical feed).
Avoid: direct depictions of cash, banknotes, or coins, glossy or metallic textures, recognizable real-world characters or brand logos, overly aggressive or wealth-flaunting aesthetics.
```

### 11.3 例：パーソナル：思想

**入力**：
- `post_text`：「大衆になるな、民衆であれ。一人ひとりが自分の足で立ち、応援を伝播させる存在に。」
- `theme_category`：パーソナル：思想
- `text_overlay`：「民衆であれ」（5文字）

**出力（英語版）**：

```
A warm, slightly 3D-rendered illustration depicting a small group of three diverse figures (different ages, different clothing styles) walking shoulder-to-shoulder along a gentle path through soft hills toward a sunrise on the horizon. Each figure carries a small lantern that emits a warm glow.
Composition: rule-of-thirds, figures positioned along the lower-left third walking toward the upper-right horizon, with ample sky for a sense of openness and journey.
Lighting: soft natural sunrise light from the upper right horizon, golden-warm hour glow, low contrast.
Style: warm and approachable illustration with soft lines, slightly 3D-rendered figures with calm and resolute expressions, an introspective yet hopeful atmosphere.
Color palette: off-white sky with gentle peach and cream gradient (#FAFAFA base), navy #003366 used for the figures' clothing and the title text, theme accent orange #FFA500 used as the warm glow of the lanterns and the rising sun's halo.
In-image Japanese text "民衆であれ" placed at the top center of the frame in a strong, slightly weighted gothic font.
Aspect ratio: 4:5 (Instagram vertical feed).
Avoid: direct depictions of crowds in a negative or chaotic manner, glossy or metallic textures, recognizable real-world characters or brand logos, overly religious or political imagery.
```

### 11.4 使用例の運用注意

上記3例は**雛形であり、実運用では投稿文の具体内容に応じて被写体・構図・象徴を都度カスタマイズする**こと。テンプレートをそのまま流用すると、投稿ごとの個別性が失われ、フィード一覧で同一視されるリスクがある。

---

## 12. メタデータ・更新履歴

### 12.1 関連スキル

| スキル名 | 関係性 |
|---|---|
| `vivid-sns-text-generator` | 投稿文を生成する前段スキル。本スキルの入力源 |
| `vivid-sns-qa-checker` | 本スキル出力のQA判定を行う後段スキル |
| `vivid-sns-orchestrator` | 統括スキル。現時点では本スキルとの統合は未対応 |
| `vivid-sns-image-prompt-generator`（旧） | 本スキルの前身。当面は併存し、オーケストレーター統合時に本スキルが置き換える |

### 12.2 関連ファイル

| ファイル | 関係性 |
|---|---|
| `visual_guideline.md` | 必須参照ファイル |
| `content_themes.md` | 必須参照ファイル |
| `brand_info.md` | 必須参照ファイル |
| `qa_criteria.md` | セルフチェック・QA連携用 |
| `data_sources.md` | 過去投稿アーカイブ参照用 |

### 12.3 想定ツール仕様

- **ツール名**：Nano Banana（Gemini 2.5 Flash Image）
- **プロンプト形式**：シーン記述型（自然言語による文章記述）
- **言語**：英語推奨、日本語も対応
- **画像内テキスト**：日本語対応、10文字以内推奨

### 12.4 更新履歴

| 日付 | バージョン | 内容 |
|---|---|---|
| 2026-04-22 | 0.1.0 | 初版作成（前半・後半2ターン分割で構築） |

### 12.5 今後の課題

本スキルの完成度を高めるため、以下を別途対応する。

1. **Nano Bananaでの実生成テスト**：本スキルが出力したプロンプトを実際にNano Banana に投入し、生成画像が参照モデル（260304系）と一致するかを検証する
2. **過去投稿との比較検証**：生成画像をフィード一覧に並べた際、過去投稿との視覚的整合性が保たれるかを確認する
3. **オーケストレーター統合**：写真・漫画・バナーの各スキルが完成した後、`vivid-sns-orchestrator` への統合作業を実施する
4. **`visual_guideline.md` の更新**：4スキル完成後、本スキルで採用したB-2方針を含む運用ルールを `visual_guideline.md` に反映する
5. **`qa_criteria.md` の連動更新**：本スキルのセルフチェック項目とQAスキルの判定項目との整合を再確認する
