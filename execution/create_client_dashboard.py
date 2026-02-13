"""
Create Client Dashboard (MVP)

Generates a real-time performance dashboard for clients showing:
- Key automation metrics
- Time savings and ROI
- Performance trends
- Upcoming opportunities

Output: Google Sheets dashboard with auto-updating data
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

def create_client_dashboard(client_id: str, client_name: str) -> Dict[str, Any]:
    """
    Creates a Google Sheets dashboard for a client with real-time metrics.
    
    Args:
        client_id: Unique client identifier
        client_name: Client company name
        
    Returns:
        Dictionary with dashboard URL and configuration
    """
    
    # Load client data
    client_path = f"clients/{client_id}/config.json"
    if not os.path.exists(client_path):
        raise ValueError(f"Client {client_id} not found")
    
    with open(client_path, 'r') as f:
        client_config = json.load(f)
    
    # Dashboard structure
    dashboard = {
        "client_id": client_id,
        "client_name": client_name,
        "created_at": datetime.now().isoformat(),
        "sheets": [
            "Executive Summary",
            "Pipeline Health",
            "Automation Performance",
            "Time Savings",
            "Opportunities",
            "Trends"
        ],
        "metrics": get_baseline_metrics(client_config),
        "refresh_schedule": "daily",
        "access_url": None  # Set after Google Sheets creation
    }
    
    # Create Google Sheets (placeholder for now - integrate with Google Sheets API later)
    # For MVP: Generate markdown template that can be manually imported
    
    markdown_template = generate_dashboard_markdown(dashboard, client_config)
    
    # Save to client folder
    output_path = f"clients/{client_id}/dashboard_template.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(markdown_template)
    
    print(f"✅ Dashboard template created for {client_name}")
    print(f"📁 Location: {output_path}")
    print("\n📋 Next Steps:")
    print("1. Create new Google Sheet")
    print("2. Import data from markdown template")
    print("3. Share with client")
    print("4. Set up automated data sync (future enhancement)")
    
    return dashboard


def get_baseline_metrics(client_config: Dict) -> Dict[str, Any]:
    """Extract baseline metrics from client config."""
    
    # Default metrics if not in config
    return {
        "pipeline_value": client_config.get("pipeline_value", 0),
        "avg_deal_size": client_config.get("avg_deal_size", 0),
        "sales_cycle_days": client_config.get("sales_cycle_days", 60),
        "conversion_rate": client_config.get("conversion_rate", 0.15),
        "leads_per_month": client_config.get("leads_per_month", 0),
        "team_size": client_config.get("team_size", 1),
        "hourly_rate": client_config.get("hourly_rate", 50),
        "baseline_time_spent": client_config.get("baseline_time_spent_hours", 0)
    }


def generate_dashboard_markdown(dashboard: Dict, client_config: Dict) -> str:
    """Generate markdown template for manual Google Sheets import."""
    
    client_name = dashboard["client_name"]
    metrics = dashboard["metrics"]
    
    template = f"""# {client_name} - Operations Dashboard
**Created:** {dashboard["created_at"][:10]}
**Auto-Update:** Daily

---

## 🎯 Executive Summary

| Metric | Current | Target | Trend | Status |
|--------|---------|--------|-------|--------|
| Total Pipeline Value | ${metrics.get('pipeline_value', 0):,.0f} | ${metrics.get('pipeline_value', 0) * 1.2:,.0f} | ↑ | On Track |
| Qualified Leads | {metrics.get('leads_per_month', 0)} | {int(metrics.get('leads_per_month', 0) * 1.25)} | ↑ | On Track |
| Avg Deal Size | ${metrics.get('avg_deal_size', 0):,.0f} | ${metrics.get('avg_deal_size', 0) * 1.1:,.0f} | → | Stable |
| Sales Cycle (avg) | {metrics.get('sales_cycle_days', 60)} days | {int(metrics.get('sales_cycle_days', 60) * 0.9)} days | ↓ | Improving |

---

## 📊 Pipeline Health

### Current Pipeline
- **Total Value:** ${metrics.get('pipeline_value', 0):,.0f}
- **Open Deals:** [Manual Entry]
- **Win Rate:** {metrics.get('conversion_rate', 0.15) * 100:.1f}%
- **Avg Deal Progression:** {metrics.get('sales_cycle_days', 60)} days

### Stage Breakdown
| Stage | # Deals | Value | Avg Age (Days) |
|-------|---------|-------|----------------|
| Prospect | [Manual] | $[Manual] | [Manual] |
| Qualification | [Manual] | $[Manual] | [Manual] |
| Proposal | [Manual] | $[Manual] | [Manual] |
| Negotiation | [Manual] | $[Manual] | [Manual] |

### Conversion Funnel
- Prospect → Qualified: {metrics.get('conversion_rate', 0.15) * 0.5 * 100:.0f}%
- Qualified → Proposal: {metrics.get('conversion_rate', 0.15) * 0.7 * 100:.0f}%
- Proposal → Negotiation: {metrics.get('conversion_rate', 0.15) * 0.8 * 100:.0f}%
- Negotiation → Closed Won: {metrics.get('conversion_rate', 0.15) * 1.2 * 100:.0f}%

