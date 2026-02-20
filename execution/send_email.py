#!/usr/bin/env python3
"""
Send email via SMTP or Resend API
Supports both simple SMTP and Resend service
"""

import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import argparse

load_dotenv()


def send_via_resend(to_email, subject, html_body, from_email=None):
    """Send email using Resend API"""
    try:
        import requests
    except ImportError:
        print("Error: requests library not installed. Run: pip install requests", file=sys.stderr)
        return False

    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("Error: RESEND_API_KEY not found in environment", file=sys.stderr)
        return False

    if not from_email:
        from_email = "jimmy@simplysmart-consulting.com"

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print(json.dumps({
            "success": True,
            "service": "resend",
            "email_id": result.get("id"),
            "to": to_email,
            "subject": subject
        }))
        return True
    else:
        print(f"Error: Failed to send email via Resend: {response.text}", file=sys.stderr)
        return False


def send_via_smtp(to_email, subject, html_body, from_email=None):
    """Send email using SMTP"""
    # Default sender
    if not from_email:
        from_email = "jimmy@simplysmart-consulting.com"

    # Determine which SMTP config to use based on sender domain
    if "simplysmart-consulting.com" in from_email:
        smtp_host = os.getenv("SIMPLYSMART_SMTP_HOST")
        smtp_port = int(os.getenv("SIMPLYSMART_SMTP_PORT", "465"))
        smtp_user = os.getenv("SIMPLYSMART_SMTP_USER")
        smtp_pass = os.getenv("SIMPLYSMART_SMTP_PASS")
        smtp_secure = os.getenv("SIMPLYSMART_SMTP_SECURE", "true").lower() == "true"
    elif "5cypress.com" in from_email:
        # Route to correct 5cypress.com account based on sender
        prefix = from_email.split("@")[0].upper()  # nick, jimmy, info, admin
        smtp_host = os.getenv(f"CYPRESS_{prefix}_SMTP_HOST", os.getenv("CYPRESS_NICK_SMTP_HOST"))
        smtp_port = int(os.getenv(f"CYPRESS_{prefix}_SMTP_PORT", os.getenv("CYPRESS_NICK_SMTP_PORT", "465")))
        smtp_user = os.getenv(f"CYPRESS_{prefix}_SMTP_USER", os.getenv("CYPRESS_NICK_SMTP_USER"))
        smtp_pass = os.getenv(f"CYPRESS_{prefix}_SMTP_PASS", os.getenv("CYPRESS_NICK_SMTP_PASS"))
        smtp_secure = os.getenv(f"CYPRESS_{prefix}_SMTP_SECURE", "true").lower() == "true"
    else:
        # Fall back to default SMTP (nexairi.com)
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        smtp_secure = os.getenv("SMTP_SECURE", "true").lower() == "true"

    if not all([smtp_host, smtp_user, smtp_pass]):
        print("Error: SMTP credentials not found in environment", file=sys.stderr)
        return False

    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Attach HTML body
    html_part = MIMEText(html_body, "html")
    msg.attach(html_part)

    try:
        # Connect and send
        if smtp_secure:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()

        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        print(json.dumps({
            "success": True,
            "service": "smtp",
            "to": to_email,
            "subject": subject,
            "from": from_email
        }))
        return True

    except Exception as e:
        print(f"Error: Failed to send email via SMTP: {str(e)}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send email via SMTP or Resend")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="HTML email body")
    parser.add_argument("--from", dest="from_email", help="Sender email address")
    parser.add_argument("--service", choices=["resend", "smtp", "auto"], default="auto",
                       help="Email service to use (default: auto)")
    parser.add_argument("--retry", type=int, default=3, help="Number of retry attempts")

    args = parser.parse_args()

    # Determine which service to use
    services = []
    if args.service == "resend":
        services = ["resend"]
    elif args.service == "smtp":
        services = ["smtp"]
    else:  # auto
        # Prefer Resend if available, fall back to SMTP
        if os.getenv("RESEND_API_KEY"):
            services = ["resend", "smtp"]
        else:
            services = ["smtp"]

    # Try sending with retries
    for attempt in range(args.retry):
        for service in services:
            if service == "resend":
                success = send_via_resend(args.to, args.subject, args.body, args.from_email)
            else:
                success = send_via_smtp(args.to, args.subject, args.body, args.from_email)

            if success:
                return 0

        if attempt < args.retry - 1:
            print(f"Retry attempt {attempt + 2}/{args.retry}...", file=sys.stderr)

    print("Error: All email send attempts failed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
