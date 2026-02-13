"""
Generate Monthly Insights Report (MVP)

Analyzes client data and generates monthly insights PDF with:
- Performance summary
- Top 3-5 optimization opportunities
- ROI calculations
- Recommended actions

This is the MVP version that uses manual data input.
Future: Integrate with predictive_analytics_orchestrator.py for automated analysis.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

def generate_monthly_insights(
    client_id: str,
    opportunities: List[Dict[str, Any]] = None,
    manual_metrics: Dict[str, Any] = None
) -> str:
    """
    Generate monthly insights report for a client.
    
    Args:
        client_id: Client identifier
        opportunities: List of opportunities (manual input for MVP)
        manual_metrics: Performance metrics (manual input for MVP)
        
    Returns:
        Path to generated markdown report
    """
    
    # Load client config
    client_path = f"clients/{client_id}/config.json"
    if not os.path.exists(client_path):
        raise ValueError(f"Client {client_id} not found")
    
    with open(client_path, 'r') as f:
        client_config = json.load(f)
    
    client_name = client_config.get("name", "Client")
    
    # Use provided metrics or defaults
    metrics = manual_metrics or get_default_metrics(client_config)
    
    # Use provided opportunities or generate templates
    opps = opportunities or generate_template_opportunities()
    
    # Generate report
    report_date = datetime.now()
    report_month = report_date.strftime("%B %Y")
    
    report_content = create_report_markdown(
        client_name=client_name,
        report_month=report_month,
        metrics=metrics,
        opportunities=opps
    )
    
    # Save report
    report_dir = f".tmp/client_insights/{client_id}"
    os.makedirs(report_dir, exist_ok=True)
    
    report_filename = f"insights_{report_date.strftime('%Y_%m')}.md"
    report_path = os.path.join(report_dir, report_filename)
    
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"✅ Monthly insights report generated for {client_name}")
    print(f"📁 Location: {report_path}")
    print(f"📅 Report Period: {report_month}")
    print(f"💡 Opportunities Identified: {len(opps)}")
    print("\n📋 Next Steps:")
    print("1. Review report for accuracy")
    print("2. Convert to PDF (use Markdown→PDF tool)")
    print("3. Email to client + upload to Google Drive")
    print("4. Schedule monthly review call")
    
    return report_path


def get_default_metrics(client_config: Dict) -> Dict[str, Any]:
    """Generate default metrics for MVP."""
    
    return {
        "time_saved_this_month": 32,  # hours
        "dollar_value_this_month": 1600,  # $
        "tasks_automated": 247,
        "error_rate": 0.5,  # %
        "uptime": 99.8,  # %
        "pipeline_value": client_config.get("pipeline_value", 250000),
        "leads_processed": 42,
        "proposals_generated": 8,
        "invoices_sent": 23
    }


def generate_template_opportunities() -> List[Dict[str, Any]]:
    """Generate template opportunities for MVP."""
    
    return [
        {
            "title": "Automate Lead Scoring",
            "description": "Implement AI-powered lead scoring to prioritize high-value prospects",
            "impact_hours": 6,
            "impact_dollars": 300,
            "effort": "Medium",
            "timeline": "2 weeks",
            "roi_score": "High"
        },
        {
            "title": "Email Sequence Optimization",
            "description": "A/B test email subject lines and optimize send times",
            "impact_hours": 4,
            "impact_dollars": 200,
            "effort": "Low",
            "timeline": "1 week",
            "roi_score": "High"
        },
        {
            "title": "Dashboard Integration",
            "description": "Connect live CRM data to real-time dashboard",
            "impact_hours": 8,
            "impact_dollars": 400,
            "effort": "High",
            "timeline": "3 weeks",
            "roi_score": "Medium"
        }
    ]


def create_report_markdown(
    client_name: str,
    report_month: str,
    metrics: Dict[str, Any],
    opportunities: List[Dict[str, Any]]
) -> str:
    """Create the markdown content for the insights report."""
    
    report = f"""# Monthly Insights Report
## {client_name} | {report_month}

---

## 📊 Executive Summary

### This Month at a Glance

**🎉 Wins:**
- Saved **{metrics['time_saved_this_month']} hours** of manual work (${metrics['dollar_value_this_month']:,} value)
- Processed **{metrics['tasks_automated']} automated tasks** with **{metrics['error_rate']}% error rate**
- System uptime: **{metrics['uptime']}%** (rock solid performance)

**⚠️ Concerns:**
- [Manual: Add any performance degradations or issues]

**💡 Top Opportunity:**
- **{opportunities[0]['title']}** — Could save an additional **{opportunities[0]['impact_hours']} hours/month** (${opportunities[0]['impact_dollars']})

---

## 📈 Performance Dashboard

### Key Metrics

| Metric | This Month | Last Month | Change |
|--------|-----------|------------|---------|
| Time Saved | {metrics['time_saved_this_month']} hrs | [Previous] | +[X]% |
| $ Value | ${metrics['dollar_value_this_month']:,} | $[Previous] | +[X]% |
| Tasks Processed | {metrics['tasks_automated']} | [Previous] | +[X]% |
| Error Rate | {metrics['error_rate']}% | [Previous] | -[X]% |
| System Uptime | {metrics['uptime']}% | [Previous] | +[X]% |

