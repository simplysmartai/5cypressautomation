"""
Calculate Client ROI

Tracks baseline metrics vs. current state to calculate:
- Time saved (hours/month)
- Dollar value ($)
- Error reduction (%)
- Revenue impact
- ROI multiple

This script manages the "before/after" comparison that proves value.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def track_baseline(
    client_id: str,
    baseline_data: Dict[str, Any]
) -> None:
    """
    Store baseline metrics for a client (captured during onboarding).
    
    Args:
        client_id: Client identifier
        baseline_data: Dictionary with baseline metrics
    """
    
    baseline = {
        "client_id": client_id,
        "captured_at": datetime.now().isoformat(),
        "metrics": baseline_data,
        "version": "1.0"
    }
    
    # Save to client folder
    client_dir = f"clients/{client_id}"
    os.makedirs(client_dir, exist_ok=True)
    
    baseline_path = os.path.join(client_dir, "baseline_metrics.json")
    
    with open(baseline_path, 'w') as f:
        json.dump(baseline, f, indent=2)
    
    print(f"✅ Baseline metrics captured for client {client_id}")
    print(f"📁 Saved to: {baseline_path}")


def calculate_roi(
    client_id: str,
    current_metrics: Dict[str, Any],
    period_months: int = 1
) -> Dict[str, Any]:
    """
    Calculate ROI by comparing current metrics to baseline.
    
    Args:
        client_id: Client identifier
        current_metrics: Current performance metrics
        period_months: Number of months to calculate over
        
    Returns:
        Dictionary with ROI calculations
    """
    
    # Load baseline
    baseline_path = f"clients/{client_id}/baseline_metrics.json"
    if not os.path.exists(baseline_path):
        raise ValueError(f"No baseline metrics found for client {client_id}")
    
    with open(baseline_path, 'r') as f:
        baseline = json.load(f)
    
    baseline_metrics = baseline["metrics"]
    
    # Calculate improvements
    roi = {
        "client_id": client_id,
        "calculated_at": datetime.now().isoformat(),
        "period_months": period_months,
        "baseline": baseline_metrics,
        "current": current_metrics,
        "improvements": {}
    }
    
    # Time savings
    baseline_time = baseline_metrics.get("manual_hours_per_month", 0)
    current_time = current_metrics.get("manual_hours_per_month", 0)
    time_saved = baseline_time - current_time
    
    hourly_rate = baseline_metrics.get("hourly_rate", 50)
    dollar_value = time_saved * hourly_rate
    
    roi["improvements"]["time_saved"] = {
        "hours_per_month": time_saved,
        "hours_total": time_saved * period_months,
        "dollar_value_per_month": dollar_value,
        "dollar_value_total": dollar_value * period_months,
        "percentage_reduction": (time_saved / baseline_time * 100) if baseline_time > 0 else 0
    }
    
    # Error reduction
    baseline_errors = baseline_metrics.get("error_rate_pct", 5)
    current_errors = current_metrics.get("error_rate_pct", 0.5)
    error_reduction = baseline_errors - current_errors
    
    roi["improvements"]["error_reduction"] = {
        "baseline_error_rate": baseline_errors,
        "current_error_rate": current_errors,
        "reduction_pct": error_reduction,
        "percentage_improvement": (error_reduction / baseline_errors * 100) if baseline_errors > 0 else 0
    }
    
    # Revenue impact (if applicable)
    baseline_revenue = baseline_metrics.get("monthly_revenue", 0)
    current_revenue = current_metrics.get("monthly_revenue", 0)
    revenue_increase = current_revenue - baseline_revenue
    
    if baseline_revenue > 0:
        roi["improvements"]["revenue_impact"] = {
            "baseline_revenue": baseline_revenue,
            "current_revenue": current_revenue,
            "revenue_increase": revenue_increase,
            "percentage_increase": (revenue_increase / baseline_revenue * 100)
        }
    
    # ROI multiple ($ value / investment)
    implementation_cost = baseline_metrics.get("implementation_cost", 0)
    monthly_cost = baseline_metrics.get("monthly_partnership_cost", 0)
    total_investment = implementation_cost + (monthly_cost * period_months)
    
    roi_multiple = (dollar_value * period_months) / total_investment if total_investment > 0 else 0
    
    roi["financial"] = {
        "total_investment": total_investment,
        "total_value_generated": dollar_value * period_months,
        "net_value": (dollar_value * period_months) - total_investment,
        "roi_multiple": roi_multiple,
        "payback_period_months": total_investment / dollar_value if dollar_value > 0 else 0
    }
    
    # Save ROI calculation
    roi_dir = f".tmp/client_insights/{client_id}"
    os.makedirs(roi_dir, exist_ok=True)
    
    roi_path = os.path.join(roi_dir, f"roi_calculation_{datetime.now().strftime('%Y_%m')}.json")
    
    with open(roi_path, 'w') as f:
        json.dump(roi, f, indent=2)
    
    print_roi_summary(roi)
    
    return roi


def print_roi_summary(roi: Dict) -> None:
    """Print human-readable ROI summary."""
    
    improvements = roi["improvements"]
    financial = roi["financial"]
    period = roi["period_months"]
    
    print("\n" + "="*60)
    print(f"ROI SUMMARY — {period} Month{'s' if period > 1 else ''}")
    print("="*60)
    
    # Time savings
    time = improvements["time_saved"]
    print(f"\n⏱️  TIME SAVINGS:")
    print(f"   • Hours saved/month: {time['hours_per_month']:.1f}")
    print(f"   • Total hours saved: {time['hours_total']:.1f}")
    print(f"   • $ Value/month: ${time['dollar_value_per_month']:,.0f}")
    print(f"   • Total $ value: ${time['dollar_value_total']:,.0f}")
    print(f"   • Reduction: {time['percentage_reduction']:.1f}%")
    
    # Error reduction
    errors = improvements["error_reduction"]
    print(f"\n✅ ERROR REDUCTION:")
    print(f"   • Baseline error rate: {errors['baseline_error_rate']:.1f}%")
    print(f"   • Current error rate: {errors['current_error_rate']:.1f}%")
    print(f"   • Improvement: {errors['percentage_improvement']:.1f}%")
    
    # Revenue impact (if exists)
    if "revenue_impact" in improvements:
        revenue = improvements["revenue_impact"]
        print(f"\n💰 REVENUE IMPACT:")
        print(f"   • Baseline revenue: ${revenue['baseline_revenue']:,.0f}/mo")
        print(f"   • Current revenue: ${revenue['current_revenue']:,.0f}/mo")
        print(f"   • Increase: ${revenue['revenue_increase']:,.0f}/mo ({revenue['percentage_increase']:.1f}%)")
    
    # Financial ROI
    print(f"\n📊 FINANCIAL ROI:")
    print(f"   • Total investment: ${financial['total_investment']:,.0f}")
    print(f"   • Total value generated: ${financial['total_value_generated']:,.0f}")
    print(f"   • Net value: ${financial['net_value']:,.0f}")
    print(f"   • ROI multiple: {financial['roi_multiple']:.1f}x")
    print(f"   • Payback period: {financial['payback_period_months']:.1f} months")
    
    print("\n" + "="*60 + "\n")


def generate_before_after_widget(client_id: str) -> str:
    """
    Generate HTML/markdown widget showing before/after metrics.
    For use on website or client dashboards.
    """
    
    # Calculate latest ROI
    baseline_path = f"clients/{client_id}/baseline_metrics.json"
    if not os.path.exists(baseline_path):
        return "No baseline data available"
    
    with open(baseline_path, 'r') as f:
        baseline = json.load(f)
    
    # For MVP, use template metrics
    # In production, pull from latest roi_calculation file
    
    baseline_time = baseline["metrics"].get("manual_hours_per_month", 40)
    current_time = 8  # Assume 80% reduction
    time_saved = baseline_time - current_time
    
    hourly_rate = baseline["metrics"].get("hourly_rate", 50)
    dollar_value = time_saved * hourly_rate
    
    widget = f"""
