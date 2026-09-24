# Information Architecture Principles

Core IA rules for sitemap design. Follow these when building page hierarchies.

---

## Hierarchy Design Rules

### The 3-Click Rule (with nuance)
- **Target**: 80%+ of content pages reachable within 3 clicks from homepage
- **Exception**: Deep archival content (blog archives, knowledge base) can go deeper if navigation aids exist (search, breadcrumbs, related links)
- **Why**: Each additional click loses ~30% of users on average

### The 7±2 Rule for Navigation
- Primary navigation: 5-7 items maximum
- Sub-navigation per section: 5-9 items maximum
- Beyond 9 items → restructure into logical subgroups
- **Why**: Working memory limits. Too many options cause decision paralysis.

### Mental Model Alignment
- Group pages by **user tasks/needs**, not by company org chart
- Test labels against user language, not internal jargon
- Use card sorting logic: "If a user needed [content], where would they look first?"

**Anti-pattern:**
```
❌ Company-centric:
├── About Division A
├── About Division B  
├── About Division C
└── Products by Division

✓ User-centric:
├── Products by Category
│   ├── Category A (may include products from multiple divisions)
│   └── Category B
├── Solutions by Industry
└── About Us (consolidated)
```

### Page Naming Conventions
- Use plain language a first-time visitor would understand
- Avoid acronyms, brand-specific terms, or ambiguous labels
- Keep labels to 1-3 words for navigation items
- Use verbs for action pages ("Get Started", "Request a Demo" vs "Demo Page")

**Label quality test:**
> Show the label to someone unfamiliar with the company. Can they predict what content is behind it within 5 seconds?

---

## URL Structure Rules

### Semantic URL Design
```
✓ /services/web-design/
✓ /case-studies/company-a-redesign/
✓ /blog/seo-basics-guide/

❌ /page-123/
❌ /services/sv01/
❌ /content/2024/03/15/post/
```

### URL Hierarchy = Site Hierarchy
- URL depth should mirror sitemap depth
- Parent pages should be navigable (no dead parent URLs)
- Use hyphens, not underscores
- Keep URLs lowercase
- Include primary keyword where natural

### Internationalization Consideration
If multi-language is planned:
```
/ja/services/web-design/
/en/services/web-design/
```
Flag this in the sitemap if source materials mention international audiences.

---

## Content Architecture Patterns

### Hub & Spoke
Best for: Knowledge-heavy sites, content marketing
```
Hub: /services/digital-marketing/
├── Spoke: /services/digital-marketing/seo/
├── Spoke: /services/digital-marketing/content-strategy/
├── Spoke: /services/digital-marketing/analytics/
└── Internal links between spokes
```

### Funnel Architecture
Best for: Lead-gen sites, SaaS
```
Top: Blog / Resources (Awareness)
Mid: Solutions / Case Studies (Consideration)
Bottom: Pricing / Demo / Contact (Decision)
```

### Catalog Architecture
Best for: E-commerce, product-heavy sites
```
Category → Subcategory → Product
With filters, search, and cross-links
```

### Hybrid (most common)
Most corporate/service sites use a hybrid:
- Hub & Spoke for service/product sections
- Funnel overlay for conversion flow
- Flat pages for legal, about, contact

---

## Common Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Mirror org chart** | Users don't care about internal structure | Reorganize by user need |
| **Mega-menus with 50+ items** | Decision paralysis, mobile nightmare | Reduce top-level items, use progressive disclosure |
| **Orphan pages** | Pages with no navigation path | Ensure every page is reachable from nav or internal links |
| **Duplicate intent** | Two pages competing for same keyword/purpose | Consolidate into one stronger page |
| **Deep nesting (>4 levels)** | Users get lost, SEO dilution | Flatten hierarchy, use cross-linking |
| **Vanity pages** | Pages that exist for stakeholder ego, not user need | Challenge with data, propose alternative placement |
| **Missing conversion path** | Content pages with no CTA or next step | Add contextual CTAs on every page |

---

## Mobile-First Considerations

- Navigation structure must work in hamburger menu format
- Deep hierarchies are worse on mobile — flatter is always better
- Touch targets need space — fewer nav items per level
- Consider thumb-zone placement for primary CTAs
- Progressive disclosure (accordions, expandable sections) over deep linking

---

## Scalability Planning

When designing the architecture, anticipate growth:

1. **Category flexibility** — Can new services/products fit existing categories?
2. **Blog/Content growth** — Is the taxonomy (categories, tags) scalable to 100+ posts?
3. **Localization** — Is the URL structure ready for additional languages?
4. **Feature additions** — Can new sections be added without restructuring?

**Stress test:** Mentally add 10 new pages. Does the hierarchy still make sense? If not, redesign the categories.
