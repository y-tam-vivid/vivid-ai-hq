# Proposal Document Template

Template and writing guidelines for the sitemap rationale document. Output as docx format (Google Docs uploadable).

---

## Document Structure

### Cover Section
```
[Project Name] サイトマップ設計提案書
[Date]
[Prepared by: Desia]
```

### 1. エグゼクティブサマリー（Executive Summary）

3-5 sentences that a decision-maker can read in 30 seconds and understand:
- What architecture is being proposed
- The primary strategic rationale
- Expected outcome

**Writing guideline:** Lead with the recommendation, not the analysis process. Decision-makers want the "what" before the "why".

**Template:**
> 本提案書は、[Company Name] の Web サイト構成として [N] ページ・[M] 階層のサイトマップを推奨するものです。[Primary source data] の分析に基づき、[Key strategic rationale] を最重視した設計としています。この構成により、[Expected outcome] が見込まれます。

---

### 2. 分析ソースサマリー（Source Analysis Summary）

List what was analyzed and key takeaways from each source.

**Format per source:**
```
■ [Source Name / Type]
  概要：[What this source contains]
  主要発見：
  ・[Finding 1 — specific, data-backed where possible]
  ・[Finding 2]
  サイトマップへの影響：[How this finding shaped the architecture]
```

**Important:** Be specific. "マーケティング調査を分析しました" is useless. "ターゲット層の 65% が「事例」を購買検討時の最重要コンテンツと回答" is valuable.

---

### 3. アーキテクチャ根拠（Architecture Rationale）

For each major section of the sitemap (L1 pages and their children), explain:

**Per-section format:**
```
### [Section Name]（例：サービス紹介）

■ 構成ページ
  [List pages in this section with hierarchy]

■ 設計意図
  [Why this section exists, why it's structured this way]

■ 根拠データ
  ・[Source] より：[Specific finding that supports this structure]
  ・[Source] より：[Another finding]

■ 代替案との比較（該当する場合）
  検討した代替構成：[What was considered]
  採用しなかった理由：[Why this option was better]
```

**Writing guideline:** Every claim must cite a source. "ユーザーにとって分かりやすいため" is not sufficient. "競合 A/B/C の全てが同様のカテゴリ分けを採用しており、ターゲットユーザーの期待するメンタルモデルに合致するため" is proper reasoning.

---

### 4. 主要設計判断（Key Design Decisions）

Highlight 3-5 non-obvious architectural choices. These are the decisions that a client might question — preemptively explain them.

**Per-decision format:**
```
### 判断 [N]：[Decision title]（例：ブログと事例を分離した理由）

決定事項：[What was decided]
背景：[Context and constraints]
根拠：[Evidence supporting this choice]
トレードオフ：[What was sacrificed, and why it's acceptable]
```

**Common decisions that need explanation:**
- Why certain pages were consolidated (or kept separate)
- Why the hierarchy is flat/deep in specific areas
- Why a particular grouping was chosen over alternatives
- Why certain competitor patterns were adopted (or rejected)
- Why specific pages were included that aren't obvious

---

### 5. SEO/AEO 整合性（SEO/AEO Alignment）

Explain how the architecture supports search visibility.

**Include:**
- Primary keyword clusters mapped to pages
- URL structure rationale
- Internal linking strategy overview
- AEO readiness (structured data opportunities, FAQ pages, etc.)
- Content gap opportunities identified

**Format:**
```
■ キーワードクラスター ↔ ページ マッピング
  [Cluster 1] → [Target page] (月間検索ボリューム: [N])
  [Cluster 2] → [Target page]

■ URL設計方針
  [Explain the URL structure logic]

■ 内部リンク戦略
  [Key cross-linking patterns planned]

■ AEO対応
  [How the structure supports AI search/citations]
```

---

### 6. 推奨ネクストステップ（Recommended Next Steps）

Prioritized action items after sitemap approval.

**Standard items:**
1. Content development priority order (which pages to write first)
2. Wireframe/design phase planning
3. Phased launch approach (if applicable)
4. Content governance — who maintains what
5. Measurement — how to evaluate if the architecture is working

---

## Writing Guidelines

### Tone
- Professional but not academic
- Confident but not dismissive of alternatives
- Data-driven — avoid subjective claims without evidence
- Japanese language, with technical terms in original language where clearer

### Length
- Target: 8-15 pages for a typical project
- Adjust based on project complexity
- Executive summary must fit on one page

### Formatting
- Use heading hierarchy consistently (H1 = document title, H2 = sections, H3 = subsections)
- Tables for comparative data
- Bullet lists for findings and recommendations
- Bold key terms on first use

### Citation Format
When referencing source materials:
> [Source type/name] より：「[specific finding]」

Or inline:
> 競合分析（[source]）によると、上位3社すべてが[finding]を採用しています。

---

## docx Generation Notes

When generating the docx file:
1. Read `/mnt/skills/public/docx/SKILL.md` for proper formatting
2. Apply professional styling (consistent headings, proper spacing)
3. Include table of contents
4. Use Desia branding if brand assets are available in the project
5. Save to `/mnt/user-data/outputs/` and present via `present_files`
