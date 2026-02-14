/**
 * GET /api/history/get
 * Retrieve job history for authenticated user
 */
export async function onRequestGet(context) {
  try {
    const { request, env } = context;
    const url = new URL(request.url);
    
    // Get API key from header
    const apiKey = request.headers.get('X-API-Key');
    if (!apiKey) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Missing API key'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Verify API key and get client
    const clients = await env.CLIENTS_KV.get('clients', 'json') || [];
    const client = clients.find(c => c.api_key === apiKey);
    
    if (!client) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Invalid API key'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Get limit parameter (default 50)
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const skillFilter = url.searchParams.get('skill');
    
    // In production, this would query Google Sheets or KV storage
    // For now, retrieve from KV storage (fallback for demo)
    const historyKey = `history_${client.id}`;
    let history = await env.CLIENTS_KV.get(historyKey, 'json') || [];
    
    // Filter by skill if specified
    if (skillFilter) {
      history = history.filter(run => run.skill_id === skillFilter);
    }
    
    // Sort by timestamp descending and limit
    history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    const limitedHistory = history.slice(0, limit);
    
    return new Response(JSON.stringify({
      success: true,
      runs: limitedHistory,
      total: limitedHistory.length,
      showing: limitedHistory.length,
      client_id: client.id
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('History retrieval error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Failed to retrieve history'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
