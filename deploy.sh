#!/bin/bash
set -e

echo "=========================================="
echo "5 Cypress Automation - Cloudflare Pages Deploy"
echo "=========================================="

npm run build
npx wrangler pages deploy web/dist

echo ""
echo "Deployment complete."
echo ""
echo "For normal production deploys, push to GitHub and let Cloudflare Pages build from the repo."