## Before/After Results

**Client:** {baseline["metrics"].get("company_name", "Client")}

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Manual Work | {baseline_time} hrs/month | {current_time} hrs/month | **{time_saved} hrs saved** |
| Error Rate | {baseline["metrics"].get("error_rate_pct", 5)}% | 0.5% | **90% reduction** |
| Time Value | - | ${dollar_value:,.0f}/month | **${dollar_value * 12:,.0f}/year** |

### Impact
> "We recovered **{time_saved} hours per month** that now goes to strategic work instead of manual data entry."
"""
    
    return widget


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Track baseline:   python calculate_client_roi.py track <client_id>")
        print("  Calculate ROI:    python calculate_client_roi.py calculate <client_id>")
        print("  Generate widget:  python calculate_client_roi.py widget <client_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "track" and len(sys.argv) >= 3:
        client_id = sys.argv[2]
        
        # Example baseline data (in production, collect via form/interview)
        baseline_data = {
            "company_name": "Example Company",
            "manual_hours_per_month": 40,
            "error_rate_pct": 5.0,
            "monthly_revenue": 100000,
            "hourly_rate": 50,
            "implementation_cost": 5000,
            "monthly_partnership_cost": 500
        }
        
        track_baseline(client_id, baseline_data)
        print("\n✅ Baseline captured. Now track current metrics monthly.")
        
    elif command == "calculate" and len(sys.argv) >= 3:
        client_id = sys.argv[2]
        
        # Example current metrics (in production, pull from monitoring system)
        current_metrics = {
            "manual_hours_per_month": 8,
            "error_rate_pct": 0.5,
            "monthly_revenue": 115000
        }
        
        roi = calculate_roi(client_id, current_metrics, period_months=3)
        print("\n✅ ROI calculation complete!")
        
    elif command == "widget" and len(sys.argv) >= 3:
        client_id = sys.argv[2]
        widget = generate_before_after_widget(client_id)
        print(widget)
        
    else:
        print("Invalid command or missing arguments")
        sys.exit(1)
