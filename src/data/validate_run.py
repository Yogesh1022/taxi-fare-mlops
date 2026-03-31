"""Data validation pipeline runner."""

import sys
from pathlib import Path

import pandas as pd

from src.data.quality import DataQualityReport
from src.data.validate import validate_data_file
from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


def run_validation_pipeline():
    """Run data validation pipeline."""
    logger.info("Starting data quality validation...")

    # Create output directory
    output_dir = Path("mlops/data_quality")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_valid = True

    # Validate training data
    logger.info("\n" + "=" * 60)
    logger.info("Validating TRAINING data...")
    logger.info("=" * 60)
    train_path = RAW_DATA_DIR / "train.csv"
    train_valid, train_report = validate_data_file(train_path)

    # Generate report
    train_df = pd.read_csv(train_path)
    report_gen = DataQualityReport(output_dir)
    train_report_path = report_gen.create_report(train_report, train_df)

    if not train_valid:
        all_valid = False
        logger.error("✗ Training data validation FAILED")
    else:
        logger.info("✓ Training data validation PASSED")

    # Validate test data
    logger.info("\n" + "=" * 60)
    logger.info("Validating TEST data...")
    logger.info("=" * 60)
    test_path = RAW_DATA_DIR / "test.csv"
    test_valid, test_report = validate_data_file(test_path)

    # Generate report
    test_df = pd.read_csv(test_path)
    test_report_path = report_gen.create_report(test_report, test_df)

    if not test_valid:
        all_valid = False
        logger.error("✗ Test data validation FAILED")
    else:
        logger.info("✓ Test data validation PASSED")

    # Save validation metrics
    import json

    metrics = {
        "train_valid": train_valid,
        "test_valid": test_valid,
        "all_valid": all_valid,
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "train_errors": len(train_report.get("errors", [])),
        "test_errors": len(test_report.get("errors", [])),
        "train_warnings": len(train_report.get("warnings", [])),
        "test_warnings": len(test_report.get("warnings", [])),
    }

    metrics_path = output_dir / "validation_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info("\n" + "=" * 60)
    logger.info("Data Validation Summary")
    logger.info("=" * 60)
    logger.info(f"Training data: {'✓ PASS' if train_valid else '✗ FAIL'}")
    logger.info(f"Test data: {'✓ PASS' if test_valid else '✗ FAIL'}")
    logger.info(f"Overall: {'✓ PASS' if all_valid else '✗ FAIL'}")
    logger.info(f"Reports saved to: {output_dir}")
    logger.info("=" * 60)

    # Note: For DVC pipeline, we log status but don't exit
    # Metrics are still captured for monitoring
    if not all_valid:
        logger.warning("Data validation issues detected - check metrics")
        # Don't exit(1) here so DVC pipeline continues
        # In production, these metrics would trigger alerts
        return False
    
    return True


if __name__ == "__main__":
    run_validation_pipeline()
