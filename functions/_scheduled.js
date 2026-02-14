/**
 * Scheduled Skills Runner
 * Runs configured skills on a schedule using Cloudflare Workers Cron Triggers
 * 
 * Configure in wrangler.toml:
 * [triggers]
 * crons = ["0 9 * * *"]  # Daily at 9am UTC
 */

export default {
  async scheduled(event, env, ctx) {
    console.log('Scheduled skills runner triggered:', event.cron);

    try {
      // Load scheduled skills configuration from KV
      const schedules = await env.CLIENTS_KV.get('scheduled_skills', 'json') || [];

      // Filter schedules that match this cron time
      const now = new Date();
      const matchingSchedules = schedules.filter(schedule => {
        return schedule.enabled && shouldRunNow(schedule, now);
      });

      console.log(`Found ${matchingSchedules.length} schedules to run`);

      // Run each scheduled skill
      const results = await Promise.allSettled(
        matchingSchedules.map(schedule => runScheduledSkill(schedule, env))
      );

      // Log results
      results.forEach((result, index) => {
        const schedule = matchingSchedules[index];
        if (result.status === 'fulfilled') {
          console.log(`✅ Scheduled skill ${schedule.skill_id} completed for ${schedule.client_id}`);
        } else {
          console.error(`❌ Scheduled skill ${schedule.skill_id} failed for ${schedule.client_id}:`, result.reason);
        }
      });

      return new Response(JSON.stringify({
        success: true,
        triggered: matchingSchedules.length,
        results: results.map(r => r.status)
      }), {
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('Scheduled runner error:', error);
      return new Response(JSON.stringify({
        success: false,
        error: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};

// Check if a schedule should run now based on its frequency
function shouldRunNow(schedule, now) {
  const { frequency, time } = schedule;
  const currentHour = now.getUTCHours();
  const currentDay = now.getUTCDay(); // 0 = Sunday
  const currentDate = now.getUTCDate();

  // Parse time (format: "HH:MM")
  const [targetHour, targetMinute] = time.split(':').map(Number);

  // Check if we're in the right hour (cron runs every hour, we filter by target hour)
  if (currentHour !== targetHour) {
    return false;
  }

  // Check frequency
  switch (frequency) {
    case 'daily':
      return true;

    case 'weekly':
      // schedule.day_of_week: 0 = Sunday, 1 = Monday, etc.
      return currentDay === schedule.day_of_week;

    case 'monthly':
      // schedule.day_of_month: 1-31
      return currentDate === schedule.day_of_month;

    case 'hourly':
      return true; // Run every hour

    default:
      return false;
  }
}

// Execute a scheduled skill
async function runScheduledSkill(schedule, env) {
  try {
    // Get client info
    const clients = await env.CLIENTS_KV.get('clients', 'json') || [];
    const client = clients.find(c => c.id === schedule.client_id);

    if (!client) {
      throw new Error(`Client not found: ${schedule.client_id}`);
    }

    // Check if skill is allowed for this client
    if (client.allowed_skills[0] !== 'all' && !client.allowed_skills.includes(schedule.skill_id)) {
      throw new Error(`Skill ${schedule.skill_id} not allowed for client`);
    }

    // Check usage limits (scheduled runs count towards limit)
    if (client.limits.current_month_runs >= client.limits.monthly_runs) {
      throw new Error(`Monthly usage limit reached for ${client.id}`);
    }

    // Call the skill execution endpoint
    const modalUrl = env.MODAL_WEBHOOK_URL || 'https://nick-90891--claude-orchestrator-directive.modal.run';
    
    const payload = {
      slug: schedule.skill_id,
      inputs: schedule.inputs || {},
      client_id: client.id,
      scheduled: true
    };

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

    // Log to history
    const runData = {
      client_id: client.id,
      client_name: client.name,
      skill_id: schedule.skill_id,
      timestamp: new Date().toISOString(),
      inputs: schedule.inputs || {},
      success: result.success !== false,
      result: result,
      error: result.error || '',
      scheduled: true,
      schedule_id: schedule.id
    };

    // Log to history (using the history log endpoint logic)
    const historyKey = `history_${client.id}`;
    let history = await env.CLIENTS_KV.get(historyKey, 'json') || [];
    history.push(runData);
    if (history.length > 100) history = history.slice(-100);
    await env.CLIENTS_KV.put(historyKey, JSON.stringify(history));

    // Send Telegram notification if configured
    const botToken = env.TELEGRAM_BOT_TOKEN;
    const chatId = env.TELEGRAM_CHAT_ID;
    if (botToken && chatId) {
      await sendScheduledNotification(botToken, chatId, runData, schedule);
    }

    // Update last run time
    schedule.last_run = new Date().toISOString();
    const schedules = await env.CLIENTS_KV.get('scheduled_skills', 'json') || [];
    const updatedSchedules = schedules.map(s => 
      s.id === schedule.id ? { ...s, last_run: schedule.last_run } : s
    );
    await env.CLIENTS_KV.put('scheduled_skills', JSON.stringify(updatedSchedules));

    return {
      success: true,
      schedule_id: schedule.id,
      result
    };

  } catch (error) {
    console.error(`Failed to run scheduled skill ${schedule.skill_id}:`, error);
    throw error;
  }
}

// Send Telegram notification for scheduled runs
async function sendScheduledNotification(botToken, chatId, runData, schedule) {
  try {
    const skillName = runData.skill_id.replace(/-/g, ' ').replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    const emoji = runData.success ? '✅' : '❌';
    const status = runData.success ? 'Success' : 'Failed';

    let messageText = `${emoji} *Scheduled Skill ${status}*\n\n`;
    messageText += `*Skill:* ${skillName}\n`;
    messageText += `*Client:* ${runData.client_name}\n`;
    messageText += `*Frequency:* ${schedule.frequency}\n`;
    messageText += `*Time:* ${new Date(runData.timestamp).toLocaleString()}`;

    if (!runData.success && runData.error) {
      messageText += `\n\n*Error:* \`${runData.error}\``;
    }

    const telegramUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;
    await fetch(telegramUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: messageText,
        parse_mode: 'Markdown'
      })
    });
  } catch (error) {
    console.error('Failed to send Telegram notification:', error);
  }
}
