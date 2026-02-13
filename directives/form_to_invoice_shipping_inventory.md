# Directive: Form to Invoice, Shipping & Inventory Automation

**Use Case:** Automated order fulfillment from form submission through delivery  
**Trigger:** Microsoft Forms submission (or similar form platform)  
**Platforms:** QuickBooks Online, Shipping Provider (ShipStation/Shopify/etc.), Inventory System  
**Execution Scripts:** `create_qbo_invoice.py`, `create_shipping_order.py`, `update_inventory.py`, `send_order_confirmation.py`

---

## Process Overview

### Input
Microsoft Forms response containing:
- Customer information (name, email, phone, address)
- Order details (products, quantities, special instructions)
- Payment method
- Shipping method preference

### Output
- QuickBooks invoice created and sent
- Shipping order created with label
- Inventory updated (stock deducted)
- Customer confirmation email sent
- Admin team notified via Slack

---

## Workflow Steps

### Step 1: Form Webhook Trigger

**What Happens:**
- Microsoft Forms submits response
- Power Automate sends webhook to n8n
- n8n receives JSON payload with form data

**Data Validation:**
```python
required_fields = [
    'customer_name',
    'customer_email',
    'shipping_address',
    'products',  # array of {sku, quantity}
    'payment_method',
    'shipping_method'
]
```

**Error Handling:**
- If required fields missing → Send alert to admin, halt workflow
- If email format invalid → Flag for manual review
- If address incomplete → Request clarification from customer

---

### Step 2: Inventory Check

**Tool:** `execution/update_inventory.py` (check mode)

**Purpose:** Verify products are in stock before creating invoice

**Process:**
```python
for product in order_products:
    available_qty = get_inventory_level(product.sku)
    if available_qty < product.quantity:
        # OUT OF STOCK
        send_out_of_stock_notification(customer_email, product)
        log_backorder(order_id, product)
        halt_workflow()
```

**Configuration:**
- `INVENTORY_SOURCE` = "quickbooks" or "google_sheets" or "custom"
- `LOW_STOCK_THRESHOLD` = 10 (send alert when stock falls below)
- `ALLOW_BACKORDERS` = false (reject order if out of stock)

**Outputs:**
- ✅ All products available → Continue to invoice creation
- ❌ Product(s) out of stock → Notify customer, halt workflow

---

### Step 3: Create QuickBooks Invoice

**Tool:** `execution/create_qbo_invoice.py`

**Inputs:**
```python
invoice_data = {
    'customer': {
        'name': form_data['customer_name'],
        'email': form_data['customer_email'],
        'phone': form_data['customer_phone'],
        'billing_address': form_data['billing_address'],
        'shipping_address': form_data['shipping_address']
    },
    'line_items': [
        {
            'sku': 'PROD-001',
            'description': 'Product Name',
            'quantity': 2,
            'rate': 49.99,
            'tax_code': 'TAX'  # if sales tax required
        }
    ],
    'payment_terms': 'Due on receipt',  # or 'Net 30', etc.
    'shipping_method': 'Standard',
    'notes': form_data['special_instructions']
}
```

**Process:**
1. **Customer Lookup/Creation**
   - Search QuickBooks for existing customer by email
   - If not found, create new customer record
   - Return customer ID

2. **Line Item Mapping**
   - Match form product selections to QuickBooks items
   - Calculate subtotal, tax, shipping charges
   - Apply any discounts or promotions

3. **Invoice Creation**
   - Create invoice in QuickBooks with "Pending" status
   - Generate invoice PDF
   - Return invoice ID and PDF URL

4. **Send Invoice (Optional)**
   - Email invoice to customer via QuickBooks
   - Or attach to custom confirmation email

**Configuration:**
```bash
QUICKBOOKS_CLIENT_ID=your_client_id
QUICKBOOKS_CLIENT_SECRET=your_client_secret
QUICKBOOKS_REALM_ID=your_company_id
QUICKBOOKS_REFRESH_TOKEN=your_refresh_token
QUICKBOOKS_SANDBOX=false  # true for testing
AUTO_SEND_INVOICE=false  # true to email via QBO
CALCULATE_SALES_TAX=true  # true if sales tax required
```

**Error Handling:**
- API rate limit hit → Wait 60 seconds, retry (max 3 attempts)
- Customer creation fails → Alert admin, use generic "Walk-in Customer"
- Invoice creation fails → Log error, create manual task for accounting team
- Network timeout → Retry with exponential backoff

