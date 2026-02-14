/**
 * POST /api/history/log
 * Log a skill run to history (called after skill execution)
 */
export async function onRequestPost(context) {
  try {
    const { request, env } = context;
    
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
    
    // Parse run data
    const runData = await request.json();
    
    // Add timestamp if not provided
    if (!runData.timestamp) {
      runData.timestamp = new Date().toISOString();
    }
    
    // Add client info
    runData.client_id = client.id;
    runData.client_tier = client.tier;
    
    // Store in KV (append to history array)
    const historyKey = `history_${client.id}`;
    let history = await env.CLIENTS_KV.get(historyKey, 'json') || [];
    
    // Add new run
    history.push(runData);
    
    // Keep only last 100 runs per client (prevent unbounded growth)
    if (history.length > 100) {
      history = history.slice(-100);
    }
    
    // Save back to KV
    await env.CLIENTS_KV.put(historyKey, JSON.stringify(history));
    
    // TODO: Also log to Google Sheets for long-term storage
    // This requires calling the Python script via Modal or direct Sheets API
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Run logged to history',
      run_id: runData.timestamp
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('History logging error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Failed to log to history'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
