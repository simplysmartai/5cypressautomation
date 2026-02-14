/**
 * POST /api/schedules/create
 * Create a new scheduled skill
 */
export async function onRequestPost(context) {
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
    
    // Parse schedule data
    const scheduleData = await request.json();
    
    // Validate required fields
    if (!scheduleData.skill_id || !scheduleData.frequency || !scheduleData.time) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Missing required fields: skill_id, frequency, time'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Validate frequency
    const validFrequencies = ['hourly', 'daily', 'weekly', 'monthly'];
    if (!validFrequencies.includes(scheduleData.frequency)) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Invalid frequency. Must be: hourly, daily, weekly, or monthly'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Check skill permissions
    if (client.allowed_skills[0] !== 'all' && !client.allowed_skills.includes(scheduleData.skill_id)) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Skill not available on your plan'
      }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Create schedule object
    const schedule = {
      id: `sched_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      client_id: client.id,
      skill_id: scheduleData.skill_id,
      frequency: scheduleData.frequency,
      time: scheduleData.time, // Format: "HH:MM" in UTC
      day_of_week: scheduleData.day_of_week || 0, // For weekly (0 = Sunday)
      day_of_month: scheduleData.day_of_month || 1, // For monthly (1-31)
      inputs: scheduleData.inputs || {},
      enabled: true,
      created_at: new Date().toISOString(),
      last_run: null
    };
    
    // Load existing schedules
    const schedules = await env.CLIENTS_KV.get('scheduled_skills', 'json') || [];
    
    // Add new schedule
    schedules.push(schedule);
    
    // Save back to KV
    await env.CLIENTS_KV.put('scheduled_skills', JSON.stringify(schedules));
    
    return new Response(JSON.stringify({
      success: true,
      schedule: schedule,
      message: 'Schedule created successfully'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Schedule creation error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Failed to create schedule'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