**Outputs:**
- Invoice ID
- Invoice PDF URL
- Customer ID (for future orders)
- Invoice total amount

---

### Step 4: Create Shipping Order

**Tool:** `execution/create_shipping_order.py`

**Supported Providers:**
- ShipStation
- Shopify Fulfillment
- ShipBob
- EasyShip
- Custom API

**Inputs:**
```python
shipping_data = {
    'order_number': invoice_id or unique_order_number,
    'order_date': datetime.now().isoformat(),
    'customer': {
        'name': customer_name,
        'email': customer_email,
        'phone': customer_phone,
        'address': {
            'street1': shipping_address_line1,
            'street2': shipping_address_line2,
            'city': city,
            'state': state,
            'postal_code': zip_code,
            'country': 'US'
        }
    },
    'items': [
        {
            'sku': 'PROD-001',
            'name': 'Product Name',
            'quantity': 2,
            'weight': {'value': 1.5, 'units': 'pounds'},
            'dimensions': {'length': 10, 'width': 8, 'height': 6, 'units': 'inches'}
        }
    ],
    'shipping_method': 'standard',  # 'express', 'overnight'
    'insurance': false,
    'signature_required': false
}
```

**Process:**
1. **Address Validation**
   - Verify address is valid and deliverable
   - Suggest corrections if needed
   - Flag PO boxes or military addresses

2. **Carrier Selection**
   - Map form shipping method to carrier service:
     - "Standard" → USPS First Class or UPS Ground
     - "Express" → FedEx 2-Day
     - "Overnight" → FedEx Priority Overnight

3. **Order Creation**
   - Submit order to shipping provider API
   - Receive order confirmation and order ID

4. **Label Generation (Optional)**
   - Request shipping label (if auto-fulfillment enabled)
   - Download label PDF
   - Store label URL for warehouse access

5. **Tracking Number Capture**
   - Extract tracking number from API response
   - Store for customer notification and dashboard

**Configuration:**
```bash
SHIPPING_PROVIDER=shipstation  # or shopify, shipbob, easyship, custom
SHIPPING_API_KEY=your_api_key
SHIPPING_API_SECRET=your_api_secret
SHIPPING_STORE_ID=your_store_id  # for ShipStation
AUTO_GENERATE_LABEL=false  # true for immediate label creation
DEFAULT_CARRIER=usps  # usps, fedex, ups
DEFAULT_SERVICE_CODE=usps_first_class_mail
```

**Error Handling:**
- Address validation fails → Notify customer, request corrected address
- API rate limit → Wait and retry
- Label generation fails → Create manual fulfillment task
- Carrier service unavailable → Try alternate carrier

**Outputs:**
- Shipping order ID
- Tracking number (if available)
- Estimated delivery date
- Shipping label PDF URL (if generated)

---

### Step 5: Update Inventory

**Tool:** `execution/update_inventory.py`

**Purpose:** Deduct stock after successful order placement

**Process:**
```python
for product in order_products:
    current_qty = get_inventory_level(product.sku)
    new_qty = current_qty - product.quantity
    
    update_inventory(product.sku, new_qty)
    
    # Check for low stock
    if new_qty <= LOW_STOCK_THRESHOLD:
        send_low_stock_alert(product.sku, new_qty)
        
    # Suggest reorder
    if new_qty <= REORDER_POINT:
        create_reorder_suggestion(product.sku, OPTIMAL_REORDER_QTY)
```

**Inventory Source Options:**

#### Option A: QuickBooks Inventory
- Use QuickBooks Inventory API
- Update item quantities directly
- Sync with accounting automatically

#### Option B: Google Sheets
- Read from "Inventory" sheet
- Update quantities via Google Sheets API
- Simpler setup, no QBO inventory module needed

#### Option C: Custom Database
- PostgreSQL, MySQL, or similar
- Connect via Python database adapter
- Full control over data structure

**Configuration:**
```bash
INVENTORY_SOURCE=quickbooks  # or google_sheets, custom_db
INVENTORY_SHEET_ID=your_sheet_id  # if using Google Sheets
INVENTORY_DB_CONNECTION_STRING=postgresql://...  # if using database
LOW_STOCK_THRESHOLD=10
REORDER_POINT=5
OPTIMAL_REORDER_QTY=50
```

