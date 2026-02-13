#!/usr/bin/env python3
"""
Create a professional proposal from discovery information.
Usage: python create_proposal.py --client <slug> --package <package> [options]
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from string import Template

# Get the project root (parent of execution/)
PROJECT_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = PROJECT_ROOT / "clients"
CONFIG_DIR = PROJECT_ROOT / "config"
TEMPLATES_DIR = PROJECT_ROOT / "templates"


def load_pricing() -> dict:
    """Load pricing configuration."""
    pricing_file = CONFIG_DIR / "pricing.json"
    with open(pricing_file, "r") as f:
        return json.load(f)


def load_client(slug: str) -> dict:
    """Load client information."""
    client_file = CLIENTS_DIR / slug / "info.json"
    if not client_file.exists():
        raise FileNotFoundError(f"Client '{slug}' not found")
    
    with open(client_file, "r") as f:
        return json.load(f)


def load_discovery(slug: str) -> str:
    """Load discovery notes if available."""
    discovery_file = CLIENTS_DIR / slug / "discovery.md"
    if discovery_file.exists():
        with open(discovery_file, "r") as f:
            return f.read()
    return None


def load_proposal_template() -> str:
    """Load the proposal template."""
    template_file = TEMPLATES_DIR / "proposals" / "proposal-template.md"
    with open(template_file, "r") as f:
        return f.read()


def create_proposal(slug: str, package: str, custom_price: float = None,
                    discount: float = None, rush: bool = False,
                    custom_scope: dict = None) -> dict:
    """
    Generate a proposal for a client.
    
    Args:
        slug: Client slug
        package: Package type (starter, growth, scale, custom)
        custom_price: Override package price
        discount: Percentage discount (0-25)
        rush: Add rush delivery premium
        custom_scope: Custom scope details
    
    Returns:
        Proposal metadata including file path
    """
    client = load_client(slug)
    pricing = load_pricing()
    discovery = load_discovery(slug)
    
    # Determine pricing
    if package == "custom":
        if not custom_price:
            raise ValueError("Custom package requires --custom-price")
        package_data = {
            "name": "Custom",
            "price": custom_price,
            "description": "Custom automation project",
            "timeline": "TBD",
            "includes": custom_scope.get("includes", []) if custom_scope else []
        }
    else:
        if package not in pricing["packages"]:
            raise ValueError(f"Invalid package: {package}")
        package_data = pricing["packages"][package]
    
    # Calculate price
    base_price = custom_price or package_data["price"]
    
    # Apply rush premium
    if rush:
        rush_modifier = pricing["common_addons"]["rush_delivery"]["price_modifier"]
        base_price = base_price * rush_modifier
    
    # Apply discount
    if discount:
        if discount > 25:
            raise ValueError("Maximum discount is 25%")
        base_price = base_price * (1 - discount / 100)
    
    total_price = round(base_price, 2)
    deposit = round(total_price * pricing["payment_terms"]["deposit"], 2)
    final_payment = round(total_price - deposit, 2)
    
    # Generate proposal data
    today = datetime.now()
    expiration = today + timedelta(days=14)
    
    proposal_data = {
        "client": {
            "name": client.get("name", slug),
            "contact": client.get("contact", {})
        },
        "package": {
            "name": package_data.get("name", package.title()),
            "description": package_data.get("description", ""),
            "includes": package_data.get("includes", []),
            "timeline": package_data.get("timeline", "TBD")
        },
        "pricing": {
            "base_price": package_data["price"],
            "rush_applied": rush,
            "discount_percent": discount or 0,
            "total_price": total_price,
            "deposit": deposit,
            "final_payment": final_payment
        },
        "dates": {
            "created": today.isoformat(),
            "expiration": expiration.strftime("%Y-%m-%d"),
            "valid_days": 14
        },
        "status": "draft"
    }
    
    # Create proposals directory
    proposals_dir = CLIENTS_DIR / slug / "proposals"
    proposals_dir.mkdir(exist_ok=True)
    
    # Generate proposal filename
    proposal_filename = f"proposal-{today.strftime('%Y-%m-%d')}"
    proposal_file = proposals_dir / f"{proposal_filename}.json"
    
    # Save proposal metadata
    with open(proposal_file, "w") as f:
        json.dump(proposal_data, f, indent=2)
    
    # Generate markdown proposal
    md_content = generate_proposal_markdown(proposal_data, discovery)
    md_file = proposals_dir / f"{proposal_filename}.md"
    with open(md_file, "w") as f:
        f.write(md_content)
    
    print(f"✅ Proposal created for {client.get('name', slug)}")
    print(f"   📄 Markdown: {md_file}")
    print(f"   📊 Metadata: {proposal_file}")
    print(f"\n   Package: {package_data.get('name', package.title())}")
    print(f"   Total: ${total_price:,.2f}")
    print(f"   Deposit: ${deposit:,.2f}")
    print(f"   Valid until: {expiration.strftime('%B %d, %Y')}")
    
    return proposal_data


def generate_proposal_markdown(data: dict, discovery: str = None) -> str:
    """Generate the markdown proposal content."""
    
    client_name = data["client"]["name"]
    package = data["package"]
    pricing = data["pricing"]
    dates = data["dates"]
    
    # Format includes as bullet list
    includes_list = "\n".join(f"- {item}" for item in package.get("includes", []))
    
    content = f"""# Automation Proposal

