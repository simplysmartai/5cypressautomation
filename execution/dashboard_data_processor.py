"""
dashboard_data_processor.py
5 Cypress Automation — Dashboard Analytics Service

Ingests raw client data (CSV/Excel), performs data quality analysis, cleaning,
schema modeling, and outputs a processed dataset ready for dashboard generation.

Usage:
    python execution/dashboard_data_processor.py \
        --client nexairi \
        --file clients/nexairi/data/raw/sales_data.csv \
        [--dry-run]

Output:
    clients/{client}/data/processed/
        ├── cleaned_data.csv          ← Dashboard-ready dataset
        ├── data_quality_report.md    ← Human-readable quality report
        ├── schema.json               ← Column types, roles, stats
        └── processing_summary.json   ← Processing metadata
"""

import argparse
import json
import os
import sys
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Any

# Force UTF-8 on Windows to avoid cp1252 encoding errors with special characters
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import pandas as pd
import numpy as np
from pydantic import BaseModel, field_validator, model_validator

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("dashboard_processor")

# ── Constants ─────────────────────────────────────────────────────────────────
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_MB = 100  # Warn if file exceeds this
NULL_THRESHOLD = 0.10   # Flag columns with >10% nulls
DUPLICATE_STRATEGY = "drop_exact"  # drop_exact | flag_only

# ── Pydantic Models ───────────────────────────────────────────────────────────

class ProcessorConfig(BaseModel):
    """Validated configuration for a processing run."""
    client_id: str
    file_path: Path
    dry_run: bool = False
    sheet_name: str | None = None  # For multi-sheet Excel files

    @field_validator("client_id")
    @classmethod
    def client_must_exist(cls, v: str) -> str:
        client_dir = Path("clients") / v
        if not client_dir.exists():
            raise ValueError(f"Client directory not found: {client_dir}")
        return v

    @field_validator("file_path")
    @classmethod
    def file_must_exist(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Input file not found: {v}")
        if v.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{v.suffix}'. "
                f"Accepted: {', '.join(SUPPORTED_EXTENSIONS)}"
            )
        return v

    @model_validator(mode="after")
    def check_file_size(self) -> "ProcessorConfig":
        size_mb = self.file_path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            log.warning(
                f"Large file detected: {size_mb:.1f}MB. Processing may be slow."
            )
        return self


class ColumnSchema(BaseModel):
    """Schema metadata for a single column."""
    name: str
    dtype_raw: str
    inferred_type: str        # date | currency | numeric | category | text | id | boolean
    suggested_role: str       # dimension | measure | date | id | label
    null_count: int
    null_pct: float
    unique_count: int
    sample_values: list[Any]
    flagged: bool = False
    flag_reason: str | None = None


class DataQualityReport(BaseModel):
    """Full data quality report for a processed file."""
    client_id: str
    source_file: str
    processed_at: str
    row_count_raw: int
    row_count_clean: int
    col_count: int
    duplicate_rows_removed: int
    columns: list[ColumnSchema]
    warnings: list[str]
    errors: list[str]

# ── Core Processor ────────────────────────────────────────────────────────────