**Low Stock Alert:**
- Triggers when inventory falls below threshold
- Sends Slack message to operations channel
- Includes: SKU, current quantity, suggested reorder quantity
- Optional: Auto-create purchase order draft

**Error Handling:**
- Inventory update fails → Log error, alert admin (critical!)
- Negative inventory detected → Halt future orders for that SKU
- Inventory system unavailable → Queue update for retry

**Outputs:**
- Updated inventory levels (per SKU)
- Low stock alerts (if triggered)
- Reorder suggestions (if needed)

---

### Step 6: Send Customer Confirmation

**Tool:** `execution/send_order_confirmation.py`

**Purpose:** Professional order confirmation email with all details

**Email Template:**
```
Subject: Order Confirmation #[ORDER_NUMBER] - Thank You!

Hi [CUSTOMER_NAME],

Thank you for your order! We're excited to get your items to you.

ORDER SUMMARY
-------------
Order Number: [ORDER_NUMBER]
Order Date: [ORDER_DATE]
Payment Method: [PAYMENT_METHOD]

ITEMS ORDERED
-------------
[PRODUCT_NAME] x [QTY] - $[PRICE]
[PRODUCT_NAME] x [QTY] - $[PRICE]

Subtotal: $[SUBTOTAL]
Shipping: $[SHIPPING_COST]
Tax: $[TAX]
Total: $[TOTAL]

SHIPPING DETAILS
----------------
Method: [SHIPPING_METHOD]
Estimated Delivery: [DELIVERY_DATE]
Tracking Number: [TRACKING_NUMBER] (available soon)
Track your order: [TRACKING_URL]

QUESTIONS?
----------
Email: support@company.com
Phone: (555) 123-4567

[INVOICE_PDF_ATTACHMENT]

Thanks again!
[COMPANY_NAME] Team
```

**Configuration:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=orders@company.com
SMTP_PASSWORD=your_app_password
ORDER_CONFIRMATION_FROM=orders@company.com
ORDER_CONFIRMATION_BCC=admin@company.com  # optional
ATTACH_INVOICE_PDF=true
INCLUDE_TRACKING_LINK=true
```

**Error Handling:**
- Email send fails → Retry 3 times
- SMTP connection error → Use backup SMTP server
- Customer email bounces → Flag for manual follow-up

---

### Step 7: Admin Notification

**Tool:** Slack webhook

**Purpose:** Notify team of new order for monitoring

**Slack Message:**
```
🎉 New Order Received!

Order: #ORD-12345
Customer: John Doe (john@email.com)
Total: $149.97
Items: 3

✅ Invoice: INV-67890 (QuickBooks)
✅ Shipping: SHP-11223 (ShipStation)
✅ Inventory: Updated
✅ Email: Sent

View Dashboard: [LINK]
```

**Configuration:**
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#orders
SLACK_ALERT_ON_ERROR=true
```

---

## Error Scenarios & Recovery

### Scenario 1: Inventory Out of Stock
**Trigger:** Product(s) not available in requested quantity

**Recovery:**
1. Send customer email: "Item temporarily unavailable"
2. Offer options:
   - Wait for restock (provide ETA)
   - Substitute with similar product
   - Cancel order and refund
3. Create backorder record
4. Alert purchasing team to reorder

### Scenario 2: QuickBooks API Failure
**Trigger:** Invoice creation fails (API error, network issue, etc.)

**Recovery:**
1. Retry 3 times with exponential backoff (1s, 5s, 15s)
2. If still fails:
   - Log error with full context
   - Create manual task in project management system
   - Alert accounting team via Slack
   - Send customer email: "Order received, invoice coming soon"
