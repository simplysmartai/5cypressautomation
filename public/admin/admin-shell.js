/**
 * admin-shell.js
 * Injects the shared sidebar into every /admin page.
 * Include at bottom of <body>. Requires #admin-sidebar placeholder div.
 * Also populates the lead count badge and status footer via /admin/api/stats.
 */
(function () {
  const PATH = window.location.pathname.replace(/\/$/, '') || '/admin';

  // ── Nav definition ────────────────────────────────────────────────────────
  const NAV = [
    {
      label: 'Overview',
      items: [
        { icon: 'ri-dashboard-line',   label: 'Dashboard',       href: '/admin' },
        { icon: 'ri-user-add-line',    label: 'Leads',           href: '/admin/leads',   badgeId: 'shellLeadBadge' },
        { icon: 'ri-briefcase-line',   label: 'Clients',         href: '/admin/clients' },
      ]
    },
    {
      label: 'Marketing Team',
      items: [
        { icon: 'ri-robot-line',       label: 'AI Marketing',    href: '/admin/marketing', badgeId: 'shellMktgBadge', badgeCls: 'gold' },
        { icon: 'ri-megaphone-line',   label: 'Marketing Page',  href: '/marketing',       external: true },
      ]
    },
    {
      label: 'Tools',
      items: [
        { icon: 'ri-search-eye-line',  label: 'SEO Audit',       href: '/admin/seo' },
        { icon: 'ri-user-star-line',   label: 'New Client',      href: '/admin/newclient' },
      ]
    },
    {
      label: 'Site',
      items: [
        { icon: 'ri-home-line',        label: 'Homepage',        href: '/', external: true },
      ]
    },
  ];

  function isActive(href) {
    if (href === '/admin') return PATH === '/admin' || PATH === '';
    return PATH === href || PATH.startsWith(href + '/');
  }

  function navItemHTML(item) {
    const active = isActive(item.href) ? ' active' : '';
    const ext = item.external
      ? `<span class="a-nav-ext"><i class="ri-external-link-line"></i></span>`
      : '';
    const badge = item.badgeId
      ? `<span class="a-nav-badge${item.badgeCls ? ' ' + item.badgeCls : ''}" id="${item.badgeId}">—</span>`
      : '';
    const target = item.external ? ' target="_blank" rel="noopener"' : '';
    return `
      <a class="a-nav-item${active}" href="${item.href}"${target}>
        <i class="${item.icon}"></i>
        <span>${item.label}</span>
        ${badge}${ext}
      </a>`;
  }

  function buildSidebar() {
    const groupsHTML = NAV.map(group => `
      <div class="a-nav-group">
        <span class="a-nav-label">${group.label}</span>
        ${group.items.map(navItemHTML).join('')}
      </div>`).join('');

    return `
      <a class="a-logo" href="/admin">
        <div class="a-logo-icon"><i class="ri-tree-line"></i></div>
        <div>
          <div class="a-logo-name">5 Cypress</div>
          <div class="a-logo-sub">Admin Hub</div>
        </div>
      </a>
      <nav class="a-nav">${groupsHTML}</nav>
      <div class="a-footer">
        <div class="a-status-dot" id="shellStatusDot"></div>
        <div>
          <div class="a-footer-label" id="shellStatusLabel">Checking…</div>
          <div class="a-footer-ts mono" id="shellStatusTs"></div>
        </div>
      </div>`;
  }

  // ── Inject sidebar ────────────────────────────────────────────────────────
  const placeholder = document.getElementById('admin-sidebar');
  if (placeholder) {
    placeholder.innerHTML = buildSidebar();
  }

  // ── Async: populate badges + status dot ───────────────────────────────────
  async function shellInit() {
    // Health check
    try {
      const r = await fetch('/health');
      const dot = document.getElementById('shellStatusDot');
      const lbl = document.getElementById('shellStatusLabel');
      const ts  = document.getElementById('shellStatusTs');
      if (dot) dot.className = 'a-status-dot' + (r.ok ? '' : ' offline');
      if (lbl) lbl.textContent = r.ok ? 'System Online' : 'API Unreachable';
      if (ts)  ts.textContent  = new Date().toLocaleTimeString();
    } catch {
      const dot = document.getElementById('shellStatusDot');
      if (dot) { dot.className = 'a-status-dot offline'; }
      const lbl = document.getElementById('shellStatusLabel');
      if (lbl) lbl.textContent = 'Unreachable';
    }

    // Stats for badges
    try {
      const s = await fetch('/admin/api/stats').then(r => r.json());
      const lb = document.getElementById('shellLeadBadge');
      if (lb) lb.textContent = s.leadCount ?? '—';
      const mb = document.getElementById('shellMktgBadge');
      // marketing count populated separately by each page that needs it
    } catch { /* non-fatal */ }
  }

  shellInit();
})();
