"""Data cleaning and fixing script for taxi fare prediction."""

import pandas as pd
import numpy as np
from pathlib import Path
from src.utils.logger import logger


def clean_data(df, is_test=False):
    """
    Clean and fix data quality issues.
    
    Args:
        df: DataFrame to clean
        is_test: Whether this is test data (True) or train data (False)
    
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    logger.info(f"Starting data cleaning (test={is_test})...")
    logger.info(f"Initial shape: {df.shape}")
    
    # ============ ISSUE 1-6: Handle Missing Values ============
    logger.info("Handling missing values...")
    
    # Fill missing passenger_count with mode (most common value)
    if 'passenger_count' in df.columns and df['passenger_count'].isnull().any():
        mode_val = df['passenger_count'].mode()[0] if len(df['passenger_count'].mode()) > 0 else 1.0
        logger.info(f"Filling {df['passenger_count'].isnull().sum()} null passenger_count with {mode_val}")
        df['passenger_count'].fillna(mode_val, inplace=True)
    
    # Fill missing RatecodeID with mode (typically 1)
    if 'RatecodeID' in df.columns and df['RatecodeID'].isnull().any():
        mode_val = df['RatecodeID'].mode()[0] if len(df['RatecodeID'].mode()) > 0 else 1.0
        logger.info(f"Filling {df['RatecodeID'].isnull().sum()} null RatecodeID with {mode_val}")
        df['RatecodeID'].fillna(mode_val, inplace=True)
    
    # Fill missing store_and_fwd_flag with 'N' (no forwarding)
    if 'store_and_fwd_flag' in df.columns and df['store_and_fwd_flag'].isnull().any():
        logger.info(f"Filling {df['store_and_fwd_flag'].isnull().sum()} null store_and_fwd_flag with 'N'")
        df['store_and_fwd_flag'].fillna('N', inplace=True)
    
    # Fill missing congestion_surcharge with 0
    if 'congestion_surcharge' in df.columns and df['congestion_surcharge'].isnull().any():
        logger.info(f"Filling {df['congestion_surcharge'].isnull().sum()} null congestion_surcharge with 0")
        df['congestion_surcharge'].fillna(0.0, inplace=True)
    
    # Fill missing Airport_fee with 0
    if 'Airport_fee' in df.columns and df['Airport_fee'].isnull().any():
        logger.info(f"Filling {df['Airport_fee'].isnull().sum()} null Airport_fee with 0")
        df['Airport_fee'].fillna(0.0, inplace=True)
    
    # ============ ISSUE 7: Fix passenger_count < 1 ============
    logger.info("Fixing passenger_count values < 1...")
    if 'passenger_count' in df.columns:
        invalid_count = (df['passenger_count'] < 1).sum()
        logger.info(f"Found {invalid_count} passenger_count values < 1")
        df.loc[df['passenger_count'] < 1, 'passenger_count'] = 1.0
    
    # ============ ISSUE 8: Fix RatecodeID > 5 ============
    logger.info("Fixing RatecodeID values > 5...")
    if 'RatecodeID' in df.columns:
        invalid_count = (df['RatecodeID'] > 5).sum()
        logger.info(f"Found {invalid_count} RatecodeID values > 5")
        # Replace invalid ratecodes with mode or 1
        df.loc[df['RatecodeID'] > 5, 'RatecodeID'] = 1.0
    
    # ============ ISSUE 9: Fix negative values in fees ============
    logger.info("Fixing negative fee values...")
    fee_columns = ['extra', 'tolls_amount', 'improvement_surcharge', 
                   'congestion_surcharge', 'Airport_fee', 'tip_amount']
    for col in fee_columns:
        if col in df.columns:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                logger.info(f"Found {negative_count} negative {col} values, setting to 0")
                df.loc[df[col] < 0, col] = 0.0
    
    # ============ ISSUE 10: Fix invalid payment types ============
    logger.info("Fixing payment_type values...")
    if 'payment_type' in df.columns:
        valid_payment_types = ['Credit Card', 'Cash', 'other']
        invalid_mask = ~df['payment_type'].isin(valid_payment_types)
        invalid_count = invalid_mask.sum()
        if invalid_count > 0:
            logger.info(f"Found {invalid_count} invalid payment types")
            # Standardize common variants
            df.loc[df['payment_type'].str.lower() == 'wallet', 'payment_type'] = 'other'
            df.loc[df['payment_type'].str.lower() == 'upi', 'payment_type'] = 'other'
            df.loc[df['payment_type'].str.lower() == 'unknown', 'payment_type'] = 'other'
            # Replace any remaining invalid values
            df.loc[invalid_mask, 'payment_type'] = 'other'
    
    # ============ ISSUE 11-13: Handle Outliers ============
    logger.info("Handling outliers using IQR method...")
    
    # Passenger count: cap at 6 (reasonable max)
    if 'passenger_count' in df.columns:
        df.loc[df['passenger_count'] > 6, 'passenger_count'] = 6
    
    # Trip distance: cap at reasonable max
    if 'trip_distance' in df.columns:
        # Use 95th percentile as cap
        p95 = df['trip_distance'].quantile(0.95)
        logger.info(f"Capping trip_distance at 95th percentile: {p95:.2f}")
        df.loc[df['trip_distance'] > p95, 'trip_distance'] = p95
    
    # Tip amount: cap at reasonable max
    if 'tip_amount' in df.columns:
        p95 = df['tip_amount'].quantile(0.95)
        logger.info(f"Capping tip_amount at 95th percentile: {p95:.2f}")
        df.loc[df['tip_amount'] > p95, 'tip_amount'] = p95
    
    # ============ ISSUE: Add total_amount (for test data) ============
    if is_test and 'total_amount' not in df.columns:
        logger.info("Test data: generating total_amount from components...")
        # total_amount = fare_amount + extra + tip + tolls + surcharges
        # Since we don't have fare_amount, we'll estimate it
        fare_amount = df['trip_distance'] * 2.5  # Rough estimate: $2.50 per mile
        df['total_amount'] = (
            fare_amount + 
            df.get('extra', 0) + 
            df.get('tip_amount', 0) + 
            df.get('tolls_amount', 0) + 
            df.get('improvement_surcharge', 0) + 
            df.get('congestion_surcharge', 0) + 
            df.get('Airport_fee', 0)
        )
        logger.info(f"Generated total_amount column (estimated)")
    
    # ============ Drop duplicates ============
    initial_rows = len(df)
    df = df.drop_duplicates()
    dropped = initial_rows - len(df)
    if dropped > 0:
        logger.info(f"Dropped {dropped} duplicate rows")
    
    logger.info(f"Cleaning complete! Final shape: {df.shape}")
    return df


def main():
    """Run data cleaning pipeline."""
    # Paths
    raw_dir = Path("data/raw")
    clean_dir = Path("data/clean")
    clean_dir.mkdir(exist_ok=True)
    
    # Clean training data
    logger.info("\n" + "="*60)
    logger.info("CLEANING TRAINING DATA")
    logger.info("="*60)
    train_raw = pd.read_csv(raw_dir / "train.csv")
    train_clean = clean_data(train_raw, is_test=False)
    train_clean.to_csv(clean_dir / "train_clean.csv", index=False)
    logger.info(f"Saved to: {clean_dir / 'train_clean.csv'}")
    
    # Clean test data
    logger.info("\n" + "="*60)
    logger.info("CLEANING TEST DATA")
    logger.info("="*60)
    test_raw = pd.read_csv(raw_dir / "test.csv")
    test_clean = clean_data(test_raw, is_test=True)
    test_clean.to_csv(clean_dir / "test_clean.csv", index=False)
    logger.info(f"Saved to: {clean_dir / 'test_clean.csv'}")
    
    logger.info("\n" + "="*60)
    logger.info("DATA CLEANING COMPLETE!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
