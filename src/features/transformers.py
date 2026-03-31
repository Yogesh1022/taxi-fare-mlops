"""Feature transformers."""

from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer


def get_preprocessor() -> ColumnTransformer:
    """Get feature preprocessor pipeline."""
    # TODO: Implement feature transformations
    return ColumnTransformer([])
