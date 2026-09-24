# Default Sitemap Output Template

Use this template when no client-specific format is specified in the project knowledge.

---

## Spreadsheet Structure (xlsx)

### Sheet 1: サイトマップ（Sitemap）

| Column | Header | Description | Example |
|---|---|---|---|
| A | Level | Hierarchy depth (1 = top-level) | 1 |
| B | Page Name (JP) | Japanese page name for navigation | サービス紹介 |
| C | Page Name (EN) | English page name (for URL/dev reference) | Services |
| D | URL Path | Proposed URL path | /services/ |
| E | Parent Page | Parent page name (blank for L1) | — |
| F | Page Purpose | One-sentence description of page role | 提供サービスの一覧と概要を表示し、詳細ページへ誘導 |
| G | Primary CTA | Main call-to-action on this page | お問い合わせフォームへ |
| H | SEO Target Keyword | Primary keyword target | Web制作 会社 |
| I | Content Priority | High / Medium / Low | High |
| J | Notes | Additional context, constraints, or dependencies | LP経由の流入想定、比較表を含む |

### Formatting Rules
- Indent page names by hierarchy level (Level 2 = 1 indent, Level 3 = 2 indents)
- Color-code by Level:
  - Level 1: Blue header row with white text
  - Level 2: Light blue background
  - Level 3: White background
  - Level 4+: Light gray background
- Freeze top row (headers)
- Auto-filter enabled on all columns
- Column widths: A=8, B=25, C=20, D=25, E=20, F=40, G=20, H=20, I=12, J=30

### Sheet 2: ページ詳細（Page Details）

Optional detailed sheet for complex projects.

| Column | Header | Description |
|---|---|---|
| A | Page Name | Same as Sheet 1 |
| B | Target Persona | Primary persona for this page |
| C | User Journey Stage | Awareness / Interest / Desire / Action / Retention |
| D | Key Content Elements | What content must be on this page |
| E | Internal Link Sources | Pages that should link TO this page |
| F | Internal Link Targets | Pages this page should link TO |
| G | Competitive Reference | Competitor pages referenced in design |
| H | Design Notes | Layout or UX considerations |

### Sheet 3: URL一覧（URL List）

Simple flat list for development handoff.

| Column | Header |
|---|---|
| A | URL Path |
| B | Page Name (JP) |
| C | Page Name (EN) |
| D | Template Type (if applicable) |
| E | Status (New / Existing / Redirect) |

---

## Markdown Table Format (inline backup)

When xlsx creation is not needed, output as markdown:

```markdown
## サイトマップ構成案

| Lv | ページ名 | URL | 目的 | 主要CTA | SEOキーワード | 優先度 |
|----|---------|-----|------|---------|-------------|--------|
| 1 | ホーム | / | ... | ... | ... | High |
| 2 | ├ サービス | /services/ | ... | ... | ... | High |
| 3 | │ ├ サービスA | /services/a/ | ... | ... | ... | High |
```

---

## Visual Sitemap (optional)

If the user requests a visual representation, generate using the `visualize:show_widget` tool as an SVG tree diagram. This is supplementary to the spreadsheet — not a replacement.

---

## xlsx Generation Notes

When generating the xlsx file:
1. Read `/mnt/skills/public/xlsx/SKILL.md` for proper formatting
2. Apply the color-coding and formatting rules above
3. Include all three sheets
4. Save to `/mnt/user-data/outputs/` and present via `present_files`
