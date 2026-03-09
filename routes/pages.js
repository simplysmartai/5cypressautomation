/**
 * routes/pages.js
 * Static page serves + client dashboard routes
 */
const express = require('express');
const path = require('path');
const fs = require('fs');

const router = express.Router();
const ROOT = path.join(__dirname, '..');

// ── Public page routes ────────────────────────────────────────────────────────
router.get('/', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'index.html')));
router.get('/dashboard', (_req, res) => res.redirect('/skills-dashboard.html'));
router.get('/form', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'form.html')));
router.get('/operations', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'operations.html')));
router.get('/seo-dashboard', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'seo-dashboard.html')));
router.get('/marketing', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'marketing-dashboard.html')));
router.get('/preview-work-item', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'preview-work-item.html')));

router.get('/health', (_req, res) =>
  res.status(200).json({
    status: 'ok',
    service: '5cypress-admin-api',
    timestamp: new Date().toISOString()
  })
);

// ── Client dashboard routes ──────────────────────────────────────────────────
router.get('/clients/remy-lasers', (_req, res) =>
  res.sendFile(path.join(ROOT, 'public', 'client-remy-lasers.html'))
);
router.get('/clients/remy-lasers/prototypes/roi-calculator', (_req, res) =>
  res.sendFile(path.join(ROOT, 'public', 'client-remy-lasers-roi.html'))
);
router.get('/clients/remy-lasers/prototypes/qbo-invoice', (_req, res) =>
  res.sendFile(path.join(ROOT, 'clients', 'remy-lasers', 'prototypes', 'qbo-invoice-preview.html'))
);
router.get('/clients/remy-lasers/prototypes/shipping-label', (_req, res) =>
  res.sendFile(path.join(ROOT, 'clients', 'remy-lasers', 'prototypes', 'shipping-label-preview.html'))
);
router.get('/clients/remy-lasers/prototypes/calendar-dashboard', (_req, res) =>
  res.sendFile(path.join(ROOT, 'clients', 'remy-lasers', 'prototypes', 'calendar-dashboard-preview.html'))
);
router.get('/clients/remy-lasers/documents/presentation', (_req, res) =>
  res.sendFile(path.join(ROOT, 'public', 'client-remy-lasers-presentation.html'))
);
router.get('/clients/remy-lasers/documents/:docType', (req, res) => {
  res.send(`Document viewer for: ${req.params.docType} - Coming soon!`);
});
router.get('/clients/:clientSlug', (req, res) => {
  const clientFile = path.join(ROOT, 'public', `client-${req.params.clientSlug}.html`);
  if (fs.existsSync(clientFile)) {
    return res.sendFile(clientFile);
  }
  res.status(404).send(`Client dashboard not found for: ${req.params.clientSlug}`);
});

// ── Catch-all: extensionless clean URLs ─────────────────────────────────────
router.get('*', (req, res, next) => {
  if (
    req.path.startsWith('/api/') ||
    req.path.startsWith('/admin/') ||
    path.extname(req.path)
  ) {
    return next();
  }
  const cleanPath = req.path.replace(/\/$/, '') || '/index';
  const htmlFile = path.join(ROOT, 'public', cleanPath + '.html');
  if (fs.existsSync(htmlFile)) return res.sendFile(htmlFile);
  res.status(404).sendFile(path.join(ROOT, 'public', 'index.html'));
});

module.exports = router;
