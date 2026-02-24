#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def run_audit(url):
    """Run the SEO audit and return the JSON result."""
    print(f"--- Auditing: {url} ---")
    script_path = Path(__file__).parent / "seo_audit_runner.py"
    
    # We output to a temp file
    domain = url.split("//")[-1].split("/")[0].replace(".", "_")
    output_path = Path(__file__).parent.parent / ".tmp" / f"teaser_{domain}.json"
    
    cmd = [
        sys.executable, str(script_path),
        "--website-url", url,
        "--output", str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        with open(output_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error auditing {url}: {e}")
        return None

def format_email(payload, domain):
    """Format the teaser email template."""
    template_path = Path(__file__).parent.parent / "templates" / "seo_teaser.md"
    if not template_path.exists():
        return "Template not found."
    
    with open(template_path, "r") as f:
        template = f.read()
    
    # Handle the "data" wrapper from seo_audit_runner.py
    data = payload.get("data", payload)
    
    score = data.get("score", "N/A")
    latency = data.get("page_speed", {}).get("metrics", {}).get("TTFB", "Unknown")
    
    # Get top 2 improvements if list is empty provide defaults
    imps = data.get("improvements", [])
    if not imps:
        imps = ["Inconsistent metadata nodes in the DOM.", "Core Web Vitals breach on mobile."]
    top_issue = imps[0]
    
    kw_count = len(data.get("keyword_analysis", {}).get("missing_keywords", []))
    if kw_count == 0:
        kw_count = "multiple" # A bit more aggressive for sales
    
    email = template.replace("{{domain}}", domain)
    email = email.replace("{{score}}", str(score))
    email = email.replace("{{latency}}", str(latency))
    email = email.replace("{{top_issue}}", top_issue)
    email = email.replace("{{kw_count}}", str(kw_count))
    email = email.replace("{{industry}}", "your niche") 
    
    return email

def main():
    parser = argparse.ArgumentParser(description="SEO Outreach Prepper")
    parser.add_argument("--url", help="Single URL to audit and prep email for")
    parser.add_argument("--csv", help="CSV file of domains to process")
    parser.add_argument("--send", action="store_true", help="Actually send the email (requires RESEND_API_KEY)")
    
    args = parser.parse_args()
    
    targets = []
    if args.url:
        targets.append(args.url)
    elif args.csv:
        # Simple CSV reading (assumes domain/url in first column)
        import csv
        with open(args.csv, "r") as f:
            reader = csv.reader(f)
            next(reader) # skip header
            for row in reader:
                if row: targets.append(row[0])
    
    for target in targets:
        if not target.startswith("http"):
            target = f"https://{target}"
            
        result = run_audit(target)
        if result:
            domain = target.split("//")[-1].split("/")[0]
            email_draft = format_email(result, domain)
            
            print(f"\n--- EMAIL DRAFT FOR {domain} ---")
            print(email_draft)
            print("-" * 40)
            
            if args.send:
                # Import send_email logic
                sys.path.append(str(Path(__file__).parent))
                from send_email import send_via_resend
                
                subject = f"SEO Intelligence Alert for {domain}"
                # In a real scenario, we'd need the prospect's email from the CSV
                # For now, we'll just log that we would send it.
                print("Note: Sending skipped (no recipient email provided in this demo skip)")

if __name__ == "__main__":
    main()
