#!/usr/bin/env python3
"""
Page CRO Analyzer
Analyzes landing pages for conversion rate optimization opportunities
"""
import json
import sys
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def analyze_page_cro(inputs):
    """Analyze a landing page for CRO opportunities"""
    url = inputs.get('url', '')
    conversion_goal = inputs.get('goal', 'general conversion')
    
    if not url:
        return {
            'success': False,
            'error': 'URL is required'
        }
    
    # Validate URL
    if not url.startswith('http'):
        url = 'https://' + url
    
    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract page elements
        title = soup.find('title').text if soup.find('title') else ''
        h1_tags = [h.text.strip() for h in soup.find_all('h1')]
        meta_description = ''
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_description = meta_tag.get('content', '')
        
        # Find forms
        forms = soup.find_all('form')
        form_count = len(forms)
        form_fields = []
        for form in forms[:3]:  # Analyze first 3 forms
            inputs_in_form = form.find_all(['input', 'textarea', 'select'])
            form_fields.append({
                'field_count': len(inputs_in_form),
                'field_types': [inp.get('type', 'text') for inp in inputs_in_form if inp.name == 'input']
            })
        
        # Find CTAs (buttons and prominent links)
        buttons = soup.find_all('button')
        cta_links = soup.find_all('a', class_=lambda x: x and ('btn' in x.lower() or 'cta' in x.lower() or 'button' in x.lower()))
        cta_count = len(buttons) + len(cta_links)
        cta_text = [btn.text.strip() for btn in buttons[:5]] + [link.text.strip() for link in cta_links[:5]]
        
        # Find trust signals
        trust_signals = {
            'testimonials': len(soup.find_all(text=lambda t: t and ('testimonial' in str(t).lower() or 'review' in str(t).lower()))),
            'security_badges': len(soup.find_all('img', {'alt': lambda x: x and ('secure' in x.lower() or 'ssl' in x.lower() or 'verified' in x.lower())})),
            'social_proof': len(soup.find_all(text=lambda t: t and ('customers' in str(t).lower() or 'trusted by' in str(t).lower())))
        }
        
        # Analyze images
        images = soup.find_all('img')
        images_without_alt = len([img for img in images if not img.get('alt')])
        
        # Check for video
        has_video = len(soup.find_all(['video', 'iframe'])) > 0
        
        # Analyze page speed factors
        external_scripts = len(soup.find_all('script', {'src': True}))
        external_styles = len(soup.find_all('link', {'rel': 'stylesheet'}))
        
        # Generate CRO analysis
        analysis = {
            'page_overview': {
                'url': url,
                'title': title,
                'h1_count': len(h1_tags),
                'h1_headlines': h1_tags[:3],
                'meta_description_length': len(meta_description),
                'has_meta_description': len(meta_description) > 0
            },
            'cta_analysis': {
                'total_ctas': cta_count,
                'cta_text_examples': cta_text,
                'score': 'Good' if 2 <= cta_count <= 5 else 'Needs Improvement',
                'recommendation': get_cta_recommendation(cta_count, cta_text)
            },
            'form_analysis': {
                'form_count': form_count,
                'forms_analyzed': form_fields,
                'score': 'Good' if form_count > 0 else 'Critical Issue',
                'recommendation': get_form_recommendation(form_count, form_fields)
            },
            'trust_signals': {
                'testimonial_mentions': trust_signals['testimonials'],
                'security_badges': trust_signals['security_badges'],
                'social_proof_mentions': trust_signals['social_proof'],
                'score': get_trust_score(trust_signals),
                'recommendation': get_trust_recommendation(trust_signals)
            },
            'media_elements': {
                'total_images': len(images),
                'images_without_alt': images_without_alt,
                'has_video': has_video,
                'score': 'Good' if has_video and images_without_alt < 5 else 'Needs Improvement',
                'recommendation': get_media_recommendation(images_without_alt, has_video)
            },
            'performance_factors': {
                'external_scripts': external_scripts,
                'external_styles': external_styles,
                'score': 'Good' if external_scripts < 10 else 'Needs Improvement',
                'recommendation': get_performance_recommendation(external_scripts, external_styles)
            }
        }
        
        # Generate prioritized recommendations
        recommendations = generate_recommendations(analysis, conversion_goal)
        
        # Calculate overall CRO score
        overall_score = calculate_cro_score(analysis)
        
        return {
            'success': True,
            'url': url,
            'conversion_goal': conversion_goal,
            'overall_score': overall_score,
            'analysis': analysis,
            'top_recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Failed to fetch page: {str(e)}',
            'tip': 'Make sure the URL is accessible and returns HTML content'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }


