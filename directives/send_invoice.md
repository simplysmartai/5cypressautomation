# Send Invoice Directive

> Generate and send invoices with payment links.

## Purpose

Create professional invoices and collect payment via Stripe, PayPal, or other methods.

## Invoice Types

### 1. Deposit Invoice
- 50% of project total
- Due before work begins
- References SOW/proposal

### 2. Final Invoice
- Remaining 50%
- Due upon completion, before handoff
- References completed deliverables

### 3. Retainer Invoice
- Monthly recurring
- Billed on the 1st
- References retainer agreement

### 4. Milestone Invoice
- For large projects with phase payments
- Due upon milestone completion

## Execution

### Generate Invoice
```bash
python execution/create_invoice.py \
  --client "client-slug" \
  --type "deposit" \
  --amount 3750 \
  --description "Growth Package - 50% Deposit" \
  --due-days 7 \
  --payment-method "stripe"
```

**Parameters:**
- `--client`: Client slug
- `--type`: deposit, final, retainer, milestone
- `--amount`: Invoice amount in USD
- `--description`: Line item description
- `--project`: Project reference (optional)
- `--due-days`: Days until due (default: 7)
- `--payment-method`: stripe, paypal, wire, check

### Script Actions

1. Load client info
2. Generate invoice number (INV-YYYYMMDD-XXX)
3. Create Stripe/PayPal payment link
4. Generate invoice PDF
5. Send email with invoice + payment link
6. Save to `clients/[slug]/invoices/`
7. Log activity

## Invoice Numbering

Format: `INV-YYYYMMDD-XXX`
- Example: `INV-20260121-001`
- Sequential per day
- Tracked in `config/invoice-counter.json`

## Payment Methods

### Stripe (Preferred)
- Create payment link via API
- 2.9% + $0.30 fee
- Instant confirmation
- Automatic receipt

### PayPal
- Create invoice via API
- Similar fees
- Some clients prefer it

### Wire Transfer
- For large invoices ($5,000+)
- Include bank details in invoice
- Manual confirmation needed

### Check
- Include mailing address
- Longer processing time
- For traditional clients

## Email Template

**Subject:** Invoice #{invoice_number} from 5 Cypress Labs

```
Hi {first_name},

Please find attached invoice #{invoice_number} for {description}. This represents the next phase of your architecture implementation.

**Amount Due:** ${amount}
**Due Date:** {due_date}

[Pay Securely via Stripe →] {stripe_link}

Or pay via:
- PayPal: {paypal_link}
- Wire transfer: Banking details available in the attached PDF

If you have any questions regarding this invoice or the associated deliverables, please reply directly to this thread.

Thank you for partnering with 5 Cypress Labs.

Best,
The 5 Cypress Labs Team
```

## Payment Tracking

After payment received:
1. Mark invoice as paid in client folder
2. Update project status if deposit
3. Send thank you / next steps email
4. Log activity

## Overdue Follow-Up

- Day 7 (due date): Automatic reminder
- Day 14: Personal follow-up email
- Day 21: Phone call
- Day 30: Escalation / pause work

## Output

Invoices saved to:
```
clients/[slug]/invoices/
├── INV-20260121-001.pdf
├── INV-20260121-001.json  # Metadata + payment status
└── INV-20260128-002.pdf
```

## Related Directives
- `send_contract.md` - Contract before invoice
- `manage_pipeline.md` - Track payment status
- `onboard_client.md` - After deposit received
