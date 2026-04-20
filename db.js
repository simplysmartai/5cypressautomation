const Database = require('better-sqlite3');
const db = new Database('platform.db');

// Initialize database schema
db.exec(`
  CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE,
    name TEXT,
    status TEXT,
    dealValue REAL,
    nextAction TEXT,
    engagement TEXT,
    industry TEXT,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customerName TEXT,
    customerEmail TEXT,
    date TEXT,
    salesRep TEXT,
    orderType TEXT,
    productName TEXT,
    quantity INTEGER,
    status TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS seo_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT,
    email TEXT,
    session_id TEXT UNIQUE,
    status TEXT DEFAULT 'pending', -- 'pending', 'paid', 'expired'
    report_data TEXT, -- JSON blob
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT,
    website TEXT,
    source TEXT,
    scanned_domain TEXT,
    challenge TEXT,
    timeline TEXT,
    status TEXT DEFAULT 'new',
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// ── Migrate leads table — add columns that may not exist in older DBs ────────
['followUpDate TEXT', 'service TEXT', 'calendlyEventUri TEXT', 'startTime TEXT', 'timezone TEXT'].forEach(col => {
  try { db.exec(`ALTER TABLE leads ADD COLUMN ${col}`); } catch (_) { /* column already exists — safe to ignore */ }
});

// ── GigClock tables ───────────────────────────────────────────────────────────
db.exec(`
  CREATE TABLE IF NOT EXISTS gc_users (
    id                INTEGER  PRIMARY KEY AUTOINCREMENT,
    email             TEXT     NOT NULL UNIQUE COLLATE NOCASE,
    password_hash     TEXT     NOT NULL,
    name              TEXT     NOT NULL,
    brand_name        TEXT,
    stripe_customer_id TEXT,
    plan              TEXT     NOT NULL DEFAULT 'free' CHECK(plan IN ('free','pro')),
    plan_expires_at   DATETIME,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS gc_projects (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES gc_users(id) ON DELETE CASCADE,
    name         TEXT    NOT NULL,
    client_name  TEXT,
    hourly_rate  REAL    DEFAULT 0,
    share_token  TEXT    NOT NULL UNIQUE,
    is_archived  INTEGER NOT NULL DEFAULT 0,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS gc_time_entries (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id       INTEGER NOT NULL REFERENCES gc_projects(id) ON DELETE CASCADE,
    description      TEXT,
    started_at       DATETIME NOT NULL,
    stopped_at       DATETIME,
    duration_seconds INTEGER
  );

  CREATE TABLE IF NOT EXISTS gc_client_views (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES gc_projects(id) ON DELETE CASCADE,
    ip_hash    TEXT,
    viewed_at  DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// ── Migrate gc_users if needed ────────────────────────────────────────────────
['plan_expires_at DATETIME', 'stripe_customer_id TEXT', 'brand_name TEXT'].forEach(col => {
  try { db.exec(`ALTER TABLE gc_users ADD COLUMN ${col}`); } catch (_) {}
});

// Seed data if empty
const clientCount = db.prepare('SELECT count(*) as count FROM clients').get().count;
if (clientCount === 0) {
  const insertClient = db.prepare('INSERT INTO clients (slug, name, status, dealValue, nextAction, engagement, industry) VALUES (?, ?, ?, ?, ?, ?, ?)');
  insertClient.run('acme-plumbing-co', 'Acme Plumbing Co', 'proposal', 7500, 'Send proposal and follow up', null, null);
  insertClient.run('tech-corp', 'Tech Corp', 'active', 12000, 'Weekly check-in', null, null);
  insertClient.run('mfg-inc', 'Manufacturing Inc', 'active', 8500, 'Monitor deployment', null, null);
}

const orderCount = db.prepare('SELECT count(*) as count FROM orders').get().count;
if (orderCount === 0) {
  const insertOrder = db.prepare('INSERT INTO orders (customerName, customerEmail, date, salesRep, orderType, productName, quantity, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)');
  insertOrder.run('Tech Corp', 'john@techcorp.com', '2026-01-20', 'Doc', 'New', 'Laser 1', 2, 'invoiced');
  insertOrder.run('Manufacturing Inc', 'sarah@mfg.com', '2026-01-21', 'Other guy', 'Renewal', 'Mini Laser 2', 1, 'shipped');
}

module.exports = db;
