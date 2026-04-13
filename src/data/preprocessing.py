"""Dataset preprocessing entrypoint for DVC pipelines."""

from pathlib import Path

import pandas as pd

from data.clean import clean_data
from utils.logger import logger


def preprocess_datasets(
    train_path: Path = Path("data/raw/train.csv"),
    test_path: Path = Path("data/raw/test.csv"),
    out_train: Path = Path("data/processed/preprocessed_train.csv"),
    out_test: Path = Path("data/processed/preprocessed_test.csv"),
) -> None:
    """Load raw datasets, clean them, and write processed artifacts."""
    logger.info("[PREPROCESS] Loading raw datasets...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    clean_train = clean_data(train_df, is_test=False)
    clean_test = clean_data(test_df, is_test=True)

    out_train.parent.mkdir(parents=True, exist_ok=True)
    out_test.parent.mkdir(parents=True, exist_ok=True)
    clean_train.to_csv(out_train, index=False)
    clean_test.to_csv(out_test, index=False)
    logger.info("[PREPROCESS] Saved processed train/test datasets")


def main() -> None:
    preprocess_datasets()


if __name__ == "__main__":
    main()
