/**
 * GET /api/skills
 * Return list of all available skills
 */
export async function onRequestGet(context) {
  try {
    // Load skills from KV storage or return default list
    const skillsJson = await context.env.CLIENTS_KV?.get('skills_list', 'json');
    
    if (skillsJson) {
      return new Response(JSON.stringify(skillsJson), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Fallback to hardcoded skill list if KV not available
    const skills = [
      {
        "id": "email-sequence",
        "name": "Email Sequence Builder",
        "category": "Email Marketing",
        "description": "Generate 5-email marketing sequences (Welcome, Nurture, Sales, Re-engagement, Post-purchase) with copywriting, timing, and subject lines",
        "inputs": [
          {
            "name": "sequence_type",
            "label": "Sequence Type",
            "type": "select",
            "options": ["Welcome", "Nurture", "Sales", "Re-engagement", "Post-purchase"],
            "required": true,
            "default": "Welcome"
          },
          {
            "name": "num_emails",
            "label": "Number of Emails",
            "type": "number",
            "required": true,
            "default": 5,
            "min": 1,
            "max": 10
          }
        ],
        "tags": ["email", "marketing", "copywriting"],
        "icon": "📧"
      },
      {
        "id": "page-cro",
        "name": "Page CRO Analyzer",
        "category": "Conversion Optimization",
        "description": "Analyze landing pages for conversion rate optimization opportunities. Scores trust signals, CTAs, forms, and engagement elements.",
        "inputs": [
          {
            "name": "url",
            "label": "Page URL",
            "type": "text",
            "required": true,
            "placeholder": "https://example.com/landing"
          },
          {
            "name": "analysis_depth",
            "label": "Analysis Depth",
            "type": "select",
            "options": ["quick", "standard", "deep"],
            "required": true,
            "default": "standard"
          }
        ],
        "tags": ["conversion", "optimization", "cro"],
        "icon": "📈"
      },
      {
        "id": "amazon-product-scraper",
        "name": "Amazon Product Scraper",
        "category": "Data Collection",
        "description": "Scrape product data from Amazon: ASIN, title, price, rating, reviews, availability, and seller information.",
        "inputs": [
          {
            "name": "asin",
            "label": "Product ASIN",
            "type": "text",
            "required": true,
            "placeholder": "B0C3XYQMYY"
          }
        ],
        "tags": ["amazon", "scraping", "ecommerce"],
        "icon": "📦"
      },
      {
        "id": "google-serp-scraper",
        "name": "Google SERP Scraper",
        "category": "Data Collection",
        "description": "Scrape Google search results for a keyword. Returns organic results, ads, featured snippets, and SERP features.",
        "inputs": [
          {
            "name": "keyword",
            "label": "Search Keyword",
            "type": "text",
            "required": true,
            "placeholder": "best email marketing software"
          },
          {
            "name": "num_results",
            "label": "Number of Results",
            "type": "number",
            "required": true,
            "default": 10,
            "min": 1,
            "max": 100
          }
        ],
        "tags": ["seo", "scraping", "serp"],
        "icon": "🔍"
      },
      {
        "id": "seo-audit",
        "name": "SEO Audit Tool",
        "category": "SEO",
        "description": "Comprehensive SEO audit: meta tags, H1/H2 structure, page speed, mobile-friendliness, schema markup.",
        "inputs": [
          {
            "name": "url",
            "label": "Website URL",
            "type": "text",
            "required": true,
            "placeholder": "https://example.com"
          },
          {
            "name": "audit_type",
            "label": "Audit Type",
            "type": "select",
            "options": ["technical", "on-page", "content", "full"],
            "required": true,
            "default": "full"
          }
        ],
        "tags": ["seo", "audit", "technical"],
        "icon": "🔍"
      },
      {
        "id": "copywriting-generator",
        "name": "Copywriting Generator",
        "category": "Copywriting",
        "description": "Generate high-converting sales copy for landing pages, ads, emails using psychological principles.",
        "inputs": [
          {
            "name": "copy_type",
            "label": "Copy Type",
            "type": "select",
            "options": ["headline", "subheading", "body", "cta"],
            "required": true,
            "default": "headline"
          },
          {
            "name": "product_description",
            "label": "Product Description",
            "type": "textarea",
            "required": true,
            "placeholder": "Describe what you're selling..."
          }
        ],
        "tags": ["copywriting", "marketing", "sales"],
        "icon": "✍️"
      },
      {
        "id": "competitor-analysis",
        "name": "Competitor Analysis",
        "category": "Market Research",
        "description": "Analyze competitors: pricing, features, messaging, traffic sources, and market positioning.",
        "inputs": [
          {
            "name": "competitor_url",
            "label": "Competitor URL",
            "type": "text",
            "required": true,
            "placeholder": "https://competitor.com"
          }
        ],
        "tags": ["competitive", "research"],
        "icon": "🎯"
      },
      {
        "id": "pricing-strategy",
        "name": "Pricing Strategy Generator",
        "category": "Business",
        "description": "Generate optimal pricing tiers based on customer segments and market positioning.",
        "inputs": [
          {
            "name": "product_type",
            "label": "Product Type",
            "type": "select",
            "options": ["saas", "marketplace", "physical", "service"],
            "required": true,
            "default": "saas"
          }
        ],
        "tags": ["pricing", "business", "strategy"],
        "icon": "💰"
      },
      {
        "id": "content-calendar",
        "name": "Content Calendar Builder",
        "category": "Content",
        "description": "Generate a 30/60/90-day content calendar with topics, formats, and publishing schedule.",
        "inputs": [
          {
            "name": "industry",
            "label": "Industry",
            "type": "text",
            "required": true,
            "placeholder": "e.g., SaaS marketing"
          }
        ],
        "tags": ["content", "marketing", "planning"],
        "icon": "📅"
      },
      {
        "id": "social-media-strategy",
        "name": "Social Media Content Generator",
        "category": "Social Media",
        "description": "Generate platform-specific content for LinkedIn, Twitter, Instagram, TikTok with hashtags and timing.",
        "inputs": [
          {
            "name": "platform",
            "label": "Platform",
            "type": "select",
            "options": ["LinkedIn", "Twitter", "Instagram", "TikTok"],
            "required": true,
            "default": "LinkedIn"
          },
          {
            "name": "topic",
            "label": "Topic",
            "type": "text",
            "required": true
          }
        ],
        "tags": ["social", "marketing", "content"],
        "icon": "📱"
      },
      {
        "id": "lead-scoring",
        "name": "Lead Scoring Model",
        "category": "Sales",
        "description": "Create lead scoring based on firmographics, behavior, and engagement metrics.",
        "inputs": [
          {
            "name": "ideal_customer_profile",
            "label": "Ideal Customer Profile",
            "type": "textarea",
            "required": true
          }
        ],
        "tags": ["sales", "leads", "scoring"],
        "icon": "📊"
      },
      {
        "id": "customer-journey",
        "name": "Customer Journey Mapper",
        "category": "Product",
        "description": "Map customer journey: awareness, consideration, decision, retention with touchpoints and pain points.",
        "inputs": [
          {
            "name": "product_type",
            "label": "Product Type",
            "type": "text",
            "required": true
          }
        ],
        "tags": ["product", "customer", "journey"],
        "icon": "🗺️"
      },
      {
        "id": "ab-test-design",
        "name": "A/B Test Designer",
        "category": "Conversion Optimization",
        "description": "Design A/B tests with hypothesis, metrics, sample size, and statistical significance.",
        "inputs": [
          {
            "name": "test_element",
            "label": "Element to Test",
            "type": "text",
            "required": true
          }
        ],
        "tags": ["testing", "optimization", "cro"],
        "icon": "🧪"
      },
      {
        "id": "roi-calculator",
        "name": "ROI Calculator",
        "category": "Sales",
        "description": "Calculate ROI: money saved, time saved, payback period, and NPV analysis.",
        "inputs": [
          {
            "name": "initial_investment",
            "label": "Initial Investment ($)",
            "type": "number",
            "required": true,
            "default": 5000
          },
          {
            "name": "monthly_benefit",
            "label": "Monthly Benefit ($)",
            "type": "number",
            "required": true,
            "default": 1000
          }
        ],
        "tags": ["sales", "roi", "analytics"],
        "icon": "💡"
      }
    ];

    return new Response(JSON.stringify(skills), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Skills API error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Failed to load skills'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