### Automation Activity

**Lead Management:**
- Leads processed: **{metrics['leads_processed']}**
- Auto-follow-ups sent: [Manual]
- Response rate: [Manual]%

**Sales Operations:**
- Proposals generated: **{metrics['proposals_generated']}**
- Contracts sent: [Manual]
- Invoices automated: **{metrics['invoices_sent']}**

**Pipeline Health:**
- Total pipeline value: **${metrics['pipeline_value']:,}**
- Deals in progress: [Manual]
- Win rate: [Manual]%

---

## 💡 Optimization Opportunities

We've identified **{len(opportunities)} high-value opportunities** to further optimize your operations this month:

"""

    # Add each opportunity
    for i, opp in enumerate(opportunities, 1):
        report += f"""
### Opportunity #{i}: {opp['title']}

**What:**  
{opp['description']}

**Impact:**  
- **Time Saved:** {opp['impact_hours']} hours/month
- **$ Value:** ${opp['impact_dollars']}/month (${opp['impact_dollars'] * 12:,}/year)
- **ROI Score:** {opp['roi_score']}

**Implementation:**  
- **Effort:** {opp['effort']}
- **Timeline:** {opp['timeline']}
- **Risk:** Low

**Why This Matters:**  
[Manual: Add context about why this opportunity is valuable for this specific client]

---
"""

    # Add recommendations section
    report += """
## 🎯 Recommended Priorities

Based on ROI and effort, we recommend tackling these in order:

### Do This Month (Quick Wins)
1. **""" + opportunities[1]['title'] + f"""** — Low effort, high impact
   - Timeline: {opportunities[1]['timeline']}
   - Expected ROI: ${opportunities[1]['impact_dollars']}/month

### Do Next Month (Strategic Improvements)
2. **""" + opportunities[0]['title'] + f"""** — Medium effort, significant value
   - Timeline: {opportunities[0]['timeline']}
   - Expected ROI: ${opportunities[0]['impact_dollars']}/month

### Explore Later (Big Bets)
3. **""" + opportunities[2]['title'] + f"""** — High effort, transformative potential
   - Timeline: {opportunities[2]['timeline']}
   - Expected ROI: ${opportunities[2]['impact_dollars']}/month

---

## 🎉 Wins This Month

### System Reliability
- ✅ {metrics['uptime']}% uptime (only {(100 - metrics['uptime']) * 7.2:.1f} minutes of downtime all month)
- ✅ {metrics['error_rate']}% error rate (industry average is 2-3%)
- ✅ 100% of critical workflows executed successfully

### Business Impact
- 💰 ${metrics['dollar_value_this_month']:,} in time value recovered
- ⏱️ {metrics['time_saved_this_month']} hours freed up for strategic work
- 📈 [Manual: Add specific business wins like "closed 3 deals faster" or "improved customer response time"]

### Client Feedback
[Manual: Add any positive feedback or testimonials from this month]

---

## 📅 Next Steps

### For Our Next Call (30 min)
1. **Review top 3 opportunities** (10 min)
   - Which ones align with your priorities?
   - Timeline and resource availability?

2. **Discuss any concerns** (5 min)
   - Performance issues?
   - New pain points emerging?

3. **Plan next month** (10 min)
   - What should we prioritize?
   - Any upcoming business changes?

4. **Action items** (5 min)
   - Who owns what?
   - Timeline for implementation?

### Proposed Implementation Schedule
- **Week 1:** """ + opportunities[1]['title'] + """
- **Week 2-3:** """ + opportunities[0]['title'] + """
- **Week 4:** Review and adjust

---

## 📞 Questions?

**Monthly Review Call:** [Schedule via Calendly]  
**Urgent Issues:** Slack channel or hello@5cypresslabs.com  
**Dashboard Access:** [Google Sheets link]

---

## 📝 Appendix

### Methodology
- **Time Savings:** Calculated as (manual time before) - (automated time after)
- **$ Value:** Time saved × team average hourly rate (${metrics['dollar_value_this_month'] / max(metrics['time_saved_this_month'], 1):.0f}/hr)
- **ROI Score:** Based on impact vs. effort (High = 3:1 or better, Medium = 2:1, Low = 1:1)

### Data Sources
- CRM: [Client's CRM platform]
- Automation logs: 5 Cypress Labs monitoring system
- Performance metrics: Real-time dashboard
- Baseline data: Collected during onboarding

---

*Generated on {datetime.now().strftime('%Y-%m-%d')} by 5 Cypress Labs Intelligence Platform*
"""

    return report


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_monthly_insights.py <client_id>")
        print("\nExample: python generate_monthly_insights.py acme-corp")
        print("\nFor custom metrics/opportunities, edit the script to pass data")
        sys.exit(1)
    
    client_id = sys.argv[1]
    
    try:
        report_path = generate_monthly_insights(client_id)
        print("\n✅ Report generation complete!")
        print(f"📄 Review at: {report_path}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
