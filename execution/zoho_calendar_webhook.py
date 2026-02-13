"""
Handle Zoho Calendar webhook events.

Directive: directives/handle_zoho_calendar_webhook.md
Deploy: modal deploy execution/zoho_calendar_webhook.py
Endpoint: POST /zoho-calendar
Trigger: Zoho Calendar sends webhook when event changes

This Modal webhook receives real-time calendar event changes from Zoho
and updates the dashboard cache within 2-3 seconds.
"""

import modal
import json
import os
from datetime import datetime, timedelta

stub = modal.Stub("zoho-calendar-webhook")

# Mount .env for credentials
stub.env = {
    "ZOHO_CLIENT_ID": modal.Secret.from_name("zoho-client-id"),
    "ZOHO_CLIENT_SECRET": modal.Secret.from_name("zoho-client-secret"),
    "ZOHO_REFRESH_TOKEN": modal.Secret.from_name("zoho-refresh-token"),
    "ZOHO_DC": modal.Secret.from_name("zoho-dc")
}

@stub.webhook(method="POST", label="zoho-webhook")
def handle_zoho_webhook(request_body: dict):
    """
    Process Zoho Calendar webhook.
    
    Webhook payload from Zoho:
    {
        "event": "event.created",  # or event.updated, event.deleted
        "calendar_id": "abc123",
        "event_id": "def456",
        "user_email": "sarah@remylasers.com",
        "event_data": {
            "id": "def456",
            "title": "Focus Time",
            "start": "2026-02-04T14:00:00Z",
            "end": "2026-02-04T16:00:00Z",
            "location": "Conference Room A",
            "attendees": ["john@remylasers.com"]
        }
    }
    
    Args:
        request_body: Webhook payload from Zoho
    
    Returns:
        dict: Success status and updated employee
    """
    
    event_type = request_body.get('event')
    user_email = request_body.get('user_email')
    event_data = request_body.get('event_data', {})
    
    print(f"📅 Zoho webhook: {event_type} for {user_email}")
    print(f"   Event: {event_data.get('title', 'Untitled')}")
    
    # Load calendar cache
    cache = load_calendar_cache()
    
    if not cache:
        print("❌ Calendar cache not found, run sync first")
        return {"error": "Calendar cache not found"}
    
    # Find employee
    employee = next((e for e in cache['employees'] if e['email'] == user_email), None)
    
    if not employee:
        print(f"❌ Employee {user_email} not found in cache")
        return {"error": f"Employee {user_email} not found"}
    
    # Update employee's events based on webhook type
    if event_type == 'event.created':
        print(f"   ➕ Adding new event: {event_data.get('title')}")
        employee['events'].append({
            'id': event_data.get('id'),
            'title': event_data.get('title', 'Untitled'),
            'start': event_data.get('start'),
            'end': event_data.get('end'),
            'location': event_data.get('location', ''),
            'attendees': len(event_data.get('attendees', [])),
            'is_all_day': event_data.get('is_all_day', False)
        })
    
    elif event_type == 'event.updated':
        print(f"   ✏️  Updating event: {event_data.get('title')}")
        # Remove old version
        employee['events'] = [e for e in employee['events'] if e['id'] != event_data.get('id')]
        # Add updated version
        employee['events'].append({
            'id': event_data.get('id'),
            'title': event_data.get('title', 'Untitled'),
            'start': event_data.get('start'),
            'end': event_data.get('end'),
            'location': event_data.get('location', ''),
            'attendees': len(event_data.get('attendees', [])),
            'is_all_day': event_data.get('is_all_day', False)
        })
    
    elif event_type == 'event.deleted':
        print(f"   🗑️  Deleting event: {event_data.get('title')}")
        employee['events'] = [e for e in employee['events'] if e['id'] != event_data.get('id')]
    
    # Recalculate availability
    print(f"   🔄 Recalculating availability...")
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    employee['availability'] = calculate_availability_slots(
        employee['events'],
        start_date,
        end_date
    )
    
    # Update cache timestamp
    cache['last_updated'] = datetime.utcnow().isoformat()
    
    # Save updated cache
    save_calendar_cache(cache)
    
    print(f"   ✅ Cache updated for {employee['name']}")
    
    # TODO: Push update to dashboard via WebSocket
    # send_dashboard_update(employee['id'], employee['availability'])
    
    # TODO: Send Slack notification for major changes
    # if event_type == 'event.created' and is_important_event(event_data):
    #     send_slack_alert(f"📅 {employee['name']} added: {event_data['title']}")
    
    return {
        "success": True,
        "employee": employee['name'],
        "event_type": event_type,
        "event_title": event_data.get('title', 'Untitled'),
        "cache_updated": True
    }

def load_calendar_cache():
    """Load calendar cache from .tmp/calendar_cache.json."""
    try:
        cache_path = '.tmp/calendar_cache.json'
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"❌ Error loading cache: {str(e)}")
        return None

def save_calendar_cache(cache):
    """Save updated calendar cache."""
    try:
        os.makedirs('.tmp', exist_ok=True)
        cache_path = '.tmp/calendar_cache.json'
        with open(cache_path, 'w') as f:
            json.dump(cache, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving cache: {str(e)}")
        return False

def calculate_availability_slots(events, start_date, end_date):
    """
    Calculate available time slots between events.
    
    Same logic as sync_zoho_calendars.py
    """
    availability = []
    
    current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    while current < end_date:
        if current.hour < 9:
            current = current.replace(hour=9, minute=0)
        
        if current.hour >= 17:
            current = (current + timedelta(days=1)).replace(hour=9, minute=0)
            continue
        
        if current.weekday() >= 5:
            current = current + timedelta(days=1)
            continue
        
        hour_end = current + timedelta(hours=1)
        
        is_busy = False
        event_name = None
        
        for event in events:
            try:
                event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                
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

# List all webhooks
@stub.function()
@modal.web_endpoint(method="GET", label="list-webhooks")
def list_webhooks():
    """
    List all registered webhooks.
    
    GET https://your-app--list-webhooks.modal.run
    """
    try:
        with open('.tmp/zoho_webhooks.json', 'r') as f:
            webhooks = json.load(f)
        
        return {
            "success": True,
            "webhooks": webhooks
        }
    except:
        return {
            "success": False,
            "error": "Webhooks not found. Run: python execution/setup_zoho_calendar_webhook.py"
        }

# Test endpoint
@stub.function()
@modal.web_endpoint(method="POST", label="test-webhook")
def test_webhook():
    """
    Test webhook processing with sample data.
    
    POST https://your-app--test-webhook.modal.run
    """
    sample_payload = {
        "event": "event.created",
        "calendar_id": "test_cal_123",
        "event_id": "test_event_456",
        "user_email": "test@remylasers.com",
        "event_data": {
            "id": "test_event_456",
            "title": "Test Meeting",
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(hours=1)).isoformat(),
            "location": "Conference Room",
            "attendees": ["jane@remylasers.com"]
        }
    }
    
    result = handle_zoho_webhook(sample_payload)
    
    return {
        "success": True,
        "message": "Test webhook processed",
        "result": result
    }
