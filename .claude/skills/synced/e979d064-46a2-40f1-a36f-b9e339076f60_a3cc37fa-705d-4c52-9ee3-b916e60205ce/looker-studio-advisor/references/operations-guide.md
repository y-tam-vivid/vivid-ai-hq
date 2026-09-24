# Looker Studio Operations Guide

Quick-reference for common Looker Studio operations. Each section provides an overview-level walkthrough and links to official Google documentation for detailed steps.

When answering operational questions, follow the response format defined in SKILL.md Role B (Operations Tutor): conclusion → step overview → common pitfalls → official docs link.

<!-- NOTE: Step descriptions use Japanese menu/button names because Looker Studio's Japanese UI is what the user sees in practice. -->

---

## Table of Contents

1. [Report & Data Source Basics](#1-report--data-source-basics)
2. [Chart & Component Operations](#2-chart--component-operations)
3. [Filter & Interactive Controls](#3-filter--interactive-controls)
4. [Calculated Fields](#4-calculated-fields)
5. [Data Blending](#5-data-blending)
6. [Key Official Documentation Links](#6-key-official-documentation-links)

---

## 1. Report & Data Source Basics

### Creating a new report
1. Go to [lookerstudio.google.com](https://lookerstudio.google.com)
2. Click 「空のレポート」(Blank Report) or choose a template
3. Select a data source to connect (Sheets, GA4, etc.)
4. The report editor opens with the connected data source ready

**Common pitfall**: Forgetting to check which Google account is signed in — data source access depends on the active account.

**Official docs**: https://support.google.com/looker-studio/answer/6292570

### Adding a data source to an existing report
1. In the report editor, click 「リソース」(Resource) → 「追加済みのデータソースの管理」(Manage added data sources)
2. Click 「データソースを追加」(Add a data source)
3. Select the connector type (Google Sheets, GA4, etc.)
4. Configure connection settings and click 「追加」(Add)
5. Click 「完了」(Done) to return to the report

**Common pitfall**: For Google Sheets, make sure the sheet is shared with the same Google account used in Looker Studio.

**Official docs**: https://support.google.com/looker-studio/answer/6370353

### Connecting Google Sheets
1. Select 「Googleスプレッドシート」connector
2. Choose the spreadsheet → choose the specific worksheet (tab)
3. Optionally check 「最初の行をヘッダーとして使用する」(Use first row as header)
4. Click 「追加」(Add)

**Common pitfalls**:
- Merged cells or multiple tables in one sheet cause schema errors
- Date columns not in YYYY-MM-DD format are often misrecognized

**Official docs**: https://support.google.com/looker-studio/answer/7020288

### Connecting GA4
1. Select 「Googleアナリティクス」connector
2. Choose the GA4 account → property
3. Click 「追加」(Add)

**Common pitfalls**:
- Selecting the wrong property when multiple exist under the same account
- GA4 data has up to 48-hour latency — don't panic if recent data is missing
- Custom dimensions/metrics must be registered in GA4 first

**Official docs**: https://support.google.com/looker-studio/answer/11985728

### Refreshing fields after data source changes
1. 「リソース」→ 「追加済みのデータソースの管理」
2. Click 「編集」(Edit) on the target data source
3. Click 「フィールドを更新」(Refresh Fields) at the top
4. Review field changes and click 「完了」(Done)

**Common pitfall**: If columns were renamed in Sheets, charts using old field names will show errors — remap them manually.

---

## 2. Chart & Component Operations

### Adding a chart
1. Click 「グラフを追加」(Add a chart) in the toolbar
2. Select chart type (table, bar, line, scorecard, etc.)
3. Click/drag on the canvas to place the chart
4. Configure dimensions and metrics in the right-side 「データ」(Data) panel
5. Adjust appearance in the 「スタイル」(Style) panel

**Common pitfall**: Adding a chart before connecting the correct data source — check which data source is selected in the chart's data panel.

**Official docs**: https://support.google.com/looker-studio/answer/6293184

### Adding a scorecard
1. 「グラフを追加」→ 「スコアカード」(Scorecard)
2. Set the metric (e.g., 売上, セッション数)
3. To add comparison: in the Data panel, set 「比較期間」(Comparison date range) to show YoY or MoM change
4. Style the scorecard in the Style panel (font size, colors, compact numbers)

**Common pitfall**: Comparison percentage shows inverted (positive/negative) if the metric is a "lower is better" type — manually invert the color logic.

### Copying and aligning components
- **Copy**: Select component → Ctrl+C → Ctrl+V (or right-click → コピー)
- **Align**: Select multiple components → right-click → 「配置」(Align) → choose alignment option
- **Distribute evenly**: Select 3+ components → right-click → 「配置」→ 「水平方向に均等配置」(Distribute horizontally)

### Multi-page reports
1. At the bottom of the canvas, click 「ページを追加」(Add page)
2. Right-click a page tab to rename, duplicate, or reorder
3. Use page navigation control to let viewers switch between pages

**Official docs**: https://support.google.com/looker-studio/answer/7059747

---

## 3. Filter & Interactive Controls

### Adding a date range filter
1. Click 「コントロールを追加」(Add a control) → 「期間設定」(Date range control)
2. Place it on the canvas (typically in the header area)
3. Set default date range in the control's Data panel
4. This filter applies to all charts on the same page using the same data source

**Common pitfall**: If charts use different data sources, the date filter may not apply to all of them — set the filter scope explicitly.

**Official docs**: https://support.google.com/looker-studio/answer/6291066

### Adding a dropdown filter
1. 「コントロールを追加」→ 「プルダウンリスト」(Drop-down list)
2. Set the dimension to filter by (e.g., チャネル, 商品カテゴリ)
3. Optionally set a default value

### Cross-filter (click-to-filter between charts)
1. Select a chart → Data panel → enable 「クロスフィルタリング」(Cross-filtering)
2. Now clicking a data point in this chart filters other charts on the same page
3. Works best with bar charts, tables, and pie charts

**Common pitfall**: Cross-filtering can confuse viewers who click charts unintentionally — add a text note explaining the interaction.

---

## 4. Calculated Fields

### Creating a calculated field in a data source
1. 「リソース」→ 「追加済みのデータソースの管理」
2. Click 「編集」on the target data source
3. Click 「フィールドを追加」(Add a field) at the top-right
4. Enter the field name and formula
5. Click 「保存」(Save) → 「完了」(Done)

**Common pitfalls**:
- Forgetting to click 「保存」before returning — the field won't be created
- Text fields used in arithmetic without CAST() conversion
- Division by zero not handled (use CASE WHEN to guard)

**Official docs**: https://support.google.com/looker-studio/answer/6299685

### Creating a chart-level calculated field
1. Select a chart → Data panel
2. At the bottom of the metrics/dimensions list, click 「フィールドを追加」
3. Enter the formula — this field exists only within this specific chart
4. Useful for quick one-off calculations without modifying the data source

**When to use which**:
- **Data source level**: When the field is reused across multiple charts
- **Chart level**: When the field is specific to one chart and experimental

### Key formula syntax reference

| Function | Purpose | Example |
|----------|---------|---------|
| `SUM(field)` | Aggregate sum | `SUM(売上)` |
| `AVG(field)` | Average | `AVG(客単価)` |
| `COUNT(field)` | Count rows | `COUNT(注文ID)` |
| `COUNT_DISTINCT(field)` | Unique count | `COUNT_DISTINCT(ユーザーID)` |
| `CASE WHEN...END` | Conditional logic | See SKILL.md examples |
| `IFNULL(field, value)` | NULL handling | `IFNULL(売上, 0)` |
| `CAST(field AS NUMBER)` | Type conversion | `CAST(文字列フィールド AS NUMBER)` |
| `TODATE(field, in, out)` | Date formatting | `TODATE(日付, "%Y%m%d", "%Y-%m-%d")` |
| `CONCAT(a, b)` | String concatenation | `CONCAT(姓, " ", 名)` |
| `REGEXP_MATCH(field, pattern)` | Regex filter (boolean) | `REGEXP_MATCH(URL, ".*blog.*")` |

**Official docs (full function list)**: https://support.google.com/looker-studio/table/6379764

---

## 5. Data Blending

### Creating a data blend
1. In the report editor, click 「リソース」→ 「統合を管理」(Manage blends)
2. Click 「統合を追加」(Add a blend)
3. Add the first data source (left table) and select its dimensions/metrics
4. Click 「別のテーブルを結合」(Join another table) to add the second source
5. Define the join key (共通ディメンション) — typically a date or ID field
6. Select dimensions/metrics from the second source
7. Click 「保存」(Save)
8. The blended data source is now available when adding charts

**Common pitfalls**:
- Join key values don't match due to formatting differences (e.g., "2026-03-16" vs "2026/03/16")
- Blending produces NULLs because it defaults to LEFT JOIN — rows without matches in the right table are null
- Creating calculated fields for blended data must be done inside the blend editor, not in the individual data source
- Too many blends (3+) significantly degrade report performance

**Official docs**: https://support.google.com/looker-studio/answer/9061420

### Blend vs pre-merge decision guide

| Scenario | Recommendation |
|----------|---------------|
| Simple date-based join, 2 sources | Use Looker Studio blend |
| 3+ sources or complex join logic | Pre-merge in Google Sheets (VLOOKUP/QUERY) |
| Large data volumes (10k+ rows per source) | Pre-merge in Sheets or use BigQuery |
| Frequently changing join keys | Pre-merge to avoid maintenance overhead |
| Quick prototype / exploration | Blend is fine for speed |

---

## 6. Key Official Documentation Links

Core reference links for when users need detailed, authoritative documentation:

| Topic | URL |
|-------|-----|
| Looker Studio Help Center (top) | https://support.google.com/looker-studio |
| Getting started guide | https://support.google.com/looker-studio/answer/6292570 |
| Data source connectors | https://support.google.com/looker-studio/answer/6370353 |
| Chart types reference | https://support.google.com/looker-studio/answer/6293184 |
| Calculated fields | https://support.google.com/looker-studio/answer/6299685 |
| Full function reference | https://support.google.com/looker-studio/table/6379764 |
| Data blending | https://support.google.com/looker-studio/answer/9061420 |
| Filters and controls | https://support.google.com/looker-studio/answer/6291066 |
| Sharing and permissions | https://support.google.com/looker-studio/answer/6286244 |
| Scheduled email delivery | https://support.google.com/looker-studio/answer/9515488 |
| GA4 connector | https://support.google.com/looker-studio/answer/11985728 |
| Google Sheets connector | https://support.google.com/looker-studio/answer/7020288 |
| Community connectors | https://support.google.com/looker-studio/answer/7020039 |
| Report embedding | https://support.google.com/looker-studio/answer/7450249 |
