#!/usr/bin/env python3
"""
Email Sequence Builder
Generates automated email sequences for onboarding, nurture, sales, or re-engagement
"""
import json
import sys
import os
from datetime import datetime

def build_email_sequence(inputs):
    """Build an email sequence based on inputs"""
    sequence_type = inputs.get('sequence_type', 'Welcome/Onboarding')
    num_emails = int(inputs.get('num_emails', 5))
    product_description = inputs.get('product_description', 'your product or service')
    
    # Email templates based on sequence type
    templates = {
        'Welcome/Onboarding': {
            'goal': 'Get new users activated and using core features',
            'cadence': [0, 1, 3, 7, 14],  # Days after signup
            'emails': [
                {
                    'day': 0,
                    'subject': 'Welcome to {product} 🎉',
                    'theme': 'Welcome + Quick Win',
                    'key_points': [
                        'Personal welcome from founder/team',
                        'What to expect in first 7 days',
                        'One quick action to get value immediately',
                        'Link to getting started guide'
                    ]
                },
                {
                    'day': 1,
                    'subject': 'Your first win with {product}',
                    'theme': 'Feature Education',
                    'key_points': [
                        'Highlight one core feature',
                        '2-3 minute tutorial or video',
                        'Real customer success story',
                        'CTA: Try the feature now'
                    ]
                },
                {
                    'day': 3,
                    'subject': 'Are you stuck? Here\'s help',
                    'theme': 'Support + Resources',
                    'key_points': [
                        'Common questions answered',
                        'Link to live chat or support',
                        'FAQ or knowledge base',
                        'Community or forum invitation'
                    ]
                },
                {
                    'day': 7,
                    'subject': 'You\'re doing great! What\'s next?',
                    'theme': 'Advanced Features',
                    'key_points': [
                        'Celebrate progress/usage',
                        'Introduce next-level features',
                        'Case study or power user tip',
                        'Upgrade path for free users'
                    ]
                },
                {
                    'day': 14,
                    'subject': 'How can we make {product} better for you?',
                    'theme': 'Feedback + Engagement',
                    'key_points': [
                        'Ask for feedback (survey)',
                        'Product roadmap preview',
                        'Referral program introduction',
                        'Personal check-in from team'
                    ]
                }
            ]
        },
        'Nurture': {
            'goal': 'Build trust and move leads toward purchase',
            'cadence': [0, 2, 5, 9, 14],
            'emails': [
                {
                    'day': 0,
                    'subject': 'Thanks for your interest in {product}',
                    'theme': 'Value Proposition',
                    'key_points': [
                        'Confirm download/signup',
                        'Core benefit statement',
                        'Social proof (testimonial or stat)',
                        'Next step: resource or guide'
                    ]
                },
                {
                    'day': 2,
                    'subject': 'How {product} solves [pain point]',
                    'theme': 'Problem Awareness',
                    'key_points': [
                        'Identify specific pain point',
                        'Show traditional approaches (and why they fail)',
                        'Introduce your solution',
                        'CTA: Learn more or watch demo'
                    ]
                },
                {
                    'day': 5,
                    'subject': '[Customer] saved [result] with {product}',
                    'theme': 'Social Proof',
                    'key_points': [
                        'Detailed case study',
                        'Before/after metrics',
                        'Customer quote or video',
                        'CTA: See similar results'
                    ]
                },
                {
                    'day': 9,
                    'subject': 'The complete guide to [outcome]',
                    'theme': 'Education',
                    'key_points': [
                        'High-value educational content',
                        'Subtly position your product',
                        'Actionable tips they can use now',
                        'CTA: Get started with {product}'
                    ]
                },
                {
                    'day': 14,
                    'subject': 'Ready to [achieve goal]?',
                    'theme': 'Soft CTA',
                    'key_points': [
                        'Recap journey so far',
                        'Clear next step (demo, trial, call)',
                        'Risk reversal (guarantee, free trial)',
                        'Urgency element if appropriate'
                    ]
                }
            ]
        },
        'Sales': {
            'goal': 'Move qualified leads to close',
            'cadence': [0, 1, 3, 5, 7],
            'emails': [
                {
                    'day': 0,
                    'subject': 'Let\'s discuss how {product} fits your needs',
                    'theme': 'Personalized Outreach',
                    'key_points': [
                        'Reference specific pain point or trigger',
                        'Quick value hypothesis',
                        'Relevant case study',
                        'CTA: Book 15-min call'
                    ]
                },
                {
                    'day': 1,
                    'subject': '[Competitor] vs {product}: The honest comparison',
                    'theme': 'Competitive Positioning',
                    'key_points': [
                        'Acknowledge alternatives',
                        'Feature comparison matrix',
                        'Unique differentiators',
                        'CTA: See for yourself (demo)'
                    ]
                },
                {
                    'day': 3,
                    'subject': 'Quick question about [their goal]',
                    'theme': 'Qualification',
                    'key_points': [
                        'Ask about specific challenge',
                        'Reference their industry or use case',
                        'Share relevant insight or data',
                        'CTA: Reply with answer'
                    ]
                },
                {
                    'day': 5,
                    'subject': 'ROI Calculator: See your potential return',
                    'theme': 'Value Justification',
                    'key_points': [
                        'Personalized ROI estimate',
                        'Implementation timeline',
                        'Risk mitigation plan',
                        'CTA: Discuss your numbers'
                    ]
                },
                {
                    'day': 7,
                    'subject': 'Should I close your file?',
                    'theme': 'Breakup',
                    'key_points': [
                        'Acknowledge no response',
                        'Ask if timing is wrong',
                        'Offer different next step',
                        'Easy opt-out'
                    ]
                }
            ]
        },
        'Re-engagement': {
            'goal': 'Win back inactive users or customers',
            'cadence': [0, 3, 7, 14, 30],
            'emails': [
                {
                    'day': 0,
                    'subject': 'We miss you at {product}',
                    'theme': 'Friendly Check-In',
                    'key_points': [
                        'Acknowledge absence',
                        'What\'s new since they left',
                        'Ask what went wrong (survey)',
                        'Easy path back'
                    ]
                },
                {
                    'day': 3,
                    'subject': 'What we\'ve improved based on your feedback',
                    'theme': 'Product Updates',
                    'key_points': [
                        'Major improvements or new features',
                        'User-requested changes',
                        'Easier/faster experience',
                        'CTA: See what\'s new'
                    ]
                },
                {
                    'day': 7,
                    'subject': 'Exclusive offer: Come back to {product}',
                    'theme': 'Incentive',
                    'key_points': [
                        'Special discount or bonus',
                        'Limited time urgency',
                        'No-strings-attached trial',
                        'What they\'ll get'
                    ]
                },
                {
                    'day': 14,
                    'subject': 'Can we win you back?',
                    'theme': 'Last Attempt',
                    'key_points': [
                        'Personal note from founder',
                        'Best offer possible',
                        'Direct line to support',
                        'Honest ask for feedback'
                    ]
                },
                {
                    'day': 30,
                    'subject': 'Goodbye from {product}',
                    'theme': 'Graceful Exit',
                    'key_points': [
                        'Confirm they\'re unsubscribed',
                        'Leave door open for future',
                        'Ask for feedback (optional)',
                        'Wish them well'
                    ]
                }
            ]
        },
        'Post-Purchase': {
            'goal': 'Ensure success, reduce churn, get referrals',
            'cadence': [0, 1, 7, 30, 90],
            'emails': [
                {
                    'day': 0,
                    'subject': 'Thank you for choosing {product}!',
                    'theme': 'Confirmation + Next Steps',
                    'key_points': [
                        'Order confirmation',
                        'What happens next',
                        'Getting started checklist',
                        'Support contact info'
                    ]
                },
                {
                    'day': 1,
                    'subject': 'Your {product} setup guide',
                    'theme': 'Onboarding',
                    'key_points': [
                        'Step-by-step setup',
                        'Video walkthrough',
                        'Tips for first week',
                        'Schedule training call'
                    ]
                },
                {
                    'day': 7,
                    'subject': 'How\'s your experience so far?',
                    'theme': 'Early Check-In',
                    'key_points': [
                        'Request feedback',
                        'Common early questions',
                        'Advanced features preview',
                        'Support resources'
                    ]
                },
                {
                    'day': 30,
                    'subject': 'Get more out of {product}',
                    'theme': 'Expansion',
                    'key_points': [
                        'Usage stats or achievements',
                        'Advanced features/integrations',
                        'Upgrade opportunities',
                        'Community or events'
                    ]
                },
                {
                    'day': 90,
                    'subject': 'Love {product}? Share the love',
                    'theme': 'Advocacy',
                    'key_points': [
                        'Results or success metrics',
                        'Request review/testimonial',
                        'Referral program details',
                        'Exclusive advocate perks'
                    ]
                }
            ]
        }
    }
    
    # Get template for sequence type
    template = templates.get(sequence_type, templates['Welcome/Onboarding'])
    
    # Trim to requested number of emails
    emails = template['emails'][:num_emails]
    
    # Format output
    sequence = {
        'sequence_type': sequence_type,
        'goal': template['goal'],
        'total_emails': len(emails),
        'duration_days': template['cadence'][len(emails)-1] if len(emails) > 0 else 0,
        'product_context': product_description,
        'emails': emails,
        'implementation_tips': [
            'Personalize subject lines with recipient name or company',
            'A/B test different subject lines and CTAs',
            'Set up tracking links for engagement metrics',
            'Monitor open rates and adjust timing if needed',
            'Add unsubscribe link in footer of every email',
            'Use marketing automation tool for scheduled sends',
            'Segment audience based on behavior and engagement'
        ],
        'metrics_to_track': [
            'Open rate (aim for 20-35%)',
            'Click-through rate (aim for 2-5%)',
            'Conversion rate to desired action',
            'Unsubscribe rate (keep below 0.5%)',
            'Time to conversion',
            'Reply rate (for sales sequences)'
        ]
    }
    
    return {
        'success': True,
        'sequence': sequence,
        'timestamp': datetime.now().isoformat(),
        'summary': f"Generated {len(emails)}-email {sequence_type} sequence over {sequence['duration_days']} days"
    }


if __name__ == '__main__':
    try:
        # Parse inputs from command line
        if len(sys.argv) > 1:
            inputs = json.loads(sys.argv[1])
        else:
            inputs = {}
        
        result = build_email_sequence(inputs)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), file=sys.stderr)
        sys.exit(1)
