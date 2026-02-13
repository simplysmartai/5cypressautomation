#!/usr/bin/env python3
"""
Create an invoice for a client.
Usage: python create_invoice.py --client <slug> --type <type> --amount <amount> [options]
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Get the project root (parent of execution/)
PROJECT_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = PROJECT_ROOT / "clients"
CONFIG_DIR = PROJECT_ROOT / "config"


def get_next_invoice_number() -> str:
    """Get the next invoice number."""
    counter_file = CONFIG_DIR / "invoice-counter.json"
    
    today = datetime.now().strftime("%Y%m%d")
    
    if counter_file.exists():
        with open(counter_file, "r") as f:
            counter = json.load(f)
    else:
        counter = {"date": today, "sequence": 0}
    
    # Reset sequence if new day
    if counter.get("date") != today:
        counter = {"date": today, "sequence": 0}
    
    counter["sequence"] += 1
    
    # Save updated counter
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(counter_file, "w") as f:
        json.dump(counter, f)
    
    return f"INV-{today}-{counter['sequence']:03d}"


def load_client(slug: str) -> dict:
    """Load client information."""
    client_file = CLIENTS_DIR / slug / "info.json"
    if not client_file.exists():
        raise FileNotFoundError(f"Client '{slug}' not found")
    
    with open(client_file, "r") as f:
        return json.load(f)


def create_invoice(slug: str, invoice_type: str, amount: float,
                   description: str = None, project: str = None,
                   due_days: int = 7, payment_method: str = "stripe") -> dict:
    """
    Create an invoice for a client.
    
    Args:
        slug: Client slug
        invoice_type: Type of invoice (deposit, final, retainer, milestone)
        amount: Invoice amount in USD
        description: Line item description
        project: Project reference
        due_days: Days until due
        payment_method: Primary payment method
    
    Returns:
        Invoice data
    """
    client = load_client(slug)
    
    invoice_number = get_next_invoice_number()
    today = datetime.now()
    due_date = today + timedelta(days=due_days)
    
    # Generate description if not provided
    if not description:
        if invoice_type == "deposit":
            description = f"Project Deposit - 50%"
        elif invoice_type == "final":
            description = f"Final Payment - Project Completion"
        elif invoice_type == "retainer":
            description = f"Monthly Retainer - {today.strftime('%B %Y')}"
        elif invoice_type == "milestone":
            description = f"Milestone Payment"
        else:
            description = "Services Rendered"
    
    if project:
        description = f"{description} ({project})"
    
    invoice = {
        "invoice_number": invoice_number,
        "client": {
            "slug": slug,
            "name": client.get("name", slug),
            "email": client.get("contact", {}).get("email"),
            "address": client.get("address")
        },
        "type": invoice_type,
        "line_items": [
            {
                "description": description,
                "amount": amount
            }
        ],
        "subtotal": amount,
        "tax": 0,
        "total": amount,
        "payment": {
            "method": payment_method,
            "stripe_link": None,  # Would be generated via Stripe API
            "paypal_link": None   # Would be generated via PayPal API
        },
        "dates": {
            "issued": today.isoformat(),
            "due": due_date.strftime("%Y-%m-%d"),
            "due_display": due_date.strftime("%B %d, %Y")
        },
        "status": "draft",  # draft, sent, paid, overdue, cancelled
        "notes": None
    }
    
    # Create invoices directory
    invoices_dir = CLIENTS_DIR / slug / "invoices"
    invoices_dir.mkdir(exist_ok=True)
    
    # Save invoice JSON
    invoice_file = invoices_dir / f"{invoice_number}.json"
    with open(invoice_file, "w") as f:
        json.dump(invoice, f, indent=2)
    
    # Generate invoice markdown
    md_content = generate_invoice_markdown(invoice)
    md_file = invoices_dir / f"{invoice_number}.md"
    with open(md_file, "w") as f:
        f.write(md_content)
    
    print(f"✅ Invoice created: {invoice_number}")
    print(f"   📄 File: {invoice_file}")
    print(f"   💰 Amount: ${amount:,.2f}")
    print(f"   📅 Due: {due_date.strftime('%B %d, %Y')}")
    print(f"   👤 Client: {client.get('name', slug)}")
    
    return invoice


def generate_invoice_markdown(invoice: dict) -> str:
    """Generate invoice as markdown."""
    
    content = f"""# Invoice {invoice['invoice_number']}

**From:** 5 Cypress Automation LLC  
**To:** {invoice['client']['name']}  
**Date:** {datetime.fromisoformat(invoice['dates']['issued']).strftime('%B %d, %Y')}  
**Due:** {invoice['dates']['due_display']}

---

## Line Items

| Description | Amount |
|-------------|--------|
"""
    
    for item in invoice['line_items']:
        content += f"| {item['description']} | ${item['amount']:,.2f} |\n"
    
    content += f"""
---

| | |
|---|---|
| Subtotal | ${invoice['subtotal']:,.2f} |
| Tax | ${invoice['tax']:,.2f} |
| **Total Due** | **${invoice['total']:,.2f}** |

---

## Payment Options

**Pay Online:** [Click here to pay securely](#)

**PayPal:** payments@5cypresslabs.com

**ACH/Wire Transfer:**
- Bank: [Bank Name]
- Routing: [Routing Number]
- Account: [Account Number]

**Check:** Mail to 5 Cypress Automation LLC, [Address]

---

*Please include invoice number {invoice['invoice_number']} with your payment.*

Questions? Reply to this email or contact hello@5cypressautomation.com
"""
    
    return content


def main():
    parser = argparse.ArgumentParser(description="Create an invoice for a client")
    parser.add_argument("--client", "-c", required=True, help="Client slug")
    parser.add_argument("--type", "-t", required=True,
                        choices=["deposit", "final", "retainer", "milestone"],
                        help="Invoice type")
    parser.add_argument("--amount", "-a", type=float, required=True, help="Invoice amount")
    parser.add_argument("--description", "-d", help="Line item description")
    parser.add_argument("--project", "-p", help="Project reference")
    parser.add_argument("--due-days", type=int, default=7, help="Days until due (default: 7)")
    parser.add_argument("--payment-method", choices=["stripe", "paypal", "wire", "check"],
                        default="stripe", help="Primary payment method")
    
    args = parser.parse_args()
    
    try:
        create_invoice(
            slug=args.client,
            invoice_type=args.type,
            amount=args.amount,
            description=args.description,
            project=args.project,
            due_days=args.due_days,
            payment_method=args.payment_method
        )
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except ValueError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
