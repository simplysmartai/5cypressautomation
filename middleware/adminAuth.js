/**
 * middleware/adminAuth.js
 * Simple Basic-Auth middleware for admin-protected routes.
 * Reads ADMIN_USER and ADMIN_PASS from environment variables.
 */
'use strict';

module.exports = function adminAuth(req, res, next) {
  const adminUser = process.env.ADMIN_USER;
  const adminPass = process.env.ADMIN_PASS;

  if (!adminUser || !adminPass) {
    return res.status(503).send('Admin authentication not configured');
  }

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Basic ')) {
    res.set('WWW-Authenticate', 'Basic realm="5Cypress Admin"');
    return res.status(401).send('Authentication required');
  }

  const [user, pass] = Buffer.from(authHeader.split(' ')[1], 'base64').toString('utf8').split(':');
  if (user === adminUser && pass === adminPass) return next();

  res.set('WWW-Authenticate', 'Basic realm="5Cypress Admin"');
  return res.status(401).send('Invalid credentials');
};
