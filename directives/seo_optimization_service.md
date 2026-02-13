# SEO Optimization & Analysis Service

## Overview
Comprehensive SEO analysis dashboard that evaluates website performance across on-page, technical, and competitive metrics. Delivers actionable insights via interactive dashboard and Google Sheets reports with keyword analysis, site health scoring, and competitor benchmarking.

## Service Tier

**Monthly Fee:** $800 - $2,000  
**Deliverable:** Interactive Dashboard + Google Sheet (updated weekly) + Monthly PDF insights  
**Agent Template:** Technical SEO Specialist + Content Analyst + Competitive Intelligence  

---

## Inputs (Client Provides)

### Required
1. **Website URL** (string)
   - Example: `"https://example.com"`
   - Primary domain to analyze

2. **Target Keywords** (array)
   - Example: `["automation services", "workflow optimization", "business process automation"]`
   - 5-15 keywords client wants to rank for

3. **Competitor URLs** (array, optional)
   - Example: `["https://competitor1.com", "https://competitor2.com"]`
   - 2-5 competitor domains for benchmarking

### Optional
- Google Search Console property ID (for actual ranking data)
- Google Analytics view ID (for traffic/conversion data)
- Focus pages (specific URLs to prioritize in analysis)
- Geographic target (for local SEO considerations)

---

## Process

### Step 1: Site Audit (Orchestration Layer)
*Directive triggers orchestrator: `execution/seo_orchestrator.py`*

1. Parse website URL and configuration
2. Crawl primary site structure (up to 100 pages)
3. Extract key technical metadata:
   - Page titles, meta descriptions, H1-H6 headings
   - Image alt text, file sizes
   - Internal/external link counts
   - Schema markup presence
   - Sitemap and robots.txt configuration

**Constraints:**
- Respect robots.txt directives
- Rate limit: 1 request per 2 seconds to avoid server overload
- JavaScript rendering via headless browser (Playwright) for SPA sites

### Step 2: Performance Analysis (Technical SEO Agent)
Evaluate technical health:

| Metric | Tool/API | Target Score |
|--------|----------|--------------|
| **Page Speed** | Google PageSpeed Insights API | >90 mobile, >95 desktop |
| **Core Web Vitals** | PageSpeed API | LCP <2.5s, FID <100ms, CLS <0.1 |
| **Mobile-Friendly** | Responsive design check | Pass |
| **HTTPS Status** | SSL certificate validation | Valid & secure |
| **Structured Data** | Schema.org markup detection | Present on key pages |

**Data Sources:**
- Google PageSpeed Insights API (free, 25k requests/day)
- Direct HTTP requests for headers/status codes
- Lighthouse CI for automated audits

### Step 3: On-Page SEO Scoring
Score each page 0-100 on:

| Factor | Weight | How Scored |
|--------|--------|-----------|
| **Title Tag Optimization** | 20% | Length (50-60 chars), keyword presence, uniqueness |
| **Meta Description** | 15% | Length (150-160 chars), CTA presence, keyword usage |
| **Heading Structure** | 15% | H1 uniqueness, H2-H6 hierarchy, keyword distribution |
| **Content Quality** | 25% | Word count (>500), readability, keyword density (1-3%) |
| **Image Optimization** | 10% | Alt text presence, file size (<200KB), WebP format |
| **Internal Linking** | 10% | Link count (3-10 per page), anchor text quality |
| **URL Structure** | 5% | Length (<75 chars), keyword presence, hyphens vs underscores |

**Scoring Logic:**
- 90-100: Excellent (minimal improvements needed)
- 75-89: Good (some optimization opportunities)
- 60-74: Fair (requires attention)
- <60: Poor (urgent fixes needed)

### Step 4: Keyword Analysis (Content Analyst Agent)
For each target keyword:
1. Check presence in:
   - Page title (highest priority)
   - URL slug
   - H1/H2 headings
   - First paragraph
   - Alt text
   - Meta description