**Prepared for:** {client_name}  
**Prepared by:** 5 Cypress Automation  
**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Valid Until:** {dates['expiration']}

---

## Executive Summary

We'll help {client_name} build resilient automation systems that scale with their growth. This proposal outlines our architecture, timeline, and investment.

---

## Proposed Solution

### {package['name']} Package

{package.get('description', '')}

### What's Included

{includes_list}

### Timeline

**Estimated Duration:** {package.get('timeline', 'TBD')}

---

## Investment

| Item | Amount |
|------|--------|
| {package['name']} Package | ${pricing['total_price']:,.2f} |

"""
    
    if pricing.get('discount_percent', 0) > 0:
        content += f"*Includes {pricing['discount_percent']}% discount*\n\n"
    
    if pricing.get('rush_applied'):
        content += "*Rush delivery premium applied*\n\n"
    
    content += f"""### Payment Terms

| Milestone | Amount | When |
|-----------|--------|------|
| Deposit | ${pricing['deposit']:,.2f} (50%) | To begin work |
| Final | ${pricing['final_payment']:,.2f} (50%) | Upon completion |

We accept credit card, PayPal, ACH transfer, or check.

---

## Next Steps

Ready to move forward?

1. **Reply to this email** confirming you'd like to proceed
2. **We'll send the contract** for your review and signature
3. **Submit the deposit** to lock in your spot
4. **We schedule kickoff** and get started!

---

*This proposal is valid until {dates['expiration']}.*

**5 Cypress Automation**  
hello@5cypressautomation.com
"""
    
    return content


def main():
    parser = argparse.ArgumentParser(description="Create a proposal for a client")
    parser.add_argument("--client", "-c", required=True, help="Client slug")
    parser.add_argument("--package", "-p", required=True, 
                        choices=["starter", "growth", "scale", "custom"],
                        help="Package type")
    parser.add_argument("--custom-price", type=float, help="Custom price (required for custom package)")
    parser.add_argument("--discount", type=float, help="Discount percentage (max 25%)")
    parser.add_argument("--rush", action="store_true", help="Apply rush delivery premium (50%)")
    parser.add_argument("--output", choices=["markdown", "pdf", "google-doc"], 
                        default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    try:
        create_proposal(
            slug=args.client,
            package=args.package,
            custom_price=args.custom_price,
            discount=args.discount,
            rush=args.rush
        )
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except ValueError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
