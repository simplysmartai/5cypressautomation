#!/usr/bin/env python3
"""
Google Sheets Logger
Logs skill execution results to Google Sheets for persistence and analytics
"""
import json
import sys
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Sheets Configuration
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_ID', '1_your_spreadsheet_id_here')
SHEET_NAME = 'Skill_Runs'

def get_sheets_service():
    """Initialize Google Sheets API service"""
    try:
        # Use service account credentials from environment
        creds_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        else:
            # Fallback to credentials.json file
            creds = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to initialize Sheets service: {e}", file=sys.stderr)
        return None


def log_skill_run(run_data):
    """
    Log a skill run to Google Sheets
    
    Args:
        run_data: dict containing:
            - client_id: Client identifier
            - skill_id: Skill that was run
            - inputs: Input parameters
            - success: Boolean success status
            - result: Result data
            - timestamp: ISO timestamp
            - duration_ms: Execution time in milliseconds
    """
    try:
        service = get_sheets_service()
        if not service:
            return {
                'success': False,
                'error': 'Failed to connect to Google Sheets'
            }
        
        # Prepare row data
        row = [
            run_data.get('timestamp', datetime.now().isoformat()),
            run_data.get('client_id', 'unknown'),
            run_data.get('skill_id', 'unknown'),
            json.dumps(run_data.get('inputs', {})),
            'Success' if run_data.get('success', False) else 'Failed',
            run_data.get('error_message', ''),
            json.dumps(run_data.get('result', {}))[:1000],  # Truncate large results
            str(run_data.get('duration_ms', 0)),
            run_data.get('client_tier', 'unknown')
        ]
        
        # Append to sheet
        range_name = f'{SHEET_NAME}!A:I'
        body = {'values': [row]}
        
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return {
            'success': True,
            'updates': result.get('updates', {}),
            'message': 'Logged to Google Sheets'
        }
        
    except HttpError as e:
        return {
            'success': False,
            'error': f'Google Sheets API error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Logging failed: {str(e)}'
        }


def get_recent_runs(client_id=None, limit=20):
    """
    Retrieve recent skill runs from Google Sheets
    
    Args:
        client_id: Filter by specific client (optional)
        limit: Number of recent runs to retrieve
    """
    try:
        service = get_sheets_service()
        if not service:
            return {
                'success': False,
                'error': 'Failed to connect to Google Sheets'
            }
        
        # Read all data
        range_name = f'{SHEET_NAME}!A:I'
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values or len(values) < 2:
            return {
                'success': True,
                'runs': [],
                'message': 'No runs found'
            }
        
        # Skip header row
        headers = values[0]
        runs = []
        
        # Reverse to get most recent first
        for row in reversed(values[1:]):
            if len(row) < 5:
                continue
            
            run = {
                'timestamp': row[0] if len(row) > 0 else '',
                'client_id': row[1] if len(row) > 1 else '',
                'skill_id': row[2] if len(row) > 2 else '',
                'inputs': json.loads(row[3]) if len(row) > 3 and row[3] else {},
                'status': row[4] if len(row) > 4 else '',
                'error': row[5] if len(row) > 5 else '',
                'result_preview': row[6][:200] if len(row) > 6 else '',
                'duration_ms': row[7] if len(row) > 7 else '0',
                'tier': row[8] if len(row) > 8 else 'unknown'
            }
            
            # Filter by client if specified
            if client_id and run['client_id'] != client_id:
                continue
            
            runs.append(run)
            
            if len(runs) >= limit:
                break
        
        return {
            'success': True,
            'runs': runs,
            'total': len(runs)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def initialize_sheet():
    """Create the sheet with headers if it doesn't exist"""
    try:
        service = get_sheets_service()
        if not service:
            return False
        
        # Check if sheet exists
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID
        ).execute()
        
        sheets = spreadsheet.get('sheets', [])
        sheet_exists = any(s['properties']['title'] == SHEET_NAME for s in sheets)
        
        if not sheet_exists:
            # Create sheet
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': SHEET_NAME
                    }
                }
            }]
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body={'requests': requests}
            ).execute()
        
        # Add headers if sheet is empty
        range_name = f'{SHEET_NAME}!A1:I1'
        headers = [[
            'Timestamp',
            'Client ID',
            'Skill ID',
            'Inputs',
            'Status',
            'Error',
            'Result (Preview)',
            'Duration (ms)',
            'Client Tier'
        ]]
        
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()
        
        return True
        
    except Exception as e:
        print(f"Sheet initialization failed: {e}", file=sys.stderr)
        return False


if __name__ == '__main__':
    # Test logging
    test_run = {
        'client_id': 'demo_client_001',
        'skill_id': 'email-sequence',
        'inputs': {'sequence_type': 'Welcome', 'num_emails': 5},
        'success': True,
        'result': {'sequence': 'Test sequence data'},
        'timestamp': datetime.now().isoformat(),
        'duration_ms': 1234,
        'client_tier': 'starter'
    }
    
    result = log_skill_run(test_run)
    print(json.dumps(result, indent=2))
