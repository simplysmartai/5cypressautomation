#!/usr/bin/env python3
"""
Log activity to a client's history
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = PROJECT_ROOT / "clients"


def log_activity(client_slug, message, activity_type="general"):
    """Add an entry to the client's history log"""

    client_path = CLIENTS_DIR / client_slug

    if not client_path.exists():
        print(f"Error: Client not found: {client_slug}", file=sys.stderr)
        return False

    history_file = client_path / "history.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{activity_type.upper()}] {message}\n"

    try:
        with open(history_file, "a") as f:
            f.write(entry)

        result = {
            "success": True,
            "client_slug": client_slug,
            "timestamp": timestamp,
            "message": message,
            "type": activity_type
        }

        print(json.dumps(result, indent=2))
        return True

    except Exception as e:
        print(f"Error: Failed to log activity: {str(e)}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Log activity to client history")
    parser.add_argument("--client", required=True, help="Client slug")
    parser.add_argument("--message", required=True, help="Activity message")
    parser.add_argument("--type", default="general",
                       choices=["general", "meeting", "email", "workflow", "deliverable", "status"],
                       help="Activity type")

    args = parser.parse_args()

    success = log_activity(args.client, args.message, args.type)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
