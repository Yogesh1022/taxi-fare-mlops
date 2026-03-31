"""Data loading and ingestion."""

import pandas as pd
from pathlib import Path


def load_raw_data(path: Path) -> pd.DataFrame:
    """Load raw CSV data."""
    return pd.read_csv(path)
