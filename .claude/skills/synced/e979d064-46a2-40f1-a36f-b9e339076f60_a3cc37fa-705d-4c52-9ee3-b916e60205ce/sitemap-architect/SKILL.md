---
name: sitemap-architect
version: 1.0.0
description: >
  Web サイト構築前のサイトマップ設計スキル。マーケティング資料・提案書・競合分析等の
  プロジェクト格納ファイルをソースとして、情報設計（IA）の専門知識に基づいたサイトマップと
  「なぜこの構成が最適か」を論証する提案ドキュメントを生成する。
  アウトプットはプロジェクトナレッジで指定されたフォーマット（スプレッドシート構成・提案書テンプレート）に準拠する。
  トリガー条件：「サイトマップ」「サイト構成」「ページ構成案」「IA設計」「情報設計」
  「サイトマップ提案」「ページ一覧」「ディレクトリマップ」「サイト設計」「ナビゲーション設計」
  「サイトツリー」「sitemap」「site architecture」「information architecture」
  「ページ階層」「URL設計」「コンテンツマップ」「サイトマップを作って」「構成案を出して」
  に言及がある場合。また、Webサイト新規構築やリニューアルの文脈でページ構成・階層設計に
  関わるあらゆるリクエストでこのスキルをトリガーすること。
  web-consulting-proposal スキルの分析結果がプロジェクトに存在する場合は積極的に活用する。
---

# Sitemap Architect — v1.0.0

Design strategic, evidence-based sitemaps for website projects. This skill acts as a senior information architect — analyzing project source materials (marketing research, proposals, competitor data, brand guidelines), structuring optimal page hierarchies, and producing both a formatted sitemap deliverable and a rationale document explaining why this architecture is the best choice.

---

## Core Philosophy

A sitemap is not just a list of pages. It is a **strategic document** that bridges business goals, user needs, and SEO/AEO requirements. Every page in the hierarchy must have a reason to exist, and that reason must be traceable to source materials.

---

## Workflow Overview

```
[Source Collection] → [Analysis] → [Architecture Design] → [Sitemap Output] → [Proposal Document]
```

### Step 1: Source Collection & Inventory

Scan the project knowledge and uploaded files. Classify each source:

| Source Type | What to Extract | Priority |
|---|---|---|
| Marketing research / analysis | Target audience, market position, key messages, USP | ★★★ |
| Proposal / RFP documents | Business goals, KPIs, scope, requirements | ★★★ |
| Competitor site analysis | Page structures, content gaps, differentiation points | ★★★ |
| SEO/AEO data (Ahrefs, GSC, KW Planner) | High-value keywords, search intent clusters, content opportunities | ★★★ |
| Brand guidelines | Tone, naming conventions, terminology constraints | ★★ |
| Existing site data (GA4, Clarity, etc.) | Top pages, user flows, drop-off points | ★★ |
| Stakeholder interview notes | Internal priorities, political constraints | ★★ |
| web-consulting-proposal skill outputs | Competitive benchmarks, SEO strategy, AEO recommendations | ★★★ |

If critical sources are missing, explicitly flag them before proceeding:
> "提案を進めるにあたり、以下の情報があるとサイトマップの精度が大幅に上がります：[list]。現時点の資料で進めますか？それとも追加情報を用意しますか？"

### Step 2: Multi-Lens Analysis

Analyze sources through multiple strategic lenses. The weight of each lens depends on what the source materials emphasize — do not apply a fixed formula. Instead, read the materials and let the content drive which lenses matter most.

See `references/analysis-lenses.md` for the full framework of each lens.

**Available Lenses:**
1. **Business Goal Lens** — What pages directly serve stated business objectives?
2. **User Journey Lens** — What pages does each persona need at each stage (Awareness → Consideration → Decision → Action → Retention)?
3. **SEO/AEO Lens** — What keyword clusters demand dedicated pages? What search intents are unmet?
4. **Competitor Gap Lens** — What pages do competitors have that this site lacks? What can differentiate?
5. **Content Efficiency Lens** — Can pages be consolidated? Are there orphan concepts?
6. **Conversion Architecture Lens** — How does the page hierarchy guide users toward conversion points?