3. Continue with shipping order creation (don't halt entire workflow)

### Scenario 3: Shipping Provider Unavailable
**Trigger:** Shipping API down or rate limit exceeded

**Recovery:**
1. Queue shipping order for later processing
2. Set retry schedule (every 15 minutes for 2 hours)
3. If still fails after 2 hours:
   - Alert operations team
   - Create manual fulfillment task
4. Send customer email: "Order confirmed, tracking info coming soon"

### Scenario 4: Invalid Shipping Address
**Trigger:** Address validation fails

**Recovery:**
1. Halt workflow (don't create invoice yet)
2. Send customer email requesting address correction
3. Provide link to address correction form
4. Hold order in "Pending Address Verification" queue
5. Resume workflow once corrected address received

### Scenario 5: Payment Method Declined
**Trigger:** Credit card declined or payment fails

**Recovery:**
1. Do not create invoice or shipping order
2. Send customer email: "Payment issue detected"
3. Provide link to update payment method
4. Hold order in "Payment Required" queue
5. Resume workflow once payment successful

---

## Configuration File

**File:** `config/order_fulfillment_config.json`

```json
{
  "quickbooks": {
    "client_id": "QUICKBOOKS_CLIENT_ID",
    "client_secret": "QUICKBOOKS_CLIENT_SECRET",
    "realm_id": "QUICKBOOKS_REALM_ID",
    "refresh_token": "QUICKBOOKS_REFRESH_TOKEN",
    "sandbox": false,
    "auto_send_invoice": false,
    "calculate_sales_tax": true,
    "default_payment_terms": "Due on receipt"
  },
  "shipping": {
    "provider": "shipstation",
    "api_key": "SHIPPING_API_KEY",
    "api_secret": "SHIPPING_API_SECRET",
    "store_id": "SHIPPING_STORE_ID",
    "auto_generate_label": false,
    "carrier_mappings": {
      "standard": {"carrier": "usps", "service": "usps_first_class_mail"},
      "express": {"carrier": "fedex", "service": "fedex_2day"},
      "overnight": {"carrier": "fedex", "service": "fedex_priority_overnight"}
    }
  },
  "inventory": {
    "source": "quickbooks",
    "low_stock_threshold": 10,
    "reorder_point": 5,
    "optimal_reorder_qty": 50,
    "allow_backorders": false
  },
  "email": {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "orders@company.com",
    "smtp_password": "SMTP_PASSWORD",
    "from_address": "orders@company.com",
    "bcc_address": "admin@company.com",
    "attach_invoice_pdf": true
  },
  "notifications": {
    "slack_webhook_url": "SLACK_WEBHOOK_URL",
    "slack_channel": "#orders",
    "alert_on_error": true,
    "alert_on_low_stock": true
  },
  "error_handling": {
    "max_retries": 3,
    "retry_delay_seconds": [1, 5, 15],
    "queue_failed_orders": true,
    "admin_alert_on_failure": true
  }
}
```

---

## Testing Checklist

### Phase 1: Component Testing
- [ ] Form webhook receives data correctly
- [ ] QuickBooks authentication works
- [ ] Customer lookup/creation succeeds
- [ ] Invoice creation succeeds
- [ ] Invoice PDF generates correctly
- [ ] Shipping provider authentication works
- [ ] Shipping order creation succeeds
- [ ] Inventory update succeeds
- [ ] Email sends successfully

### Phase 2: Integration Testing
- [ ] End-to-end workflow completes with sample order
- [ ] All data passes correctly between steps
- [ ] Error handling triggers correctly
- [ ] Retry logic works as expected
- [ ] Admin notifications sent

### Phase 3: Production Testing
- [ ] Process 10 test orders successfully
- [ ] Verify invoices in QuickBooks match form data
- [ ] Verify shipping orders created correctly
- [ ] Verify inventory levels accurate
- [ ] Verify customer emails received

### Phase 4: Scale Testing
- [ ] Process 50 orders in 1 hour (stress test)
- [ ] Verify no data loss or corruption
- [ ] Verify error rate <1%
- [ ] Verify system performance acceptable

---

## Monitoring & Maintenance

### Daily Checks
- Review error logs in n8n
- Check Slack alerts for failed orders
- Verify inventory levels accurate
- Review dashboard for anomalies

### Weekly Checks
- Review order processing metrics (volume, errors, avg time)
- Check API rate limit usage
- Update product catalog if new products added
- Review and clear failed order queue

### Monthly Checks
- Review and optimize workflow performance
- Update API credentials if needed
- Train new team members on monitoring
- Identify automation expansion opportunities

---

## Success Metrics

### Week 1-2 (MVP)
- **Goal:** 95% success rate
- **Metric:** Orders processed without errors / Total orders
- **Target:** 19/20 orders successful

### Week 3-4 (Full Automation)
- **Goal:** 99% success rate, <2 min avg processing time
- **Metric:** Successful orders / Total orders, Avg time per order
- **Target:** 99/100 orders, <2 minutes

### Month 3 (Mature System)
- **Goal:** 99.9% uptime, <30 sec avg processing time
- **Metric:** System availability, Avg processing time
- **Target:** 99.9% uptime, <30 seconds per order

---

**This directive provides complete guidance for building a bulletproof form-to-fulfillment automation system.**
