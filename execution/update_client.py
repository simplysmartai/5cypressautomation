#!/usr/bin/env python3
"""
Update client information.
Usage: python update_client.py <client_slug> [--status STATUS] [--field KEY=VALUE]
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# Get the project root (parent of execution/)
PROJECT_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = PROJECT_ROOT / "clients"


def load_client(slug: str) -> dict:
    """Load info.json for the given slug."""
    client_file = CLIENTS_DIR / slug / "info.json"
    if not client_file.exists():
        raise FileNotFoundError(f"Client '{slug}' not found at {client_file}")
    
    with open(client_file, "r") as f:
        return json.load(f)


def save_client(slug: str, data: dict) -> None:
    """Save info.json for the given slug."""
    client_file = CLIENTS_DIR / slug / "info.json"
    
    # Update the updated_at timestamp
    data["updated_at"] = datetime.now().isoformat()
    
    with open(client_file, "w") as f:
        json.dump(data, f, indent=2)


def update_client(slug: str, status: str = None, fields: dict = None) -> dict:
    """
    Update a client's information.
    
    Args:
        slug: Client slug/folder name
        status: New status (lead, discovery, proposal, negotiation, contract, active, completed, lost)
        fields: Dictionary of field key=value pairs to update
    
    Returns:
        Updated client data
    """
    client = load_client(slug)
    
    valid_statuses = ["lead", "discovery", "proposal", "negotiation", "contract", 
                      "active", "completed", "lost", "onboarding", "paused"]
    
    if status:
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
        
        old_status = client.get("status", "unknown")
        client["status"] = status
        
        # Track status history
        if "status_history" not in client:
            client["status_history"] = []
        
        client["status_history"].append({
            "from": old_status,
            "to": status,
            "changed_at": datetime.now().isoformat()
        })
        
        print(f"✓ Status updated: {old_status} → {status}")
    
    if fields:
        for key, value in fields.items():
            # Handle nested keys like "contact.email"
            if "." in key:
                parts = key.split(".")
                obj = client
                for part in parts[:-1]:
                    if part not in obj:
                        obj[part] = {}
                    obj = obj[part]
                obj[parts[-1]] = value
            else:
                client[key] = value
            
            print(f"✓ Updated {key} = {value}")
    
    save_client(slug, client)
    return client


def main():
    parser = argparse.ArgumentParser(description="Update client information")
    parser.add_argument("slug", help="Client slug (folder name)")
    parser.add_argument("--status", "-s", help="Update client status")
    parser.add_argument("--field", "-f", action="append", 
                        help="Field to update (format: key=value). Can be used multiple times.")
    parser.add_argument("--deal-value", type=float, help="Update deal value")
    parser.add_argument("--next-action", help="Set next action")
    parser.add_argument("--next-action-date", help="Set next action date (YYYY-MM-DD)")
    parser.add_argument("--lost-reason", help="Reason for losing deal (use with --status lost)")
    
    args = parser.parse_args()
    
    # Parse field arguments
    fields = {}
    if args.field:
        for f in args.field:
            if "=" not in f:
                print(f"Error: Field must be in format key=value, got: {f}")
                return
            key, value = f.split("=", 1)
            # Try to parse as JSON for complex values
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass  # Keep as string
            fields[key] = value
    
    # Add shorthand arguments to fields
    if args.deal_value is not None:
        fields["deal_value"] = args.deal_value
    if args.next_action:
        fields["next_action"] = args.next_action
    if args.next_action_date:
        fields["next_action_date"] = args.next_action_date
    if args.lost_reason:
        fields["lost_reason"] = args.lost_reason
    
    try:
        client = update_client(args.slug, status=args.status, fields=fields if fields else None)
        print(f"\n✅ Client '{args.slug}' updated successfully")
        print(f"   Status: {client.get('status', 'N/A')}")
        print(f"   Updated: {client.get('updated_at', 'N/A')}")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except ValueError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
