#!/usr/bin/env python3
"""
SEO Monthly Insights Generator
Generates monthly PDF reports with SEO performance trends and recommendations.

Usage:
    python execution/generate_seo_insights.py \
        --client-id client-slug \
        --report-path .tmp/seo_reports/client-slug.json \
        --output documents/client-slug-seo-insights-2026-02.pdf
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SEOInsightsGenerator:
    """Generate monthly PDF insights from SEO analysis data."""
    
    def __init__(self, client_id: str, report_path: str):
        self.client_id = client_id
        self.report_path = report_path
        self.report_data = self._load_report()
        
        logger.info(f"📊 Initialized SEO Insights Generator for {client_id}")
    
    def _load_report(self) -> Dict:
        """Load the latest SEO analysis report."""
        try:
            with open(self.report_path, 'r') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded report from {self.report_path}")
            return data
        except FileNotFoundError:
            logger.error(f"❌ Report not found: {self.report_path}")
            raise
    
    def generate_markdown(self) -> str:
        """Generate markdown content for the insights report."""
        logger.info("📝 Generating markdown insights...")
        
        summary = self.report_data.get('summary', {})
        pages = self.report_data.get('pages', [])
        keywords = self.report_data.get('keyword_analysis', {})
        recommendations = self.report_data.get('top_recommendations', [])
        
        # Calculate some insights
        avg_score = summary.get('overall_score', 0)
        total_pages = summary.get('total_pages_crawled', 0)
        pages_needing_work = summary.get('pages_needing_attention', 0)
        
        # Keyword stats
        keywords_optimized = sum(1 for k in keywords.values() if k['status'] == 'optimized')
        keywords_missing = len(keywords) - keywords_optimized
        
        # Month/year
        report_date = datetime.fromisoformat(self.report_data['analysis_date'])
        month_year = report_date.strftime('%B %Y')
        
        markdown = f"""# SEO Performance Insights
## {self.client_id.replace('-', ' ').title()}
### {month_year}

---

## Executive Summary

Your website's SEO health score is **{avg_score}/100**. We analyzed {total_pages} pages and identified {summary.get('total_issues_found', 0)} issues that need attention.

### Key Highlights

- **Overall SEO Score:** {avg_score}/100
- **Pages Analyzed:** {total_pages}
- **Pages Needing Improvement:** {pages_needing_work}
- **Keywords Optimized:** {keywords_optimized}/{len(keywords)}
- **Mobile Page Speed:** {summary.get('page_speed_mobile', 'N/A')}/100
- **Desktop Page Speed:** {summary.get('page_speed_desktop', 'N/A')}/100

---

## Performance Breakdown

