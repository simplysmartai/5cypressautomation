"""
Sync all Zoho calendars to dashboard cache.

Directive: directives/sync_zoho_calendars.md
Run after: python execution/setup_zoho_calendar_webhook.py
Run anytime: python execution/sync_zoho_calendars.py

Trigger: Manual run, or cron job (every 5 minutes as backup)
Output: .tmp/calendar_cache.json

This script pulls all events from all employee calendars and calculates
availability slots. Dashboard reads this file to display real-time availability.
"""

import requests
import json
import os
from datetime import datetime, timedelta

def sync_all_calendars():
    """
    Pull latest events from all employee calendars.
    
    Called by:
    - Manual run (python execution/sync_zoho_calendars.py)
    - Zoho webhook (when event changes)
    - Cron job (every 5 min as backup)
    
    Returns:
        dict: Calendar cache with all employee data
    """
    
    print("=" * 70)
    print("ZOHO CALENDAR SYNC")
    print("=" * 70)
    print()
    
    # Load credentials
    refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
    dc = os.getenv('ZOHO_DC', 'com')
    
    if not refresh_token:
        print("❌ Error: ZOHO_REFRESH_TOKEN not found in .env")
        return None
    
    # Get fresh access token
    access_token = refresh_access_token(refresh_token, dc)
    
    if not access_token:
        print("❌ Failed to refresh access token")
        return None
    
    print("✅ Access token refreshed")
    print()
    
    # Get all users
    print("🔍 Fetching organization users...")
    users = get_all_users(access_token, dc)
    
    if not users:
        print("❌ No users found")
        return None
    
    print(f"✅ Found {len(users)} users")
    print()
    
    # Date range: next 30 days
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    
    print(f"📅 Syncing events from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print()
    
    calendar_cache = {
        'last_updated': datetime.utcnow().isoformat(),
        'sync_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'employees': []
    }
    
    total_events = 0
    
    for i, user in enumerate(users, 1):
        print(f"[{i}/{len(users)}] Syncing {user['name']} ({user['email']})...")
        
        # Get user's primary calendar
        calendars = get_user_calendars(access_token, user['email'], dc)
        
        if not calendars:
            print(f"   ⚠️  No calendars found, skipping")
            print()
            continue
        
        primary_cal = next((c for c in calendars if c.get('is_primary')), calendars[0])
        
        # Get events for date range
        events = get_calendar_events(
            access_token,
            primary_cal['id'],
            start_date.isoformat(),
            end_date.isoformat(),
            dc
        )
        
        total_events += len(events)
        
        print(f"   ✅ {len(events)} events")
        
        # Calculate availability slots
        availability = calculate_availability_slots(events, start_date, end_date)
        
        calendar_cache['employees'].append({
            'id': user['zuid'],
            'name': user['name'],
            'email': user['email'],
            'calendar_id': primary_cal['id'],
            'events': events,
            'availability': availability
        })
        
        print()
    
    # Save cache
    os.makedirs('.tmp', exist_ok=True)
    cache_path = '.tmp/calendar_cache.json'
    
    with open(cache_path, 'w') as f:
        json.dump(calendar_cache, f, indent=2)
    
    print("=" * 70)
    print("SYNC COMPLETE")
    print("=" * 70)
    print()
    print(f"✅ Synced {len(calendar_cache['employees'])} calendars")
    print(f"✅ Cached {total_events} events")
    print(f"✅ Calendar cache saved to {cache_path}")
    print()
    print("Dashboard can now display real-time availability!")
    print()
    
    return calendar_cache

def get_all_users(access_token, dc):
    """Get all users in Zoho organization."""
    try:
        response = requests.get(
            f'https://calendar.zoho.{dc}/api/v1/users',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            return response.json().get('users', [])
        return []
    except:
        return []

def get_user_calendars(access_token, user_email, dc):
    """Get all calendars for a specific user."""
    try:
        response = requests.get(
            f'https://calendar.zoho.{dc}/api/v1/calendars',
            headers={'Authorization': f'Bearer {access_token}'},
            params={'email': user_email}
        )
        
        if response.status_code == 200:
            return response.json().get('calendars', [])
        return []
    except:
        return []

def get_calendar_events(access_token, calendar_id, start_date, end_date, dc):
    """
    Get all events in date range for a calendar.
    
    Args:
        access_token: OAuth access token
        calendar_id: Zoho calendar ID
        start_date: ISO format date string
        end_date: ISO format date string
        dc: Data center
    
    Returns:
        list: Event objects with id, title, start, end, attendees
    """
    try:
        response = requests.get(
            f'https://calendar.zoho.{dc}/api/v1/calendars/{calendar_id}/events',
            headers={'Authorization': f'Bearer {access_token}'},
            params={
                'start': start_date,
                'end': end_date,
                'include_deleted': False
            }
        )
        
        if response.status_code == 200:
            events = response.json().get('events', [])
            
            # Simplify event data
            simplified_events = []
            for event in events:
                simplified_events.append({
                    'id': event.get('id'),
                    'title': event.get('title', 'Untitled'),
                    'start': event.get('start'),
                    'end': event.get('end'),
                    'location': event.get('location', ''),
                    'attendees': len(event.get('attendees', [])),
                    'is_all_day': event.get('is_all_day', False)
                })
            
            return simplified_events
        else:
            print(f"      ❌ Error getting events: {response.status_code}")
            return []
    except Exception as e:
        print(f"      ❌ Exception: {str(e)}")
        return []

def calculate_availability_slots(events, start_date, end_date):
    """
    Find available time slots between events.
    
    Returns list of {time, available, event_name} for each hour during work hours.
    
    Args:
        events: List of event objects
        start_date: Start date
        end_date: End date
    
    Returns:
        list: Availability slots with time, available flag, event name
    """
    availability = []
    
    current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)  # Start at 9 AM
    
    while current < end_date:
        # Only check work hours (9 AM - 5 PM)
        if current.hour < 9:
            current = current.replace(hour=9, minute=0)
        
        if current.hour >= 17:
            # Skip to next day at 9 AM
            current = (current + timedelta(days=1)).replace(hour=9, minute=0)
            continue
        
        # Skip weekends
        if current.weekday() >= 5:  # Saturday = 5, Sunday = 6
            current = current + timedelta(days=1)
            continue
        
        hour_end = current + timedelta(hours=1)
        
        # Check if any event overlaps this hour
        is_busy = False
        event_name = None
        
        for event in events:
            try:
                event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                
                # Check overlap
                if event_start < hour_end and event_end > current:
                    is_busy = True
                    event_name = event['title']
                    break
            except:
                continue
        
        availability.append({
            'time': current.isoformat(),
            'available': not is_busy,
            'event_name': event_name
        })
        
        current = hour_end
    
    return availability

def refresh_access_token(refresh_token, dc):
    """Refresh access token using refresh token."""
    CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
    CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
    
    try:
        response = requests.post(
            f'https://accounts.zoho.{dc}/oauth/v2/token',
            data={
                'refresh_token': refresh_token,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'refresh_token'
            }
        )
        
        tokens = response.json()
        return tokens.get('access_token')
    except:
        return None

if __name__ == '__main__':
    sync_all_calendars()
