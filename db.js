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
`);

// Seed data if empty
const clientCount = db.prepare('SELECT count(*) as count FROM clients').get().count;
if (clientCount === 0) {
  const insertClient = db.prepare('INSERT INTO clients (slug, name, status, dealValue, nextAction, engagement, industry) VALUES (?, ?, ?, ?, ?, ?, ?)');
  insertClient.run('remy-lasers', 'Remy Lasers', 'prospecting', 2500, 'Present 30-day trial program to CFO', 'trial_program', 'Laser Manufacturing');
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
