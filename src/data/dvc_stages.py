"""Data quality reporting and artifact generation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from utils.logger import logger


class DataQualityReport:
    """Generate and export data quality reports."""

    def __init__(self, output_dir: Path = None):
        """Initialize report generator."""
        self.output_dir = output_dir or Path("mlops/data_quality")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_report(self, validation_result: dict, df: pd.DataFrame) -> str:
        """
        Create comprehensive data quality report.

        Args:
            validation_result: Output from DataValidator.validate()
            df: The validated DataFrame

        Returns:
            Path to generated report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "PASS" if validation_result["is_valid"] else "FAIL",
            "validation": validation_result,
            "data_summary": self._summarize_data(df),
        }

        # Save JSON report
        report_path = (
            self.output_dir / f"data_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Generate markdown report
        md_path = self.output_dir / f"data_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self._write_markdown_report(report, md_path)

        logger.info(f"Data quality report generated: {report_path}")
        return str(report_path)

    def _summarize_data(self, df: pd.DataFrame) -> dict[str, Any]:
        """Summarize dataset characteristics."""
        summary = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing": df.isnull().sum().to_dict(),
            "missing_pct": (df.isnull().sum() / len(df) * 100).to_dict(),
            "duplicates": len(df[df.duplicated()]),
        }

        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = {}
            for col in numeric_cols:
                summary["numeric_summary"][col] = {
                    "count": int(df[col].count()),
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "25%": float(df[col].quantile(0.25)),
                    "50%": float(df[col].quantile(0.50)),
                    "75%": float(df[col].quantile(0.75)),
                    "max": float(df[col].max()),
                }

        return summary

    def _write_markdown_report(self, report: dict, path: Path) -> None:
        """Write markdown formatted report."""
        with open(path, "w") as f:
            f.write("# Data Quality Report\n\n")
            f.write(f"Generated: {report['timestamp']}\n")
            f.write(f"Status: **{report['status']}**\n\n")

            # Validation summary
            f.write("## Validation Summary\n\n")
            f.write(f"- Valid: {report['validation']['is_valid']}\n")
            f.write(f"- Errors: {len(report['validation']['errors'])}\n")
            f.write(f"- Warnings: {len(report['validation']['warnings'])}\n\n")

            # Errors
            if report["validation"]["errors"]:
                f.write("### Errors\n\n")
                for error in report["validation"]["errors"]:
                    f.write(f"- {error}\n")
                f.write("\n")

            # Warnings
            if report["validation"]["warnings"]:
                f.write("### Warnings\n\n")
                for warning in report["validation"]["warnings"]:
                    f.write(f"- {warning}\n")
                f.write("\n")

            # Data summary
            f.write("## Data Summary\n\n")
            summary = report["data_summary"]
            f.write(f"- **Rows**: {summary['shape']['rows']}\n")
            f.write(f"- **Columns**: {summary['shape']['columns']}\n")
            f.write(f"- **Duplicates**: {summary['duplicates']}\n\n")

            # Null analysis
            f.write("### Missing Values\n\n")
            missing = summary["missing"]
            if any(missing.values()):
                for col, count in missing.items():
                    pct = summary["missing_pct"].get(col, 0)
                    f.write(f"- {col}: {count} ({pct:.2f}%)\n")
            else:
                f.write("No missing values\n")
            f.write("\n")

            # Numeric summary
            if "numeric_summary" in summary:
                f.write("### Numeric Columns Summary\n\n")
                for col, stats in summary["numeric_summary"].items():
                    f.write(f"#### {col}\n\n")
                    f.write("| Statistic | Value |\n")
                    f.write("|-----------|-------|\n")
                    f.write(f"| Count | {stats['count']} |\n")
                    f.write(f"| Mean | {stats['mean']:.2f} |\n")
                    f.write(f"| Std | {stats['std']:.2f} |\n")
                    f.write(f"| Min | {stats['min']:.2f} |\n")
                    f.write(f"| 25% | {stats['25%']:.2f} |\n")
                    f.write(f"| 50% | {stats['50%']:.2f} |\n")
                    f.write(f"| 75% | {stats['75%']:.2f} |\n")
                    f.write(f"| Max | {stats['max']:.2f} |\n\n")

        logger.info(f"Markdown report written: {path}")
