# Analysis Lenses — Detailed Framework

Use these lenses to analyze project source materials and build evidence-based page justifications. Not all lenses apply equally to every project — let the source materials guide which lenses carry the most weight.

---

## Lens 1: Business Goal Lens

Map stated business objectives to page requirements.

**Process:**
1. Extract explicit goals from proposals/RFPs (e.g., "increase inquiries by 30%", "establish thought leadership")
2. For each goal, identify what pages directly serve it
3. Identify pages that indirectly support goals (trust-building, education)

**Evidence markers to look for:**
- KPI targets → what conversion pages are needed
- Revenue model → what product/service pages are required
- Brand positioning statements → what messaging pages support the position

**Example mapping:**
```
Goal: "Generate 50 qualified leads/month"
→ Required pages: Service detail pages (per service), Case studies, Contact/Inquiry form, 
  Pricing/Plans page, Comparison page (vs. competitors)
→ Supporting pages: Blog (SEO entry points), About/Team (trust), FAQ (objection handling)
```

---

## Lens 2: User Journey Lens

Map target personas through their decision journey to identify content needs at each stage.

**Process:**
1. Identify personas from source materials (or infer from target audience data)
2. For each persona, map the AIDA+ journey:
   - **Awareness** — How do they discover the site? What are they searching for?
   - **Interest** — What content keeps them engaged? What questions do they have?
   - **Desire** — What convinces them this is the right choice? Social proof, comparisons?
   - **Action** — What is the conversion action? How frictionless is the path?
   - **Retention** — What brings them back? Support, community, updates?
3. Identify page needs at each stage

**Key principle:** Different personas may need different pages for the same journey stage. A CEO and a technical lead both evaluate a SaaS product, but through different content.

---

## Lens 3: SEO/AEO Lens

Map search intent clusters to page requirements.

**Process:**
1. Group keywords by search intent (informational, commercial, transactional, navigational)
2. Cluster related keywords into topic groups
3. Each significant cluster → potential dedicated page
4. Check for content cannibalization (two pages targeting same intent)
5. Identify featured snippet / AI overview opportunities → structure content accordingly

**Intent-to-Page mapping:**
| Intent Type | Page Type | Example |
|---|---|---|
| Informational | Blog / Knowledge base / Guide | "What is [service]", "How to [task]" |
| Commercial investigation | Comparison / Case study / Review | "[service] vs [competitor]", "best [category]" |
| Transactional | Product / Service / Pricing / Contact | "[service] pricing", "buy [product]" |
| Navigational | Homepage / Brand pages | "[company name]", "[company] login" |

**AEO considerations:**
- Structure content for AI extraction (clear headers, Q&A format, structured data)
- Identify "zero-click" queries that need definitive answers on-page
- Plan for citation-worthy content that AI systems will reference

---

## Lens 4: Competitor Gap Lens

Analyze competitor site structures to find opportunities.

**Process:**
1. Map competitor sitemaps (from web-consulting-proposal data or manual analysis)
2. Identify common pages across all competitors → table stakes (must-have)
3. Identify unique pages from top performers → potential differentiators
4. Identify gaps no competitor fills → blue ocean opportunity
5. Evaluate competitor navigation patterns — what works, what's confusing

**Gap classification:**
- **Parity gaps** — pages all competitors have that this site needs (e.g., case studies)
- **Quality gaps** — pages that exist but are poorly executed across competitors
- **Innovation gaps** — content types no competitor offers (interactive tools, calculators, etc.)

---

## Lens 5: Content Efficiency Lens

Optimize the page structure for maintainability and clarity.

**Process:**
1. Review proposed pages for content overlap
2. Identify pages that could be sections within a parent page
3. Check for "thin content" risk — pages without enough substance to stand alone
4. Evaluate content production capacity — can the team actually maintain all proposed pages?

**Decision framework:**
- If a page has < 300 words of unique content → merge into parent
- If two pages share > 60% of their content intent → consolidate
- If a page requires monthly updates but no one is assigned → flag as risk

---

## Lens 6: Conversion Architecture Lens

Design the page hierarchy as a conversion funnel.

**Process:**
1. Identify all conversion points (primary: inquiry/purchase; secondary: newsletter, download)
2. Map conversion paths: entry page → consideration pages → conversion page
3. Ensure every page has a clear "next step" pointing toward conversion
4. Minimize path length: ≤ 3 pages from any entry to primary conversion
5. Identify friction points and plan for objection-handling content

**Conversion path patterns:**
```
Pattern A (Direct): SEO Entry → Service Page → Contact
Pattern B (Education): SEO Entry → Guide → Case Study → Service Page → Contact
Pattern C (Trust-first): SEO Entry → About/Team → Service Page → Contact
```

Each page in the sitemap should be assignable to at least one conversion path.

---

## Lens Summary Template

After analysis, produce this internal working document:

```markdown
## Lens Summary — [Project Name]

### Dominant Lenses (ranked by source material emphasis)
1. [Lens name] — [why this lens is most important for this project]
2. [Lens name] — [why]
3. [Lens name] — [why]

### Page Justification Matrix
| Page | Biz Goal | User Journey | SEO/AEO | Competitor | Efficiency | Conversion | Score |
|---|---|---|---|---|---|---|---|
| Home | ✓ | ✓ | ✓ | ✓ | — | ✓ | 5/6 |
| Service A | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 6/6 |
| Blog post X | — | ✓ | ✓ | — | ? | ✓ | 3/6 |

Pages scoring ≤ 2/6 should be questioned. Pages scoring 1/6 should be removed unless there's a strong strategic override.
```
