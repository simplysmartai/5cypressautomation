#!/usr/bin/env python3
"""
Create a calendar scheduling link using Calendly or similar service
For now, generates a simple calendar link that can be customized
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def generate_microsoft_bookings_link(event_name="Onboarding Kickoff Call", duration=45):
    """
    Generate a Microsoft Bookings link if configured
    Returns the scheduling URL from environment variable
    """
    bookings_url = os.getenv("MICROSOFT_BOOKINGS_URL")

    if bookings_url:
        return {
            "success": True,
            "service": "microsoft_bookings",
            "link": bookings_url,
            "event_name": event_name,
            "duration": duration
        }

    return None


def generate_calendly_link(event_name="Onboarding Kickoff Call", duration=45):
    """
    Generate a Calendly link if configured
    Returns the scheduling URL
    """
    calendly_username = os.getenv("CALENDLY_USERNAME")

    if calendly_username:
        # Return Calendly link
        event_slug = event_name.lower().replace(" ", "-")
        link = f"https://calendly.com/{calendly_username}/{event_slug}"

        return {
            "success": True,
            "service": "calendly",
            "link": link,
            "event_name": event_name,
            "duration": duration
        }

    return None


def generate_google_calendar_link(event_name, duration=45, description=""):
    """
    Generate a Google Calendar event creation link
    This allows the recipient to add the meeting to their calendar
    """
    from urllib.parse import quote

    # Calculate suggested time (tomorrow at 10 AM)
    start_time = datetime.now() + timedelta(days=1)
    start_time = start_time.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=duration)

    # Format for Google Calendar (YYYYMMDDTHHMMSS)
    start_str = start_time.strftime("%Y%m%dT%H%M%S")
    end_str = end_time.strftime("%Y%m%dT%H%M%S")

    # Build Google Calendar link
    base_url = "https://calendar.google.com/calendar/render"
    params = {
        "action": "TEMPLATE",
        "text": event_name,
        "dates": f"{start_str}/{end_str}",
        "details": description,
        "sf": "true",
        "output": "xml"
    }

    param_str = "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
    link = f"{base_url}?{param_str}"

    return {
        "success": True,
        "service": "google_calendar",
        "link": link,
        "event_name": event_name,
        "duration": duration,
        "suggested_time": start_time.isoformat()
    }


def generate_generic_instructions(event_name, duration=45):
    """
    Generate generic scheduling instructions as fallback
    """
    instructions = f"""
To schedule your {event_name} ({duration} minutes):

Option 1: Reply to this email with your availability for the next 2 weeks
Option 2: Contact us at hello@nexairi.com with your preferred times

We typically offer meetings:
- Monday-Friday: 9 AM - 5 PM EST
- We'll send a calendar invite once we confirm a time

Looking forward to connecting!
"""

    return {
        "success": True,
        "service": "manual",
        "instructions": instructions.strip(),
        "event_name": event_name,
        "duration": duration
    }


def main():
    parser = argparse.ArgumentParser(description="Create a calendar scheduling link")
    parser.add_argument("--event-name", default="Onboarding Kickoff Call",
                       help="Name of the calendar event")
    parser.add_argument("--duration", type=int, default=45,
                       help="Meeting duration in minutes")
    parser.add_argument("--description", default="",
                       help="Event description")
    parser.add_argument("--service", choices=["calendly", "google", "manual", "auto"],
                       default="auto", help="Calendar service to use")

    args = parser.parse_args()

    result = None

    # Try services in order based on preference
    # Microsoft Bookings has highest priority (preferred over Calendly)
    if args.service == "microsoft_bookings" or args.service == "auto":
        result = generate_microsoft_bookings_link(args.event_name, args.duration)

    if not result and (args.service == "calendly" or args.service == "auto"):
        result = generate_calendly_link(args.event_name, args.duration)

    if not result and (args.service == "google" or args.service == "auto"):
        result = generate_google_calendar_link(args.event_name, args.duration, args.description)

    if not result or args.service == "manual":
        result = generate_generic_instructions(args.event_name, args.duration)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
