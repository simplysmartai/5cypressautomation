// Cloudflare Pages Function: /api/skills/:id/run
// Executes a skill by calling Modal webhook

export async function onRequestPost(context) {
  const { params, request, env } = context;
  const skillId = params.id;
  
  try {
    // Parse request body
    const body = await request.json();
    
    // Call Modal webhook to execute the skill
    const modalUrl = env.MODAL_WEBHOOK_URL || 'https://nick-90891--claude-orchestrator-directive.modal.run';
    const response = await fetch(`${modalUrl}?slug=${skillId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${env.MODAL_API_TOKEN || ''}`
      },
      body: JSON.stringify(body)
    });
    
    const result = await response.json();
    
    return new Response(JSON.stringify({
      success: true,
      skillId,
      result,
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
      tip: 'Make sure Modal webhook is deployed and MODAL_API_TOKEN is set'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
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
