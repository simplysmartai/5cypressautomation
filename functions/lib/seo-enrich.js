/**
 * seo-enrich.js — OpenAI-powered SEO report enrichment
 * 
 * Takes raw DataForSEO audit data and returns expert-level analysis:
 * - Human-readable explanation of each finding
 * - Priority rating (Critical / Important / Nice-to-Have)
 * - Specific actionable fix recommendation
 * - AI-ready copy-paste prompt the user can give to ChatGPT/Claude
 * - Executive summary paragraph
 * - 90-day priority roadmap (3 phases)
 * 
 * Uses gpt-4o-mini with structured JSON output — cost ~$0.005–0.01 per report.
 */

export async function enrichReport(auditData, env) {
  const apiKey = env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not configured');

  const domain = auditData.domain || 'this website';

  // Build a compact summary of all findings to send to OpenAI
  const findings = buildFindingsSummary(auditData);

  const systemPrompt = `You are an expert SEO consultant and technical writer for 5 Cypress Automation, a B2B marketing automation agency. You write in clear, direct, non-jargon language for small business owners who are NOT SEO experts. When you write "AI Fix Prompts," they should be ready to paste directly into ChatGPT or Claude to get implementation help.`;

  const userPrompt = `Analyze these SEO audit findings for ${domain} and return a JSON object exactly matching this structure:

FINDINGS:
${JSON.stringify(findings, null, 2)}

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{
  "executive_summary": "2-3 sentence plain-English summary of the site's overall SEO health, biggest opportunity, and what to do first. Be specific, not generic.",
  "overall_grade": "A|B|C|D|F",
  "findings": [
    {
      "id": "unique_snake_case_id",
      "category": "On-Page|Speed|Keywords|Backlinks|Technical|Accessibility",
      "check": "Name of the check (e.g. 'Meta Description')",
      "status": "Pass|Warning|Fail",
      "value": "What was found (e.g. '152 chars' or 'Missing')",
      "expert_explanation": "2-3 sentences explaining WHY this matters in plain English. What impact does this have on rankings or traffic? Avoid jargon.",
      "priority": "Critical|Important|Nice-to-Have",
      "fix_recommendation": "Specific step-by-step fix. Be concrete, not vague. If code is needed, say what kind.",
      "ai_prompt": "A complete, ready-to-use prompt the user can paste into ChatGPT or Claude to implement this fix. Include relevant context from the audit (their actual values, domain, etc). Start with 'I need help with...'"
    }
  ],
  "quick_wins": ["Top 3 highest-impact, lowest-effort fixes as plain sentences. These should be doable in under 1 hour without a developer."],
  "roadmap": {
    "phase1": {
      "label": "Weeks 1–4: Fix Critical Issues",
      "focus": "1 sentence describing this phase's goal",
      "tasks": ["3–4 specific tasks for this phase"]
    },
    "phase2": {
      "label": "Weeks 5–8: Optimize Content & Structure",
      "focus": "1 sentence describing this phase's goal",
      "tasks": ["3–4 specific tasks for this phase"]
    },
    "phase3": {
      "label": "Weeks 9–12: Build Authority",
      "focus": "1 sentence describing this phase's goal",
      "tasks": ["3–4 specific tasks for this phase"]
    }
  },
  "keyword_strategy": "2-3 sentences on keyword opportunities — what they rank for now, what gaps exist, what to target next. Based on the keyword data provided.",
  "backlink_insight": "2-3 sentences on the backlink profile health — domain authority, referring domains, and what acquiring more links would do for rankings."
}

For any section with no data available (e.g. keywords were not scanned), write "Keyword data was not included in this scan. Run a full audit with keywords selected for this insight."

Focus findings ONLY on items with status Warning or Fail. Skip Pass items entirely.`;

  let response;
  try {
    response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        temperature: 0.3,
        max_tokens: 4000,
        response_format: { type: 'json_object' },
      }),
    });
  } catch (e) {
    throw new Error(`OpenAI fetch failed: ${e.message}`);
  }

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`OpenAI API error ${response.status}: ${errText}`);
  }

  const json = await response.json();
  const content = json.choices?.[0]?.message?.content;
  if (!content) throw new Error('OpenAI returned no content');

  let enriched;
  try {
    enriched = JSON.parse(content);
  } catch (e) {
    throw new Error(`OpenAI returned invalid JSON: ${content.slice(0, 200)}`);
  }

  return {
    ...enriched,
    raw_audit: auditData,
    enriched_at: new Date().toISOString(),
    model_used: 'gpt-4o-mini',
  };
}

