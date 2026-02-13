"""
Modal Deployment for 5 Cypress Automation
Production-ready serverless functions for client automations

Deploy: modal deploy execution/modal_production.py
"""

import modal
import os
from datetime import datetime

# Create Modal app
app = modal.App("5-cypress-automation")

# Define secrets needed
secrets = [
    modal.Secret.from_name("qbo-credentials"),  # QuickBooks OAuth
    modal.Secret.from_name("smtp-credentials"),  # Email sending
    modal.Secret.from_name("google-credentials"),  # Google Sheets
]

# Python dependencies
image = modal.Image.debian_slim().pip_install([
    "google-auth",
    "google-auth-oauthlib",
    "google-api-python-client",
    "requests",
    "python-dotenv",
])


@app.function(
    secrets=secrets,
    image=image,
    timeout=300,  # 5 minutes max per order
)
def process_order_automation(order_data: dict):
    """
    Main automation function for order processing.
    Triggered by Microsoft Forms webhook or API call.
    
    Args:
        order_data: {
            "customer_name": str,
            "customer_email": str,
            "product": str,
            "quantity": int,
            "price": float,
            "shipping_address": dict,
            "client_id": str  # Which client this order is for
        }
    
    Returns:
        {
            "status": "success" | "error",
            "order_id": str,
            "invoice_id": str,
            "tracking": str,
            "message": str
        }
    """
    print(f"🚀 Processing order for {order_data['customer_name']}")
    
    try:
        # Import the automation script
        import sys
        sys.path.append('/root')
        
        from live_demo_automation import LiveDemoAutomation
        
        # Run the full automation
        demo = LiveDemoAutomation()
        results = demo.run_full_demo(order_data)
        
        # Send Slack notification
        send_slack_notification({
            "client": order_data.get("client_id", "unknown"),
            "customer": order_data["customer_name"],
            "order_id": results["order_id"],
            "status": "success" if not results["errors"] else "partial",
            "errors": results["errors"]
        })
        
        return {
            "status": "success" if not results["errors"] else "error",
            "order_id": results["order_id"],
            "invoice_id": results["invoice_id"],
            "tracking": results["shipping_label"],
            "message": "Order processed successfully" if not results["errors"] else f"Partial success: {results['errors']}"
        }
        
    except Exception as e:
        print(f"❌ Error processing order: {str(e)}")
        
        # Send error to Slack
        send_slack_notification({
            "client": order_data.get("client_id", "unknown"),
            "customer": order_data["customer_name"],
            "status": "failed",
            "error": str(e)
        })
        
        return {
            "status": "error",
            "message": str(e)
        }


@app.function(secrets=secrets, image=image)
def generate_monthly_insights(client_id: str):
    """
    Scheduled function for monthly client insights reports.
    Run via cron: @modal.cron("0 6 1 * *")  # First of month at 6 AM
    
    Args:
        client_id: Client slug (e.g., "remy-lasers")
    
    Returns:
        Path to generated PDF report
    """
    print(f"📊 Generating monthly insights for {client_id}")
    
    try:
        import sys
        sys.path.append('/root')
        
        from generate_monthly_insights import MonthlyInsightsGenerator
        
        generator = MonthlyInsightsGenerator(client_id)
        report_path = generator.generate_report()
        
        # Send to client via email
        # (Implementation depends on your email setup)
        
        return {
            "status": "success",
            "report_path": report_path,
            "client_id": client_id
        }
        
    except Exception as e:
        print(f"❌ Error generating insights: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.function(secrets=secrets)
def send_slack_notification(data: dict):
    """Send notification to Slack channel."""
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    
    if not slack_webhook:
        print("⚠️ No Slack webhook configured")
        return
    
    import requests
    
    # Format message
    if data["status"] == "success":
        emoji = "✅"
        color = "good"
    elif data["status"] == "partial":
        emoji = "⚠️"
        color = "warning"
    else:
        emoji = "❌"
        color = "danger"
    
    message = {
        "attachments": [{
            "color": color,
            "title": f"{emoji} Order Automation Update",
            "fields": [
                {"title": "Client", "value": data["client"], "short": True},
                {"title": "Customer", "value": data.get("customer", "N/A"), "short": True},
                {"title": "Order ID", "value": data.get("order_id", "N/A"), "short": True},
                {"title": "Status", "value": data["status"], "short": True},
            ],
            "footer": "5 Cypress Automation",
            "ts": int(datetime.now().timestamp())
        }]
    }
    
    if "error" in data:
        message["attachments"][0]["fields"].append({
            "title": "Error",
            "value": str(data["error"]),
            "short": False
        })
    
    try:
        response = requests.post(slack_webhook, json=message)
        response.raise_for_status()
        print("✅ Slack notification sent")
    except Exception as e:
        print(f"⚠️ Failed to send Slack notification: {str(e)}")


# Webhook endpoints
@app.function()
@modal.web_endpoint(method="POST")
def webhook_order(data: dict):
    """
    Public webhook for order submissions.
    URL: https://[your-modal-url]/webhook_order
    
    Called by: Microsoft Forms, Zapier, custom forms, etc.
    """
    print(f"📥 Webhook received: {data}")
    
    # Validate required fields
    required = ["customer_name", "customer_email", "product", "quantity", "price"]
    missing = [f for f in required if f not in data]
    
    if missing:
        return {
            "status": "error",
            "message": f"Missing required fields: {missing}"
        }, 400
    
    # Process order asynchronously
    result = process_order_automation.remote(data)
    
    return result


@app.function()
@modal.web_endpoint(method="GET")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "5 Cypress Automation",
        "timestamp": datetime.now().isoformat()
    }


# Scheduled jobs
@app.function(
    schedule=modal.Cron("0 6 1 * *"),  # First of month at 6 AM UTC
    secrets=secrets,
    image=image
)
def monthly_insights_all_clients():
    """Run monthly insights for all active clients."""
    # List of active clients (could be pulled from database)
    active_clients = [
        "remy-lasers",
        # Add more as you onboard clients
    ]
    
    print(f"📅 Running monthly insights for {len(active_clients)} clients")
    
    for client_id in active_clients:
        try:
            result = generate_monthly_insights.remote(client_id)
            print(f"✅ {client_id}: {result['status']}")
        except Exception as e:
            print(f"❌ {client_id}: {str(e)}")


@app.local_entrypoint()
def main():
    """Test the automation locally."""
    print("🧪 Testing order automation...")
    
    test_order = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "product": "Laser Engraver XL",
        "quantity": 1,
        "price": 2499.00,
        "client_id": "remy-lasers",
        "shipping_address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94102"
        }
    }
    
    result = process_order_automation.remote(test_order)
    print("\n" + "="*60)
    print("RESULT:", result)
    print("="*60)


if __name__ == "__main__":
    # Deploy: modal deploy execution/modal_production.py
    # Test: modal run execution/modal_production.py
    pass
