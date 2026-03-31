"""Data quality tests."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from src.data.quality import DataQualityReport


@pytest.fixture
def sample_data():
    """Create sample data."""
    return pd.DataFrame(
        {
            "col_numeric": [1.0, 2.0, 3.0],
            "col_string": ["a", "b", "c"],
        }
    )


@pytest.fixture
def sample_validation_result():
    """Create sample validation result."""
    return {"is_valid": True, "errors": [], "warnings": ["Test warning"], "stats": {}}


def test_report_creation(sample_data, sample_validation_result):
    """Test that quality report can be created."""
    with TemporaryDirectory() as tmpdir:
        report_gen = DataQualityReport(Path(tmpdir))
        report_path = report_gen.create_report(sample_validation_result, sample_data)

        assert Path(report_path).exists()

        # Verify JSON content
        with open(report_path) as f:
            report = json.load(f)

        assert report["status"] == "PASS"
        assert "timestamp" in report
        assert "data_summary" in report


def test_data_summarization(sample_data):
    """Test data summarization."""
    report_gen = DataQualityReport()
    summary = report_gen._summarize_data(sample_data)

    assert summary["shape"]["rows"] == 3
    assert summary["shape"]["columns"] == 2
    assert summary["duplicates"] == 0


@pytest.mark.unit
def test_placeholder():
    """Placeholder test."""
    assert True
