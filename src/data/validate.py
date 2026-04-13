"""Data validation utilities.

Validates data against schema and performs quality checks.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from data.schema import CRITICAL_FIELDS, OUTLIER_IQR_MULTIPLIER, DataSchema, DataType
from utils.logger import logger


class DataValidator:
    """Validates data against schema and quality rules."""

    def __init__(self, schema: DataSchema = None):
        """Initialize validator with schema."""
        self.schema = schema or DataSchema()
        self.validation_errors = []
        self.validation_warnings = []

    def validate(self, df: pd.DataFrame) -> tuple[bool, dict]:
        """
        Validate dataset against schema.

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (is_valid, validation_report)
        """
        self.validation_errors = []
        self.validation_warnings = []

        # Run all validations
        self._validate_columns(df)
        self._validate_dtypes(df)
        self._validate_nulls(df)
        self._validate_value_ranges(df)
        self._validate_categorical_values(df)
        self._detect_outliers(df)

        is_valid = len(self.validation_errors) == 0

        report = {
            "is_valid": is_valid,
            "errors": self.validation_errors,
            "warnings": self.validation_warnings,
            "stats": self._calculate_stats(df),
        }

        return is_valid, report

    def _validate_columns(self, df: pd.DataFrame) -> None:
        """Check if all required columns exist."""
        required = set(self.schema.get_required_columns())
        present = set(df.columns)

        missing = required - present
        if missing:
            self.validation_errors.append(f"Missing required columns: {missing}")

        extra = present - required
        if extra:
            self.validation_warnings.append(f"Extra columns found (will be ignored): {extra}")

    def _validate_dtypes(self, df: pd.DataFrame) -> None:
        """Validate column data types."""
        schema = self.schema.get_full_schema()

        for col_name, col_spec in schema.items():
            if col_name not in df.columns:
                continue

            dtype_valid = False
            col = df[col_name]

            if col_spec.dtype == DataType.FLOAT:
                try:
                    pd.to_numeric(col, errors="coerce")
                    dtype_valid = True
                except (TypeError, ValueError):
                    pass
            elif col_spec.dtype == DataType.INT:
                try:
                    col.astype(int)
                    dtype_valid = True
                except (TypeError, ValueError):
                    pass
            elif col_spec.dtype == DataType.DATETIME:
                try:
                    pd.to_datetime(col, errors="coerce")
                    dtype_valid = True
                except (TypeError, ValueError):
                    pass
            elif col_spec.dtype == DataType.STRING:
                dtype_valid = col.dtype == object

            if not dtype_valid:
                self.validation_warnings.append(
                    f"Column '{col_name}' has unexpected dtype (found: {col.dtype}, expected: {col_spec.dtype.value})"
                )

    def _validate_nulls(self, df: pd.DataFrame) -> None:
        """Check for unexpected null values."""
        schema = self.schema.get_full_schema()

        for col_name, col_spec in schema.items():
            if col_name not in df.columns:
                continue

            null_count = df[col_name].isnull().sum()
            null_pct = null_count / len(df) * 100

            if not col_spec.nullable and null_count > 0:
                self.validation_errors.append(
                    f"Column '{col_name}' should not have nulls but has {null_count} ({null_pct:.2f}%)"
                )
            elif null_pct > 5:  # Warning if > 5%
                self.validation_warnings.append(
                    f"Column '{col_name}' has high null percentage: {null_pct:.2f}%"
                )

    def _validate_value_ranges(self, df: pd.DataFrame) -> None:
        """Check numerical values are within acceptable ranges."""
        schema = self.schema.get_full_schema()

        for col_name, col_spec in schema.items():
            if col_name not in df.columns or col_spec.dtype not in [DataType.FLOAT, DataType.INT]:
                continue

            col = pd.to_numeric(df[col_name], errors="coerce")

            # Check min value
            if col_spec.min_value is not None:
                below_min = (col < col_spec.min_value).sum()
                if below_min > 0:
                    self.validation_errors.append(
                        f"Column '{col_name}': {below_min} values below minimum {col_spec.min_value}"
                    )

            # Check max value
            if col_spec.max_value is not None:
                above_max = (col > col_spec.max_value).sum()
                if above_max > 0:
                    self.validation_errors.append(
                        f"Column '{col_name}': {above_max} values above maximum {col_spec.max_value}"
                    )

    def _validate_categorical_values(self, df: pd.DataFrame) -> None:
        """Check categorical columns have allowed values."""
        schema = self.schema.get_full_schema()

        for col_name, col_spec in schema.items():
            if col_name not in df.columns or col_spec.dtype != DataType.STRING:
                continue

            if col_spec.allowed_values is None:
                continue

            col = df[col_name].dropna()
            invalid = col[~col.isin(col_spec.allowed_values)]

            if len(invalid) > 0:
                unique_invalid = invalid.unique()
                self.validation_errors.append(
                    f"Column '{col_name}': found invalid values {set(unique_invalid)}. "
                    f"Allowed: {col_spec.allowed_values}"
                )

    def _detect_outliers(self, df: pd.DataFrame) -> None:
        """Detect outliers in numeric columns using IQR method."""
        numeric_cols = self.schema.get_numeric_columns()

        for col_name in numeric_cols:
            if col_name not in df.columns:
                continue

            col = pd.to_numeric(df[col_name], errors="coerce")
            col_clean = col.dropna()

            if len(col_clean) < 4:  # Need at least 4 values for IQR
                continue

            Q1 = col_clean.quantile(0.25)
            Q3 = col_clean.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - OUTLIER_IQR_MULTIPLIER * IQR
            upper_bound = Q3 + OUTLIER_IQR_MULTIPLIER * IQR

            outliers = ((col_clean < lower_bound) | (col_clean > upper_bound)).sum()
            outlier_pct = outliers / len(col_clean) * 100

            # Only warn if there are outliers in critical fields
            if col_name in CRITICAL_FIELDS and outlier_pct > 0:
                self.validation_warnings.append(
                    f"Column '{col_name}': {outliers} outliers detected ({outlier_pct:.2f}%)"
                )

    def _calculate_stats(self, df: pd.DataFrame) -> dict:
        """Calculate data statistics."""
        stats = {
            "n_rows": len(df),
            "n_columns": len(df.columns),
            "memory_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "missing_values": df.isnull().sum().to_dict(),
        }

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats["numeric_stats"] = {}
        for col in numeric_cols:
            stats["numeric_stats"][col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
            }

        return stats


def validate_data_file(filepath: Path) -> tuple[bool, dict]:
    """Load and validate a data file."""
    logger.info(f"Validating data file: {filepath}")

    try:
        df = pd.read_csv(filepath)
        validator = DataValidator()
        is_valid, report = validator.validate(df)

        if is_valid:
            logger.info("✓ Data validation passed")
        else:
            logger.error(f"✗ Data validation failed: {report['errors']}")

        return is_valid, report

    except Exception as e:
        logger.error(f"Error validating data file: {e}")
        return False, {"error": str(e)}