### Technical SEO
"""
        
        # Technical checklist
        technical_items = [
            ('HTTPS Enabled', summary.get('https_enabled', False)),
            ('XML Sitemap Present', summary.get('has_sitemap', False)),
            ('Robots.txt Configured', summary.get('has_robots_txt', False)),
            ('Mobile Friendly', summary.get('mobile_friendly', False))
        ]
        
        for item, status in technical_items:
            icon = '✅' if status else '❌'
            markdown += f"\n- {icon} **{item}**"
        
        markdown += "\n\n### On-Page SEO\n"
        
        # Calculate on-page stats
        pages_with_title = sum(1 for p in pages if p.get('title'))
        pages_with_desc = sum(1 for p in pages if p.get('meta_description'))
        pages_with_h1 = sum(1 for p in pages if p.get('h1_count', 0) > 0)
        
        if total_pages > 0:
            markdown += f"\n- **{pages_with_title}/{total_pages}** pages have title tags"
            markdown += f"\n- **{pages_with_desc}/{total_pages}** pages have meta descriptions"
            markdown += f"\n- **{pages_with_h1}/{total_pages}** pages have H1 tags"
        
        markdown += "\n\n### Keyword Optimization\n"
        
        if keywords:
            markdown += "\n| Keyword | Status | Pages Found |\n"
            markdown += "|---------|--------|-------------|\n"
            for keyword, data in keywords.items():
                status_icon = '✅' if data['status'] == 'optimized' else '❌'
                markdown += f"| {keyword} | {status_icon} {data['status'].title()} | {data['pages_count']} |\n"
        else:
            markdown += "\n*No target keywords configured. Consider adding target keywords to track optimization progress.*\n"
        
        markdown += "\n---\n\n## Top Priority Recommendations\n"
        
        # Group recommendations by priority
        critical_recs = [r for r in recommendations if r['priority'] == 'critical']
        high_recs = [r for r in recommendations if r['priority'] == 'high']
        medium_recs = [r for r in recommendations if r['priority'] == 'medium']
        
        if critical_recs:
            markdown += "\n### 🔴 Critical Issues\n"
            for rec in critical_recs:
                markdown += f"\n**{rec['issue']}**\n"
                markdown += f"- Impact: {rec['impact']}\n"
                markdown += f"- Action: {rec['action']}\n"
        
        if high_recs:
            markdown += "\n### 🟠 High Priority\n"
            for rec in high_recs:
                markdown += f"\n**{rec['issue']}**\n"
                markdown += f"- Impact: {rec['impact']}\n"
                markdown += f"- Action: {rec['action']}\n"
        
        if medium_recs:
            markdown += "\n### 🟡 Medium Priority\n"
            for rec in medium_recs[:5]:  # Top 5 medium priority
                markdown += f"\n**{rec['issue']}**\n"
                markdown += f"- Impact: {rec['impact']}\n"
                markdown += f"- Action: {rec['action']}\n"
        
        markdown += "\n---\n\n## Page Performance Details\n"
        markdown += "\n### Top Performing Pages\n"
        
        # Sort pages by score (descending)
        sorted_pages = sorted(pages, key=lambda p: p.get('page_score', 0), reverse=True)
        
        markdown += "\n| Page | Score | Word Count | Issues |\n"
        markdown += "|------|-------|------------|--------|\n"
        
        for page in sorted_pages[:10]:  # Top 10
            url_path = page['url'].replace(self.report_data['website_url'], '') or '/'
            score = page.get('page_score', 0)
            word_count = page.get('word_count', 0)
            issues_count = len(page.get('issues', []))
            markdown += f"| {url_path[:40]} | {score}/100 | {word_count} | {issues_count} |\n"
        
        markdown += "\n### Pages Needing Attention\n"
        markdown += "\n| Page | Score | Primary Issues |\n"
        markdown += "|------|-------|----------------|\n"
        
        # Pages with lowest scores
        for page in sorted_pages[-10:]:  # Bottom 10
            url_path = page['url'].replace(self.report_data['website_url'], '') or '/'
            score = page.get('page_score', 0)
            issues = page.get('issues', [])
            issues_text = ', '.join(issues[:2]) if issues else 'None'
            markdown += f"| {url_path[:40]} | {score}/100 | {issues_text[:50]} |\n"
        
        markdown += "\n---\n\n## Next Steps\n"
        markdown += "\n1. **Immediate Actions** - Address critical and high-priority issues first\n"
        markdown += "2. **Content Optimization** - Improve pages with scores below 75\n"
        markdown += "3. **Keyword Strategy** - Optimize pages for missing target keywords\n"
        markdown += "4. **Technical Improvements** - Fix any missing technical elements (HTTPS, sitemap, etc.)\n"
        markdown += "5. **Monthly Review** - Re-run analysis next month to track progress\n"
        
        markdown += "\n---\n\n*Report generated on " + datetime.now().strftime('%B %d, %Y') + "*\n"
        markdown += "*Powered by 5 Cypress Automation SEO Analysis Engine*\n"
        
        return markdown
    
    def save_markdown(self, output_path: str) -> str:
        """Save the markdown insights to a file."""
        markdown = self.generate_markdown()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        logger.info(f"✅ Markdown insights saved to {output_path}")
        return output_path
    
    def generate_pdf(self, output_path: str) -> str:
        """
        Generate PDF from markdown insights.
        Note: Requires markdown-pdf or similar tool to be installed.
        For now, we'll just create the markdown file.
        """
        # First create markdown
        md_path = output_path.replace('.pdf', '.md')
        self.save_markdown(md_path)
        
        # TODO: Convert markdown to PDF using tool like:
        # - markdown-pdf (Node.js)
        # - pandoc
        # - wkhtmltopdf
        # - or Python libraries like reportlab, weasyprint
        
        logger.info(f"📄 Markdown created at {md_path}")
        logger.info("ℹ️  PDF generation requires additional tools (pandoc, markdown-pdf, etc.)")
        logger.info("    For now, the markdown file can be manually converted to PDF")
        
        return md_path


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate monthly SEO insights report')
    parser.add_argument('--client-id', required=True, help='Client slug identifier')
    parser.add_argument('--report-path', required=True, help='Path to SEO analysis JSON report')
    parser.add_argument('--output', required=True, help='Output path for insights document')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = SEOInsightsGenerator(args.client_id, args.report_path)
    
    # Generate report
    if args.output.endswith('.pdf'):
        output_file = generator.generate_pdf(args.output)
    else:
        output_file = generator.save_markdown(args.output)
    
    print("\n" + "="*60)
    print("SEO INSIGHTS REPORT GENERATED")
    print("="*60)
    print(f"Client: {args.client_id}")
    print(f"Output: {output_file}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
