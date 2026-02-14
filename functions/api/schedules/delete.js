/**
 * DELETE /api/schedules/delete
 * Delete a scheduled skill
 */
export async function onRequestDelete(context) {
  try {
    const { request, env } = context;
    const url = new URL(request.url);
    const scheduleId = url.searchParams.get('id');
    
    if (!scheduleId) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Missing schedule ID'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
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
    
    // Find schedule
    const schedule = allSchedules.find(s => s.id === scheduleId);
    
    if (!schedule) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Schedule not found'
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Verify ownership
    if (schedule.client_id !== client.id) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Unauthorized to delete this schedule'
      }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Remove schedule
    const updatedSchedules = allSchedules.filter(s => s.id !== scheduleId);
    
    // Save back to KV
    await env.CLIENTS_KV.put('scheduled_skills', JSON.stringify(updatedSchedules));
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Schedule deleted successfully'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Schedule deletion error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Failed to delete schedule'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
