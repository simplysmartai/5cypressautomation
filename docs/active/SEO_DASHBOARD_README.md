# SEO Optimization Dashboard

Comprehensive SEO analysis dashboard for 5 Cypress Labs that evaluates website performance across on-page, technical, and competitive metrics.

## ✨ Features

- **Real-time Analysis**: Enter any website URL and get instant SEO audit
- **Comprehensive Metrics**: 
  - Overall SEO score (0-100)
  - Page speed analysis (mobile + desktop)
  - Core Web Vitals tracking
  - Keyword optimization status
  - Technical SEO checklist
- **Page-by-Page Audit**: Detailed analysis of every page crawled
- **Actionable Recommendations**: Prioritized list of improvements
- **Monthly Insights**: Automated PDF reports with trends and progress

## 🚀 Quick Start

### 1. Access the Dashboard

Navigate to: **http://localhost:3000/seo-dashboard**

### 2. Run Analysis

1. Enter a website URL (e.g., `https://example.com`)
2. Click "Analyze Website"
3. Wait 1-2 minutes for analysis to complete
4. Review results and recommendations

## 📊 What Gets Analyzed

### On-Page SEO (40 points)
- Title tags (length, keyword presence, uniqueness)
- Meta descriptions (length, CTAs, keywords)
- Heading structure (H1-H6 hierarchy)
- Content quality (word count, readability)
- Image optimization (alt text, file sizes)
- Internal linking (anchor text, link counts)
- URL structure

### Technical SEO (35 points)
- Page speed (Google PageSpeed Insights API)
- Core Web Vitals (LCP, FID, CLS)
- Mobile-friendliness
- HTTPS/SSL certificate
- XML sitemap presence
- Robots.txt configuration
- Structured data (Schema.org)

### Keyword Analysis (15 points)
- Target keyword presence in titles, H1s, URLs
- Keyword density (1-3% target)
- Keyword cannibalization detection
- LSI keyword suggestions

### Competitive Analysis (10 points)
- Domain comparison with competitors
- Keyword overlap analysis
- Technical feature benchmarking

## 🔧 Configuration

### Client Configuration

Create a config file at `clients/{client-slug}/config/seo_config.json`:

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
    "/about"
  ],
  "google_search_console_property": null,
  "google_analytics_view_id": null,
  "update_frequency": "weekly",
  "dashboard_access_token": "unique_token_here"
}
```

### Environment Variables

Add to `.env`:

```bash
# Google PageSpeed Insights API (free tier)
GOOGLE_PAGESPEED_API_KEY=your_api_key_here

# Dashboard authentication
SEO_DASHBOARD_TOKEN=secure_random_token
```

**Get PageSpeed API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "PageSpeed Insights API"
4. Create credentials (API Key)
5. Add to `.env`

## 📁 File Structure

```
directives/
  └── seo_optimization_service.md      # Service definition & SOP

execution/
  ├── seo_orchestrator.py              # Main analysis engine
  └── generate_seo_insights.py         # Monthly report generator

public/
  └── seo-dashboard.html               # Interactive dashboard UI

clients/
  └── {client-slug}/
      └── config/
          └── seo_config.json          # Client SEO configuration

.tmp/
  └── seo_reports/
      └── {domain}.json                # Cached analysis results