def get_cta_recommendation(count, text_examples):
    """Generate CTA recommendation"""
    if count == 0:
        return '🚨 CRITICAL: No CTAs found. Add clear, action-oriented buttons above the fold.'
    elif count == 1:
        return '⚠️ Only one CTA found. Consider adding a secondary CTA later in the page.'
    elif count > 5:
        return '⚠️ Too many CTAs may cause decision paralysis. Focus on 2-3 primary actions.'
    else:
        action_verbs = ['get', 'start', 'try', 'download', 'sign up', 'book', 'request', 'join']
        has_action_verb = any(verb in ' '.join(text_examples).lower() for verb in action_verbs)
        if not has_action_verb:
            return '💡 CTAs found but could be more action-oriented. Use verbs like "Get Started", "Try Free", or "Book Demo".'
        return '✅ Good CTA presence. A/B test different copy and placement for optimization.'


def get_form_recommendation(count, fields):
    """Generate form recommendation"""
    if count == 0:
        return '🚨 CRITICAL: No forms found. If conversion requires a form, this is blocking conversions.'
    
    avg_fields = sum(f['field_count'] for f in fields) / len(fields) if fields else 0
    
    if avg_fields > 7:
        return f'⚠️ Forms have ~{avg_fields:.0f} fields on average. Reduce to 3-5 fields to increase completion rate.'
    elif avg_fields > 5:
        return '💡 Forms have moderate length. Test removing non-essential fields.'
    else:
        return '✅ Form length is good. Ensure labels are clear and consider inline validation.'


def get_trust_recommendation(signals):
    """Generate trust signal recommendation"""
    total_signals = sum(signals.values())
    
    if total_signals == 0:
        return '🚨 CRITICAL: No trust signals found. Add testimonials, reviews, security badges, or social proof.'
    elif total_signals < 3:
        return '⚠️ Limited trust signals. Add more testimonials, customer logos, case studies, or guarantees.'
    else:
        return '✅ Good trust signal presence. Ensure they\'re prominently placed near CTAs.'


def get_trust_score(signals):
    """Calculate trust signal score"""
    total = sum(signals.values())
    if total == 0:
        return 'Critical'
    elif total < 3:
        return 'Needs Improvement'
    else:
        return 'Good'


def get_media_recommendation(missing_alt, has_video):
    """Generate media recommendation"""
    recs = []
    if missing_alt > 0:
        recs.append(f'⚠️ {missing_alt} images missing alt text (impacts accessibility and SEO)')
    if not has_video:
        recs.append('💡 Consider adding explainer video - can increase conversions by 80%+')
    if not recs:
        return '✅ Good use of media elements'
    return ' | '.join(recs)


def get_performance_recommendation(scripts, styles):
    """Generate performance recommendation"""
    if scripts > 15 or styles > 10:
        return f'⚠️ High number of external resources ({scripts} scripts, {styles} styles). Optimize for faster load times.'
    elif scripts > 10:
        return '💡 Consider consolidating or lazy-loading scripts to improve page speed.'
    else:
        return '✅ Reasonable number of external resources.'


