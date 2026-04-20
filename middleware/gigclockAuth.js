'use strict';
const jwt = require('jsonwebtoken');

/**
 * Middleware: verifies GigClock JWT from Authorization: Bearer <token> header.
 * On success, attaches req.gcUser = { id, email, plan, plan_expires_at }.
 */
module.exports = function verifyGigClockToken(req, res, next) {
  const header = req.headers.authorization || '';
  if (!header.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  try {
    req.gcUser = jwt.verify(header.slice(7), process.env.GC_JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
};
