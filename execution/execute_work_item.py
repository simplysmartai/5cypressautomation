#!/usr/bin/env python3
"""
execute_work_item.py - Route work items to appropriate execution scripts

This is the orchestration layer that takes a work item and routes it to the correct
deterministic execution script based on work item type.

Execution flow:
1. Receive work item type and context
2. Route to appropriate script (create_proposal.py, send_email.py, etc.)
3. Return execution result with artifacts
4. Log activity
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add execution scripts to path
sys.path.insert(0, str(Path(__file__).parent))

# Import execution scripts (these would be actual scripts in execution/)
# For now, we're defining placeholder handlers

def route_work_item(work_item_type, client_slug, context):
    """
    Route work item to appropriate execution script based on type.
    
    Args:
        work_item_type (str): Type of work (new_lead, create_proposal, etc.)
        client_slug (str): Client identifier
        context (dict): Additional context for execution
    
    Returns:
        dict: Execution result with success flag and artifacts
    """
    
    routing_map = {
        # Sales & Pipeline
        'new_lead': handle_new_lead,
        'schedule_discovery_call': handle_schedule_discovery_call,
        'create_proposal': handle_create_proposal,
        'send_contract': handle_send_contract,
        
        # Client Operations
        'onboard_client': handle_onboard_client,
        'modify_workflow': handle_modify_workflow,
        
        # Financial
        'create_invoice': handle_create_invoice,
        'send_payment_reminder': handle_send_payment_reminder,
        'log_payment_received': handle_log_payment_received,
        
        # Documents & Communication
        'send_email': handle_send_email,
        'generate_sow': handle_generate_sow,
        
        # Integrations & Automation
        'add_workflow': handle_add_workflow,
        'resolve_integration_issue': handle_resolve_integration_issue,
        
        # Monitoring & Alerts
        'handle_alert': handle_alert,
    }
    
    handler = routing_map.get(work_item_type)
    if not handler:
        return {
            'success': False,
            'error': f'Unknown work item type: {work_item_type}',
            'artifacts': {}
        }
    
    try:
        result = handler(client_slug, context)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'artifacts': {}
        }


# Handlers for each work item type
# In production, these would call actual scripts like create_proposal.py, send_email.py, etc.

def handle_new_lead(client_slug, context):
    """Create new lead and send initial contact email"""
    return {
        'success': True,
        'script': 'create_client.py + send_email.py',
        'artifacts': {
            'client_folder': f'clients/{client_slug}/',
            'welcome_email': f'sent to {context.get("email", "client@example.com")}'
        }
    }


def handle_schedule_discovery_call(client_slug, context):
    """Schedule discovery call and send calendar link"""
    return {
        'success': True,
        'script': 'create_calendar_link.py + send_email.py',
        'artifacts': {
            'calendar_link': 'https://calendly.com/example',
            'email_sent': f'sent to client contact'
        }
    }


def handle_create_proposal(client_slug, context):
    """Generate proposal from discovery notes"""
    return {
        'success': True,
        'script': 'create_proposal.py',
        'artifacts': {
            'google_doc_url': 'https://docs.google.com/document/d/example',
            'pdf_path': f'clients/{client_slug}/proposals/proposal-{datetime.now().timestamp()}.pdf',
            'email_sent': 'Proposal sent to client'
        }
    }


def handle_send_contract(client_slug, context):
    """Route contract to e-signature platform"""
    contract_type = context.get('contract_type', 'MSA')
    return {
        'success': True,
        'script': 'send_contract.py',
        'artifacts': {
            'contract_type': contract_type,
            'docusign_url': f'https://docusign.example.com/sign/{client_slug}',
            'email_sent': f'{contract_type} sent for signature'
        }
    }


def handle_onboard_client(client_slug, context):
    """Send welcome email and schedule kickoff call"""
    return {
        'success': True,
        'script': 'onboard_client.py',
        'artifacts': {
            'welcome_email_sent': True,
            'kickoff_call_link': 'https://calendly.com/example',
            'project_folder_created': f'clients/{client_slug}/project/'
        }
    }


def handle_modify_workflow(client_slug, context):
    """Document modification request and schedule follow-up"""
    return {
        'success': True,
        'script': 'log_activity.py + send_email.py',
        'artifacts': {
            'request_logged': True,
            'follow_up_scheduled': 'email sent asking clarifying questions',
            'call_link': 'https://calendly.com/example'
        }
    }


def handle_create_invoice(client_slug, context):
    """Generate invoice with payment links"""
    invoice_type = context.get('invoice_type', 'final')
    amount = context.get('amount', 0)
    invoice_num = f'INV-{datetime.now().strftime("%Y%m%d")}-001'
    
    return {
        'success': True,
        'script': 'create_invoice.py',
        'artifacts': {
            'invoice_number': invoice_num,
            'invoice_type': invoice_type,
            'amount': f'${amount:,.2f}',
            'invoice_pdf': f'clients/{client_slug}/invoices/{invoice_num}.pdf',
            'payment_link': 'https://stripe.com/pay/example',
            'email_sent': 'Invoice sent to client'
        }
    }


def handle_send_payment_reminder(client_slug, context):
    """Send payment reminder for overdue invoice"""
    invoice_num = context.get('invoice_number', 'INV-XXXX')
    return {
        'success': True,
        'script': 'send_email.py',
        'artifacts': {
            'reminder_email_sent': True,
            'invoice_number': invoice_num,
            'status_updated': 'reminder_sent'
        }
    }


def handle_log_payment_received(client_slug, context):
    """Log payment and mark invoice as paid"""
    invoice_num = context.get('invoice_number', 'INV-XXXX')
    amount = context.get('amount', 0)
    return {
        'success': True,
        'script': 'update_client.py',
        'artifacts': {
            'invoice_marked_paid': invoice_num,
            'amount_received': f'${amount:,.2f}',
            'thank_you_email_sent': True,
            'client_status_updated': True
        }
    }


def handle_send_email(client_slug, context):
    """Send templated email to client"""
    template = context.get('template', 'generic')
    recipient = context.get('recipient_email', 'client@example.com')
    return {
        'success': True,
        'script': 'send_email.py',
        'artifacts': {
            'email_template': template,
            'sent_to': recipient,
            'timestamp': datetime.now().isoformat(),
            'email_logged': True
        }
    }


def handle_generate_sow(client_slug, context):
    """Generate statement of work"""
    return {
        'success': True,
        'script': 'create_document.py',
        'artifacts': {
            'sow_document': f'clients/{client_slug}/proposals/SOW-{datetime.now().timestamp()}.pdf',
            'google_doc_url': 'https://docs.google.com/document/d/example',
            'email_sent': 'SOW sent to client for review'
        }
    }


def handle_add_workflow(client_slug, context):
    """Document new workflow/automation"""
    workflow_name = context.get('workflow_name', 'New Workflow')
    return {
        'success': True,
        'script': 'add_workflow.py',
        'artifacts': {
            'workflow_name': workflow_name,
            'workflow_folder': f'clients/{client_slug}/workflows/{workflow_name.lower().replace(" ", "-")}/',
            'readme_created': True,
            'activity_logged': True
        }
    }


def handle_resolve_integration_issue(client_slug, context):
    """Handle integration failures (QB, ShipStation, etc.)"""
    integration = context.get('integration', 'unknown')
    issue = context.get('issue', 'unknown')
    return {
        'success': True,
        'script': 'debug_integration.py',
        'artifacts': {
            'integration': integration,
            'issue': issue,
            'action_taken': 'auto-retry initiated',
            'debug_logs': 'logged to system',
            'status': 'investigating'
        }
    }


def handle_alert(client_slug, context):
    """Handle monitoring alert"""
    alert_type = context.get('alert_type', 'unknown')
    severity = context.get('severity', 'medium')
    return {
        'success': True,
        'script': 'monitor_recovery.py',
        'artifacts': {
            'alert_type': alert_type,
            'severity': severity,
            'action_taken': 'auto-recovery attempted',
            'timestamp': datetime.now().isoformat(),
            'escalation_status': 'escalated to manual' if severity == 'critical' else 'auto-resolved'
        }
    }


def main():
    """CLI interface for executing work items"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Usage: python execute_work_item.py <work_item_type> [client_slug] [context_json]'
        }))
        sys.exit(1)
    
    work_item_type = sys.argv[1]
    client_slug = sys.argv[2] if len(sys.argv) > 2 else 'unknown'
    
    context = {}
    if len(sys.argv) > 3:
        try:
            context = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            pass
    
    result = route_work_item(work_item_type, client_slug, context)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