def generate_recommendations(analysis, goal):
    """Generate prioritized recommendations"""
    recommendations = []
    
    # Priority 1: Critical conversion blockers
    if analysis['form_analysis']['score'] == 'Critical Issue':
        recommendations.append({
            'priority': 'P0 - Critical',
            'category': 'Conversion Path',
            'issue': 'No conversion form found',
            'impact': 'Blocking all conversions',
            'fix': f'Add a form for {goal} above the fold with 3-5 fields maximum'
        })
    
    if analysis['cta_analysis']['total_ctas'] == 0:
        recommendations.append({
            'priority': 'P0 - Critical',
            'category': 'Call-to-Action',
            'issue': 'No clear CTAs',
            'impact': 'Users don\'t know what action to take',
            'fix': 'Add prominent CTA button above the fold with action-oriented copy (e.g., "Start Free Trial")'
        })
    
    # Priority 2: High-impact improvements
    if analysis['trust_signals']['score'] == 'Critical':
        recommendations.append({
            'priority': 'P1 - High Impact',
            'category': 'Trust & Credibility',
            'issue': 'No trust signals present',
            'impact': '30-40% of visitors need social proof to convert',
            'fix': 'Add testimonials, customer logos, security badges, or 5-star reviews near CTAs'
        })
    
    if not analysis['media_elements']['has_video']:
        recommendations.append({
            'priority': 'P1 - High Impact',
            'category': 'Engagement',
            'issue': 'No video content',
            'impact': 'Video can increase conversions by 80%+',
            'fix': 'Add 60-90 second explainer video showing product value and how it works'
        })
    
    # Priority 3: Optimization opportunities
    if len(analysis['form_analysis']['forms_analyzed']) > 0:
        avg_fields = sum(f['field_count'] for f in analysis['form_analysis']['forms_analyzed']) / len(analysis['form_analysis']['forms_analyzed'])
        if avg_fields > 5:
            recommendations.append({
                'priority': 'P2 - Optimization',
                'category': 'Form Optimization',
                'issue': f'Forms have {avg_fields:.0f} fields on average',
                'impact': 'Each removed field can increase completion by 5-10%',
                'fix': 'Remove non-essential fields, use progressive disclosure, or split into multi-step form'
            })
    
    if analysis['page_overview']['h1_count'] != 1:
        recommendations.append({
            'priority': 'P2 - Optimization',
            'category': 'Messaging Clarity',
            'issue': f'{analysis["page_overview"]["h1_count"]} H1 headlines found (should be exactly 1)',
            'impact': 'Unclear hierarchy confuses visitors and search engines',
            'fix': 'Use single H1 that clearly states value proposition, then H2s for supporting points'
        })
    
    return recommendations[:5]  # Return top 5


def calculate_cro_score(analysis):
    """Calculate overall CRO score out of 100"""
    score = 100
    
    # Deductions
    if analysis['cta_analysis']['total_ctas'] == 0:
        score -= 30
    elif analysis['cta_analysis']['total_ctas'] > 5:
        score -= 10
    
    if analysis['form_analysis']['form_count'] == 0:
        score -= 25
    elif analysis['form_analysis']['forms_analyzed']:
        avg_fields = sum(f['field_count'] for f in analysis['form_analysis']['forms_analyzed']) / len(analysis['form_analysis']['forms_analyzed'])
        if avg_fields > 7:
            score -= 15
    
    if sum(analysis['trust_signals'].values() if isinstance(analysis['trust_signals'], dict) else [0]) == 0:
        score -= 20
    
    if not analysis['media_elements']['has_video']:
        score -= 10
    
    if analysis['media_elements']['images_without_alt'] > 5:
        score -= 5
    
    return max(0, score)


if __name__ == '__main__':
    try:
        # Parse inputs from command line
        if len(sys.argv) > 1:
            inputs = json.loads(sys.argv[1])
        else:
            inputs = {}
        
        result = analyze_page_cro(inputs)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), file=sys.stderr)
        sys.exit(1)
