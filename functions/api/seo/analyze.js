// POST /api/seo/analyze — live SEO audit via DataForSEO + Google PageSpeed
// Free tier: on_page + speed
// Admin/premium tier: all 6 modules

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Content-Type': 'application/json',
};

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;

  // Check if admin (Basic Auth)
  let isAdmin = false;
  const authHeader = request.headers.get('Authorization') || '';
  if (authHeader.startsWith('Basic ')) {
    try {
      const [user, pass] = atob(authHeader.slice(6)).split(':');
      if (user === env.ADMIN_USER && pass === env.ADMIN_PASS) isAdmin = true;
    } catch {}
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return err('Invalid JSON body', 400);
  }

  const { website_url, modules = [], keywords = [], competitors = [], tier = 'free' } = body;
  if (!website_url) return err('website_url is required', 400);

  let targetUrl;
  try {
    targetUrl = new URL(website_url.startsWith('http') ? website_url : `https://${website_url}`);
  } catch {
    return err('Invalid URL', 400);
  }

  const isPremium = isAdmin || tier === 'premium';
  const domain = targetUrl.hostname;
  const href = targetUrl.href;

  // Run modules in parallel — failures are caught per-module, never fatal
  const [pagespeed, onpage, kwData, blData, compData, serpData] = await Promise.all([
    safeRun(() => runPageSpeed(href, env)),
    safeRun(() => runOnPage(href, env)),
    isPremium ? safeRun(() => runKeywords(domain, keywords, env)) : null,
    isPremium ? safeRun(() => runBacklinks(domain, env)) : null,
    isPremium ? safeRun(() => runCompetitors(domain, env)) : null,
    isPremium ? safeRun(() => runRankings(domain, keywords, env)) : null,
  ]);

  // Build data in the shape seo-dashboard.html and admin/seo.html both expect
  const scores = pagespeed?.scores || {};
  const vitals = pagespeed?.vitals || {};
  const overallScore = computeOverall(scores);

  const data = {
    status: 'success',
    score: overallScore,
    domain,
    is_sample: false,
    full_report: {
      recap: buildRecap(domain, onpage, pagespeed, isPremium),
      on_page: buildOnPageRows(onpage),
      technical: buildTechnicalRows(onpage, targetUrl),
    },
    page_speed: {
      scores,
      metrics: {
        LCP:  vitals.lcp  || 'N/A',
        TTFB: vitals.ttfb || 'N/A',
        CLS:  vitals.cls  || 'N/A',
        FID:  vitals.fcp  || 'N/A',
        TBT:  vitals.tbt  || 'N/A',
        SI:   vitals.si   || 'N/A',
      },
      opportunities: pagespeed?.opportunities || [],
    },
    keywords:    kwData    ? formatKeywords(kwData)    : [],
    backlinks:   blData    ? formatBacklinks(blData)   : null,
    competitors: compData  ? formatCompetitors(compData) : [],
    serp:        serpData  ? serpData.rankings         : [],
    improvements: buildImprovements(onpage, pagespeed, blData),
  };

  return new Response(JSON.stringify({ status: 'success', data }), {
    status: 200,
    headers: CORS,
  });
}

