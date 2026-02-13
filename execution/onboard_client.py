#!/usr/bin/env python3
"""
Client onboarding orchestration script
Coordinates email sending and calendar link creation
"""

import os
import sys
import json
import re
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# Add execution directory to path
EXECUTION_DIR = Path(__file__).parent


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def extract_name_from_email(email):
    """Extract and format name from email address"""
    local_part = email.split('@')[0]
    # Replace common separators with spaces
    name = local_part.replace('.', ' ').replace('_', ' ').replace('-', ' ')
    # Capitalize each word
    return ' '.join(word.capitalize() for word in name.split())


def extract_company_from_email(email):
    """Extract company name from email domain"""
    domain = email.split('@')[1]
    company = domain.split('.')[0]
    return company.capitalize()


def run_script(script_name, args):
    """Run a Python script and return the output"""
    script_path = EXECUTION_DIR / script_name
    cmd = [sys.executable, str(script_path)] + args

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            # Try to parse JSON output
            try:
                return True, json.loads(result.stdout)
            except json.JSONDecodeError:
                return True, {"output": result.stdout}
        else:
            return False, {"error": result.stderr or result.stdout}

    except Exception as e:
        return False, {"error": str(e)}


def create_welcome_email_html(client_name, company_name, calendar_info):
    """Generate the welcome email HTML"""

    # Determine calendar link based on service
    # Use table-based button for better email client compatibility
    if calendar_info.get("service") == "microsoft_bookings":
        calendar_button = f'''<table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
            <tr>
                <td style="border-radius: 6px; background-color: #4CAF50;">
                    <a href="{calendar_info["link"]}" target="_blank" style="background-color: #4CAF50; border: 15px solid #4CAF50; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5; text-decoration: none; color: #ffffff; display: block; border-radius: 6px; font-weight: bold;">Book your kickoff call here</a>
                </td>
            </tr>
        </table>'''
        availability_note = '<p style="font-size: 0.9em; color: #666; margin-top: 10px;">Available: Mon-Fri, 10am-3pm EST</p>'
    elif calendar_info.get("service") == "calendly":
        calendar_button = f'''<table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
            <tr>
                <td style="border-radius: 6px; background-color: #4CAF50;">
                    <a href="{calendar_info["link"]}" target="_blank" style="background-color: #4CAF50; border: 15px solid #4CAF50; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5; text-decoration: none; color: #ffffff; display: block; border-radius: 6px; font-weight: bold;">Book your kickoff call here</a>
                </td>
            </tr>
        </table>'''
        availability_note = '<p style="font-size: 0.9em; color: #666; margin-top: 10px;">Available: Mon-Fri, 10am-3pm EST</p>'
    elif calendar_info.get("service") == "google_calendar":
        calendar_button = f'''<table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
            <tr>
                <td style="border-radius: 6px; background-color: #4CAF50;">
                    <a href="{calendar_info["link"]}" target="_blank" style="background-color: #4CAF50; border: 15px solid #4CAF50; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5; text-decoration: none; color: #ffffff; display: block; border-radius: 6px; font-weight: bold;">Book your kickoff call here</a>
                </td>
            </tr>
        </table>'''
        availability_note = '<p style="font-size: 0.9em; color: #666; margin-top: 10px;">Available: Mon-Fri, 10am-3pm EST</p>'
    else:
        calendar_button = "Reply to this email with your availability and I'll send over a calendar invite!"
        availability_note = '<p style="font-size: 0.9em; color: #666; margin-top: 10px;">Typical availability: Mon-Fri, 10am-3pm EST</p>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.8; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 10px; }}
            .cta-section {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 25px 0;
                text-align: center;
            }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
            .ps {{ margin-top: 20px; font-size: 0.95em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <p>Hi {client_name},</p>

            <p>Welcome to 5 Cypress Labs. You've just anchored your operations with a system built for resilience and scale.</p>

            <p>Here's how we start rooting your new automation architecture:</p>

            <ul>
                <li><strong>Root Audit:</strong> A 30-min discovery session to map your high-leverage bottlenecks.</li>
                <li><strong>Architecture Design:</strong> We'll branch out your custom roadmap directly on the call.</li>
                <li><strong>Endurance Build:</strong> Our labs will build and harden your workflows, keeping you updated at every stage.</li>
            </ul>

            <div class="cta-section">
                <p style="margin-bottom: 15px;"><strong>👉 Next step:</strong> Grab a time that works for you</p>
                <p>{calendar_button}</p>
                {availability_note}
            </div>

            <p>Looking forward to connecting!</p>

            <p>Regards,<br>
            The 5 Cypress Labs Team</p>

            <p class="ps"><strong>P.S.</strong> Have questions before the call? Just hit reply—we typically respond within a few hours.</p>

            <div class="footer">
                <p>5 Cypress Labs<br>
                Resilient AI Automation<br>
                <a href="https://www.5cypresslabs.com">www.5cypresslabs.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    return html


def main():
    parser = argparse.ArgumentParser(description="Onboard a new client")
    parser.add_argument("email", help="Client email address")
    parser.add_argument("--name", help="Client name (optional, will extract from email)")
    parser.add_argument("--company", help="Company name (optional, will extract from email)")
    parser.add_argument("--dry-run", action="store_true", help="Preview email without sending")

    args = parser.parse_args()

    # Validate email
    if not validate_email(args.email):
        print(json.dumps({
            "success": False,
            "error": f"Invalid email address: {args.email}"
        }))
        return 1

    # Extract or use provided name and company
    client_name = args.name or extract_name_from_email(args.email)
    company_name = args.company or extract_company_from_email(args.email)

    print(f"Starting onboarding for {client_name} ({args.email}) from {company_name}...", file=sys.stderr)

    # Step 1: Create or update client folder
    print("Setting up client folder...", file=sys.stderr)
    client_slug = company_name.lower().replace(" ", "-").replace("&", "and").replace(",", "")

    # Try to create client folder (will fail gracefully if exists)
    create_result = run_script("create_client.py", [
        "--name", company_name,
        "--email", args.email,
        "--contact", client_name
    ])

    if create_result[0]:
        print(f"Client folder created: {client_slug}", file=sys.stderr)
    else:
        print(f"Using existing client folder: {client_slug}", file=sys.stderr)

    # Log onboarding activity
    run_script("log_activity.py", [
        "--client", client_slug,
        "--message", f"Onboarding email sent to {client_name} ({args.email})",
        "--type", "email"
    ])

    # Step 2: Create calendar link
    print("Creating calendar scheduling link...", file=sys.stderr)
    success, calendar_info = run_script("create_calendar_link.py", [
        "--event-name", "5 Cypress Automation - Onboarding Kickoff",
        "--duration", "45",
        "--description", f"Architecture discovery and kickoff call with {client_name} from {company_name}"
    ])

    if not success:
        print(f"Warning: Calendar link creation failed: {calendar_info.get('error')}", file=sys.stderr)
        calendar_info = {"service": "manual"}

    print(f"Calendar link created via {calendar_info.get('service')}", file=sys.stderr)

    # Step 2: Generate email
    print("Generating welcome email...", file=sys.stderr)
    email_html = create_welcome_email_html(client_name, company_name, calendar_info)

    # Step 3: Send email (or preview in dry-run mode)
    if args.dry_run:
        # Write preview to file to avoid console encoding issues
        preview_file = Path(".tmp") / "email_preview.html"
        preview_file.parent.mkdir(exist_ok=True)
        preview_file.write_text(email_html, encoding='utf-8')
        print(f"\n=== DRY RUN MODE ===", file=sys.stderr)
        print(f"Email preview saved to: {preview_file}", file=sys.stderr)
        print(f"Calendar service: {calendar_info.get('service')}", file=sys.stderr)
        print(f"Booking link: {calendar_info.get('link', 'N/A')}", file=sys.stderr)
        print(f"=== End Preview ===\n", file=sys.stderr)

        result = {
            "success": True,
            "dry_run": True,
            "client_email": args.email,
            "client_name": client_name,
            "company_name": company_name,
            "calendar_service": calendar_info.get("service")
        }
    else:
        print("Sending welcome email...", file=sys.stderr)
        subject = f"Welcome to 5 Cypress Automation - Your Onboarding Kickoff"
        success, email_result = run_script("send_email.py", [
            "--to", args.email,
            "--subject", subject,
            "--body", email_html,
            "--service", "auto"
        ])

        if not success:
            result = {
                "success": False,
                "error": f"Failed to send email: {email_result.get('error')}",
                "client_email": args.email,
                "client_name": client_name,
                "company_name": company_name
            }
        else:
            result = {
                "success": True,
                "client_email": args.email,
                "client_name": client_name,
                "company_name": company_name,
                "email_sent": True,
                "email_service": email_result.get("service"),
                "calendar_service": calendar_info.get("service"),
                "calendar_link": calendar_info.get("link", "N/A")
            }

    print(json.dumps(result, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
