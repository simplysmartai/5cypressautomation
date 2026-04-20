/**
 * server.js — 5 Cypress Automation
 *
 * Slim orchestrator. Business logic lives in routes/:
 *   routes/pages.js         — static page serves + client dashboards + catch-all
 *   routes/admin.js         — /admin/* page + API routes (protected by adminAuth)
 *   routes/api-dashboard.js — /api/dashboard, /api/orders, /api/work-items
 *   routes/api-leads.js     — /api/lead-capture, /api/leads, /api/webhooks/*, /api/contact, /submit-inquiry
 *   routes/api-seo.js       — /api/seo/* (analyze, report, checkout, config)
 *   routes/api-skills.js    — /api/skills
 *   routes/api-gigclock.js  — /api/gigclock/* (GigClock time tracking SaaS)
 *   routes/gigclock-pages.js — /gigclock/c/:shareToken (server-rendered client view)
 */
'use strict';

const express = require('express');
const path    = require('path');
const fs      = require('fs');
require('dotenv').config();
const helmet    = require('helmet');
const morgan    = require('morgan');
const rateLimit = require('express-rate-limit');
const xss       = require('xss-clean');
const hpp       = require('hpp');
const db        = require('./db');
const adminAuth = require('./middleware/adminAuth');

// Route modules
const pagesRouter     = require('./routes/pages');
const adminRouter     = require('./routes/admin');
const dashboardRouter = require('./routes/api-dashboard');
const leadsRouter     = require('./routes/api-leads');
const seoRouter       = require('./routes/api-seo');
const skillsRouter      = require('./routes/api-skills');
const gigclockApiRouter = require('./routes/api-gigclock');
const gigclockPagesRouter = require('./routes/gigclock-pages');

// Stripe (optional)
let stripe;
if (process.env.STRIPE_SECRET_KEY) {
  stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
} else {
  console.warn('WARNING: STRIPE_SECRET_KEY is missing. Payment features will be disabled.');
}

const app = express();
app.set('db', db);
app.set('stripe', stripe);

// Rate limiting
app.use('/api/', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many requests from this IP, please try again after 15 minutes'
}));

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc:    ["'self'"],
      scriptSrc:     ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://unpkg.com", "https://assets.calendly.com", "https://*.cloudflare.com", "https://cdnjs.cloudflare.com"],
      styleSrc:      ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://assets.calendly.com", "https://fonts.googleapis.com", "https://cdnjs.cloudflare.com"],
      styleSrcElem:  ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://assets.calendly.com"],
      imgSrc:        ["'self'", "data:", "https:"],
      connectSrc:    ["'self'", "https://unpkg.com", "https://cdn.jsdelivr.net", "https://*.cloudflare.com", "https://cdnjs.cloudflare.com", "https://assets.calendly.com"],
      fontSrc:       ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
      scriptSrcAttr: ["'unsafe-inline'"],
      objectSrc:     ["'none'"],
      frameSrc:      ["https://calendly.com"],
      upgradeInsecureRequests: []
    }
  }
}));
app.use(xss());
app.use(hpp());

// Body parsing (rawBody stored for Calendly webhook signature verification)
app.use(express.json({
  limit: '10kb',
  verify: (req, _res, buf) => { req.rawBody = buf; }
}));
app.use(express.urlencoded({ extended: true, limit: '10kb' }));
app.use(express.static('public'));

// Structured logging
app.use(morgan(':remote-addr - :remote-user [:date[clf]] ":method :url HTTP/:http-version" :status :res[content-length] ":referrer" ":user-agent" - :response-time ms'));

// Route mounting (specific prefixes first, catch-all pages router last)
app.use('/admin',          adminAuth, adminRouter);
app.use('/api/seo',        seoRouter);
app.use('/api/gigclock',   gigclockApiRouter);   // GigClock time tracking SaaS
app.use('/api',            leadsRouter);
app.use('/api',            dashboardRouter);
// Skills: GET /api/skills is public; POST /api/skills/:id/run is admin-only (enforced in router)
app.use('/api/skills',     skillsRouter);
app.use('/gigclock',       gigclockPagesRouter); // GigClock server-rendered client views
app.use('/',               pagesRouter);

// Start server
const PORT   = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

server.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use.`);
    setTimeout(() => { server.close(); server.listen(0); }, 1000);
  } else {
    console.error('Server error:', e);
  }
});
