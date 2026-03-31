"""Data ingestion pipeline stage."""

from pathlib import Path

import pandas as pd

from src.utils.config import CLEAN_DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.utils.logger import logger


def load_raw_data(path: Path) -> pd.DataFrame:
    """Load raw CSV data."""
    return pd.read_csv(path)


def ingest_data(input_file: str) -> Path:
    """
    Ingest raw data from input file.

    This is the second DVC pipeline stage (after clean).
    Reads from clean data folder if available, otherwise raw.

    Args:
        input_file: Path to raw CSV file

    Returns:
        Path to ingested data file
    """
    logger.info(f"Ingesting data from {input_file}")

    # Try clean data first, fall back to raw
    clean_path = CLEAN_DATA_DIR / f"*{input_file.replace('.csv', '')}_clean.csv"
    raw_path = RAW_DATA_DIR / input_file
    
    # Use clean data if it exists
    input_paths = list(CLEAN_DATA_DIR.glob(f"*{input_file.replace('.csv', '')}_clean.csv"))
    if input_paths:
        input_path = input_paths[0]
        logger.info(f"Using cleaned data: {input_path}")
    else:
        input_path = raw_path
        logger.info(f"Clean data not found, using raw data: {input_path}")
    
    if not input_path.exists():
        raise FileNotFoundError(f"Data file not found: {input_path}")

    # Load data
    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    # Basic cleaning (remove duplicates)
    n_dupes = df.duplicated().sum()
    if n_dupes > 0:
        logger.warning(f"Removing {n_dupes} duplicate rows")
        df = df.drop_duplicates()

    # Save to processed directory
    output_filename = f"ingested_{input_file}"
    output_path = PROCESSED_DATA_DIR / output_filename
    df.to_csv(output_path, index=False)
    logger.info(f"Ingested data saved to {output_path}")

    return output_path


def main():
    """Run ingestion stage."""
    ingest_data("train.csv")
    ingest_data("test.csv")


if __name__ == "__main__":
    main()
