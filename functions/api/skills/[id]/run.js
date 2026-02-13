// Cloudflare Pages Function: /api/skills/:id/run
// Executes a skill by calling Modal webhook

export async function onRequestPost(context) {
  const { params, request, env } = context;
  const skillId = params.id;
  
  try {
    // Parse request body (contains form inputs)
    const formInputs = await request.json();
    
    // Format payload for Modal webhook
    const payload = {
      slug: skillId,
      inputs: formInputs
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
    
    // Return formatted response
    return new Response(JSON.stringify({
      success: result.success !== false,
      skillId,
      data: result,
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
