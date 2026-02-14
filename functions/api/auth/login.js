// Cloudflare Pages Function: /api/auth/login
// Simple login endpoint (email-based for now)

export async function onRequestPost(context) {
  const { request } = context;
  
  try {
    const { email, password } = await request.json();
    
    if (!email) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Email is required'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Fetch clients configuration
    const clientsResponse = await fetch(new URL('/config/clients.json', request.url));
    const clientsData = await clientsResponse.json();
    
    // Find client by email (simple auth for demo)
    const client = Object.values(clientsData.clients).find(c => 
      c.email.toLowerCase() === email.toLowerCase()
    );
    
    if (!client) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Account not found. Contact support to get started.'
      }), {
        status: 404,
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
    
    // Return API key (in production, verify password first)
    return new Response(JSON.stringify({
      success: true,
      message: 'Login successful',
      api_key: client.api_key,
      client: {
        id: client.id,
        name: client.name,
        email: client.email,
        tier: client.tier,
        role: client.role,
        limits: client.limits
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
      error: 'Login failed',
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