After analysis, produce a **Lens Summary** (internal working document, not for client) that maps each proposed page to the lens(es) that justify it.

### Step 3: Architecture Design

Build the sitemap following IA best practices. See `references/ia-principles.md` for detailed rules.

**Key Design Rules:**
- **Flat is better than deep** — aim for ≤3 clicks from home to any content page
- **Group by user mental model**, not by org chart
- **Every page needs a job** — if you can't articulate its role in one sentence, merge or remove it
- **Navigation labels must pass the "5-second test"** — a new visitor should understand what's behind each label instantly
- **Plan for growth** — design categories that can accommodate future content without restructuring
- **URL structure mirrors hierarchy** — clean, semantic, keyword-aware paths
- **CTA flow is intentional** — every page should have a clear "next action" for the user

**Output the sitemap as a hierarchical structure with these fields per page:**

```
Level | Page Name | URL Path | Purpose (1 sentence) | Primary Lens | Content Priority
```

### Step 4: Format Conversion

Convert the sitemap into the client-specified format.

**Important:** The output format (spreadsheet structure, column definitions, styling) is defined in the **Project Knowledge**, not in this skill. Check the project for:
- Spreadsheet template / column specifications
- Naming conventions
- Any required metadata fields

If no format is specified in the project, output as:
1. **xlsx file** — using the default template (see `references/default-output.md`)
2. **Markdown table** — as inline backup

### Step 5: Proposal Document Generation

Generate a rationale document that explains **why this sitemap is the right architecture**. This is the strategic deliverable that accompanies the sitemap.

See `references/proposal-template.md` for the full template structure.

**Document Structure:**
1. Executive Summary — 3-5 sentence overview of the recommended architecture
2. Source Analysis Summary — What was analyzed and key findings from each source
3. Architecture Rationale — For each major section of the sitemap, explain the strategic reasoning with evidence citations from source materials
4. Key Design Decisions — Call out 3-5 important architectural choices and their tradeoffs
5. SEO/AEO Alignment — How the structure supports search visibility
6. Recommended Next Steps — Content development priorities, phased implementation if applicable

**Output format:** docx file (uploadable to Google Docs).

When generating the proposal document, always read `/mnt/skills/public/docx/SKILL.md` first for proper document creation.

---

## Integration Points

### With web-consulting-proposal Skill
If web-consulting-proposal outputs exist in the project (competitive analysis, SEO recommendations, etc.), use them as primary sources in Step 1. Reference specific findings in the proposal document.

### With ai-ui-prompt-gen Skill
After sitemap approval, the page structure feeds directly into ai-ui-prompt-gen for wireframe/UI prompt generation. Design the sitemap with this downstream use in mind — clear page purposes and content priorities make prompt generation more effective.

---

## Quality Checklist

Before delivering, verify:

- [ ] Every page traces to at least one source finding (no "gut feel" pages)
- [ ] Hierarchy depth ≤ 3 levels for 80%+ of pages
- [ ] No duplicate content intent across pages
- [ ] Navigation labels are user-language, not jargon
- [ ] URL paths are clean, semantic, and keyword-aware
- [ ] CTA flow is traceable from every leaf page to a conversion point
- [ ] Proposal document cites specific source materials for each recommendation
- [ ] Output format matches project-specified template (if any)

---

## References

Read these files as needed during the workflow:

| File | When to Read | Content |
|---|---|---|
| `references/analysis-lenses.md` | Step 2 — when analyzing sources | Detailed framework for each analysis lens with examples |
| `references/ia-principles.md` | Step 3 — when designing architecture | IA best practices, anti-patterns, hierarchy rules |
| `references/proposal-template.md` | Step 5 — when generating proposal | Full docx template structure and writing guidelines |
| `references/default-output.md` | Step 4 — when no format is specified | Default spreadsheet template and column definitions |
