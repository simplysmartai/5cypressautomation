#!/usr/bin/env python3
"""
Create a new client folder with structured organization
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = PROJECT_ROOT / "clients"


def slugify(text):
    """Convert text to URL-friendly slug"""
    return text.lower().replace(" ", "-").replace("&", "and").replace(",", "")


def create_client_folder(client_name, contact_email, contact_name=None, phone=None,
                        website=None, industry=None, tags=None):
    """Create a new client folder with all necessary structure"""

    # Create slug for folder name
    client_slug = slugify(client_name)
    client_path = CLIENTS_DIR / client_slug

    # Check if client already exists
    if client_path.exists():
        print(f"Error: Client folder already exists: {client_path}", file=sys.stderr)
        return None

    # Create directory structure
    try:
        client_path.mkdir(parents=True, exist_ok=False)
        (client_path / "workflows").mkdir()
        (client_path / "communications" / "emails").mkdir(parents=True)
        (client_path / "deliverables").mkdir()

        # Create info.json
        info = {
            "client_name": client_name,
            "client_slug": client_slug,
            "contact_name": contact_name or "",
            "contact_email": contact_email,
            "phone": phone or "",
            "website": website or "",
            "status": "onboarding",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "industry": industry or "",
            "tags": tags or [],
            "workflows": [],
            "deliverables": [],
            "notes": ""
        }

        with open(client_path / "info.json", "w") as f:
            json.dump(info, f, indent=2)

        # Create notes.md
        notes_content = f"""# {client_name} - Notes

## Client Overview
- **Contact**: {contact_name or 'TBD'}
- **Email**: {contact_email}
- **Status**: Onboarding
- **Start Date**: {datetime.now().strftime("%Y-%m-%d")}

## Goals & Objectives
[Document client goals here]

## Current Workflows
[List and track workflows in development]

## Meeting Notes
[Add notes from calls and meetings]

## Action Items
- [ ] Complete kickoff call
- [ ] Define workflow requirements
- [ ] Begin implementation

## Important Links
[Add links to shared documents, tools, etc.]
"""

        with open(client_path / "notes.md", "w") as f:
            f.write(notes_content)

        # Create history.log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = f"[{timestamp}] Client folder created - Status: onboarding\n"

        with open(client_path / "history.log", "w") as f:
            f.write(history_entry)

        # Create README
        readme_content = f"""# {client_name}

**Status**: {info['status'].capitalize()}
**Contact**: {contact_email}
**Started**: {info['start_date']}

## Folder Structure

- `info.json` - Client metadata and configuration
- `notes.md` - General notes, goals, and meeting notes
- `history.log` - Timeline of all activities
- `workflows/` - Documentation for automations built for this client
- `communications/` - Email templates and correspondence
- `deliverables/` - Links and exports of deliverables

## Quick Links

[Add links to client's Google Sheets, dashboards, etc.]
"""

        with open(client_path / "README.md", "w") as f:
            f.write(readme_content)

        result = {
            "success": True,
            "client_name": client_name,
            "client_slug": client_slug,
            "client_path": str(client_path),
            "created": datetime.now().isoformat()
        }

        print(json.dumps(result, indent=2))
        return result

    except Exception as e:
        print(f"Error: Failed to create client folder: {str(e)}", file=sys.stderr)
        # Clean up partial creation
        if client_path.exists():
            import shutil
            shutil.rmtree(client_path)
        return None


def main():
    parser = argparse.ArgumentParser(description="Create a new client folder")
    parser.add_argument("--name", required=True, help="Client company name")
    parser.add_argument("--email", required=True, help="Primary contact email")
    parser.add_argument("--contact", help="Primary contact name")
    parser.add_argument("--phone", help="Phone number")
    parser.add_argument("--website", help="Client website")
    parser.add_argument("--industry", help="Industry/sector")
    parser.add_argument("--tags", help="Comma-separated tags")

    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    result = create_client_folder(
        client_name=args.name,
        contact_email=args.email,
        contact_name=args.contact,
        phone=args.phone,
        website=args.website,
        industry=args.industry,
        tags=tags
    )

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
