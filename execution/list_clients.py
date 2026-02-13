#!/usr/bin/env python3
"""
List all clients and their current status
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = PROJECT_ROOT / "clients"


def list_clients(status_filter=None, format_type="table"):
    """List all clients with their information"""

    if not CLIENTS_DIR.exists():
        print("No clients directory found", file=sys.stderr)
        return []

    clients = []

    for client_dir in CLIENTS_DIR.iterdir():
        if not client_dir.is_dir() or client_dir.name.startswith("_"):
            continue

        info_file = client_dir / "info.json"
        if not info_file.exists():
            continue

        try:
            with open(info_file, "r") as f:
                info = json.load(f)

            # Apply status filter
            if status_filter and info.get("status") != status_filter:
                continue

            # Get last activity from history
            history_file = client_dir / "history.log"
            last_activity = "Never"
            if history_file.exists():
                with open(history_file, "r") as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1]
                        # Extract timestamp from [YYYY-MM-DD HH:MM:SS]
                        if last_line.startswith("["):
                            last_activity = last_line[1:20]

            clients.append({
                "name": info.get("client_name"),
                "slug": info.get("client_slug"),
                "email": info.get("contact_email"),
                "status": info.get("status", "unknown"),
                "workflows": len(info.get("workflows", [])),
                "deliverables": len(info.get("deliverables", [])),
                "start_date": info.get("start_date", "N/A"),
                "last_activity": last_activity,
                "path": str(client_dir)
            })

        except Exception as e:
            print(f"Warning: Could not load {client_dir.name}: {str(e)}", file=sys.stderr)
            continue

    # Sort by start_date (most recent first)
    clients.sort(key=lambda x: x.get("start_date", ""), reverse=True)

    if format_type == "json":
        print(json.dumps({"clients": clients, "total": len(clients)}, indent=2))
    else:
        # Print table
        print(f"\n{'Client':<30} {'Status':<15} {'Workflows':<12} {'Last Activity':<20}")
        print("-" * 80)
        for client in clients:
            print(f"{client['name']:<30} {client['status']:<15} {client['workflows']:<12} {client['last_activity']:<20}")
        print(f"\nTotal clients: {len(clients)}\n")

    return clients


def main():
    parser = argparse.ArgumentParser(description="List all clients")
    parser.add_argument("--status", choices=["onboarding", "active", "paused", "completed", "archived"],
                       help="Filter by status")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                       help="Output format")

    args = parser.parse_args()

    list_clients(status_filter=args.status, format_type=args.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