```

## 🎯 How It Works

### Architecture (3-Layer Pattern)

**Layer 1: Directive** (`directives/seo_optimization_service.md`)
- Defines what to analyze and how
- Inputs, outputs, success metrics
- Edge cases and troubleshooting

**Layer 2: Orchestration** (You/Agent)
- Reads directive
- Calls execution scripts
- Handles errors and retries
- Updates directive with learnings

**Layer 3: Execution** (`execution/seo_orchestrator.py`)
- Crawls website (respects robots.txt)
- Extracts metadata (titles, descriptions, headings)
- Calls PageSpeed API for performance
- Analyzes keywords and competitors
- Generates JSON report

### Analysis Phases

**Phase 1: Site Crawl** (30-60 seconds)
- Discovers up to 50 pages
- Extracts HTML metadata
- Identifies internal links
- Respects rate limits (2 sec/request)

**Phase 2: Technical Analysis** (30-40 seconds)
- Calls Google PageSpeed API
- Checks HTTPS, sitemap, robots.txt
- Measures Core Web Vitals

**Phase 3: Keyword Analysis** (5 seconds)
- Matches target keywords to pages
- Calculates keyword density
- Identifies optimization opportunities

**Phase 4: Competitive Analysis** (20-30 seconds)
- Scrapes competitor homepages
- Compares technical features
- Benchmarks performance

**Phase 5: Report Generation** (5 seconds)
- Calculates overall score
- Prioritizes recommendations
- Saves JSON to `.tmp/seo_reports/`

## 📈 Scoring System

### Overall SEO Score (0-100)

```
90-100: Excellent - minimal improvements needed
75-89:  Good - some optimization opportunities
60-74:  Fair - requires attention
0-59:   Poor - urgent fixes needed
```

### Page-Level Scoring

Each page receives a score based on:
- **Title Tag** (20 pts): Length 50-60 chars, keyword presence
- **Meta Description** (15 pts): Length 150-160 chars, CTA
- **Headings** (15 pts): Single H1, H2-H6 hierarchy
- **Content** (25 pts): 500+ words, readability
- **Images** (10 pts): Alt text, optimized sizes
- **Internal Links** (10 pts): 3-10 links per page
- **URL** (5 pts): Short, keyword-optimized

## 🔄 Automation

### Weekly Auto-Updates

Schedule via cron or task scheduler:

```bash
# Run every Monday at 6am
python execution/seo_orchestrator.py \
  --website-url https://example.com \
  --config clients/client-slug/config/seo_config.json \
  --output .tmp/seo_reports/client-slug.json
```

### Monthly Insights Generation

```bash
# Generate monthly PDF insights
python execution/generate_seo_insights.py \
  --client-id client-slug \
  --report-path .tmp/seo_reports/client-slug.json \
  --output documents/client-slug-seo-insights-2026-02.md
```

## 🛠️ API Endpoints

### POST `/api/seo/analyze`

Trigger new SEO analysis:

```json
{
  "website_url": "https://example.com"
}
```

**Response**: Full SEO analysis report (JSON)

### GET `/api/seo/:domain`

Retrieve cached report:

```
GET /api/seo/example-com
```

**Response**: Previously generated SEO report

## 🚨 Troubleshooting

### "Analysis timeout" error
**Cause**: Website is too large or slow to respond  
**Solution**: Reduce `--max-pages` parameter or analyze specific sections

### "Failed to crawl" errors
**Cause**: Website blocks bots or requires JavaScript  
**Solution**: Check robots.txt, consider using Playwright for JS-heavy sites

### "PageSpeed API rate limit"
**Cause**: Exceeded 25k requests/day (free tier)  
**Solution**: Wait 24 hours or cache results longer

### No PageSpeed scores
**Cause**: Missing `GOOGLE_PAGESPEED_API_KEY` in `.env`  
**Solution**: Get API key from Google Cloud Console and add to `.env`

## 📝 Service Pricing

**Basic ($800/month)**
- Up to 50 pages analyzed
- Weekly dashboard updates
- Monthly PDF report
- 10 target keywords
- 2 competitors tracked

**Pro ($1,200/month)**
- Up to 200 pages
- Daily updates
- Bi-weekly reports
- 20 keywords
- 5 competitors
- Google Search Console integration

**Enterprise ($2,000/month)**
- Unlimited pages
- Real-time updates
- Weekly reports
- Unlimited keywords
- 10 competitors
- Full GSC + GA integration
- Implementation support

## 🔒 Security & Privacy

- **Authentication**: Simple token-based auth (add OAuth later)
- **Data Storage**: Reports cached locally in `.tmp/` (gitignored)
- **API Keys**: Stored in `.env` (never committed)
- **Rate Limiting**: Respects website robots.txt and rate limits

## 🎓 Best Practices

1. **Respectful Crawling**: Always respect robots.txt and rate limits
2. **Regular Updates**: Run analysis weekly to track progress
3. **Prioritize Actions**: Focus on critical/high priority recommendations first
4. **Track Progress**: Compare month-over-month scores
5. **Client Communication**: Share monthly PDF insights with clients

## 📞 Support

For issues or questions about the SEO dashboard:
1. Check `directives/seo_optimization_service.md` for troubleshooting
2. Review logs in terminal output
3. Inspect cached reports in `.tmp/seo_reports/`
4. Update directive with new learnings (self-annealing)

---

**Built by 5 Cypress Labs**  
*Powered by the 3-layer architecture (Directive → Orchestration → Execution)*
