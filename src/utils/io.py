"""I/O utilities for loading and saving models/data."""

import joblib
from pathlib import Path
from typing import Any

def save_model(obj: Any, path: Path) -> None:
    """Save model/preprocessor using joblib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)

def load_model(path: Path) -> Any:
    """Load model/preprocessor using joblib."""
    return joblib.load(path)
