"""
Set up Zoho Calendar organization-level integration.

Directive: directives/setup_zoho_calendar.md
Run once: python execution/setup_zoho_calendar_admin.py

Systems: Zoho Workplace (Calendar component)
Auth: OAuth 2.0 with organization scope
Output: Refresh token saved to .env (never expires)

This script sets up admin-level access to all employee calendars.
No individual logins required - one admin authorization grants org-wide access.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def setup_zoho_admin():
    """
    Set up Zoho Calendar with admin consent.
    
    Steps:
    1. Generate authorization URL
    2. Admin visits URL and clicks "Accept"
    3. Admin copies authorization code from callback URL
    4. Script exchanges code for refresh token
    5. Refresh token saved to .env (never expires)
    6. Test access to all employee calendars
    
    Returns:
        tuple: (access_token, refresh_token)
    """
    
    print("=" * 70)
    print("ZOHO CALENDAR ADMIN SETUP")
    print("=" * 70)
    print()
    
    # Load credentials from .env
    CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
    CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
    REDIRECT_URI = 'http://localhost:8000/callback'
    
    # Zoho data center (US, EU, IN, AU, JP)
    ZOHO_DC = os.getenv('ZOHO_DC', 'com')  # Default to US
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET not found in .env")
        print()
        print("Add these to your .env file:")
        print("ZOHO_CLIENT_ID=1000.ABC123XYZ")
        print("ZOHO_CLIENT_SECRET=abc123def456...")
        print("ZOHO_DC=com  # or eu, in, au, jp")
        return None
    
    print(f"✅ Loaded credentials from .env")
    print(f"   Client ID: {CLIENT_ID[:20]}...")
    print(f"   Data Center: zoho.{ZOHO_DC}")
    print()
    
    # Generate authorization URL
    auth_url = (
        f'https://accounts.zoho.{ZOHO_DC}/oauth/v2/auth'
        f'?scope=ZohoCalendar.calendar.ALL,ZohoCalendar.event.ALL'
        f'&client_id={CLIENT_ID}'
        f'&response_type=code'
        f'&redirect_uri={REDIRECT_URI}'
        f'&access_type=offline'  # Get refresh token
        f'&prompt=consent'  # Force consent screen
    )
    
    print("=" * 70)
    print("STEP 1: ADMIN AUTHORIZATION")
    print("=" * 70)
    print()
    print("📧 Send this URL to your client's Zoho admin:")
    print()
    print(auth_url)
    print()
    print("After they authorize:")
    print("1. They'll see a callback URL like: http://localhost:8000/callback?code=1000.abc123...")
    print("2. Tell them to copy everything after 'code=' (the authorization code)")
    print("3. Paste it below")
    print()
    print("-" * 70)
    
    # Get authorization code from admin
    auth_code = input("📋 Paste authorization code here: ").strip()
    
    if not auth_code:
        print("❌ No code provided. Exiting.")
        return None
    
    print()
    print("🔄 Exchanging authorization code for tokens...")
    print()
    
    # Exchange code for tokens
    token_response = requests.post(
        f'https://accounts.zoho.{ZOHO_DC}/oauth/v2/token',
        data={
            'code': auth_code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
    )
    
    tokens = token_response.json()
    
    if 'error' in tokens:
        print(f"❌ Error: {tokens.get('error')}")
        print(f"   Description: {tokens.get('error_description', 'No details')}")
        print()
        print("Common issues:")
        print("- Authorization code already used (get a new one)")
        print("- Client ID/Secret incorrect")
        print("- Wrong data center (check ZOHO_DC in .env)")
        return None
    
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    
    print("✅ Tokens acquired successfully!")
    print()
    
    # Save refresh token to .env
    env_path = Path('.env')
    
    # Read existing .env
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
    else:
        env_content = ""
    
    # Update or add refresh token
    if 'ZOHO_REFRESH_TOKEN=' in env_content:
        # Replace existing token
        lines = env_content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('ZOHO_REFRESH_TOKEN='):
                new_lines.append(f'ZOHO_REFRESH_TOKEN={refresh_token}')
            else:
                new_lines.append(line)
        env_content = '\n'.join(new_lines)
    else:
        # Add new token
        if not env_content.endswith('\n'):
            env_content += '\n'
        env_content += f'\n# Zoho Calendar Integration\nZOHO_REFRESH_TOKEN={refresh_token}\n'
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Refresh token saved to .env")
    print(f"   Token: {refresh_token[:20]}...")
    print(f"   Expiry: Never (unless admin revokes)")
    print()
    
    # Test access
    print("=" * 70)
    print("STEP 2: TESTING ACCESS TO EMPLOYEE CALENDARS")
    print("=" * 70)
    print()
    
    # Get all users in organization
    users = get_all_users(access_token, ZOHO_DC)
    
    if not users:
        print("❌ Could not retrieve users. Check API permissions.")
        return access_token, refresh_token
    
    print(f"✅ Found {len(users)} users in organization:")
    print()
    for user in users:
        print(f"   - {user['name']} ({user['email']})")
    print()
    
    # Test calendars for first 3 users
    print("🔍 Testing calendar access for first 3 users:")
    print()
    
    for user in users[:3]:
        calendars = get_user_calendars(access_token, user['email'], ZOHO_DC)
        if calendars:
            print(f"✅ {user['name']}: {len(calendars)} calendar(s)")
            for cal in calendars:
                print(f"   - {cal['name']} (ID: {cal['id']})")
        else:
            print(f"⚠️  {user['name']}: No calendars found")
        print()
    
    print("=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Run: python execution/setup_zoho_calendar_webhook.py")
    print("2. Run: python execution/sync_zoho_calendars.py")
    print("3. Deploy: modal deploy execution/zoho_calendar_webhook.py")
    print()
    
    return access_token, refresh_token

def get_all_users(access_token, dc):
    """
    Get all users in Zoho organization.
    
    With admin consent, you can list all users and their calendars.
    
    Args:
        access_token: OAuth access token
        dc: Data center (com, eu, in, au, jp)
    
    Returns:
        list: User objects with name, email, zuid
    """
    try:
        response = requests.get(
            f'https://calendar.zoho.{dc}/api/v1/users',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            return response.json().get('users', [])
        else:
            print(f"❌ Error listing users: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Exception getting users: {str(e)}")
        return []

def get_user_calendars(access_token, user_email, dc):
    """
    Get all calendars for a specific user.
    
    Admin token allows accessing any user's calendars.
    
    Args:
        access_token: OAuth access token
        user_email: User's email address
        dc: Data center
    
    Returns:
        list: Calendar objects with id, name, is_primary
    """
    try:
        response = requests.get(
            f'https://calendar.zoho.{dc}/api/v1/calendars',
            headers={'Authorization': f'Bearer {access_token}'},
            params={'email': user_email}
        )
        
        if response.status_code == 200:
            return response.json().get('calendars', [])
        else:
            return []
    except Exception as e:
        return []

def refresh_access_token(refresh_token, dc):
    """
    Refresh access token when it expires (1 hour lifespan).
    
    Refresh token never expires unless admin revokes.
    
    Args:
        refresh_token: OAuth refresh token
        dc: Data center
    
    Returns:
        str: New access token
    """
    CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
    CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
    
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

if __name__ == '__main__':
    setup_zoho_admin()
