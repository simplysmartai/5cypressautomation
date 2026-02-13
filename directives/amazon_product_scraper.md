# Amazon Product Scraper

## Goal
Extract product details (title, price, rating, reviews, ASIN, seller info) from Amazon listings for market research, competitor analysis, and client reporting.

## Inputs
- Search keywords or product URLs
- Number of products to scrape
- Client identifier (for reporting)

## Tools/Scripts
- execution/amazon_product_scraper.py
- .env for API keys (if using Apify or proxy)

## Outputs
- CSV or Google Sheet with product data
- Summary report (optional)

## Edge Cases
- Amazon rate limits and CAPTCHAs
- Product variations (size, color)
- Out-of-stock or unavailable listings

## Steps
1. Accept keywords or URLs as input
2. Use Apify Amazon Product Scraper or custom script
3. Parse product details: title, price, rating, reviews, ASIN, seller info
4. Save results to CSV or Google Sheet
5. Handle errors, retries, and CAPTCHAs
6. Notify user when complete

## Improvements
- Add proxy rotation for reliability
- Integrate with client dashboard for real-time updates
- Batch processing for large keyword lists

---

**Execution script:** execution/amazon_product_scraper.py
**Deliverable:** Google Sheet or CSV