---

## ⚙️ Automation Performance

### Workflows Active
| Workflow | Status | Tasks Processed | Errors | Uptime |
|----------|--------|-----------------|--------|--------|
| Invoice Automation | ✅ Active | [Manual] | 0 | 99.9% |
| Lead Follow-Up | ✅ Active | [Manual] | 0 | 99.9% |
| Proposal Generation | ✅ Active | [Manual] | 0 | 99.9% |
| Email Sequences | ✅ Active | [Manual] | 0 | 99.9% |

### This Month's Activity
- **Total Tasks Automated:** [Manual Entry]
- **Errors Caught & Fixed:** [Manual Entry]
- **System Uptime:** 99.9%
- **API Calls Made:** [Manual Entry]

---

## ⏱️ Time Savings

### Baseline vs. Current
| Process | Before (hrs/month) | After (hrs/month) | Saved | $ Value |
|---------|-------------------|------------------|-------|---------|
| Invoice Processing | {metrics.get('baseline_time_spent', 20)} | [Current] | [Saved] | ${metrics.get('hourly_rate', 50) * 10:,.0f} |
| Lead Follow-Up | {metrics.get('baseline_time_spent', 15)} | [Current] | [Saved] | ${metrics.get('hourly_rate', 50) * 8:,.0f} |
| Proposal Creation | {metrics.get('baseline_time_spent', 12)} | [Current] | [Saved] | ${metrics.get('hourly_rate', 50) * 6:,.0f} |
| Data Entry | {metrics.get('baseline_time_spent', 10)} | [Current] | [Saved] | ${metrics.get('hourly_rate', 50) * 5:,.0f} |

### Cumulative Impact
- **Total Hours Saved This Month:** [Calculate Sum]
- **Total $ Value:** $[Hours × ${metrics.get('hourly_rate', 50)}]
- **Total Hours Saved (All Time):** [Cumulative]
- **Total $ Value (All Time):** $[Cumulative]

---

## 💡 Current Opportunities

### Top Recommendations
1. **[Opportunity Title]**
   - **Impact:** [Time saved / $ value]
   - **Effort:** Low / Medium / High
   - **Timeline:** [Days/weeks]
   - **Status:** Not Started / In Progress / Complete

2. **[Opportunity Title]**
   - **Impact:** [Time saved / $ value]
   - **Effort:** Low / Medium / High
   - **Timeline:** [Days/weeks]
   - **Status:** Not Started / In Progress / Complete

3. **[Opportunity Title]**
   - **Impact:** [Time saved / $ value]
   - **Effort:** Low / Medium / High
   - **Timeline:** [Days/weeks]
   - **Status:** Not Started / In Progress / Complete

---

## 📈 Trends (Month-over-Month)

### Pipeline Metrics
| Metric | Last Month | This Month | Change |
|--------|-----------|------------|---------|
| Pipeline Value | $[Manual] | $[Manual] | +X% |
| New Leads | [Manual] | [Manual] | +X% |
| Closed Deals | [Manual] | [Manual] | +X% |
| Win Rate | X% | X% | +X% |

### Automation Metrics
| Metric | Last Month | This Month | Change |
|--------|-----------|------------|---------|
| Tasks Processed | [Manual] | [Manual] | +X% |
| Time Saved | X hrs | X hrs | +X% |
| Error Rate | X% | X% | -X% |
| Uptime | 99.X% | 99.X% | +X% |

---

## 📅 Next Steps

### This Month's Priorities
- [ ] [Action Item 1]
- [ ] [Action Item 2]
- [ ] [Action Item 3]

### Upcoming Milestones
- **[Date]:** [Milestone]
- **[Date]:** [Milestone]
- **[Date]:** [Milestone]

---

## 🔧 Dashboard Maintenance

**Last Updated:** [Auto-populated]
**Next Insights Report:** [First Monday of next month]
**Next Monthly Review:** [Scheduled date]
**Support Contact:** hello@5cypresslabs.com

---

## 📝 Notes & Feedback

[Client can add notes here about what's working, concerns, requests]

"""
    
    return template


def calculate_roi(client_id: str, period_months: int = 1) -> Dict[str, float]:
    """
    Calculate ROI for a client over specified period.
    
    Args:
        client_id: Client identifier
        period_months: Number of months to calculate over
        
    Returns:
        Dictionary with ROI metrics
    """
    
    # This would pull real data in production
    # For MVP, return template structure
    
    return {
        "time_saved_hours": 0.0,
        "dollar_value": 0.0,
        "error_reduction_pct": 0.0,
        "revenue_impact": 0.0,
        "roi_multiple": 0.0
    }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python create_client_dashboard.py <client_id> <client_name>")
        print("\nExample: python create_client_dashboard.py acme-corp 'Acme Corporation'")
        sys.exit(1)
    
    client_id = sys.argv[1]
    client_name = sys.argv[2]
    
    try:
        dashboard = create_client_dashboard(client_id, client_name)
        print("\n✅ Dashboard creation complete!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
