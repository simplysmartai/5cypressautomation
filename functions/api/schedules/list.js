/**
 * GET /api/schedules/list
 * List all scheduled skills for authenticated user
 */
export async function onRequestGet(context) {
  try {
    const { request, env } = context;
    
    // Get API key
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
    
    // Verify API key
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
    
    // Load all schedules
    const allSchedules = await env.CLIENTS_KV.get('scheduled_skills', 'json') || [];
    
    // Filter by client
    const clientSchedules = allSchedules.filter(s => s.client_id === client.id);
    
    return new Response(JSON.stringify({
      success: true,
      schedules: clientSchedules,
      total: clientSchedules.length
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Schedule list error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Failed to list schedules'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