// ── PageSpeed (Google) ────────────────────────────────────────────────────────
async function runPageSpeed(url, env) {
  const key = env.GOOGLE_PAGESPEED_API_KEY;
  if (!key) throw new Error('GOOGLE_PAGESPEED_API_KEY not configured');

  const endpoint = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`
    + `?url=${encodeURIComponent(url)}&strategy=mobile&key=${key}`;

  const res = await fetch(endpoint, { cf: { cacheTtl: 300 } });
  if (!res.ok) throw new Error(`PageSpeed HTTP ${res.status}`);
  const json = await res.json();

  const cats   = json.lighthouseResult?.categories || {};
  const audits = json.lighthouseResult?.audits     || {};

  return {
    scores: {
      performance:   Math.round((cats.performance?.score   || 0) * 100),
      accessibility: Math.round((cats.accessibility?.score || 0) * 100),
      bestPractices: Math.round((cats['best-practices']?.score || 0) * 100),
      seo:           Math.round((cats.seo?.score           || 0) * 100),
    },
    vitals: {
      lcp:  audits['largest-contentful-paint']?.displayValue || 'N/A',
      cls:  audits['cumulative-layout-shift']?.displayValue  || 'N/A',
      ttfb: audits['server-response-time']?.displayValue     || 'N/A',
      fcp:  audits['first-contentful-paint']?.displayValue   || 'N/A',
      tbt:  audits['total-blocking-time']?.displayValue      || 'N/A',
      si:   audits['speed-index']?.displayValue              || 'N/A',
    },
    opportunities: Object.values(audits)
      .filter(a => a.details?.type === 'opportunity' && (a.score ?? 1) < 0.9)
      .slice(0, 5)
      .map(a => ({
        title:       a.title,
        description: a.description,
        savings: a.details?.overallSavingsMs
          ? `${Math.round(a.details.overallSavingsMs)}ms faster`
          : null,
      })),
  };
}

// ── On-Page SEO (DataForSEO) ──────────────────────────────────────────────────
async function runOnPage(url, env) {
  const auth = dfsAuth(env);
  const res = await fetch(
    'https://api.dataforseo.com/v3/on_page/instant_pages',
    {
      method: 'POST',
      headers: { Authorization: auth, 'Content-Type': 'application/json' },
      body: JSON.stringify([{ url, enable_javascript: false, load_resources: false }]),
    }
  );
  if (!res.ok) throw new Error(`DataForSEO On-Page HTTP ${res.status}`);
  const json = await res.json();

  const item  = json?.tasks?.[0]?.result?.[0]?.items?.[0] || {};
  const meta  = item.meta  || {};
  const stats = item.statistics || {};
  const htags = meta.htags || {};

  return {
    title:            meta.title || '',
    description:      meta.description || '',
    h1:               htags.h1?.[0]  || '',
    h1Count:          htags.h1?.length || 0,
    h2Count:          htags.h2?.length || 0,
    wordCount:        meta.content?.plain_text_word_count || 0,
    internalLinks:    stats.links_internal  || 0,
    externalLinks:    stats.links_external  || 0,
    imagesTotal:      stats.images_count    || 0,
    imagesMissingAlt: stats.images_without_alt_count || 0,
    canonical:        meta.canonical || '',
    robots:           meta.robots   || '',
    hasSchema:        (meta.structured_data || []).length > 0,
    charset:          meta.charset || '',
  };
}

// ── Keywords ──────────────────────────────────────────────────────────────────
async function runKeywords(domain, keywords, env) {
  const auth = dfsAuth(env);
  const res = await fetch(
    'https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live',
    {
      method: 'POST',
      headers: { Authorization: auth, 'Content-Type': 'application/json' },
      body: JSON.stringify([{
        target: domain,
        language_code: 'en',
        location_code: 2840,
        limit: 20,
        order_by: ['keyword_data.keyword_info.search_volume,desc'],
      }]),
    }
  );
  if (!res.ok) throw new Error(`DataForSEO Keywords HTTP ${res.status}`);
  const json = await res.json();
  const result = json?.tasks?.[0]?.result?.[0] || {};
  return { total: result.total_count || 0, items: result.items || [] };
}

// ── Backlinks ─────────────────────────────────────────────────────────────────
async function runBacklinks(domain, env) {
  const auth = dfsAuth(env);
  const res = await fetch(
    'https://api.dataforseo.com/v3/backlinks/summary/live',
    {
      method: 'POST',
      headers: { Authorization: auth, 'Content-Type': 'application/json' },
      body: JSON.stringify([{ target: domain }]),
    }
  );
  if (!res.ok) throw new Error(`DataForSEO Backlinks HTTP ${res.status}`);
  const json = await res.json();
  return json?.tasks?.[0]?.result?.[0] || {};
}

// ── Competitors ───────────────────────────────────────────────────────────────
async function runCompetitors(domain, env) {
  const auth = dfsAuth(env);
  const res = await fetch(
    'https://api.dataforseo.com/v3/dataforseo_labs/google/competitors_domain/live',
    {
      method: 'POST',
      headers: { Authorization: auth, 'Content-Type': 'application/json' },
      body: JSON.stringify([{
        target: domain,
        language_code: 'en',
        location_code: 2840,
        limit: 8,
      }]),
    }
  );
  if (!res.ok) throw new Error(`DataForSEO Competitors HTTP ${res.status}`);
  const json = await res.json();
  return { items: json?.tasks?.[0]?.result?.[0]?.items || [] };
}

// ── SERP / Rankings ───────────────────────────────────────────────────────────
async function runRankings(domain, keywords, env) {
  if (!keywords.length) return { rankings: [] };
  const auth = dfsAuth(env);
  const res = await fetch(
    'https://api.dataforseo.com/v3/serp/google/organic/live/regular',
    {
      method: 'POST',
      headers: { Authorization: auth, 'Content-Type': 'application/json' },
      body: JSON.stringify(
        keywords.slice(0, 5).map(kw => ({
          keyword: kw,
          language_code: 'en',
          location_code: 2840,
          depth: 20,
        }))
      ),
    }
  );
  if (!res.ok) throw new Error(`DataForSEO SERP HTTP ${res.status}`);
  const json = await res.json();

  return {
    rankings: (json?.tasks || []).map(task => {
      const items = task?.result?.[0]?.items || [];
      const mine  = items.find(i => i.url?.includes(domain));
      return {
        keyword:    task?.data?.keyword,
        myPosition: mine?.rank_absolute || null,
        myUrl:      mine?.url || null,
        top3: items.slice(0, 3).map(i => ({ url: i.url, position: i.rank_absolute })),
      };
    }),
  };
}

// ── Data Formatters ───────────────────────────────────────────────────────────
function formatKeywords(raw) {
  return (raw.items || []).slice(0, 15).map(k => ({
    keyword: k.keyword_data?.keyword,
    volume:  fmtNum(k.keyword_data?.keyword_info?.search_volume),
    rank:    `#${k.ranked_serp_element?.serp_item?.rank_absolute || '?'}`,
    difficulty: k.keyword_data?.keyword_properties?.keyword_difficulty,
    cpc:    k.keyword_data?.keyword_info?.cpc,
  }));
}

