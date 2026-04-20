'use strict';
const express = require('express');
const crypto = require('crypto');
const router = express.Router();

function fmtTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

// GET /gigclock/c/:shareToken — server-rendered live client view
router.get('/c/:shareToken', (req, res) => {
  const db = req.app.get('db');
  const project = db.prepare(`
    SELECT p.*, u.plan, u.brand_name, u.plan_expires_at
    FROM gc_projects p
    JOIN gc_users u ON p.user_id = u.id
    WHERE p.share_token = ? AND p.is_archived = 0
  `).get(req.params.shareToken);

  if (!project) {
    return res.status(404).send(`<!DOCTYPE html><html><head><title>Not Found</title></head>
    <body style="font-family:sans-serif;text-align:center;padding:80px">
    <h1>Project not found</h1><p>This dashboard link is invalid or has expired.</p>
    <a href="/gigclock/">Learn about GigClock →</a></body></html>`);
  }

  // Record the view
  const ipHash = crypto.createHash('sha256').update(req.ip || '').digest('hex');
  try { db.prepare('INSERT INTO gc_client_views (project_id, ip_hash) VALUES (?, ?)').run(project.id, ipHash); } catch (_) {}

  const ownerIsPro = project.plan === 'pro' && project.plan_expires_at && new Date(project.plan_expires_at) > new Date();
  const brandName = ownerIsPro && project.brand_name ? project.brand_name : '5 Cypress Automation';
  const showGigClockBranding = !ownerIsPro;
  const shareToken = req.params.shareToken;

  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${project.name} — Live Project Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #fafaf9; --surface: #fff; --border: #e7e5e4;
      --text: #1c1917; --muted: #78716c; --faint: #a8a29e;
      --accent: #f97316; --green: #16a34a; --green-bg: #f0fdf4;
      --mono: 'Space Mono', monospace; --sans: 'DM Sans', sans-serif;
    }
    body { font-family: var(--sans); background: var(--bg); color: var(--text); min-height: 100vh; }

    /* Header */
    .header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 20px 40px; }
    .header-inner { max-width: 820px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .header-project { font-size: 12px; color: var(--faint); font-weight: 500; margin-bottom: 4px; }
    .header-name { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; }
    .header-brand { text-align: right; }
    .header-brand-label { font-size: 12px; color: var(--faint); margin-bottom: 4px; }
    .header-brand-name { font-weight: 600; font-size: 15px; }

    /* Status bar */
    .status-bar { background: var(--surface); border-bottom: 1px solid var(--border); padding: 12px 40px; }
    .status-inner { max-width: 820px; margin: 0 auto; display: flex; align-items: center; gap: 8px; font-size: 13px; }
    .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #22c55e; margin-right: 4px; animation: pulse 2s ease-in-out infinite; }
    .dot-idle { background: #d1d5db; animation: none; }
    .sep { color: var(--faint); }
    .live-task { color: var(--muted); }
    .live-elapsed { font-family: var(--mono); color: var(--accent); font-weight: 700; }

    /* Main */
    .main { max-width: 820px; margin: 0 auto; padding: 32px 40px; }

    /* Cards */
    .cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 40px; }
    @media (max-width: 600px) { .cards { grid-template-columns: repeat(2, 1fr); } }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px 16px; }
    .card.accent { background: linear-gradient(135deg, #f97316, #ea580c); border: none; color: #fff; }
    .card-label { font-size: 12px; color: var(--faint); font-weight: 500; margin-bottom: 6px; }
    .card.accent .card-label { color: rgba(255,255,255,0.7); }
    .card-value { font-size: 26px; font-weight: 700; font-family: var(--mono); letter-spacing: -0.02em; }

    /* Section header */
    .section-label { font-size: 11px; color: var(--faint); font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
    .section-name { font-size: 18px; font-weight: 700; margin-bottom: 20px; }

    /* Task table */
    .table-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; margin-bottom: 32px; }
    .table-head { display: grid; grid-template-columns: 1fr 100px 80px 80px; padding: 12px 20px; font-size: 11px; font-weight: 600; color: var(--faint); text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 1px solid #f5f5f4; }
    .table-row { display: grid; grid-template-columns: 1fr 100px 80px 80px; padding: 16px 20px; align-items: center; border-bottom: 1px solid #f5f5f4; }
    .table-row:last-child { border-bottom: none; }
    .task-name { font-weight: 600; font-size: 14px; }
    .task-date { font-size: 12px; color: var(--faint); margin-top: 2px; }
    .task-hours { font-family: var(--mono); font-size: 15px; font-weight: 700; }
    .task-hours.live { color: var(--accent); }
    .task-cost { font-size: 14px; color: var(--muted); }
    .badge { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 100px; font-size: 12px; font-weight: 600; }
    .badge-live { background: rgba(249,115,22,0.1); color: var(--accent); }
    .badge-done { background: var(--green-bg); color: var(--green); }

    /* Bar chart */
    .chart { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 24px; }
    .bar-row { margin-bottom: 12px; }
    .bar-row:last-child { margin-bottom: 0; }
    .bar-meta { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; }
    .bar-track { height: 8px; background: #f5f5f4; border-radius: 100px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 100px; transition: width 0.8s ease; }
    .bar-fill.live { background: linear-gradient(90deg, #f97316, #fbbf24); }
    .bar-fill.done { background: var(--text); }

    /* Footer */
    .footer { margin-top: 48px; text-align: center; font-size: 12px; color: var(--faint); padding-bottom: 40px; }
    .footer a { color: var(--accent); text-decoration: none; }

    /* Empty state */
    .empty { padding: 40px 20px; text-align: center; color: var(--faint); }

    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
    @keyframes fadeUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
    .fade-up { animation: fadeUp 0.4s ease-out both; }
  </style>
</head>
<body>

  <div class="header">
    <div class="header-inner">
      <div>
        <div class="header-project">Project dashboard for</div>
        <div class="header-name" id="client-name">${project.client_name || 'Your Client'}</div>
      </div>
      <div class="header-brand">
        <div class="header-brand-label">Managed by</div>
        <div class="header-brand-name">${brandName}</div>
      </div>
    </div>
  </div>

  <div class="status-bar">
    <div class="status-inner" id="status-bar">
      <span class="dot dot-idle" id="status-dot"></span>
      <span id="status-text" style="color:var(--muted)">Loading…</span>
    </div>
  </div>

  <div class="main">
    <div class="cards fade-up" id="cards">
      <div class="card"><div class="card-label">Total hours</div><div class="card-value" id="card-hours">—</div></div>
      <div class="card"><div class="card-label">Running total</div><div class="card-value" id="card-cost">—</div></div>
      <div class="card"><div class="card-label">Tasks completed</div><div class="card-value" id="card-tasks">—</div></div>
      <div class="card accent"><div class="card-label">Rate</div><div class="card-value" id="card-rate">—</div></div>
    </div>

    <div class="fade-up" style="animation-delay:0.1s">
      <div class="section-label">Project</div>
      <div class="section-name" id="project-name">${project.name}</div>
    </div>

    <div class="table-wrap fade-up" style="animation-delay:0.15s">
      <div class="table-head">
        <span>Task</span><span>Hours</span><span>Cost</span><span>Status</span>
      </div>
      <div id="entries-body">
        <div class="empty">Loading time entries…</div>
      </div>
    </div>

    <div class="chart fade-up" style="animation-delay:0.2s">
      <div class="section-label" style="margin-bottom:20px">Hours by task</div>
      <div id="chart-body"></div>
    </div>

    <div class="footer">
      ${showGigClockBranding ? `
        <div style="margin-bottom:6px">
          Transparency powered by <strong>GigClock</strong> — A 5 Cypress Automation Tool
        </div>
        <div>Freelancers: get your own live dashboard free at <a href="/gigclock/">gigclock.5cypress.com</a></div>
      ` : `
        <div>Live project dashboard by <strong>${brandName}</strong></div>
        <div style="margin-top:4px;color:#d6d3d1">Powered by GigClock</div>
      `}
    </div>
  </div>

<script>
(function() {
  const TOKEN = '${shareToken}';
  let runningInterval = null;
  let runningStart = null;
  let lastData = null;

  function fmtSeconds(s) {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    if (h > 0) return h + 'h ' + m + 'm';
    if (m > 0) return m + 'm ' + sec + 's';
    return sec + 's';
  }
  function fmtHours(s) { return (Math.round(s / 36) / 100).toFixed(2) + 'h'; }
  function fmtCost(hours, rate) { return '$' + (Math.round(hours * rate * 100) / 100).toFixed(2); }

  function renderLiveElapsed() {
    if (!runningStart) return;
    const elapsed = Math.floor((Date.now() - runningStart) / 1000);
    const el = document.getElementById('live-elapsed');
    if (el) el.textContent = fmtSeconds(elapsed);

    // Update card totals in real time
    if (lastData) {
      const completedSeconds = lastData.summary.total_seconds - elapsed; // base
      const grandTotal = completedSeconds + elapsed + lastData.running.elapsed_seconds + (Math.floor((Date.now() - runningStart) / 1000) - lastData.running.elapsed_seconds);
      // simpler: just use elapsed from runningStart
      const total = lastData.summary.total_seconds - lastData.running.elapsed_seconds + Math.floor((Date.now() - runningStart) / 1000);
      const totalHours = total / 3600;
      const rate = lastData.project.hourly_rate;
      document.getElementById('card-hours').textContent = fmtHours(total);
      document.getElementById('card-cost').textContent = fmtCost(totalHours, rate);
    }
  }

  function render(data) {
    lastData = data;
    const { project, entries, summary, running, brand } = data;
    const rate = project.hourly_rate;

    // Cards
    document.getElementById('card-hours').textContent = fmtHours(summary.total_seconds);
    document.getElementById('card-cost').textContent = fmtCost(summary.total_hours, rate);
    document.getElementById('card-tasks').textContent = summary.entry_count + (running ? '+' : '');
    document.getElementById('card-rate').textContent = '$' + rate + '/hr';

    // Status bar
    const dot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    if (running) {
      dot.classList.remove('dot-idle');
      runningStart = new Date(running.started_at).getTime();
      statusText.innerHTML =
        '<span style="color:var(--green);font-weight:600">Currently working</span>' +
        '<span class="sep">·</span>' +
        '<span class="live-task">' + (running.description || 'Active task') + '</span>' +
        '<span class="sep">·</span>' +
        '<span class="live-elapsed" id="live-elapsed">' + fmtSeconds(running.elapsed_seconds) + '</span>';
    } else {
      dot.classList.add('dot-idle');
      runningStart = null;
      statusText.innerHTML = '<span style="color:var(--muted)">No active timer</span>';
    }

    // Entries
    const tbody = document.getElementById('entries-body');
    const allEntries = running
      ? [{ ...running, isRunning: true }, ...entries]
      : entries;

    if (allEntries.length === 0) {
      tbody.innerHTML = '<div class="empty">No time entries yet.</div>';
    } else {
      tbody.innerHTML = allEntries.map(e => {
        const hrs = e.isRunning ? e.elapsed_seconds / 3600 : e.duration_seconds / 3600;
        const cost = Math.round(hrs * rate * 100) / 100;
        const dateLabel = new Date(e.started_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const badge = e.isRunning
          ? '<span class="badge badge-live"><span class="dot" style="width:6px;height:6px;margin-right:3px"></span>Live</span>'
          : '<span class="badge badge-done">Done</span>';
        const hoursDisplay = e.isRunning
          ? '<span class="task-hours live" id="live-elapsed">' + fmtSeconds(e.elapsed_seconds) + '</span>'
          : '<span class="task-hours">' + (hrs).toFixed(1) + 'h</span>';
        return '<div class="table-row">' +
          '<div><div class="task-name">' + (e.description || 'Task') + '</div><div class="task-date">' + dateLabel + '</div></div>' +
          hoursDisplay +
          '<div class="task-cost">$' + cost.toFixed(0) + '</div>' +
          '<div>' + badge + '</div>' +
          '</div>';
      }).join('');
    }

    // Bar chart
    const chartBody = document.getElementById('chart-body');
    const maxHours = Math.max(...allEntries.map(e => e.isRunning ? e.elapsed_seconds / 3600 : e.duration_seconds / 3600), 0.1);
    chartBody.innerHTML = allEntries.map(e => {
      const hrs = e.isRunning ? e.elapsed_seconds / 3600 : e.duration_seconds / 3600;
      const pct = Math.min((hrs / maxHours) * 100, 100);
      return '<div class="bar-row">' +
        '<div class="bar-meta"><span style="color:var(--muted);font-weight:500">' + (e.description || 'Task') + '</span>' +
        '<span style="font-family:var(--mono);font-weight:700;font-size:12px">' + hrs.toFixed(1) + 'h</span></div>' +
        '<div class="bar-track"><div class="bar-fill ' + (e.isRunning ? 'live' : 'done') + '" style="width:' + pct.toFixed(1) + '%"></div></div>' +
        '</div>';
    }).join('');
  }

  async function fetchData() {
    try {
      const resp = await fetch('/api/gigclock/public/' + TOKEN);
      if (!resp.ok) return;
      const data = await resp.json();
      render(data);
    } catch (e) { /* silent */ }
  }

  // Live tick every second
  setInterval(renderLiveElapsed, 1000);
  // Sync from server every 30s
  setInterval(fetchData, 30000);
  // Initial load
  fetchData();
})();
</script>
</body>
</html>`);
});

module.exports = router;
