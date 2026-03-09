"""
generate_dashboard.py
5 Cypress Automation — Dashboard Analytics Service

Generates a dashboard from processed client data. Supports three output formats:
  - web:    Self-contained HTML/JS dashboard (Chart.js) — fully automated, no assembly
  - pbi:    Power BI prep package (data model, DAX measures, layout wireframe, design spec)
  - tableau: Tableau prep package (data source, calculated fields, layout wireframe)

Usage:
    python execution/generate_dashboard.py \
        --client nexairi \
        --format web \
        --title "Sales Performance Dashboard" \
        [--version 1] \
        [--dry-run]

Output:
    clients/{client}/deliverables/dashboard-v{n}/
        Web:     dashboard.html
        PBI:     data-model.csv, dax-measures.txt, power-query.txt,
                 layout-wireframe.md, design-spec.md, data-validation.md
        Tableau: data-source.csv, calculated-fields.md,
                 layout-wireframe.md, filter-spec.md, design-spec.md
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

# Force UTF-8 on Windows to avoid cp1252 encoding errors with special characters
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import pandas as pd
import numpy as np
from pydantic import BaseModel, field_validator

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("dashboard_generator")

# ── Brand Constants ───────────────────────────────────────────────────────────
BRAND = {
    "primary": "#1B4332",
    "primary_mid": "#2D6A4F",
    "primary_light": "#52B788",
    "accent": "#74C69D",
    "accent_light": "#B7E4C7",
    "bg_dark": "#0A1628",
    "bg_card": "#111827",
    "bg_card2": "#1F2937",
    "text_primary": "#F9FAFB",
    "text_secondary": "#9CA3AF",
    "text_muted": "#6B7280",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "success": "#10B981",
    "font_heading": "Playfair Display",
    "font_body": "Inter",
    "agency": "5 Cypress Automation",
    "website": "www.5cypress.com",
}

# ── Config Model ──────────────────────────────────────────────────────────────

class DashboardConfig(BaseModel):
    client_id: str
    format: str
    title: str
    version: int = 1
    dry_run: bool = False

    @field_validator("format")
    @classmethod
    def valid_format(cls, v: str) -> str:
        allowed = {"web", "pbi", "tableau"}
        if v.lower() not in allowed:
            raise ValueError(f"Format must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("client_id")
    @classmethod
    def client_must_exist(cls, v: str) -> str:
        if not (Path("clients") / v).exists():
            raise ValueError(f"Client directory not found: clients/{v}")
        return v


# ── Dashboard Generator ───────────────────────────────────────────────────────

class DashboardGenerator:

    def __init__(self, config: DashboardConfig):
        self.config = config
        self.processed_dir = Path("clients") / config.client_id / "data" / "processed"
        self.output_dir = (
            Path("clients") / config.client_id / "deliverables"
            / f"dashboard-v{config.version}"
        )
        self.df: pd.DataFrame | None = None
        self.schema: dict = {}

    # ── Load Processed Data ───────────────────────────────────────────────────

    def load(self):
        """Load cleaned dataset and schema from processor output."""
        clean_csv = self.processed_dir / "cleaned_data.csv"
        schema_json = self.processed_dir / "schema.json"

        if not clean_csv.exists():
            raise FileNotFoundError(
                f"Processed data not found: {clean_csv}\n"
                "Run dashboard_data_processor.py first."
            )

        self.df = pd.read_csv(clean_csv, low_memory=False)
        # Parse dates
        for col in self.df.columns:
            if "date" in col.lower() or "time" in col.lower():
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
                except Exception:
                    pass

        if schema_json.exists():
            self.schema = json.loads(schema_json.read_text())

        log.info(f"Loaded processed data: {len(self.df):,} rows × {len(self.df.columns)} cols")

    # ── Identify Column Roles ─────────────────────────────────────────────────

    def _get_columns_by_role(self) -> dict[str, list[str]]:
        """Returns columns grouped by their inferred role from schema."""
        roles: dict[str, list[str]] = {
            "measures": [], "dimensions": [], "dates": [], "ids": [], "labels": []
        }
        if "columns" in self.schema:
            for col in self.schema["columns"]:
                role = col.get("suggested_role", "label")
                name = col["name"].lower().replace(" ", "_")
                if name in self.df.columns:
                    if role == "measure":
                        roles["measures"].append(name)
                    elif role == "dimension":
                        roles["dimensions"].append(name)
                    elif role == "date":
                        roles["dates"].append(name)
                    elif role == "id":
                        roles["ids"].append(name)
                    else:
                        roles["labels"].append(name)
        else:
            # Fallback: infer from dtypes
            for col in self.df.columns:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    roles["measures"].append(col)
                elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                    roles["dates"].append(col)
                else:
                    roles["dimensions"].append(col)
        return roles

    # ── Compute KPIs ──────────────────────────────────────────────────────────

    def _compute_kpis(self, roles: dict) -> list[dict]:
        """Compute top-level KPI cards from measure columns."""
        kpis = []
        measures = roles["measures"][:6]  # Cap at 6 KPIs

        for col in measures:
            series = self.df[col].dropna()
            if len(series) == 0:
                continue

            # Skip datetime columns — they can't be summed
            if pd.api.types.is_datetime64_any_dtype(series):
                continue
            if not pd.api.types.is_numeric_dtype(series):
                continue

            total = series.sum()
            mean = series.mean()
            max_val = series.max()
            min_val = series.min()

            # Detect if currency-like
            is_currency = any(
                kw in col.lower() for kw in
                ["price", "revenue", "cost", "amount", "total", "sales",
                 "fee", "charge", "profit", "margin", "spend", "budget",
                 "earning", "wage", "salary", "invoice"]
            )

            def fmt(v: float) -> str:
                if is_currency:
                    if abs(v) >= 1_000_000:
                        return f"${v/1_000_000:.1f}M"
                    if abs(v) >= 1_000:
                        return f"${v/1_000:.1f}K"
                    return f"${v:,.2f}"
                if abs(v) >= 1_000_000:
                    return f"{v/1_000_000:.1f}M"
                if abs(v) >= 1_000:
                    return f"{v/1_000:.1f}K"
                return f"{v:,.1f}"

            label = col.replace("_", " ").title()
            kpis.append({
                "label": label,
                "value": fmt(total),
                "sub": f"Avg: {fmt(mean)} | Max: {fmt(max_val)}",
                "raw_total": float(total),
                "raw_mean": float(mean),
                "is_currency": is_currency,
                "col": col,
            })

        return kpis

    # ── Build Trend Data ──────────────────────────────────────────────────────

    def _build_trend_data(self, roles: dict) -> dict | None:
        """Build monthly trend for the first date + measure combination."""
        if not roles["dates"] or not roles["measures"]:
            return None

        date_col = roles["dates"][0]
        measure_col = roles["measures"][0]

        df_trend = self.df[[date_col, measure_col]].dropna()
        df_trend[date_col] = pd.to_datetime(df_trend[date_col], errors="coerce")
        df_trend = df_trend.dropna(subset=[date_col])
        df_trend["period"] = df_trend[date_col].dt.to_period("M")

        monthly = (
            df_trend.groupby("period")[measure_col]
            .sum()
            .reset_index()
            .sort_values("period")
        )

        if len(monthly) < 2:
            return None

        return {
            "labels": [str(p) for p in monthly["period"]],
            "values": [round(v, 2) for v in monthly[measure_col]],
            "measure_label": measure_col.replace("_", " ").title(),
        }

    # ── Build Category Breakdown ──────────────────────────────────────────────

    def _build_category_data(self, roles: dict) -> dict | None:
        """Build a category breakdown for the first dimension + measure pair."""
        if not roles["dimensions"] or not roles["measures"]:
            return None

        dim_col = roles["dimensions"][0]
        measure_col = roles["measures"][0]

        grouped = (
            self.df.groupby(dim_col)[measure_col]
            .sum()
            .reset_index()
            .sort_values(measure_col, ascending=False)
            .head(10)
        )

        return {
            "labels": grouped[dim_col].astype(str).tolist(),
            "values": [round(v, 2) for v in grouped[measure_col]],
            "dimension_label": dim_col.replace("_", " ").title(),
            "measure_label": measure_col.replace("_", " ").title(),
        }

    # ── WEB DASHBOARD ─────────────────────────────────────────────────────────

    def generate_web(self) -> Path:
        """Generate a self-contained HTML dashboard."""
        roles = self._get_columns_by_role()
        kpis = self._compute_kpis(roles)
        trend = self._build_trend_data(roles)
        category = self._build_category_data(roles)

        kpi_html = ""
        for kpi in kpis[:4]:
            kpi_html += f"""
            <div class="kpi-card">
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-value">{kpi['value']}</div>
                <div class="kpi-sub">{kpi['sub']}</div>
            </div>"""

        trend_js = ""
        trend_section = ""
        if trend:
            trend_js = f"""
            new Chart(document.getElementById('trendChart'), {{
                type: 'line',
                data: {{
                    labels: {json.dumps(trend['labels'])},
                    datasets: [{{
                        label: '{trend["measure_label"]}',
                        data: {json.dumps(trend['values'])},
                        borderColor: '{BRAND["primary_light"]}',
                        backgroundColor: '{BRAND["primary_light"]}22',
                        borderWidth: 2,
                        pointRadius: 3,
                        tension: 0.4,
                        fill: true,
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '{BRAND["text_secondary"]}', maxTicksLimit: 8 }},
                               grid: {{ color: '#ffffff10' }} }},
                        y: {{ ticks: {{ color: '{BRAND["text_secondary"]}' }},
                               grid: {{ color: '#ffffff10' }} }}
                    }}
                }}
            }});"""
            trend_section = """
            <div class="chart-card full-width">
                <div class="chart-title">Monthly Trend</div>
                <div class="chart-container"><canvas id="trendChart"></canvas></div>
            </div>"""

        category_js = ""
        category_section = ""
        if category:
            colors = [BRAND["primary_light"], BRAND["accent"], BRAND["primary_mid"],
                      BRAND["accent_light"], "#A78BFA", "#60A5FA", "#F472B6",
                      "#34D399", "#FBBF24", "#F87171"]
            category_js = f"""
            new Chart(document.getElementById('categoryChart'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(category['labels'])},
                    datasets: [{{
                        label: '{category["measure_label"]}',
                        data: {json.dumps(category['values'])},
                        backgroundColor: {json.dumps(colors[:len(category['labels'])])},
                        borderRadius: 4,
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '{BRAND["text_secondary"]}' }},
                               grid: {{ color: '#ffffff10' }} }},
                        y: {{ ticks: {{ color: '{BRAND["text_secondary"]}' }},
                               grid: {{ display: false }} }}
                    }}
                }}
            }});"""
            category_section = f"""
            <div class="chart-card">
                <div class="chart-title">By {category['dimension_label']}</div>
                <div class="chart-container"><canvas id="categoryChart"></canvas></div>
            </div>"""

        now = datetime.utcnow().strftime("%B %Y")
        row_count = f"{len(self.df):,}"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self.config.title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --primary: {BRAND['primary']};
    --primary-mid: {BRAND['primary_mid']};
    --primary-light: {BRAND['primary_light']};
    --accent: {BRAND['accent']};
    --bg: {BRAND['bg_dark']};
    --bg-card: {BRAND['bg_card']};
    --bg-card2: {BRAND['bg_card2']};
    --text: {BRAND['text_primary']};
    --text-sub: {BRAND['text_secondary']};
    --text-muted: {BRAND['text_muted']};
    --success: {BRAND['success']};
    --warning: {BRAND['warning']};
    --danger: {BRAND['danger']};
  }}
  body {{
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }}
  header {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-mid) 100%);
    padding: 24px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--primary-light)30;
  }}
  header h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #fff;
  }}
  header .meta {{
    font-size: 0.8rem;
    color: var(--accent);
    text-align: right;
  }}
  .container {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 28px 24px;
  }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }}
  .kpi-card {{
    background: var(--bg-card);
    border: 1px solid var(--primary-mid)40;
    border-radius: 12px;
    padding: 20px 24px;
    border-top: 3px solid var(--primary-light);
  }}
  .kpi-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-sub);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
  }}
  .kpi-value {{
    font-size: 2rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
  }}
  .kpi-sub {{
    font-size: 0.72rem;
    color: var(--text-muted);
  }}
  .charts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }}
  .chart-card {{
    background: var(--bg-card);
    border: 1px solid var(--primary-mid)40;
    border-radius: 12px;
    padding: 20px 24px;
  }}
  .chart-card.full-width {{
    grid-column: 1 / -1;
  }}
  .chart-title {{
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-sub);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 16px;
  }}
  .chart-container {{
    height: 280px;
  }}
  .data-table-card {{
    background: var(--bg-card);
    border: 1px solid var(--primary-mid)40;
    border-radius: 12px;
    padding: 20px 24px;
    overflow-x: auto;
    margin-bottom: 24px;
  }}
  .data-table-card h3 {{
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-sub);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 16px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
  }}
  th {{
    background: var(--bg-card2);
    padding: 10px 14px;
    text-align: left;
    color: var(--text-sub);
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-bottom: 1px solid var(--primary-mid)30;
  }}
  td {{
    padding: 10px 14px;
    border-bottom: 1px solid #ffffff08;
    color: var(--text);
  }}
  tr:hover td {{ background: var(--bg-card2); }}
  footer {{
    border-top: 1px solid var(--primary-mid)30;
    padding: 16px 24px;
    text-align: center;
    font-size: 0.72rem;
    color: var(--text-muted);
  }}
  footer a {{ color: var(--primary-light); text-decoration: none; }}
  @media (max-width: 768px) {{
    header {{ flex-direction: column; gap: 12px; text-align: center; }}
    .charts-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <div>
    <div style="font-size:0.7rem;color:var(--accent);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">5 Cypress Automation</div>
    <h1>{self.config.title}</h1>
  </div>
  <div class="meta">
    <div>{now}</div>
    <div style="margin-top:4px">{row_count} records</div>
  </div>
</header>

<div class="container">

  <!-- KPI Cards -->
  <div class="kpi-grid">
    {kpi_html}
  </div>

  <!-- Charts -->
  <div class="charts-grid">
    {trend_section}
    {category_section}
  </div>

  <!-- Data Preview Table -->
  <div class="data-table-card">
    <h3>Data Preview (first 25 rows)</h3>
    {self.df.head(25).to_html(index=False, classes='', border=0, na_rep='—')}
  </div>

</div>

<footer>
  Built by <a href="https://www.5cypress.com" target="_blank">5 Cypress Automation</a>
  &nbsp;·&nbsp; {now} &nbsp;·&nbsp; {row_count} records processed
</footer>

<script>
{trend_js}
{category_js}
</script>

</body>
</html>"""

        if not self.config.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            out_path = self.output_dir / "dashboard.html"
            out_path.write_text(html, encoding="utf-8")
            log.info(f"Web dashboard written: {out_path}")
            return out_path
        else:
            log.info("[DRY RUN] Web dashboard HTML generated (not written)")
            return self.output_dir / "dashboard.html"

    # ── PBI PREP PACKAGE ──────────────────────────────────────────────────────

    def generate_pbi(self) -> dict[str, Path]:
        """Generate Power BI prep package."""
        roles = self._get_columns_by_role()
        kpis = self._compute_kpis(roles)

        if not self.config.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}

        # 1. Data model CSV (same as cleaned data)
        data_path = self.output_dir / "data-model.csv"
        if not self.config.dry_run:
            self.df.to_csv(data_path, index=False)
        outputs["data_model"] = data_path

        # 2. DAX measures
        dax_lines = [
            f"// Power BI DAX Measures — {self.config.title}",
            f"// Generated: {datetime.utcnow().strftime('%Y-%m-%d')}",
            f"// Client: {self.config.client_id}",
            "",
        ]
        for kpi in kpis:
            col = kpi["col"]
            label = kpi["label"]
            dax_lines += [
                f"// ── {label} ──────────────────────────────────────",
                f"Total {label} = SUM(data[{col}])",
                f"Avg {label} = AVERAGE(data[{col}])",
                f"Max {label} = MAX(data[{col}])",
                "",
            ]

        if roles["dates"]:
            date_col = roles["dates"][0]
            dax_lines += [
                "// ── Time Intelligence ─────────────────────────────────",
                f"// Ensure '{date_col}' is marked as Date Table in PBI",
                f"MTD {kpis[0]['label'] if kpis else 'Sales'} = ",
                f"    CALCULATE([Total {kpis[0]['label'] if kpis else 'Sales'}],",
                f"              DATESMTD(data[{date_col}]))",
                "",
                f"YTD {kpis[0]['label'] if kpis else 'Sales'} = ",
                f"    CALCULATE([Total {kpis[0]['label'] if kpis else 'Sales'}],",
                f"              DATESYTD(data[{date_col}]))",
                "",
                f"MoM Change = ",
                f"    VAR CurrentMonth = [Total {kpis[0]['label'] if kpis else 'Sales'}]",
                f"    VAR PrevMonth = CALCULATE([Total {kpis[0]['label'] if kpis else 'Sales'}],",
                f"                             DATEADD(data[{date_col}], -1, MONTH))",
                f"    RETURN IF(PrevMonth = 0, BLANK(), DIVIDE(CurrentMonth - PrevMonth, PrevMonth))",
                "",
            ]

        dax_path = self.output_dir / "dax-measures.txt"
        if not self.config.dry_run:
            dax_path.write_text("\n".join(dax_lines), encoding="utf-8")
        outputs["dax_measures"] = dax_path

        # 3. Power Query M stub
        pq_lines = [
            f"// Power Query M Code — {self.config.title}",
            "// Paste into Power Query Advanced Editor",
            "",
            'let',
            '    Source = Csv.Document(',
            '        File.Contents("[REPLACE WITH FULL PATH TO data-model.csv]"),',
            '        [Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]',
            '    ),',
            '    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        ]

        # Type conversions
        type_lines = []
        if "columns" in self.schema:
            for col_info in self.schema["columns"]:
                col = col_info["name"].lower().replace(" ", "_")
                itype = col_info.get("inferred_type", "text")
                if itype == "date":
                    type_lines.append(f'        {{"{col}", type datetime}}')
                elif itype in ("numeric", "currency"):
                    type_lines.append(f'        {{"{col}", type number}}')
                else:
                    type_lines.append(f'        {{"{col}", type text}}')

        if type_lines:
            pq_lines.append("    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {")
            pq_lines.append(",\n".join(type_lines))
            pq_lines.append("    }),")
            pq_lines.append("in")
            pq_lines.append("    ChangeTypes")
        else:
            pq_lines += ["in", "    PromoteHeaders"]

        pq_path = self.output_dir / "power-query.txt"
        if not self.config.dry_run:
            pq_path.write_text("\n".join(pq_lines), encoding="utf-8")
        outputs["power_query"] = pq_path

        # 4. Layout wireframe
        wireframe = f"""# Power BI Layout Wireframe — {self.config.title}
Generated: {datetime.utcnow().strftime('%Y-%m-%d')}

---

## Page 1: Overview

### Header Bar (top, full width)
- Title: "{self.config.title}"
- Date slicer (top-right corner, date range picker)
- If dimensions available: Category slicer (dropdown)

### KPI Cards Row (below header, equal-width columns)
"""
        for kpi in kpis[:4]:
            wireframe += f"- **{kpi['label']}**: Card visual — value from [Total {kpi['label']}] measure\n"

        wireframe += """
### Charts Section (2-column grid below KPIs)

"""
        if roles["dates"] and roles["measures"]:
            wireframe += f"""**Left (half width): Monthly Trend**
- Visual type: Line chart
- X-axis: {roles['dates'][0]} (by Month)
- Y-axis: [Total {kpis[0]['label']}]
- Enable data labels on last point only
- Color: Green (#52B788)

"""
        if roles["dimensions"] and roles["measures"]:
            wireframe += f"""**Right (half width): By {roles['dimensions'][0].replace('_', ' ').title()}**
- Visual type: Clustered bar chart (horizontal)
- Y-axis: {roles['dimensions'][0]}
- X-axis: [Total {kpis[0]['label']}]
- Sort: Descending by value
- Show top 10 only

"""

        wireframe += """### Data Table (full width, bottom)
- All columns from data-model.csv
- Enable column filtering and sorting
- Conditional formatting on measure columns (green = high, red = low)

---

## Design Notes
- Background: #0A1628 (dark blue-black)
- Card backgrounds: #111827
- Accent color: #52B788 (green)
- Font: Segoe UI (PBI default — matches Inter closely)
- No grid lines on charts (clean look)
- Round all measure values to 2 decimal places in card format strings
"""
        wireframe_path = self.output_dir / "layout-wireframe.md"
        if not self.config.dry_run:
            wireframe_path.write_text(wireframe, encoding="utf-8")
        outputs["wireframe"] = wireframe_path

        # 5. Design spec
        design = f"""# Power BI Design Spec — {self.config.title}

## Colors
| Element | Hex | Usage |
|---|---|---|
| Background | #0A1628 | Canvas background |
| Card background | #111827 | Visual card backgrounds |
| Primary green | #1B4332 | Header bar |
| Accent green | #52B788 | Lines, highlights, positive values |
| Light green | #74C69D | Secondary accents |
| Text primary | #F9FAFB | All labels, values |
| Text secondary | #9CA3AF | Axis labels, subtitles |
| Warning | #F59E0B | Below-target values |
| Danger | #EF4444 | Significantly below target |

## Typography
- Title font: Segoe UI Semibold, 18pt
- KPI values: Segoe UI Bold, 28pt
- KPI labels: Segoe UI, 9pt, ALL CAPS
- Chart labels: Segoe UI, 9pt
- Table headers: Segoe UI Semibold, 9pt

## Card Formatting
- Corner radius: 8px
- Border: 1px solid #2D6A4F (25% opacity)
- Top border accent: 3px solid #52B788
- Padding: 16px all sides

## Measure Format Strings
| Type | Format String | Example |
|---|---|---|
| Currency | $#,##0.00 | $1,234.56 |
| Currency (millions) | $#,##0.0,,\"M\" | $1.2M |
| Integer | #,##0 | 1,234 |
| Percentage | 0.0% | 12.3% |
| MoM change | +0.0%;-0.0%;0.0% | +5.2% |

## Branding Footer
- Add text box at bottom-right of each page
- Text: "Built by 5 Cypress Automation | www.5cypress.com"
- Font: Segoe UI, 8pt, color: #6B7280
"""
        design_path = self.output_dir / "design-spec.md"
        if not self.config.dry_run:
            design_path.write_text(design, encoding="utf-8")
        outputs["design_spec"] = design_path

        # 6. Data validation checklist
        validation = f"""# Data Validation Checklist — {self.config.title}
Run these checks BEFORE presenting to client.

## Row Counts
- Source CSV rows: **{len(self.df):,}**
- After PBI import, confirm row count matches: _____ rows

## Totals to Verify
"""
        for kpi in kpis:
            validation += f"- **{kpi['label']}**: expected total ≈ {kpi['value']}\n"

        validation += """
## Visual Checks
- [ ] All KPI card values match expected totals above
- [ ] Date slicer spans the full data range
- [ ] Bar chart sorted descending by value
- [ ] Trend line has no unexplained gaps or spikes
- [ ] Table shows all columns with correct types (no [Object] errors)
- [ ] Conditional formatting colors not inverted (green = good, red = bad)
- [ ] Dashboard title and date correct
- [ ] 5 Cypress footer visible on all pages

## Filters Test
- [ ] Date range filter narrows all visuals correctly
- [ ] Category slicer (if present) filters all visuals
- [ ] Cross-filtering between visuals works as expected

## Sign-off
- [ ] Nick reviewed before client presentation
"""
        validation_path = self.output_dir / "data-validation.md"
        if not self.config.dry_run:
            validation_path.write_text(validation, encoding="utf-8")
        outputs["validation"] = validation_path

        log.info(f"PBI prep package written to: {self.output_dir}")
        return outputs

    # ── TABLEAU PREP PACKAGE ──────────────────────────────────────────────────

    def generate_tableau(self) -> dict[str, Path]:
        """Generate Tableau prep package."""
        roles = self._get_columns_by_role()
        kpis = self._compute_kpis(roles)

        if not self.config.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}

        # 1. Data source CSV
        data_path = self.output_dir / "data-source.csv"
        if not self.config.dry_run:
            self.df.to_csv(data_path, index=False)
        outputs["data_source"] = data_path

        # 2. Calculated fields
        calc_lines = [
            f"# Tableau Calculated Fields — {self.config.title}",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d')}",
            "",
            "## Basic Aggregations",
            "",
        ]
        for kpi in kpis:
            col = kpi["col"]
            label = kpi["label"]
            calc_lines += [
                f"### {label} — Total",
                f"SUM([{col}])",
                "",
                f"### {label} — Average",
                f"AVG([{col}])",
                "",
            ]

        if roles["dates"]:
            date_col = roles["dates"][0]
            measure_col = roles["measures"][0] if roles["measures"] else None
            if measure_col:
                calc_lines += [
                    "## Time Intelligence",
                    "",
                    f"### Month-over-Month Change (LOD)",
                    f"{{FIXED DATETRUNC('month', [{date_col}]): SUM([{measure_col}])}}",
                    "",
                    f"### Running Total",
                    f"RUNNING_SUM(SUM([{measure_col}]))",
                    "",
                    f"### % of Total",
                    f"SUM([{measure_col}]) / TOTAL(SUM([{measure_col}]))",
                    "",
                ]

        calc_lines += [
            "## Conditional Logic",
            "",
            "### RAG Status (adapt thresholds to client targets)",
            f"IF SUM([{kpis[0]['col'] if kpis else 'value'}]) > [target_high] THEN \"Green\"",
            f"ELSEIF SUM([{kpis[0]['col'] if kpis else 'value'}]) > [target_low] THEN \"Amber\"",
            "ELSE \"Red\"",
            "END",
            "",
        ]

        calc_path = self.output_dir / "calculated-fields.md"
        if not self.config.dry_run:
            calc_path.write_text("\n".join(calc_lines), encoding="utf-8")
        outputs["calculated_fields"] = calc_path

        # 3. Layout wireframe
        wireframe = f"""# Tableau Layout Wireframe — {self.config.title}
Generated: {datetime.utcnow().strftime('%Y-%m-%d')}

## Dashboard Layout (1200 × 800px)

### Header (height: 60px, full width)
- Title: "{self.config.title}"
- Background: #1B4332
- Font: Georgia or Times New Roman Bold, white, 20pt

### KPI Bar (height: 120px, below header)
Horizontal layout, equal-width text sheets:
"""
        for kpi in kpis[:4]:
            wireframe += f"- {kpi['label']}: SUM([{kpi['col']}]) — large number, label above\n"

        wireframe += """
### Charts Area (remaining height, 2-column layout)

**Left column:**
"""
        if roles["dates"] and roles["measures"]:
            wireframe += f"""- Sheet: Monthly Trend
  - Columns: MONTH([{roles['dates'][0]}])
  - Rows: SUM([{roles['measures'][0]}])
  - Mark type: Line
  - Color: #52B788

"""
        if roles["dimensions"] and roles["measures"]:
            wireframe += f"""**Right column:**
- Sheet: By {roles['dimensions'][0].replace('_', ' ').title()}
  - Columns: SUM([{roles['measures'][0]}])
  - Rows: [{roles['dimensions'][0]}]
  - Mark type: Bar
  - Sort: Descending by SUM([{roles['measures'][0]}])
  - Show top 10: Add filter on [{roles['dimensions'][0]}] → Top 10 by field

"""

        wireframe += """### Filter Bar (sidebar or top strip)
- Date range filter
- Category quick filter (if applicable)

### Footer (height: 30px)
- Text: "Built by 5 Cypress Automation | www.5cypress.com"
- Right-aligned, small font, gray

---

## Design Notes
- Use floating layout for full control
- No grid lines on charts
- Apply custom color palette via Preferences.tps or Color Picker
- Match colors to spec in design-spec.md
"""
        wireframe_path = self.output_dir / "layout-wireframe.md"
        if not self.config.dry_run:
            wireframe_path.write_text(wireframe, encoding="utf-8")
        outputs["wireframe"] = wireframe_path

        # 4. Filter spec
        filter_spec = f"""# Tableau Filter Spec — {self.config.title}

## Filters to Implement

"""
        if roles["dates"]:
            filter_spec += f"""### Date Range Filter
- Field: [{roles['dates'][0]}]
- Filter type: Relative date OR Range of dates
- Apply to: All worksheets using this data source
- Show as: Date range picker slider

"""
        if roles["dimensions"]:
            for dim in roles["dimensions"][:2]:
                filter_spec += f"""### {dim.replace('_', ' ').title()} Filter
- Field: [{dim}]
- Filter type: Multiple values (list)
- Apply to: All worksheets
- Show as: Dropdown or compact list

"""

        filter_spec += """## Filter Actions (cross-filtering)
- Clicking a bar in the category chart → filters the trend chart
- Clicking a point on the trend → filters the data table
- Method: Dashboard Actions → Filter → Source = chart sheet → Target = all other sheets

## Highlight Actions
- Hovering over a category in the category chart highlights that category across all views
"""
        filter_path = self.output_dir / "filter-spec.md"
        if not self.config.dry_run:
            filter_path.write_text(filter_spec, encoding="utf-8")
        outputs["filter_spec"] = filter_path

        # 5. Design spec (shared with PBI, minor tweaks)
        design = f"""# Tableau Design Spec — {self.config.title}

## Color Palette
| Name | Hex | Use |
|---|---|---|
| Primary dark | #1B4332 | Header background |
| Primary | #2D6A4F | Highlighted bars |
| Accent | #52B788 | Line charts, positive |
| Light accent | #74C69D | Secondary measures |
| Background | #0A1628 | Dashboard background |
| Card | #111827 | Floating containers |
| Text | #F9FAFB | All labels |
| Muted | #9CA3AF | Axis labels |

## Typography
- Title: Georgia Bold, 20pt, white
- KPI values: Arial Bold, 28pt, white
- KPI labels: Arial, 9pt, #9CA3AF, ALL CAPS
- Axis labels: Arial, 9pt, #9CA3AF
- Tooltip text: Arial, 10pt

## Formatting
- Numbers: #,##0
- Currency: $#,##0.00
- Percentages: 0.0%
- Date axis: MMM YYYY

## Branding
- Footer text: "Built by 5 Cypress Automation | www.5cypress.com"
- Add as floating text box, bottom-right, 8pt, #6B7280
"""
        design_path = self.output_dir / "design-spec.md"
        if not self.config.dry_run:
            design_path.write_text(design, encoding="utf-8")
        outputs["design_spec"] = design_path

        log.info(f"Tableau prep package written to: {self.output_dir}")
        return outputs

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self) -> dict[str, Path]:
        log.info(f"=== Dashboard Generator | Client: {self.config.client_id} | Format: {self.config.format} ===")

        self.load()

        if self.config.format == "web":
            out_path = self.generate_web()
            outputs = {"dashboard": out_path}
        elif self.config.format == "pbi":
            outputs = self.generate_pbi()
        elif self.config.format == "tableau":
            outputs = self.generate_tableau()
        else:
            raise ValueError(f"Unknown format: {self.config.format}")

        print("\n" + "=" * 60)
        print(f"  DASHBOARD GENERATED — {self.config.client_id}")
        print("=" * 60)
        print(f"  Format:  {self.config.format.upper()}")
        print(f"  Title:   {self.config.title}")
        print(f"  Output:  {self.output_dir}/")
        print(f"  Files:")
        for key, path in outputs.items():
            print(f"    • {path.name}")
        if self.config.format == "web":
            print(f"\n  Open in browser to preview:")
            print(f"    {outputs['dashboard']}")
        elif self.config.format == "pbi":
            print(f"\n  Next steps:")
            print(f"    1. Open Power BI Desktop")
            print(f"    2. Import data-model.csv")
            print(f"    3. Open Advanced Editor → paste power-query.txt")
            print(f"    4. Open DAX editor → paste dax-measures.txt")
            print(f"    5. Follow layout-wireframe.md to arrange visuals")
            print(f"    6. Apply design-spec.md for colors/fonts")
            print(f"    7. Run data-validation.md checklist before presenting")
        elif self.config.format == "tableau":
            print(f"\n  Next steps:")
            print(f"    1. Open Tableau Desktop")
            print(f"    2. Connect to data-source.csv")
            print(f"    3. Create calculated fields from calculated-fields.md")
            print(f"    4. Build sheets per layout-wireframe.md")
            print(f"    5. Add filters per filter-spec.md")
            print(f"    6. Apply design-spec.md for styling")
        print("=" * 60 + "\n")

        return outputs


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="5 Cypress — Dashboard Generator")
    parser.add_argument("--client", required=True, help="Client ID")
    parser.add_argument("--format", required=True, choices=["web", "pbi", "tableau"],
                        help="Output format")
    parser.add_argument("--title", required=True, help="Dashboard title")
    parser.add_argument("--version", type=int, default=1, help="Version number (default: 1)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate without writing files")
    args = parser.parse_args()

    try:
        config = DashboardConfig(
            client_id=args.client,
            format=args.format,
            title=args.title,
            version=args.version,
            dry_run=args.dry_run,
        )
    except Exception as e:
        log.error(f"Configuration error: {e}")
        sys.exit(1)

    generator = DashboardGenerator(config)
    try:
        generator.run()
    except Exception as e:
        log.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