/** Build a compact findings summary from the raw audit data shape */
function buildFindingsSummary(data) {
  const findings = [];

  // On-page rows (array of [check, value, status])
  if (Array.isArray(data.full_report?.on_page)) {
    for (const row of data.full_report.on_page) {
      if (row[2] && row[2] !== 'Pass') {
        findings.push({ category: 'On-Page', check: row[0], value: row[1], status: row[2] });
      }
    }
  }

  // Technical rows
  if (Array.isArray(data.full_report?.technical)) {
    for (const row of data.full_report.technical) {
      if (Array.isArray(row) && row[1] && row[1] !== 'Pass') {
        findings.push({ category: 'Technical', check: row[0], value: row[1], status: row[2] || 'Warning' });
      }
    }
  }

  // Page speed issues
  if (data.page_speed) {
    const ps = data.page_speed;
    const scores = ps.scores || {};
    if (scores.performance !== undefined && scores.performance < 90) {
      findings.push({ category: 'Speed', check: 'Performance Score', value: `${scores.performance}/100`, status: scores.performance < 50 ? 'Fail' : 'Warning' });
    }
    if (scores.seo !== undefined && scores.seo < 90) {
      findings.push({ category: 'Speed', check: 'Lighthouse SEO Score', value: `${scores.seo}/100`, status: scores.seo < 70 ? 'Fail' : 'Warning' });
    }
    if (scores.accessibility !== undefined && scores.accessibility < 90) {
      findings.push({ category: 'Accessibility', check: 'Accessibility Score', value: `${scores.accessibility}/100`, status: scores.accessibility < 70 ? 'Fail' : 'Warning' });
    }
    const vitals = ps.metrics || {};
    if (vitals.LCP && vitals.LCP !== 'N/A') findings.push({ category: 'Speed', check: 'Largest Contentful Paint (LCP)', value: vitals.LCP, status: 'Info' });
    if (vitals.CLS && vitals.CLS !== 'N/A') findings.push({ category: 'Speed', check: 'Cumulative Layout Shift (CLS)', value: vitals.CLS, status: 'Info' });
    if (vitals.TTFB && vitals.TTFB !== 'N/A') findings.push({ category: 'Speed', check: 'Time to First Byte (TTFB)', value: vitals.TTFB, status: 'Info' });

    // Speed opportunities
    if (Array.isArray(ps.opportunities)) {
      for (const opp of ps.opportunities.slice(0, 3)) {
        findings.push({ category: 'Speed', check: opp.title, value: opp.savings || 'Improvement available', status: 'Warning', description: opp.description });
      }
    }
  }

  // Keywords
  if (Array.isArray(data.keywords) && data.keywords.length > 0) {
    findings.push({ category: 'Keywords', check: 'Ranked Keywords', value: `${data.keywords.length} keywords tracked`, status: 'Info', keywords: data.keywords.slice(0, 5) });
  }

  // Backlinks
  if (data.backlinks && typeof data.backlinks === 'object') {
    const bl = data.backlinks;
    findings.push({ category: 'Backlinks', check: 'Backlink Profile', value: `${bl.total || 0} total from ${bl.referring_domains || 0} domains, rank ${bl.rank || 0}`, status: (bl.rank || 0) < 20 ? 'Warning' : 'Info' });
    if (bl.spam_score && bl.spam_score > 30) {
      findings.push({ category: 'Backlinks', check: 'Spam Score', value: `${bl.spam_score}/100`, status: 'Warning' });
    }
  }

  // Add overall context
  findings.push({ category: 'Summary', check: 'Overall SEO Score', value: `${data.score || 0}/100`, status: (data.score || 0) > 80 ? 'Pass' : (data.score || 0) > 60 ? 'Warning' : 'Fail' });

  return findings;
}