function formatBacklinks(raw) {
  return {
    total:             raw.total_count        || 0,
    referring_domains: raw.referring_domains  || 0,
    rank:              raw.rank               || 0,
    spam_score:        raw.spam_score         || 0,
    new_backlinks:     raw.new_backlinks_count || 0,
    lost_backlinks:    raw.lost_backlinks_count || 0,
  };
}

function formatCompetitors(raw) {
  return (raw.items || []).map(c => ({
    domain:          c.domain,
    relevance:       Math.round((c.competitor_relevance || 0) * 100),
    sharedKeywords:  c.intersections || 0,
    organicKeywords: c.metrics?.organic?.count || 0,
  }));
}

function buildOnPageRows(op) {
  if (!op) return [];
  const tLen  = (op.title || '').length;
  const dLen  = (op.description || '').length;
  const rows  = [
    ['Title Tag',        `${op.title ? op.title.slice(0, 50) + (op.title.length > 50 ? '…' : '') : 'Not found'} (${tLen} chars)`,
                         tLen === 0 ? 'Fail' : tLen < 30 || tLen > 60 ? 'Warning' : 'Pass'],
    ['Meta Description', `${op.description ? op.description.slice(0, 60) + '…' : 'Not found'} (${dLen} chars)`,
                         dLen === 0 ? 'Fail' : dLen < 120 || dLen > 160 ? 'Warning' : 'Pass'],
    ['H1 Tag',           `${op.h1Count} found${op.h1 ? ` — "${op.h1.slice(0, 40)}"` : ''}`,
                         op.h1Count === 0 ? 'Fail' : op.h1Count > 1 ? 'Warning' : 'Pass'],
    ['H2 Structure',     `${op.h2Count} headings`, op.h2Count > 0 ? 'Pass' : 'Warning'],
    ['Word Count',       `${op.wordCount.toLocaleString()} words`, op.wordCount >= 500 ? 'Pass' : 'Warning'],
    ['Image Alt Text',   `${op.imagesMissingAlt} of ${op.imagesTotal} missing`,
                         op.imagesMissingAlt === 0 ? 'Pass' : op.imagesMissingAlt <= 3 ? 'Warning' : 'Fail'],
    ['Internal Links',   `${op.internalLinks} found`, op.internalLinks >= 3 ? 'Pass' : 'Warning'],
    ['Canonical Tag',    op.canonical ? 'Present' : 'Not set', op.canonical ? 'Pass' : 'Warning'],
    ['Schema Markup',    op.hasSchema ? 'Detected' : 'None found', op.hasSchema ? 'Pass' : 'Warning'],
  ];
  return rows;
}

