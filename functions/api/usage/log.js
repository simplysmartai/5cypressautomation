// Cloudflare Pages Function: /api/usage/log
// Log skill usage to Google Sheets or local storage

export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    const usage = await request.json();
    
    // In production, this would:
    // 1. Append to Google Sheets via API
    // 2. Update Cloudflare KV storage
    // 3. Send to analytics service
    
    // For now, we'll respond with success
    // The actual increment happens in clients.json (would be database in production)
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Usage logged',
      usage
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
      error: error.message
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
