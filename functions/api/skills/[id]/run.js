// Cloudflare Pages Function: /api/skills/:id/run
// Executes a skill by calling Modal webhook (with authentication & rate limiting)

export async function onRequestPost(context) {
  const { params, request, env } = context;
  const skillId = params.id;
  
  try {
    // Parse request body (contains form inputs + api_key)
    const body = await request.json();
    const { api_key, ...formInputs } = body;
    
    // Check for API key
    if (!api_key) {
      return new Response(JSON.stringify({
        success: false,
        error: 'API key required',
        tip: 'Please login to get your API key',
        auth_required: true
      }), {
        status: 401,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    // Verify API key and get client info
    const clientsResponse = await fetch(new URL('/config/clients.json', request.url));
    const clientsData = await clientsResponse.json();
    const client = Object.values(clientsData.clients).find(c => c.api_key === api_key);
    
    if (!client) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Invalid API key',
        auth_required: true
      }), {
        status: 401,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    if (client.status !== 'active') {
      return new Response(JSON.stringify({
        success: false,
        error: 'Account inactive. Contact support.'
      }), {
        status: 403,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    // Check usage limits
    if (client.limits.current_month_runs >= client.limits.monthly_runs) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Monthly usage limit reached',
        current_usage: client.limits.current_month_runs,
        limit: client.limits.monthly_runs,
        tip: 'Upgrade your plan or wait until next month'
      }), {
        status: 429,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    // Check skill permissions
    if (client.allowed_skills[0] !== 'all' && !client.allowed_skills.includes(skillId)) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Skill not available on your plan',
        allowed_skills: client.allowed_skills
      }), {
        status: 403,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
    
    // Format payload for Modal webhook
    const payload = {
      slug: skillId,
      inputs: formInputs,
      client_id: client.id
    };
    
    // Call Modal webhook to execute the skill
    const modalUrl = env.MODAL_WEBHOOK_URL || 'https://nick-90891--claude-orchestrator-directive.modal.run';
    const response = await fetch(modalUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${env.MODAL_API_TOKEN || ''}`
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Modal webhook returned ${response.status}: ${errorText}`);
    }
    
    const result = await response.json();
    
    // Log usage (in production, this would update a database/sheets)
    // For now, we track in-memory (resets on deploy)
    await logUsage(request.url, {
      client_id: client.id,
      skill_id: skillId,
      timestamp: new Date().toISOString(),
      inputs: formInputs,
      success: result.success !== false
    });
    
    // Return formatted response
    return new Response(JSON.stringify({
      success: result.success !== false,
      skillId,
      data: result,
      usage: {
        current: client.limits.current_month_runs + 1,
        limit: client.limits.monthly_runs,
        remaining: client.limits.monthly_runs - client.limits.current_month_runs - 1
      },
      timestamp: new Date().toISOString()
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message,
      skillId,
      tip: 'Check Modal webhook deployment and environment variables',
      timestamp: new Date().toISOString()
    }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}

async function logUsage(baseUrl, usage) {
  try {
    // Log to usage tracking endpoint
    await fetch(new URL('/api/usage/log', baseUrl), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(usage)
    });
  } catch (e) {
    console.error('Failed to log usage:', e);
  }
}

// Handle OPTIONS for CORS
export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