2. Calculate keyword density (target: 1-3%)
3. Identify keyword cannibalization (multiple pages targeting same keyword)
4. Suggest LSI keywords (semantically related terms)

**Output:**
- Keyword coverage matrix (which pages rank for which keywords)
- Missing keyword opportunities
- Over-optimization warnings (keyword stuffing)

### Step 5: Competitive Analysis (Competitive Intelligence Agent)
For each competitor:
- Domain authority estimate (via backlink count proxy)
- Page speed comparison
- Keyword overlap analysis (which keywords they rank for)
- Content gap identification (topics they cover but client doesn't)
- Technical feature comparison (schema, HTTPS, mobile-friendly)

**Scoring:**
- Calculate "SEO Competitiveness Gap" score (-100 to +100)
- Negative = client behind competitors
- Positive = client ahead of competitors

### Step 6: Deliverable Generation
**Interactive Dashboard** (`public/seo-dashboard.html`):
- Overall SEO health score (0-100)
- Core Web Vitals gauges
- Keyword ranking status grid
- Page-by-page audit table (sortable)
- Competitor comparison chart
- Top 10 priority recommendations

**Google Sheet** (`{ClientName}_SEO_Report_{Date}`):
- **Tab 1: Overview** - Summary scores, trends, action items
- **Tab 2: Page Audit** - Per-page scores with issues
- **Tab 3: Keywords** - Coverage matrix, opportunities
- **Tab 4: Competitors** - Benchmarking data
- **Tab 5: Technical** - Speed, mobile, HTTPS status
- **Tab 6: Recommendations** - Prioritized fixes with impact estimates

**Monthly PDF Insights** (via `execution/generate_seo_insights.py`):
- Performance trends (month-over-month)
- Keyword ranking changes
- Competitor movements
- ROI estimate from SEO improvements

---

## Output Template

### Dashboard KPIs (Real-time)
```json
{
  "overall_score": 78,
  "page_speed_mobile": 85,
  "page_speed_desktop": 92,
  "total_pages_crawled": 47,
  "pages_needing_attention": 12,
  "keywords_ranked": 8,
  "keywords_missing": 7,
  "competitor_gap": -15,
  "last_updated": "2026-02-05T10:30:00Z"
}
```

### Google Sheet Structure
| Page URL | Title | Page Score | Speed | Mobile | Keywords Found | Issues | Priority |
|----------|-------|------------|-------|--------|----------------|---------|----------|
| /index | Homepage Title | 85 | 90 | Yes | automation, workflow | Missing H1 | Medium |
| /services | Services Page | 72 | 78 | Yes | automation services | Title too long | High |

---

## Execution Checklist

- [ ] Client website URL validated (accessible, not password-protected)
- [ ] Target keywords confirmed (5-15 keywords)
- [ ] Competitor URLs provided (2-5 sites)
- [ ] Google PageSpeed API key configured in `.env`
- [ ] Dashboard access token generated for client
- [ ] Initial site crawl completed (all pages discovered)
- [ ] Google Sheet template created and shared with client
- [ ] First SEO report generated successfully
- [ ] Weekly auto-refresh scheduled (every Monday 6am)
- [ ] Client training session (how to interpret scores and act on recommendations)

---

## Success Metrics

- **Report Accuracy:** % of identified issues that are valid (target: >95%)
- **Actionability:** % of recommendations client can implement (target: >80%)
- **Performance Improvement:** Average page speed increase after fixes (target: +15 points)
- **Keyword Visibility:** % of target keywords where client improves ranking (target: >40% within 90 days)

---

## Continuous Improvement Loop

**Weekly Monitoring:**
1. Re-scan website for changes (new pages, updated content)
2. Re-check Core Web Vitals (detect performance regressions)
3. Update keyword rankings (if GSC connected)
4. Flag new issues (broken links, missing alt text)

**Monthly Review:**
1. Compare current scores vs previous month
2. Identify which recommendations were implemented
3. Measure impact (did page speed improve? keyword rankings up?)
4. Refine recommendations based on what worked
5. Adjust competitor tracking (add/remove competitors)

**Quarterly Optimization:**
1. Full site re-crawl (detect structural changes)
2. Update keyword targets based on client goals
3. Expand analysis depth (more pages, more metrics)
4. Client feedback session (what insights are most valuable?)

---

## Edge Cases & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Site inaccessible | Password-protected, dev site, or down | Request staging URL or temporary access credentials |
| JavaScript-heavy site (React/Vue) | Standard HTTP request doesn't render content | Use Playwright headless browser to render JS |
| Very large site (1000+ pages) | Crawl would take hours | Focus on top 100 pages by priority (homepage, key landing pages) |
| No competitors provided | Client unsure who to benchmark against | Auto-discover competitors via Google search for target keywords |
| Page speed API rate limit | Free tier = 25k requests/day | Cache results, only re-check pages that changed |
| Keyword rankings unavailable | No GSC access | Use estimated rankings based on on-page optimization score |
| Client wants local SEO | Need Google My Business data | Add GMB API integration for local pack rankings |

---

## API Keys & Configuration

**Required in `.env`:**
```bash
# Google PageSpeed Insights (free tier)
GOOGLE_PAGESPEED_API_KEY=your_api_key_here

# Dashboard access (simple token auth)
SEO_DASHBOARD_TOKEN=secure_random_token

# Optional: Paid SEO APIs (for richer data)
# SEMRUSH_API_KEY=xxx
# AHREFS_API_KEY=xxx
# MOZ_API_KEY=xxx
```

**Client Configuration** (`clients/{client_slug}/config/seo_config.json`):
```json
{
  "website_url": "https://example.com",
  "target_keywords": [
    "automation services",
    "workflow optimization",
    "business process automation"
  ],
  "competitors": [
    "https://competitor1.com",
    "https://competitor2.com"
  ],
  "focus_pages": [
    "/",
    "/services",
    "/about",
    "/contact"
  ],
  "google_search_console_property": null,
  "google_analytics_view_id": null,
  "update_frequency": "weekly",
  "dashboard_access_token": "client_specific_token_here"
}
```

---

## Related Directives

- `directives/lead_research_service.md` - Uses similar data gathering patterns
- `directives/sales_analytics_service.md` - Dashboard and reporting patterns

## Related Execution Scripts

- `execution/seo_orchestrator.py` - Main SEO analysis workflow
- `execution/create_seo_dashboard_data.py` - Generate dashboard JSON payload
- `execution/generate_seo_insights.py` - Monthly PDF report generation
- `execution/scrape_single_site.py` - Website crawling (if doesn't exist, create)

---

## Tools Used

**Web Scraping & Analysis:**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `playwright` - JavaScript rendering for SPAs
- `lighthouse` - Performance auditing

**Data Processing:**
- `pandas` - Data manipulation for scoring
- `numpy` - Statistical calculations

**APIs:**
- Google PageSpeed Insights API (page speed, Core Web Vitals)
- Google Search Console API (optional: actual keyword rankings)
- Google Analytics API (optional: traffic data)

**Output Generation:**
- `gspread` - Google Sheets API
- `markdown` - PDF report generation
- JSON files cached in `.tmp/seo_reports/`

---

## Pricing Tiers

**Basic ($800/month):**
- Up to 50 pages analyzed
- Weekly dashboard updates
- Monthly PDF report
- 10 target keywords
- 2 competitors tracked

**Pro ($1,200/month):**
- Up to 200 pages analyzed
- Daily dashboard updates
- Bi-weekly PDF reports
- 20 target keywords
- 5 competitors tracked
- Google Search Console integration

**Enterprise ($2,000/month):**
- Unlimited pages
- Real-time dashboard updates
- Weekly PDF reports
- Unlimited keywords
- 10 competitors tracked
- Full GSC + GA integration
- Custom recommendations with implementation support