class DashboardDataProcessor:
    """
    Orchestrates data loading, quality analysis, cleaning, and export.
    """

    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.df_raw: pd.DataFrame | None = None
        self.df_clean: pd.DataFrame | None = None
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self.col_schemas: list[ColumnSchema] = []
        self.output_dir = (
            Path("clients") / config.client_id / "data" / "processed"
        )

    # ── Load ─────────────────────────────────────────────────────────────────

    def load(self) -> pd.DataFrame:
        """Load raw data from CSV or Excel."""
        path = self.config.file_path
        log.info(f"Loading: {path}")

        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, low_memory=False)
        else:
            sheet = self.config.sheet_name or 0
            df = pd.read_excel(path, sheet_name=sheet)
            # If multiple sheets were returned (sheet_name=None), take the first
            if isinstance(df, dict):
                sheet_names = list(df.keys())
                log.warning(
                    f"Multi-sheet Excel detected. Sheets: {sheet_names}. "
                    f"Using first sheet: '{sheet_names[0]}'. "
                    "Use --sheet to specify a different sheet."
                )
                df = df[sheet_names[0]]

        log.info(f"Loaded {len(df):,} rows × {len(df.columns)} columns")
        self.df_raw = df
        return df

    # ── Infer Types ───────────────────────────────────────────────────────────

    def _infer_column_type(self, series: pd.Series, col_name: str) -> tuple[str, str]:
        """
        Returns (inferred_type, suggested_role).
        inferred_type: date | currency | numeric | category | text | id | boolean
        suggested_role: dimension | measure | date | id | label
        """
        col_lower = col_name.lower()
        sample = series.dropna()

        # Boolean detection
        unique_vals = set(sample.astype(str).str.lower().unique())
        if unique_vals <= {"true", "false", "yes", "no", "1", "0", "y", "n"}:
            return "boolean", "dimension"

        # ID column heuristic
        id_keywords = ["id", "key", "code", "uuid", "ref", "number", "num", "#"]
        if any(kw in col_lower for kw in id_keywords):
            if series.nunique() / max(len(series), 1) > 0.8:
                return "id", "id"

        # Date detection
        date_keywords = ["date", "time", "day", "month", "year", "period", "week", "at", "on"]
        if any(kw in col_lower for kw in date_keywords):
            try:
                pd.to_datetime(sample.head(100), infer_datetime_format=True)
                return "date", "date"
            except Exception:
                pass
        if pd.api.types.is_datetime64_any_dtype(series):
            return "date", "date"

        # Numeric types
        if pd.api.types.is_numeric_dtype(series):
            currency_keywords = ["price", "cost", "revenue", "sales", "amount", "total",
                                  "fee", "charge", "payment", "balance", "profit", "margin",
                                  "spend", "budget", "invoice", "earning", "wage", "salary"]
            if any(kw in col_lower for kw in currency_keywords):
                return "currency", "measure"
            return "numeric", "measure"

        # Try parsing numeric from string (e.g., "$1,234.56")
        if series.dtype == object:
            cleaned = sample.astype(str).str.replace(r"[$,€£%\s]", "", regex=True)
            try:
                pd.to_numeric(cleaned.head(100))
                currency_keywords = ["price", "cost", "revenue", "amount", "total", "fee"]
                if any(kw in col_lower for kw in currency_keywords):
                    return "currency", "measure"
                return "numeric", "measure"
            except Exception:
                pass

        # Category vs. free text
        if series.dtype == object:
            cardinality_ratio = series.nunique() / max(len(series), 1)
            if cardinality_ratio < 0.15 or series.nunique() <= 30:
                return "category", "dimension"
            return "text", "label"

        return "text", "label"

    # ── Quality Analysis ──────────────────────────────────────────────────────

    def analyze(self) -> list[ColumnSchema]:
        """Build ColumnSchema for every column and flag issues."""
        df = self.df_raw
        schemas = []

        for col in df.columns:
            series = df[col]
            null_count = int(series.isna().sum())
            null_pct = null_count / max(len(series), 1)
            unique_count = int(series.nunique(dropna=True))
            inferred_type, suggested_role = self._infer_column_type(series, col)

            sample_vals = (
                series.dropna()
                .head(5)
                .tolist()
            )
            # Make sample values JSON-serializable
            sample_vals = [
                str(v) if isinstance(v, (pd.Timestamp, date)) else v
                for v in sample_vals
            ]

            flagged = False
            flag_reason = None

            if null_pct > NULL_THRESHOLD:
                flagged = True
                flag_reason = f"{null_pct:.0%} null values — confirm with client if expected"
                self.warnings.append(
                    f"Column '{col}': {null_pct:.0%} nulls ({null_count:,} rows)"
                )

            if unique_count == 1 and len(series) > 1:
                flagged = True
                flag_reason = "Only one unique value — this column may not be useful"
                self.warnings.append(f"Column '{col}': only one unique value '{sample_vals[0] if sample_vals else ''}'")

            if unique_count == 0:
                flagged = True
                flag_reason = "All values are null — column is empty"
                self.errors.append(f"Column '{col}': entirely empty")

            schema = ColumnSchema(
                name=col,
                dtype_raw=str(series.dtype),
                inferred_type=inferred_type,
                suggested_role=suggested_role,
                null_count=null_count,
                null_pct=round(null_pct, 4),
                unique_count=unique_count,
                sample_values=sample_vals,
                flagged=flagged,
                flag_reason=flag_reason,
            )
            schemas.append(schema)

        self.col_schemas = schemas
        return schemas

    # ── Clean ────────────────────────────────────────────────────────────────

    def clean(self) -> pd.DataFrame:
        """Apply standard cleaning operations."""
        df = self.df_raw.copy()
        raw_rows = len(df)

        # Strip leading/trailing whitespace from string columns
        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda s: s.str.strip() if s.dtype == "object" else s)

        # Normalize column names (lowercase, underscores, strip special chars)
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(r"[^\w\s]", "", regex=True)
            .str.replace(r"\s+", "_", regex=True)
        )

        # Parse date columns
        for schema in self.col_schemas:
            col_normalized = (
                schema.name.strip().lower()
                .replace(" ", "_")
            )
            if schema.inferred_type == "date" and col_normalized in df.columns:
                try:
                    df[col_normalized] = pd.to_datetime(
                        df[col_normalized], infer_datetime_format=True, errors="coerce"
                    )
                    nat_count = df[col_normalized].isna().sum()
                    if nat_count > 0:
                        self.warnings.append(
                            f"Column '{col_normalized}': {nat_count} dates could not be parsed (set to NaT)"
                        )
                except Exception as e:
                    self.warnings.append(f"Could not parse dates in '{col_normalized}': {e}")

        # Parse currency columns (strip $, commas, spaces)
        for schema in self.col_schemas:
            col_normalized = schema.name.strip().lower().replace(" ", "_")
            if schema.inferred_type == "currency" and col_normalized in df.columns:
                if df[col_normalized].dtype == object:
                    df[col_normalized] = (
                        df[col_normalized]
                        .astype(str)
                        .str.replace(r"[$,€£\s]", "", regex=True)
                        .str.strip()
                    )
                    df[col_normalized] = pd.to_numeric(df[col_normalized], errors="coerce")

        # Remove duplicate rows
        before = len(df)
        df = df.drop_duplicates()
        dupes_removed = before - len(df)
        if dupes_removed > 0:
            self.warnings.append(f"Removed {dupes_removed:,} exact duplicate rows")

        # Remove completely empty rows
        df = df.dropna(how="all")

        clean_rows = len(df)
        log.info(f"Cleaned: {raw_rows:,} → {clean_rows:,} rows ({raw_rows - clean_rows:,} removed)")
        self.df_clean = df
        return df

    # ── Export ────────────────────────────────────────────────────────────────

    def export(self) -> dict[str, Path]:
        """Write all outputs to the processed directory."""
        if self.config.dry_run:
            log.info("[DRY RUN] Skipping file writes.")
            return {}

        self.output_dir.mkdir(parents=True, exist_ok=True)
        outputs: dict[str, Path] = {}

        # 1. Cleaned CSV
        clean_csv = self.output_dir / "cleaned_data.csv"
        self.df_clean.to_csv(clean_csv, index=False)
        outputs["cleaned_data"] = clean_csv
        log.info(f"Exported: {clean_csv}")

        # 2. Schema JSON
        schema_json = self.output_dir / "schema.json"
        schema_data = {
            "client_id": self.config.client_id,
            "source_file": str(self.config.file_path),
            "processed_at": datetime.utcnow().isoformat(),
            "columns": [s.model_dump() for s in self.col_schemas],
        }
        schema_json.write_text(json.dumps(schema_data, indent=2, default=str), encoding="utf-8")
        outputs["schema"] = schema_json
        log.info(f"Exported: {schema_json}")

        # 3. Processing summary JSON
        summary_json = self.output_dir / "processing_summary.json"
        summary = {
            "client_id": self.config.client_id,
            "source_file": str(self.config.file_path),
            "processed_at": datetime.utcnow().isoformat(),
            "row_count_raw": len(self.df_raw),
            "row_count_clean": len(self.df_clean),
            "col_count": len(self.df_clean.columns),
            "warnings": self.warnings,
            "errors": self.errors,
        }
        summary_json.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        outputs["summary"] = summary_json
        log.info(f"Exported: {summary_json}")

        # 4. Human-readable quality report
        report_md = self.output_dir / "data_quality_report.md"
        report_md.write_text(self._build_quality_report(), encoding="utf-8")
        outputs["quality_report"] = report_md
        log.info(f"Exported: {report_md}")

        return outputs

    # ── Report Builder ────────────────────────────────────────────────────────

    def _build_quality_report(self) -> str:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        flagged_cols = [s for s in self.col_schemas if s.flagged]

        lines = [
            f"# Data Quality Report",
            f"",
            f"**Client:** {self.config.client_id}",
            f"**Source file:** `{self.config.file_path.name}`",
            f"**Processed:** {now}",
            f"",
            f"---",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Raw rows | {len(self.df_raw):,} |",
            f"| Clean rows | {len(self.df_clean):,} |",
            f"| Rows removed | {len(self.df_raw) - len(self.df_clean):,} |",
            f"| Columns | {len(self.col_schemas)} |",
            f"| Flagged columns | {len(flagged_cols)} |",
            f"| Warnings | {len(self.warnings)} |",
            f"| Errors | {len(self.errors)} |",
            f"",
        ]

        if self.errors:
            lines += ["## ❌ Errors (Must Resolve Before Build)", ""]
            for e in self.errors:
                lines.append(f"- {e}")
            lines.append("")

        if self.warnings:
            lines += ["## ⚠️ Warnings (Review Before Build)", ""]
            for w in self.warnings:
                lines.append(f"- {w}")
            lines.append("")

        lines += [
            "## Column Schema",
            "",
            "| Column | Type | Role | Nulls | Unique | Flag |",
            "|---|---|---|---|---|---|",
        ]
        for s in self.col_schemas:
            flag = f"[!] {s.flag_reason}" if s.flagged else "[OK]"
            lines.append(
                f"| `{s.name}` | {s.inferred_type} | {s.suggested_role} "
                f"| {s.null_pct:.0%} | {s.unique_count:,} | {flag} |"
            )

        lines += [
            "",
            "## Sample Values (first 5 non-null per column)",
            "",
        ]
        for s in self.col_schemas:
            samples = ", ".join(str(v) for v in s.sample_values[:5])
            lines.append(f"**`{s.name}`:** {samples}")

        lines += [
            "",
            "---",
            "",
            "## Next Steps",
            "",
            "1. Review all ⚠️ warnings above with the client before proceeding",
            "2. Resolve ❌ errors — do not proceed until all errors are cleared",
            "3. Confirm flagged columns are expected (or fix the data export)",
            "4. Pass `processed/cleaned_data.csv` and `schema.json` to `generate_dashboard.py`",
        ]

        return "\n".join(lines)

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self) -> dict[str, Path]:
        """Execute full processing pipeline."""
        log.info(f"=== Dashboard Data Processor | Client: {self.config.client_id} ===")

        self.load()
        self.analyze()
        self.clean()
        outputs = self.export()

        # Print summary
        flagged = [s for s in self.col_schemas if s.flagged]
        print("\n" + "=" * 60)
        print(f"  PROCESSING COMPLETE — {self.config.client_id}")
        print("=" * 60)
        print(f"  Rows:     {len(self.df_raw):,} raw → {len(self.df_clean):,} clean")
        print(f"  Columns:  {len(self.col_schemas)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Errors:   {len(self.errors)}")
        print(f"  Flagged:  {len(flagged)} column(s)")
        if self.errors:
            print("\n  ❌ RESOLVE ERRORS BEFORE BUILDING DASHBOARD:")
            for e in self.errors:
                print(f"     • {e}")
        if flagged:
            print("\n  ⚠️  REVIEW WITH CLIENT:")
            for s in flagged:
                print(f"     • {s.name}: {s.flag_reason}")
        if outputs:
            print(f"\n  Output: {self.output_dir}/")
        print("=" * 60 + "\n")

        return outputs


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="5 Cypress — Dashboard Data Processor"
    )
    parser.add_argument(
        "--client", required=True,
        help="Client ID (must match clients/ folder name)"
    )
    parser.add_argument(
        "--file", required=True,
        help="Path to raw data file (CSV or Excel)"
    )
    parser.add_argument(
        "--sheet", default=None,
        help="Sheet name for Excel files (default: first sheet)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Analyze and report without writing output files"
    )
    args = parser.parse_args()

    try:
        config = ProcessorConfig(
            client_id=args.client,
            file_path=Path(args.file),
            dry_run=args.dry_run,
            sheet_name=args.sheet,
        )
    except Exception as e:
        log.error(f"Configuration error: {e}")
        sys.exit(1)

    processor = DashboardDataProcessor(config)

    try:
        processor.run()
    except Exception as e:
        log.error(f"Processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