function buildTechnicalRows(op, url) {
  return [
    ['HTTPS',           url.protocol === 'https:' ? 'Pass' : 'Fail'],
    ['Robots Tag',      op?.robots || 'Not set'],
    ['Charset',         op?.charset || 'Not set'],
  ];
}

function buildImprovements(op, ps, bl) {
  const fixes = [];
  if (!op) return fixes;
  if (!op.description)            fixes.push('Add a meta description — currently missing (critical for CTR)');
  if (op.imagesMissingAlt > 0)    fixes.push(`Add alt text to ${op.imagesMissingAlt} image${op.imagesMissingAlt > 1 ? 's' : ''} — impacts accessibility & image SEO`);
  if (!op.hasSchema)              fixes.push('Add schema.org structured markup (Organization, WebPage, or Product)');
  if ((op.title || '').length > 60) fixes.push('Shorten title tag to under 60 characters to prevent truncation in search results');
  if (!op.description || op.description.length < 120) fixes.push('Write a meta description between 120–160 characters with a clear value proposition');
  if (ps?.scores?.performance < 70) fixes.push('Improve page performance score — compress images, eliminate render-blocking resources');
  if (ps?.vitals?.lcp && parseFloat(ps.vitals.lcp) > 2.5) fixes.push('Reduce Largest Contentful Paint (LCP) below 2.5s — optimize server response and image sizes');
  if (bl && bl.rank < 20)         fixes.push('Build more backlinks from industry publications — current domain rank is low');
  if (op.internalLinks < 3)       fixes.push('Add more internal links to distribute page authority and improve crawlability');
  return fixes.slice(0, 6);
}

function buildRecap(domain, op, ps, isPremium) {
  const parts = [];
  if (ps?.scores?.performance !== undefined) {
    const score = ps.scores.performance;
    parts.push(`Page performance score: ${score}/100 (${score >= 90 ? 'excellent' : score >= 50 ? 'needs improvement' : 'poor'}).`);
  }
  if (op) {
    const checks = [
      op.title        ? 'title tag ✓' : 'title tag ✗',
      op.description  ? 'meta description ✓' : 'meta description ✗',
      op.h1Count === 1 ? 'H1 ✓' : `H1 issues (${op.h1Count} found)`,
      op.hasSchema    ? 'schema markup ✓' : 'no schema markup',
    ];
    parts.push(`On-page status: ${checks.join(', ')}.`);
    if (op.imagesMissingAlt > 0) {
      parts.push(`${op.imagesMissingAlt} image${op.imagesMissingAlt > 1 ? 's are' : ' is'} missing alt text.`);
    }
  }
  if (!isPremium) {
    parts.push('Upgrade to Premium for keyword rankings, backlink profile, competitor analysis, and SERP position tracking.');
  }
  return parts.join(' ') || `Audit complete for ${domain}. See tabs for details.`;
}

function computeOverall(scores) {
  const vals = Object.values(scores).filter(v => typeof v === 'number');
  if (!vals.length) return 0;
  return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
}

function fmtNum(n) {
  if (!n) return '—';
  return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function dfsAuth(env) {
  if (!env.DATAFORSEO_USERNAME || !env.DATAFORSEO_PASSWORD) {
    throw new Error('DataForSEO credentials not configured — set DATAFORSEO_USERNAME and DATAFORSEO_PASSWORD in Cloudflare Pages secrets');
  }
  return `Basic ${btoa(`${env.DATAFORSEO_USERNAME}:${env.DATAFORSEO_PASSWORD}`)}`;
}

async function safeRun(fn) {
  try { return await fn(); } catch (e) { console.error('[seo/analyze]', e.message); return null; }
}

function err(msg, status = 400) {
  return new Response(JSON.stringify({ status: 'error', error: msg }), {
    status,
    headers: CORS,
  });
}
