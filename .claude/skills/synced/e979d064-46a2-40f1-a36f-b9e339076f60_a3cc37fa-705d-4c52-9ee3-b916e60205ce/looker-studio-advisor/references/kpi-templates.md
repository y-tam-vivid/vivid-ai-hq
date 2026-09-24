# Industry-Specific KPI Templates

KPI templates by industry vertical for Looker Studio dashboard construction.
Select the relevant section based on the client's industry.

<!-- NOTE: Table content (KPI names, formulas, chart labels) is in Japanese because these templates are directly used in client-facing dashboards and design documents. -->

---

## Table of Contents

1. [EC / E-commerce](#ec--e-commerce)
2. [SaaS / Subscription](#saas--subscription)
3. [BtoB Sales Organization](#btob-sales-organization)
4. [Media / Content](#media--content)
5. [Retail / Food Service](#retail--food-service)
6. [Real Estate / Housing](#real-estate--housing)
7. [Education / School](#education--school)
8. [Welfare / Nursing Care](#welfare--nursing-care)
9. [Manufacturing](#manufacturing)
10. [Universal Template (Cross-Industry)](#universal-template-cross-industry)

---

## EC / E-commerce

### KGI
- 月次売上（税込/税抜）
- 月次営業利益

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| 売上 | 注文金額の合計 | Sheets / GA4 ecommerce | スコアカード + 折れ線 |
| 注文件数 | 購入完了イベント数 | GA4 purchase event | スコアカード |
| 客単価 | 売上 ÷ 注文件数 | 計算フィールド | スコアカード（前期比） |
| CVR | 購入件数 ÷ セッション数 | GA4 | スコアカード（前期比） |
| カート離脱率 | 1 - (購入数 ÷ カート追加数) | GA4 | スコアカード |
| リピート率 | リピート購入者数 ÷ 全購入者数 | Sheets(CRM) | 折れ線 |
| LTV | 顧客あたり累計売上 | Sheets(CRM) | 棒グラフ(コホート) |

### KAI (Action Metrics)
- 商品ページPV数、カート追加数、決済開始数（ファネル分析用）
- 新規 vs リピートセッション比率
- 流入チャネル別CVR（自然検索/広告/SNS/直接）

### Recommended Page Structure
1. **サマリー**: 売上・注文件数・客単価・CVRの4スコアカード + 売上推移折れ線
2. **集客分析**: チャネル別セッション + CVR比較
3. **商品分析**: 商品別売上ランキング + カテゴリ構成比
4. **ファネル**: カート追加→決済開始→購入完了の遷移率

---

## SaaS / Subscription

### KGI
- MRR（月次経常収益）
- ARR（年次経常収益）

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| MRR | 月額課金の合計 | Sheets(請求データ) | スコアカード + 折れ線 |
| 新規MRR | 当月新規契約分のMRR | Sheets | 積み上げ棒 |
| チャーンMRR | 当月解約分のMRR | Sheets | 積み上げ棒（負の値） |
| チャーンレート | 解約数 ÷ 前月末契約数 | 計算フィールド | 折れ線（目標線付き） |
| ARPU | MRR ÷ 有効契約数 | 計算フィールド | 折れ線 |
| CAC | 広告費+営業人件費 ÷ 新規獲得数 | Sheets | 棒グラフ |
| LTV/CAC比 | LTV ÷ CAC | 計算フィールド | スコアカード |

### Recommended Page Structure
1. **MRRサマリー**: MRR推移 + 新規/解約/拡大の内訳積み上げ
2. **顧客分析**: プラン別契約数 + チャーンレート推移
3. **獲得効率**: CAC推移 + チャネル別獲得数

---

## BtoB Sales Organization

### KGI
- 月次/四半期受注金額
- 受注件数

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| パイプライン金額 | 商談金額 × 確度の加重合計 | Sheets(CRM) | 横棒（ステージ別） |
| 商談数 | 有効商談の件数 | Sheets(CRM) | スコアカード |
| 受注率 | 受注件数 ÷ 商談件数 | 計算フィールド | 折れ線 |
| 平均商談期間 | 商談開始〜クローズの平均日数 | 計算フィールド | スコアカード |
| 営業1人あたり売上 | 売上 ÷ 営業人数 | 計算フィールド | 棒グラフ |
| リード獲得数 | 新規リードの件数 | Sheets / GA4 | 折れ線 |
| リード→商談転換率 | 商談化件数 ÷ リード数 | 計算フィールド | ファネル |

### Recommended Page Structure
1. **営業サマリー**: 受注金額・件数・受注率のスコアカード + 月次推移
2. **パイプライン**: ステージ別商談金額の横棒 + 期限別一覧
3. **メンバー分析**: 担当者別実績比較
4. **リード分析**: チャネル別リード獲得 + 転換率

---

## Media / Content

### KGI
- 月間PV / UU
- 広告収益 / アフィリエイト収益

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| PV | ページビュー数 | GA4 | 折れ線 |
| UU | アクティブユーザー数 | GA4 | 折れ線 |
| PV/セッション | PV ÷ セッション数 | GA4 | スコアカード |
| 平均滞在時間 | エンゲージメント時間の平均 | GA4 | スコアカード |
| 直帰率 | エンゲージなしセッション率 | GA4 | スコアカード（低いほど良い） |
| 記事別PVランキング | ページパス別PV | GA4 | テーブル |
| 流入チャネル構成 | チャネル別セッション比率 | GA4 | 積み上げ棒 |

### Recommended Page Structure
1. **トラフィックサマリー**: PV・UU・滞在時間のスコアカード + 推移
2. **コンテンツ分析**: 記事別PVランキング + カテゴリ別構成
3. **集客分析**: チャネル別 + 検索クエリ（Search Console連携時）

---

## Retail / Food Service

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| 売上 | 日次/月次売上合計 | Sheets(POS) | スコアカード + 折れ線 |
| 客数 | 来店客数 | Sheets | 折れ線 |
| 客単価 | 売上 ÷ 客数 | 計算フィールド | スコアカード |
| 原価率 | 原価 ÷ 売上 | 計算フィールド | 折れ線（目標線付き） |
| 人時売上 | 売上 ÷ 総労働時間 | 計算フィールド | 棒グラフ |
| 商品別売上構成 | 商品カテゴリ別売上 | Sheets | ツリーマップ |

---

## Real Estate / Housing

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| 反響数 | 問い合わせ件数 | Sheets / GA4 | スコアカード + 折れ線 |
| 来場数 | モデルハウス・展示場来場数 | Sheets | スコアカード |
| 来場率 | 来場数 ÷ 反響数 | 計算フィールド | 折れ線 |
| 契約数 | 成約件数 | Sheets | スコアカード |
| 契約率 | 契約数 ÷ 来場数 | 計算フィールド | 折れ線 |
| 反響単価 | 広告費 ÷ 反響数 | 計算フィールド | 棒グラフ（媒体別） |

---

## Education / School

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| 受講生数 | アクティブ受講生の総数 | Sheets | スコアカード + 折れ線 |
| 新規入会数 | 当月新規入会者数 | Sheets | スコアカード |
| 退会率 | 退会数 ÷ 前月末在籍数 | 計算フィールド | 折れ線 |
| 受講率 | 出席回数 ÷ 開講回数 | 計算フィールド | 棒グラフ（コース別） |
| 売上 | 月謝 + 入会金 + 教材費 | Sheets | 折れ線 |
| LTV | 平均在籍月数 × 月額単価 | 計算フィールド | スコアカード |

---

## Welfare / Nursing Care

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| 利用者数 | アクティブ利用者数 | Sheets | スコアカード |
| 稼働率 | 実利用者数 ÷ 定員 | 計算フィールド | スコアカード（目標比） |
| 収支差額 | 収入 - 支出 | 計算フィールド | 折れ線 |
| 人件費率 | 人件費 ÷ 収入 | 計算フィールド | 折れ線（目標線付き） |
| 職員配置率 | 配置人数 ÷ 基準人数 | 計算フィールド | スコアカード |
| 新規利用者数 | 当月新規契約者 | Sheets | 棒グラフ |

---

## Manufacturing

### KPI (Primary Metrics)
| KPI | 計算式 | データソース例 | 推奨チャート |
|-----|--------|--------------|-------------|
| 生産数量 | 完成品数量 | Sheets | 折れ線 |
| 不良率 | 不良品数 ÷ 生産数 | 計算フィールド | 折れ線（目標線付き） |
| 設備稼働率 | 稼働時間 ÷ 計画時間 | 計算フィールド | スコアカード |
| 納期遵守率 | 期限内納品数 ÷ 総納品数 | 計算フィールド | スコアカード |
| 原材料コスト | 原材料費合計 | Sheets | 棒グラフ（月次） |

---

## Universal Template (Cross-Industry)

Use this template when the client's industry is unspecified or spans multiple verticals.

### Executive Dashboard (Universal)
| KPI | 計算式 | 推奨チャート |
|-----|--------|-------------|
| 売上 | 売上合計 | スコアカード + 折れ線 |
| 粗利 | 売上 - 原価 | スコアカード |
| 粗利率 | 粗利 ÷ 売上 | スコアカード（前期比） |
| 顧客数 | アクティブ顧客数 | スコアカード |
| 新規顧客数 | 当月新規 | 棒グラフ |
| 顧客単価 | 売上 ÷ 顧客数 | 折れ線 |

### Web Marketing Dashboard (Universal)
| KPI | 計算式 | 推奨チャート |
|-----|--------|-------------|
| セッション数 | GA4 sessions | 折れ線 |
| CV数 | 目標完了数 | スコアカード + 折れ線 |
| CVR | CV数 ÷ セッション数 | スコアカード（前期比） |
| CPA | 広告費 ÷ CV数 | 棒グラフ（チャネル別） |
| ROAS | 売上 ÷ 広告費 | スコアカード |
| 直帰率 | エンゲージなし率 | スコアカード（低いほど良い） |
