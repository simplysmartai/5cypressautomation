# Website Layout & Foundation Plan

This document outlines the first draft layout for the Simply Smart Automation website, focusing on addressing current integration errors and establishing a strong technical foundation.

## 1. Directory Structure

The project follows a 3-layer architecture (Directive -> Orchestration -> Execution) with a standard Express.js web server structure.

```
/
├── public/                  # Static assets (served at root /)
│   ├── css/                 # Stylesheets
│   ├── js/                  # Client-side scripts
│   ├── data/                # JSON data sources (Fixes 404s)
│   │   ├── proposed_topics.json
│   │   ├── article-drafts.json
│   │   ├── author_roster.json
│   │   └── corrections.json
│   ├── index.html           # Landing page
│   ├── dashboard.html       # Client dashboard
│   ├── operations.html      # Internal operations
│   └── posts.json           # Public posts (Fixes 404)
├── server.js                # Express application entry point
├── routes/                  # (Future) API route handlers
└── README.md                # Project documentation
```

## 2. Integration Fixes

The following issues identified in the console logs will be addressed:

### A. Missing Data Sources (404 Errors)
The frontend expects several JSON data files which are currently missing. We will scaffold these in the `public/data/` directory.

- `/data/proposed_topics.json`: Store list of topics for content generation.
- `/data/article-drafts.json`: Store current drafts in progress.
- `/data/author_roster.json`: List of contributing authors.
- `/data/corrections.json`: Log of content corrections.
- `/public/posts.json`: Publicly available blog posts (accessed as `/posts.json` if in public root, or `/public/posts.json` if explicitly requested).

### B. API Method Not Allowed (405 Error)
- **Endpoint:** `/api/admin/pipeline-action`
- **Issue:** The server likely lacks a `POST` handler for this route (or it's missing entirely).
- **Fix:** Implement a `POST` route in `server.js` to handle pipeline actions (e.g., moving a lead, approving a draft).

### C. Deprecated Meta Tags
- **Issue:** `<meta name="apple-mobile-web-app-capable" content="yes">` is deprecated.
- **Fix:** Replace/Upgrade to `<meta name="mobile-web-app-capable" content="yes">` in HTML heads.

### D. Ad Blocker Warnings
- **Issue:** `ezoic/sa.min.js` and `adsbygoogle.js` blocked.
- **Resolution:** These are effective external scripts blocked by the client's browser extension (like uBlock Origin). This is expected behavior for dev environments and not a server error. We will ensure these scripts are only conditionally loaded or properly error-handled in production code.

## 3. Technology Stack

- **Backend:** Node.js with Express
- **Frontend:** HTML5, CSS3, Vanilla JS (lightweight, fast)
- **Data:** JSON files (for current phase), scalable to proper Database.
- **Architecture:** 3-Layer Agent Architecture (Directive, Orchestration, Execution).
