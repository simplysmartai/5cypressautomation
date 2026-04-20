#!/usr/bin/env python3
"""
SEO Orchestrator - Comprehensive SEO Analysis Engine
Analyzes websites for on-page, technical, and competitive SEO metrics.

Usage:
    python execution/seo_orchestrator.py \
        --website-url https://example.com \
        --config clients/client-slug/config/seo_config.json \
        --output .tmp/seo_reports/client-slug.json
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from urllib.parse import urlparse, urljoin
import logging

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SEOOrchestrator:
    """Main orchestrator for SEO analysis workflow."""
    
    def __init__(self, website_url: str, config_path: Optional[str] = None):
        self.website_url = website_url
        self.domain = urlparse(website_url).netloc
        self.config = self._load_config(config_path) if config_path else {}
        self.pagespeed_api_key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
        
        # Results storage
        self.pages_analyzed = []
        self.technical_metrics = {}
        self.keyword_analysis = {}
        self.competitor_data = []
        
        logger.info(f"🔍 Initialized SEO Orchestrator for {self.website_url}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load client SEO configuration."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"✅ Loaded config from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"⚠️  Config file not found: {config_path}, using defaults")
            return {}
    
    def phase_1_crawl_site(self, max_pages: int = 50) -> List[Dict]:
        """
        PHASE 1: SITE CRAWL
        Discover and crawl website pages to extract SEO metadata.
        """
        logger.info("🕷️  PHASE 1: CRAWLING WEBSITE")
        
        visited = set()
        to_visit = [self.website_url]
        pages_data = []
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SEOBot/1.0; +https://5cypresslabs.com/bot)'
        }
        
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            
            if url in visited or not url.startswith(self.website_url):
                continue
            
            try:
                logger.info(f"  Crawling: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    logger.warning(f"  ⚠️  Status {response.status_code} for {url}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract SEO metadata
                page_data = self._extract_page_metadata(url, soup, response)
                pages_data.append(page_data)
                visited.add(url)
                
                # Find internal links
                for link in soup.find_all('a', href=True):
                    href = urljoin(url, link['href'])
                    parsed = urlparse(href)
                    
                    # Only follow same-domain links, ignore anchors and query params
                    if parsed.netloc == self.domain and '#' not in href:
                        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        if clean_url not in visited and clean_url not in to_visit:
                            to_visit.append(clean_url)
                
                # Rate limiting - be respectful
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"  ❌ Error crawling {url}: {str(e)}")
                continue
        
        self.pages_analyzed = pages_data
        logger.info(f"✅ Crawled {len(pages_data)} pages")
        return pages_data
    
    def _extract_page_metadata(self, url: str, soup: BeautifulSoup, response) -> Dict:
        """Extract comprehensive SEO metadata from a page."""
        
        # Title tag
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else ""
        
        # Headings
        h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
        h2_tags = [h.get_text().strip() for h in soup.find_all('h2')]
        
        # Images
        images = soup.find_all('img')
        images_without_alt = [img.get('src', '') for img in images if not img.get('alt')]
        
        # Internal/external links
        links = soup.find_all('a', href=True)
        internal_links = [l for l in links if self.domain in l['href'] or l['href'].startswith('/')]
        external_links = [l for l in links if l not in internal_links and l['href'].startswith('http')]
        
        # Content analysis
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text_content = soup.get_text()
        words = text_content.split()
        word_count = len([w for w in words if len(w) > 3])  # Meaningful words
        
        # Schema markup
        schema_scripts = soup.find_all('script', type='application/ld+json')
        has_schema = len(schema_scripts) > 0
        
        # Calculate page score
        score = self._calculate_page_score({
            'title': title,
            'description': description,
            'h1_count': len(h1_tags),
            'h2_count': len(h2_tags),
            'word_count': word_count,
            'images_without_alt_count': len(images_without_alt),
            'internal_links_count': len(internal_links),
            'has_schema': has_schema
        })
        
        return {
            'url': url,
            'title': title,
            'title_length': len(title),
            'meta_description': description,
            'meta_description_length': len(description),
            'h1_tags': h1_tags,
            'h2_tags': h2_tags,
            'h1_count': len(h1_tags),
            'word_count': word_count,
            'images_total': len(images),
            'images_without_alt': len(images_without_alt),
            'internal_links_count': len(internal_links),
            'external_links_count': len(external_links),
            'has_schema': has_schema,
            'https': url.startswith('https://'),
            'page_score': score,
            'issues': self._identify_issues({
                'title': title,
                'description': description,
                'h1_tags': h1_tags,
                'images_without_alt_count': len(images_without_alt),
                'word_count': word_count
            })
        }
    
    def _calculate_page_score(self, data: Dict) -> int:
        """Calculate SEO score for a page (0-100)."""
        score = 100
        
        # Title optimization (20 points)
        if not data['title']:
            score -= 20
        elif len(data['title']) < 30 or len(data['title']) > 60:
            score -= 10
        
        # Meta description (15 points)
        if not data['description']:
            score -= 15
        elif len(data['description']) < 120 or len(data['description']) > 160:
            score -= 7
        
        # Heading structure (15 points)
        if data['h1_count'] == 0:
            score -= 15
        elif data['h1_count'] > 1:
            score -= 7
        
        if data['h2_count'] == 0:
            score -= 5
        
        # Content quality (25 points)
        if data['word_count'] < 300:
            score -= 25
        elif data['word_count'] < 500:
            score -= 12
        
        # Image optimization (10 points)
        if data['images_without_alt_count'] > 0:
            score -= min(10, data['images_without_alt_count'] * 2)
        
        # Internal linking (10 points)
        if data['internal_links_count'] < 3:
            score -= 10
        elif data['internal_links_count'] > 10:
            score -= 3
        
        # Schema markup (5 points)
        if not data['has_schema']:
            score -= 5
        
        return max(0, score)
    
    def _identify_issues(self, data: Dict) -> List[str]:
        """Identify specific SEO issues for a page."""
        issues = []
        
        if not data['title']:
            issues.append("Missing title tag")
        elif len(data['title']) > 60:
            issues.append("Title too long (>60 chars)")
        elif len(data['title']) < 30:
            issues.append("Title too short (<30 chars)")
        
        if not data['description']:
            issues.append("Missing meta description")
        elif len(data['description']) > 160:
            issues.append("Meta description too long")
        
        if len(data['h1_tags']) == 0:
            issues.append("Missing H1 tag")
        elif len(data['h1_tags']) > 1:
            issues.append("Multiple H1 tags detected")
        
        if data['word_count'] < 300:
            issues.append("Thin content (<300 words)")
        
        if data['images_without_alt_count'] > 0:
            issues.append(f"{data['images_without_alt_count']} images missing alt text")
        
        return issues
    
    def phase_2_technical_analysis(self) -> Dict:
        """
        PHASE 2: TECHNICAL SEO ANALYSIS
        Check page speed, Core Web Vitals, mobile-friendliness.
        """
        logger.info("⚡ PHASE 2: TECHNICAL ANALYSIS")
        
        metrics = {
            'page_speed_mobile': None,
            'page_speed_desktop': None,
            'core_web_vitals': {},
            'mobile_friendly': None,
            'https': self.website_url.startswith('https://'),
            'has_sitemap': False,
            'has_robots_txt': False
        }
        
        # Check for robots.txt and sitemap
        try:
            robots_url = f"{self.website_url.rstrip('/')}/robots.txt"
            robots_response = requests.get(robots_url, timeout=5)
            metrics['has_robots_txt'] = robots_response.status_code == 200
            
            sitemap_url = f"{self.website_url.rstrip('/')}/sitemap.xml"
            sitemap_response = requests.get(sitemap_url, timeout=5)
            metrics['has_sitemap'] = sitemap_response.status_code == 200
        except:
            pass
        
        # Google PageSpeed Insights (if API key provided)
        if self.pagespeed_api_key:
            logger.info("  📊 Running PageSpeed Insights...")
            
            # Mobile analysis
            mobile_data = self._get_pagespeed_score('mobile')
            if mobile_data:
                metrics['page_speed_mobile'] = mobile_data['score']
                metrics['core_web_vitals'] = mobile_data['vitals']
                metrics['mobile_friendly'] = True
            
            # Desktop analysis
            desktop_data = self._get_pagespeed_score('desktop')
            if desktop_data:
                metrics['page_speed_desktop'] = desktop_data['score']
            
            logger.info(f"  ✅ Mobile: {metrics['page_speed_mobile']}/100, Desktop: {metrics['page_speed_desktop']}/100")
        else:
            logger.warning("  ⚠️  No PageSpeed API key - skipping performance analysis")
        
        self.technical_metrics = metrics
        return metrics
    
    def _get_pagespeed_score(self, strategy: str = 'mobile') -> Optional[Dict]:
        """Get PageSpeed Insights score via API."""
        try:
            api_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
            params = {
                'url': self.website_url,
                'key': self.pagespeed_api_key,
                'strategy': strategy,
                'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO']
            }
            
            response = requests.get(api_url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                lighthouse_result = data.get('lighthouseResult', {})
                categories = lighthouse_result.get('categories', {})
                audits = lighthouse_result.get('audits', {})
                
                # Extract Core Web Vitals
                vitals = {}
                if 'largest-contentful-paint' in audits:
                    vitals['lcp'] = audits['largest-contentful-paint'].get('numericValue', 0) / 1000
                if 'first-input-delay' in audits:
                    vitals['fid'] = audits['first-input-delay'].get('numericValue', 0)
                if 'cumulative-layout-shift' in audits:
                    vitals['cls'] = audits['cumulative-layout-shift'].get('numericValue', 0)
                
                return {
                    'score': int(categories.get('performance', {}).get('score', 0) * 100),
                    'vitals': vitals
                }
            else:
                logger.error(f"  ❌ PageSpeed API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"  ❌ PageSpeed API request failed: {str(e)}")
            return None
    
    def phase_3_keyword_analysis(self) -> Dict:
        """
        PHASE 3: KEYWORD ANALYSIS
        Analyze target keyword presence and distribution.
        """
        logger.info("🔑 PHASE 3: KEYWORD ANALYSIS")
        
        target_keywords = self.config.get('target_keywords', [])
        
        if not target_keywords:
            logger.warning("  ⚠️  No target keywords configured")
            return {}
        
        keyword_data = {}
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            pages_with_keyword = []
            
            for page in self.pages_analyzed:
                # Check keyword presence in various elements
                in_title = keyword_lower in page['title'].lower()
                in_description = keyword_lower in page['meta_description'].lower()
                in_h1 = any(keyword_lower in h1.lower() for h1 in page['h1_tags'])
                in_url = keyword_lower.replace(' ', '-') in page['url'].lower()
                
                if any([in_title, in_description, in_h1, in_url]):
                    pages_with_keyword.append({
                        'url': page['url'],
                        'in_title': in_title,
                        'in_description': in_description,
                        'in_h1': in_h1,
                        'in_url': in_url
                    })
            
            keyword_data[keyword] = {
                'pages_count': len(pages_with_keyword),
                'pages': pages_with_keyword,
                'status': 'optimized' if len(pages_with_keyword) > 0 else 'missing'
            }
            
            logger.info(f"  🔑 '{keyword}': Found on {len(pages_with_keyword)} pages")
        
        self.keyword_analysis = keyword_data
        return keyword_data
    
    def phase_4_competitor_analysis(self) -> List[Dict]:
        """
        PHASE 4: COMPETITOR ANALYSIS
        Basic competitor benchmarking (simplified version).
        """
        logger.info("🏆 PHASE 4: COMPETITOR ANALYSIS")
        
        competitors = self.config.get('competitors', [])
        
        if not competitors:
            logger.warning("  ⚠️  No competitors configured")
            return []
        
        competitor_results = []
        
        for comp_url in competitors[:3]:  # Limit to 3 competitors
            logger.info(f"  Analyzing: {comp_url}")
            
            try:
                response = requests.get(comp_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; SEOBot/1.0)'
                })
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else ""
                    
                    h1_count = len(soup.find_all('h1'))
                    has_schema = len(soup.find_all('script', type='application/ld+json')) > 0
                    
                    competitor_results.append({
                        'url': comp_url,
                        'title_length': len(title_text),
                        'h1_count': h1_count,
                        'has_schema': has_schema,
                        'https': comp_url.startswith('https://')
                    })
                    
                    time.sleep(2)  # Rate limiting
                    
            except Exception as e:
                logger.error(f"  ❌ Error analyzing {comp_url}: {str(e)}")
        
        self.competitor_data = competitor_results
        logger.info(f"✅ Analyzed {len(competitor_results)} competitors")
        return competitor_results
    
    def generate_report(self, output_path: str) -> Dict:
        """
        PHASE 5: GENERATE REPORT
        Compile all analysis into comprehensive JSON report.
        """
        logger.info("📊 PHASE 5: GENERATING REPORT")
        
        # Calculate overall score
        if self.pages_analyzed:
            avg_page_score = sum(p['page_score'] for p in self.pages_analyzed) / len(self.pages_analyzed)
        else:
            avg_page_score = 0
        
        # Count issues
        total_issues = sum(len(p['issues']) for p in self.pages_analyzed)
        pages_needing_attention = sum(1 for p in self.pages_analyzed if p['page_score'] < 75)
        
        # Keywords status
        keywords_ranked = sum(1 for k in self.keyword_analysis.values() if k['status'] == 'optimized')
        keywords_missing = len(self.keyword_analysis) - keywords_ranked
        
        report = {
            'website_url': self.website_url,
            'analysis_date': datetime.now().isoformat(),
            'summary': {
                'overall_score': int(avg_page_score),
                'total_pages_crawled': len(self.pages_analyzed),
                'pages_needing_attention': pages_needing_attention,
                'total_issues_found': total_issues,
                'keywords_ranked': keywords_ranked,
                'keywords_missing': keywords_missing,
                'page_speed_mobile': self.technical_metrics.get('page_speed_mobile'),
                'page_speed_desktop': self.technical_metrics.get('page_speed_desktop'),
                'mobile_friendly': self.technical_metrics.get('mobile_friendly'),
                'https_enabled': self.technical_metrics.get('https'),
                'has_sitemap': self.technical_metrics.get('has_sitemap'),
                'has_robots_txt': self.technical_metrics.get('has_robots_txt')
            },
            'pages': self.pages_analyzed,
            'technical_metrics': self.technical_metrics,
            'keyword_analysis': self.keyword_analysis,
            'competitor_data': self.competitor_data,
            'top_recommendations': self._generate_recommendations()
        }
        
        # Save report
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Report saved to {output_path}")
        return report
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate prioritized list of recommendations."""
        recommendations = []
        
        # Check for common issues across all pages
        pages_missing_title = [p for p in self.pages_analyzed if not p['title']]
        pages_missing_desc = [p for p in self.pages_analyzed if not p['meta_description']]
        pages_missing_h1 = [p for p in self.pages_analyzed if p['h1_count'] == 0]
        pages_thin_content = [p for p in self.pages_analyzed if p['word_count'] < 300]
        
        if pages_missing_title:
            recommendations.append({
                'priority': 'high',
                'category': 'on-page',
                'issue': f'{len(pages_missing_title)} pages missing title tags',
                'impact': 'Critical for search rankings',
                'action': 'Add unique, keyword-optimized title tags (50-60 characters)'
            })
        
        if pages_missing_desc:
            recommendations.append({
                'priority': 'high',
                'category': 'on-page',
                'issue': f'{len(pages_missing_desc)} pages missing meta descriptions',
                'impact': 'Reduces click-through rate from search results',
                'action': 'Write compelling meta descriptions (150-160 characters)'
            })
        
        if pages_missing_h1:
            recommendations.append({
                'priority': 'medium',
                'category': 'on-page',
                'issue': f'{len(pages_missing_h1)} pages missing H1 tags',
                'impact': 'Affects content hierarchy and keyword relevance',
                'action': 'Add single, descriptive H1 tag to each page'
            })
        
        if pages_thin_content:
            recommendations.append({
                'priority': 'medium',
                'category': 'content',
                'issue': f'{len(pages_thin_content)} pages have thin content (<300 words)',
                'impact': 'Low-quality content signals to search engines',
                'action': 'Expand content to 500+ words with valuable information'
            })
        
        if self.technical_metrics.get('page_speed_mobile', 100) < 80:
            recommendations.append({
                'priority': 'high',
                'category': 'technical',
                'issue': 'Poor mobile page speed',
                'impact': 'High bounce rates, lower rankings',
                'action': 'Optimize images, enable compression, minify CSS/JS'
            })
        
        if not self.technical_metrics.get('https'):
            recommendations.append({
                'priority': 'critical',
                'category': 'technical',
                'issue': 'Site not using HTTPS',
                'impact': 'Security warnings, ranking penalty',
                'action': 'Install SSL certificate and redirect HTTP to HTTPS'
            })
        
        if not self.technical_metrics.get('has_sitemap'):
            recommendations.append({
                'priority': 'medium',
                'category': 'technical',
                'issue': 'No XML sitemap detected',
                'impact': 'Search engines may miss pages',
                'action': 'Create and submit XML sitemap to Google Search Console'
            })
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 999))
        
        return recommendations[:10]  # Top 10 recommendations


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SEO Orchestrator - Comprehensive SEO Analysis')
    parser.add_argument('--website-url', required=True, help='Website URL to analyze')
    parser.add_argument('--config', help='Path to SEO config JSON file')
    parser.add_argument('--output', required=True, help='Output path for JSON report')
    parser.add_argument('--max-pages', type=int, default=50, help='Maximum pages to crawl (default: 50)')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = SEOOrchestrator(args.website_url, args.config)
    
    # Run analysis phases
    orchestrator.phase_1_crawl_site(max_pages=args.max_pages)
    orchestrator.phase_2_technical_analysis()
    orchestrator.phase_3_keyword_analysis()
    orchestrator.phase_4_competitor_analysis()
    report = orchestrator.generate_report(args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("SEO ANALYSIS COMPLETE")
    print("="*60)
    print(f"Website: {args.website_url}")
    print(f"Overall Score: {report['summary']['overall_score']}/100")
    print(f"Pages Analyzed: {report['summary']['total_pages_crawled']}")
    print(f"Issues Found: {report['summary']['total_issues_found']}")
    print(f"Pages Needing Attention: {report['summary']['pages_needing_attention']}")
    print(f"\nReport saved to: {args.output}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
