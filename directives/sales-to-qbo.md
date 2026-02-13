# Sales to QBO Directive

## Goal
Build a client-hosted workflow that takes a sales form submission, validates input, checks inventory, creates/updates the customer in QuickBooks Online, creates an invoice, and flags oversells.

## Inputs
- `customer`: name, email, phone (at least name + email)
- `items`: list of `{ sku, qty }`
- `shipping_address`: line1, line2 (optional), city, state, postal_code, country

## Process

### Step 1: Validate Input
- Validate with Zod (Node) or Pydantic (Python)
- Reject missing customer, empty items list, or invalid SKU/qty values
- Normalize address fields and email casing

### Step 2: Inventory Check
- Look up each SKU in inventory source (local DB or inventory API)
- Compare available qty vs requested qty
- If any item oversells, flag and continue based on policy:
  - Default: create invoice with a warning flag and backorder note
  - Optional: stop and return 409 with oversell details

### Step 3: QBO Customer and Invoice
- Find or create customer in QBO by email
- Create invoice with line items for each SKU/qty
- Attach shipping address to the invoice
- Store QBO invoice id for tracking

### Step 4: Return Response
- Return invoice id, status, and any oversell flags
- Log every API call and response summary (no secrets)

## Outputs
- Node.js Express app implementing the workflow
- Unit/integration tests (Jest) with dry-run mode
- `.env.example` with all required configuration keys

## Tools Used
- QBO SDK (official)
- Inventory API or DB client
- Validation library (Zod)

## Error Handling
- Input validation errors: return 400 with field details
- QBO API errors: retry on 429/5xx with backoff, return 502 on failure
- Inventory lookup failure: return 503 with retry guidance
- Idempotency: use a request id to avoid duplicate invoices

## Edge Cases
- Duplicate customer emails with different names
- SKU not found in inventory
- Partial inventory (some items in stock, some oversold)
- QBO rate limits or auth expiration

## Environment Variables
- `QBO_CLIENT_ID`, `QBO_CLIENT_SECRET`, `QBO_REDIRECT_URI`
- `QBO_REALM_ID`, `QBO_REFRESH_TOKEN`
- `INVENTORY_API_URL` (or DB connection string)
- `APP_PORT`, `NODE_ENV`

## Success Criteria
- [ ] Valid input creates QBO invoice
- [ ] Oversells are flagged and surfaced in response
- [ ] Tests cover happy path + oversell + QBO error
- [ ] `.env.example` documents all required keys

## Example Usage
```
POST /api/sales
{
  "customer": {"name":"Acme Co","email":"ops@acme.com","phone":"555-0100"},
  "items": [{"sku":"SKU-123","qty":2},{"sku":"SKU-456","qty":1}],
  "shipping_address": {"line1":"1 Main St","city":"Austin","state":"TX","postal_code":"78701","country":"US"}
}
```
