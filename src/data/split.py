"""Data splitting utilities."""

import pandas as pd
from sklearn.model_selection import train_test_split


def split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Split data into train and test sets."""
    return train_test_split(df, test_size=test_size, random_state=random_state)
