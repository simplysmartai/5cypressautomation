#!/usr/bin/env python3
"""
Slack Notifier
Send notifications to Slack when skills complete
"""
import json
import sys
import os
import requests
from datetime import datetime

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')

def send_slack_notification(notification_data):
    """
    Send a notification to Slack
    
    Args:
        notification_data: dict containing:
            - client_id: Client who ran skill
            - skill_id: Skill that completed
            - success: Boolean success status
            - duration_ms: Execution time
            - error: Error message if failed
    """
    if not SLACK_WEBHOOK_URL:
        return {
            'success': False,
            'error': 'SLACK_WEBHOOK_URL not configured'
        }
    
    try:
        # Determine color and emoji
        if notification_data.get('success', False):
            color = '#00e5a0'  # Green
            emoji = '✅'
            status_text = 'Completed Successfully'
        else:
            color = '#ef4444'  # Red
            emoji = '❌'
            status_text = 'Failed'
        
        # Format skill name
        skill_name = notification_data.get('skill_id', 'Unknown Skill').replace('_', ' ').replace('-', ' ').title()
        
        # Build Slack message
        message = {
            'attachments': [{
                'color': color,
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': f'{emoji} Skill {status_text}',
                            'emoji': True
                        }
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f'*Skill:*\n{skill_name}'
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f'*Client:*\n{notification_data.get("client_name", notification_data.get("client_id", "Unknown"))}'
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f'*Duration:*\n{notification_data.get("duration_ms", 0)}ms'
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f'*Time:*\n{datetime.now().strftime("%I:%M %p")}'
                            }
                        ]
                    }
                ]
            }]
        }
        
        # Add error details if failed
        if not notification_data.get('success', False) and notification_data.get('error'):
            message['attachments'][0]['blocks'].append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Error:*\n```{notification_data.get("error")[:200]}```'
                }
            })
        
        # Add result preview if successful
        if notification_data.get('success', False) and notification_data.get('result_summary'):
            message['attachments'][0]['blocks'].append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Result:*\n{notification_data.get("result_summary")[:300]}'
                }
            })
        
        # Send to Slack
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=message,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Notification sent to Slack'
            }
        else:
            return {
                'success': False,
                'error': f'Slack API returned {response.status_code}'
            }
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Failed to send Slack notification: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Notification error: {str(e)}'
        }


def send_usage_alert(alert_data):
    """
    Send usage alert to Slack (e.g., approaching limit)
    
    Args:
        alert_data: dict containing:
            - client_id: Client identifier
            - client_name: Client name
            - usage_percent: Percentage of limit used
            - current_usage: Current usage count
            - limit: Usage limit
    """
    if not SLACK_WEBHOOK_URL:
        return {'success': False, 'error': 'SLACK_WEBHOOK_URL not configured'}
    
    try:
        usage_percent = alert_data.get('usage_percent', 0)
        
        # Determine urgency
        if usage_percent >= 90:
            color = '#ef4444'  # Red
            emoji = '🚨'
            urgency = 'CRITICAL'
        elif usage_percent >= 75:
            color = '#f59e0b'  # Orange
            emoji = '⚠️'
            urgency = 'WARNING'
        else:
            color = '#3b82f6'  # Blue
            emoji = 'ℹ️'
            urgency = 'INFO'
        
        message = {
            'attachments': [{
                'color': color,
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': f'{emoji} {urgency}: Usage Alert',
                            'emoji': True
                        }
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f'*Client:*\n{alert_data.get("client_name", alert_data.get("client_id"))}'
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f'*Usage:*\n{alert_data.get("current_usage")}/{alert_data.get("limit")} ({usage_percent}%)'
                            }
                        ]
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f'Client is at *{usage_percent}%* of their monthly limit.'
                        }
                    }
                ]
            }]
        }
        
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=message,
            headers={'Content-Type': 'application/json'},
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
