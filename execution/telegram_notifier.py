#!/usr/bin/env python3
"""
Telegram Notifier
Send notifications to Telegram when skills complete
"""
import json
import sys
import os
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

def send_telegram_notification(notification_data):
    """
    Send a notification to Telegram
    
    Args:
        notification_data: dict containing:
            - client_id: Client who ran skill
            - skill_id: Skill that completed
            - success: Boolean success status
            - duration_ms: Execution time
            - error: Error message if failed
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            'success': False,
            'error': 'TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured'
        }
    
    try:
        # Determine emoji
        if notification_data.get('success', False):
            emoji = '✅'
            status_text = 'Completed Successfully'
        else:
            emoji = '❌'
            status_text = 'Failed'
        
        # Format skill name
        skill_name = notification_data.get('skill_id', 'Unknown Skill').replace('_', ' ').replace('-', ' ').title()
        
        # Build Telegram message (Markdown format)
        message_lines = [
            f"{emoji} *Skill {status_text}*",
            "",
            f"*Skill:* {skill_name}",
            f"*Client:* {notification_data.get('client_name', notification_data.get('client_id', 'Unknown'))}",
            f"*Duration:* {notification_data.get('duration_ms', 0)}ms",
            f"*Time:* {datetime.now().strftime('%I:%M %p')}"
        ]
        
        # Add error details if failed
        if not notification_data.get('success', False) and notification_data.get('error'):
            message_lines.append("")
            message_lines.append(f"*Error:*")
            message_lines.append(f"```\n{notification_data.get('error')[:200]}\n```")
        
        # Add result preview if successful
        if notification_data.get('success', False) and notification_data.get('result_summary'):
            message_lines.append("")
            message_lines.append(f"*Result:* {notification_data.get('result_summary')[:300]}")
        
        message_text = "\n".join(message_lines)
        
        # Send to Telegram
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message_text,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(
            telegram_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Notification sent to Telegram'
            }
        else:
            return {
                'success': False,
                'error': f'Telegram API returned {response.status_code}: {response.text}'
            }
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Failed to send Telegram notification: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Notification error: {str(e)}'
        }


def send_usage_alert(alert_data):
    """
    Send usage alert to Telegram (e.g., approaching limit)
    
    Args:
        alert_data: dict containing:
            - client_id: Client identifier
            - client_name: Client name
            - usage_percent: Percentage of limit used
            - current_usage: Current usage count
            - limit: Usage limit
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {'success': False, 'error': 'TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured'}
    
    try:
        usage_percent = alert_data.get('usage_percent', 0)
        
        # Determine urgency
        if usage_percent >= 90:
            emoji = '🚨'
            urgency = 'CRITICAL'
        elif usage_percent >= 75:
            emoji = '⚠️'
            urgency = 'WARNING'
        else:
            emoji = 'ℹ️'
            urgency = 'INFO'
        
        message_lines = [
            f"{emoji} *{urgency}: Usage Alert*",
            "",
            f"*Client:* {alert_data.get('client_name', alert_data.get('client_id'))}",
            f"*Usage:* {alert_data.get('current_usage')}/{alert_data.get('limit')} ({usage_percent}%)",
            "",
            f"Client is at *{usage_percent}%* of their monthly limit."
        ]
        
        message_text = "\n".join(message_lines)
        
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message_text,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(
            telegram_url,
            json=payload,
            timeout=10
        )
        
        return {
            'success': response.status_code == 200,
            'message': 'Usage alert sent' if response.status_code == 200 else f'Error {response.status_code}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == '__main__':
    # Test notification
    test_notification = {
        'client_id': 'demo_client_001',
        'client_name': 'Demo Client',
        'skill_id': 'email-sequence',
        'success': True,
        'duration_ms': 1234,
        'result_summary': 'Generated 5-email Welcome sequence with subject lines and timing'
    }
    
    result = send_slack_notification(test_notification)
    print(json.dumps(result, indent=2))
