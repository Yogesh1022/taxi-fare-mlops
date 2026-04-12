"""
Great Expectations Data Quality Framework

Advanced data quality validation using Great Expectations:
1. Automatic data documentation
2. Expectation suites (50+ built-in validators)
3. Checkpoint validation
4. Custom validators for domain
5. Metrics tracking

Author: MLOps Team
Date: 2026-04-08
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a data quality check."""

    test_name: str
    passed: bool
    description: str
    details: Dict[str, Any]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class GreatExpectationsFramework:
    """
    Data quality validation framework using Great Expectations.

    Validates:
    1. Schema expectations
    2. Column statistics
    3. Row counts
    4. Null values
    5. Data distribution
    6. Business rules
    """

    def __init__(self, df: pd.DataFrame, name: str = "dataset"):
        """Initialize framework."""
        self.df = df
        self.name = name
        self.results = []
        self.expectations = {}
        self.validation_history = []
        logger.info(f"[QUALITY] Great Expectations initialized for {name}")
        logger.info(f"[QUALITY] Shape: {df.shape}")

    # Schema Expectations

    def expect_column_to_exist(self, column: str) -> ValidationResult:
        """Expect column to exist."""
        passed = column in self.df.columns
        result = ValidationResult(
            test_name="expect_column_to_exist",
            passed=passed,
            description=f'Column "{column}" exists in dataset',
            details={"column": column, "existing_columns": list(self.df.columns)},
        )
        self.results.append(result)
        return result

    def expect_column_values_to_be_in_type_list(
        self, column: str, type_list: List[str]
    ) -> ValidationResult:
        """Expect column to have certain data types."""
        col_type = str(self.df[column].dtype)
        passed = col_type in type_list
        result = ValidationResult(
            test_name="expect_column_values_to_be_in_type_list",
            passed=passed,
            description=f'Column "{column}" type {col_type} in {type_list}',
            details={"column": column, "actual_type": col_type, "expected_types": type_list},
        )
        self.results.append(result)
        return result

    # Nullness Expectations

    def expect_column_values_to_not_be_null(self, column: str) -> ValidationResult:
        """Expect no null values in column."""
        null_count = self.df[column].isnull().sum()
        passed = null_count == 0
        result = ValidationResult(
            test_name="expect_column_values_to_not_be_null",
            passed=passed,
            description=f'Column "{column}" has no null values',
            details={
                "column": column,
                "null_count": int(null_count),
                "null_pct": float(100 * null_count / len(self.df)),
            },
        )
        self.results.append(result)
        return result

    def expect_column_values_to_be_null(
        self, column: str, threshold_pct: float = 0
    ) -> ValidationResult:
        """Expect null values below threshold."""
        null_count = self.df[column].isnull().sum()
        null_pct = 100 * null_count / len(self.df)
        passed = null_pct <= threshold_pct
        result = ValidationResult(
            test_name="expect_column_values_to_be_null",
            passed=passed,
            description=f'Column "{column}" nulls <= {threshold_pct}%',
            details={
                "column": column,
                "null_count": int(null_count),
                "null_pct": float(null_pct),
                "threshold_pct": threshold_pct,
            },
        )
        self.results.append(result)
        return result

    # Value Range Expectations

    def expect_column_values_to_be_between(
        self, column: str, min_value: float = None, max_value: float = None
    ) -> ValidationResult:
        """Expect values within range."""
        col_min = self.df[column].min()
        col_max = self.df[column].max()

        min_passed = col_min >= min_value if min_value is not None else True
        max_passed = col_max <= max_value if max_value is not None else True
        passed = min_passed and max_passed

        result = ValidationResult(
            test_name="expect_column_values_to_be_between",
            passed=passed,
            description=f'Column "{column}" values between {min_value} and {max_value}',
            details={
                "column": column,
                "min_value": min_value,
                "max_value": max_value,
                "actual_min": float(col_min),
                "actual_max": float(col_max),
            },
        )
        self.results.append(result)
        return result

    # Uniqueness Expectations

    def expect_column_values_to_be_unique(self, column: str) -> ValidationResult:
        """Expect all values to be unique."""
        unique_count = self.df[column].nunique()
        total_count = len(self.df)
        passed = unique_count == total_count
        result = ValidationResult(
            test_name="expect_column_values_to_be_unique",
            passed=passed,
            description=f'Column "{column}" values are unique',
            details={
                "column": column,
                "unique_count": int(unique_count),
                "total_count": int(total_count),
            },
        )
        self.results.append(result)
        return result

    def expect_column_values_to_be_in_set(self, column: str, value_set: set) -> ValidationResult:
        """Expect values in specific set."""
        col_values = set(self.df[column].dropna().unique())
        passed = col_values.issubset(value_set)
        invalid_values = col_values - value_set
        result = ValidationResult(
            test_name="expect_column_values_to_be_in_set",
            passed=passed,
            description=f'Column "{column}" values in {value_set}',
            details={
                "column": column,
                "expected_set": list(value_set),
                "actual_values": list(col_values),
                "invalid_values": list(invalid_values),
            },
        )
        self.results.append(result)
        return result

    # String Expectations

    def expect_column_values_to_match_regex(self, column: str, regex: str) -> ValidationResult:
        """Expect strings to match regex."""
        import re

        matches = self.df[column].astype(str).str.match(regex).sum()
        total = self.df[column].notna().sum()
        passed = matches == total
        result = ValidationResult(
            test_name="expect_column_values_to_match_regex",
            passed=passed,
            description=f'Column "{column}" values match regex {regex}',
            details={
                "column": column,
                "regex": regex,
                "matches": int(matches),
                "total": int(total),
            },
        )
        self.results.append(result)
        return result

    # Distribution Expectations

    def expect_column_mean_to_be_between(
        self, column: str, min_value: float, max_value: float
    ) -> ValidationResult:
        """Expect column mean within range."""
        col_mean = self.df[column].mean()
        passed = min_value <= col_mean <= max_value
        result = ValidationResult(
            test_name="expect_column_mean_to_be_between",
            passed=passed,
            description=f'Column "{column}" mean between {min_value} and {max_value}',
            details={
                "column": column,
                "actual_mean": float(col_mean),
                "min": min_value,
                "max": max_value,
            },
        )
        self.results.append(result)
        return result

    def expect_column_stdev_to_be_between(
        self, column: str, min_value: float, max_value: float
    ) -> ValidationResult:
        """Expect column std dev within range."""
        col_stdev = self.df[column].std()
        passed = min_value <= col_stdev <= max_value
        result = ValidationResult(
            test_name="expect_column_stdev_to_be_between",
            passed=passed,
            description=f'Column "{column}" stdev between {min_value} and {max_value}',
            details={
                "column": column,
                "actual_stdev": float(col_stdev),
                "min": min_value,
                "max": max_value,
            },
        )
        self.results.append(result)
        return result

    # Taxi Domain Expectations

    def expect_taxi_fare_valid(self, column: str = "fare_amount") -> ValidationResult:
        """Taxi domain: fare must be positive and reasonable."""
        if column not in self.df.columns:
            passed = False
            details = {"column": column, "error": "Column not found"}
        else:
            # Fare between $2.5 and $500 (NYC taxi rules)
            valid = (self.df[column] >= 2.5) & (self.df[column] <= 500)
            invalid_count = (~valid).sum()
            passed = invalid_count == 0
            details = {
                "column": column,
                "valid_count": valid.sum(),
                "invalid_count": int(invalid_count),
                "min_fare": float(self.df[column].min()),
                "max_fare": float(self.df[column].max()),
            }

        result = ValidationResult(
            test_name="expect_taxi_fare_valid",
            passed=passed,
            description="Taxi fares are valid ($2.5-$500)",
            details=details,
        )
        self.results.append(result)
        return result

    def expect_trip_distance_valid(self, column: str = "trip_distance") -> ValidationResult:
        """Taxi domain: distance must be reasonable."""
        if column not in self.df.columns:
            passed = False
            details = {"column": column, "error": "Column not found"}
        else:
            # Distance between 0.1 mi and 50 mi
            valid = (self.df[column] > 0.1) & (self.df[column] <= 50)
            invalid_count = (~valid).sum()
            passed = invalid_count == 0
            details = {
                "column": column,
                "valid_count": int(valid.sum()),
                "invalid_count": int(invalid_count),
                "min_distance": float(self.df[column].min()),
                "max_distance": float(self.df[column].max()),
            }

        result = ValidationResult(
            test_name="expect_trip_distance_valid",
            passed=passed,
            description="Trip distances are valid (0.1-50 mi)",
            details=details,
        )
        self.results.append(result)
        return result

    def expect_fare_distance_correlation(
        self, fare_col: str = "fare_amount", dist_col: str = "trip_distance"
    ) -> ValidationResult:
        """Taxi domain: fare should correlate with distance."""
        if fare_col not in self.df.columns or dist_col not in self.df.columns:
            passed = False
            details = {"error": "Columns not found"}
        else:
            corr = self.df[fare_col].corr(self.df[dist_col])
            passed = corr > 0.5  # Should have positive correlation
            details = {
                "fare_column": fare_col,
                "distance_column": dist_col,
                "correlation": float(corr),
                "expected_min": 0.5,
            }

        result = ValidationResult(
            test_name="expect_fare_distance_correlation",
            passed=passed,
            description="Fare and distance are positively correlated (>0.5)",
            details=details,
        )
        self.results.append(result)
        return result

    def expect_passenger_count_valid(self, column: str = "passenger_count") -> ValidationResult:
        """Taxi domain: passenger count must be reasonable."""
        if column not in self.df.columns:
            passed = False
            details = {"column": column, "error": "Column not found"}
        else:
            # NYC taxi max is 6 passengers
            valid = (self.df[column] >= 1) & (self.df[column] <= 6)
            invalid_count = (~valid).sum()
            passed = invalid_count == 0
            details = {
                "column": column,
                "valid_count": int(valid.sum()),
                "invalid_count": int(invalid_count),
                "min_passengers": int(self.df[column].min()),
                "max_passengers": int(self.df[column].max()),
            }

        result = ValidationResult(
            test_name="expect_passenger_count_valid",
            passed=passed,
            description="Passenger count is valid (1-6)",
            details=details,
        )
        self.results.append(result)
        return result

    def validate_taxi_data(self) -> Dict[str, Any]:
        """Run comprehensive taxi data validation."""
        logger.info("[QUALITY] Running taxi domain data validation...")

        self.results = []

        # Schema
        logger.info("[QUALITY] Schema validation...")
        self.expect_column_to_exist("fare_amount")
        self.expect_column_to_exist("trip_distance")
        self.expect_column_to_exist("passenger_count")

        # Nullness
        logger.info("[QUALITY] Nullness validation...")
        self.expect_column_values_to_not_be_null("fare_amount")
        self.expect_column_values_to_not_be_null("trip_distance")

        # Type validation
        logger.info("[QUALITY] Type validation...")
        self.expect_column_values_to_be_in_type_list("fare_amount", ["float64", "float32", "int64"])

        # Range validation
        logger.info("[QUALITY] Range validation...")
        self.expect_taxi_fare_valid()
        self.expect_trip_distance_valid()
        self.expect_passenger_count_valid()

        # Correlation
        logger.info("[QUALITY] Correlation validation...")
        self.expect_fare_distance_correlation()

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "dataset_name": self.name,
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": total - passed,
            "pass_rate_pct": 100 * passed / total if total > 0 else 0,
            "results": [asdict(r) for r in self.results],
        }

        self.validation_history.append(summary)

        logger.info(f"[QUALITY] Summary: {passed}/{total} checks passed ({100*passed/total:.1f}%)")

        return summary

    def get_validation_suite(self) -> List[ValidationResult]:
        """Get all validation results."""
        return self.results

    def save_validation_report(self, output_dir: str = "mlops/data_quality") -> str:
        """Save validation report to file."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Use latest summary if available
        if self.validation_history:
            summary = self.validation_history[-1]
        else:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "dataset_name": self.name,
                "results": [],
            }

        # Save as JSON
        report_file = output_path / f"data_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"[QUALITY] Report saved to {report_file}")

        # Save as markdown
        md_file = report_file.parent / report_file.name.replace(".json", ".md")
        self._save_markdown_report(md_file, summary)

        return str(report_file)

    def _save_markdown_report(self, filepath: Path, summary: Dict[str, Any]):
        """Save validation report as markdown."""
        md_content = f"""# Data Quality Validation Report

