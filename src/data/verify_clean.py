"""Verify that cleaned data passes validation."""

import pandas as pd
from pathlib import Path
from src.data.validate import DataValidator
from src.utils.logger import logger


def verify_clean_data():
    """Verify cleaned data against schema."""
    clean_dir = Path("data/clean")
    
    # Validate training data
    logger.info("\n" + "="*60)
    logger.info("VERIFYING CLEANED TRAINING DATA")
    logger.info("="*60)
    train_clean = pd.read_csv(clean_dir / "train_clean.csv")
    validator = DataValidator()
    report_train = validator.validate(train_clean)
    
    if report_train['is_valid']:
        logger.info("✅ TRAINING DATA PASSED VALIDATION!")
    else:
        logger.error(f"❌ TRAINING DATA FAILED: {report_train['errors']}")
    
    # Validate test data
    logger.info("\n" + "="*60)
    logger.info("VERIFYING CLEANED TEST DATA")
    logger.info("="*60)
    test_clean = pd.read_csv(clean_dir / "test_clean.csv")
    report_test = validator.validate(test_clean)
    
    if report_test['is_valid']:
        logger.info("✅ TEST DATA PASSED VALIDATION!")
    else:
        logger.error(f"❌ TEST DATA FAILED: {report_test['errors']}")
    
    logger.info("\n" + "="*60)
    logger.info("VERIFICATION COMPLETE")
    logger.info("="*60)
    
    return report_train['is_valid'] and report_test['is_valid']


if __name__ == "__main__":
    verify_clean_data()
