// Cloudflare Pages Function: /api/auth/verify
// Verify API key and return client info

export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    const { api_key } = await request.json();
    
    if (!api_key) {
      return new Response(JSON.stringify({
        success: false,
        error: 'API key is required'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Fetch clients configuration
    const clientsResponse = await fetch(new URL('/config/clients.json', request.url));
    const clientsData = await clientsResponse.json();
    
    // Find client by API key
    const client = Object.values(clientsData.clients).find(c => c.api_key === api_key);
    
    if (!client) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Invalid API key'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    if (client.status !== 'active') {
      return new Response(JSON.stringify({
        success: false,
        error: 'Account is inactive. Please contact support.'
      }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Return client info (without sensitive data)
    return new Response(JSON.stringify({
      success: true,
      client: {
        id: client.id,
        name: client.name,
        email: client.email,
        tier: client.tier,
        role: client.role,
        limits: client.limits,
        allowed_skills: client.allowed_skills
      }
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
      error: 'Authentication failed',
      message: error.message
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