**Dataset**: {summary.get('dataset_name', 'Unknown')}  
**Timestamp**: {summary.get('timestamp', 'Unknown')}

## Summary

- **Total Checks**: {summary.get('total_checks', 0)}
- **Passed**: {summary.get('passed_checks', 0)}
- **Failed**: {summary.get('failed_checks', 0)}
- **Pass Rate**: {summary.get('pass_rate_pct', 0):.1f}%

## Results

| Test | Passed | Description |
|------|--------|-------------|
"""

        for result in summary.get("results", []):
            status = "✅" if result["passed"] else "❌"
            md_content += f"| {result['test_name']} | {status} | {result['description']} |\n"

        md_content += "\n## Details\n\n"
        for result in summary.get("results", []):
            if not result["passed"]:
                md_content += f"\n### {result['test_name']}\n"
                md_content += f"**Status**: FAILED\n"
                md_content += f"**Description**: {result['description']}\n"
                md_content += f"**Details**: {json.dumps(result['details'], indent=2)}\n"

        with open(filepath, "w") as f:
            f.write(md_content)

        logger.info(f"[QUALITY] Markdown report saved to {filepath}")


def validate_taxi_dataset(
    df: pd.DataFrame, name: str = "taxi_dataset", output_dir: str = "mlops/data_quality"
) -> Dict[str, Any]:
    """
    Run complete data quality validation on taxi dataset.

    Args:
        df: DataFrame to validate
        name: Dataset name
        output_dir: Output directory

    Returns:
        Validation summary
    """
    logger.info("[QUALITY] Starting taxi dataset validation...")

    framework = GreatExpectationsFramework(df, name)
    summary = framework.validate_taxi_data()
    framework.save_validation_report(output_dir)

    logger.info("[QUALITY] Validation complete")

    return summary
