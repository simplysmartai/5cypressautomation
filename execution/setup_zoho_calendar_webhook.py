"""
Register webhooks with Zoho Calendar API.

Directive: directives/setup_zoho_calendar.md
Run after: python execution/setup_zoho_calendar_admin.py
Run once per client: python execution/setup_zoho_calendar_webhook.py

Trigger: When employee creates/updates/deletes calendar event
Destination: Modal webhook endpoint

This script registers webhooks for all employee calendars.
Zoho will POST to your Modal endpoint when events change.
"""

import requests
import json
import os
from datetime import datetime

def register_zoho_webhooks():
    """
    Register webhook for each user's primary calendar.
    
    Zoho supports webhooks for:
    - event.created (new event)
    - event.updated (event modified)
    - event.deleted (event removed)
    
    One webhook per user calendar.
    
    Returns:
        list: Registered webhook IDs
    """
    
    print("=" * 70)
    print("ZOHO CALENDAR WEBHOOK SETUP")
    print("=" * 70)
    print()
    
    # Load credentials
    refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
    dc = os.getenv('ZOHO_DC', 'com')
    
    if not refresh_token:
        print("❌ Error: ZOHO_REFRESH_TOKEN not found in .env")
        print()
        print("Run this first: python execution/setup_zoho_calendar_admin.py")
        return []
    
    print("✅ Loaded credentials from .env")
    print()
    
    # Get fresh access token
    print("🔄 Refreshing access token...")
    access_token = refresh_access_token(refresh_token, dc)
    
    if not access_token:
        print("❌ Failed to refresh access token")
        return []
    
    print("✅ Access token refreshed")
    print()
    
    # Get all users
    print("🔍 Fetching organization users...")
    users = get_all_users(access_token, dc)
    
    if not users:
        print("❌ No users found")
        return []
    
    print(f"✅ Found {len(users)} users")
    print()
    
    # TODO: Update this URL after deploying to Modal
    webhook_url = 'https://your-app--zoho-webhook.modal.run'
    
    print(f"📡 Webhook URL: {webhook_url}")
    print()
    print("⚠️  NOTE: Update webhook_url in this script after deploying to Modal")
    print("   Run: modal deploy execution/zoho_calendar_webhook.py")
    print()
    print("-" * 70)
    print()
    
    registered_webhooks = []
    
    for i, user in enumerate(users, 1):
        print(f"[{i}/{len(users)}] Registering webhook for {user['email']}...")
        
        # Get user's calendars
        calendars = get_user_calendars(access_token, user['email'], dc)
        
        if not calendars:
            print(f"   ⚠️  No calendars found, skipping")
            continue
        
        # Find primary calendar
        primary_cal = next((c for c in calendars if c.get('is_primary')), calendars[0])
        
        # Register webhook for primary calendar
        webhook = {
            'url': webhook_url,
            'events': ['event.created', 'event.updated', 'event.deleted'],
            'calendar_id': primary_cal['id']
        }
        
        try:
            response = requests.post(
                f'https://calendar.zoho.{dc}/api/v1/webhooks',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=webhook
            )
            
            if response.status_code in [200, 201]:
                webhook_data = response.json()
                webhook_id = webhook_data.get('webhook', {}).get('id')
                registered_webhooks.append({
                    'user_email': user['email'],
                    'calendar_id': primary_cal['id'],
                    'webhook_id': webhook_id
                })
                print(f"   ✅ Registered (webhook ID: {webhook_id})")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"      {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        print()
    
    # Save webhook IDs to file
    os.makedirs('.tmp', exist_ok=True)
    with open('.tmp/zoho_webhooks.json', 'w') as f:
        json.dump({
            'registered_at': datetime.utcnow().isoformat(),
            'webhook_url': webhook_url,
            'webhooks': registered_webhooks
        }, f, indent=2)
    
    print("=" * 70)
    print("WEBHOOK REGISTRATION COMPLETE")
    print("=" * 70)
    print()
    print(f"✅ Registered {len(registered_webhooks)} webhooks")
    print(f"✅ Webhook details saved to .tmp/zoho_webhooks.json")
    print()
    print("Next steps:")
    print("1. Run: python execution/sync_zoho_calendars.py (initial sync)")
    print("2. Test: Create an event in Zoho Calendar")
    print("3. Verify: Check Modal logs for webhook delivery")
    print()
    
    return registered_webhooks

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
    register_zoho_webhooks()
