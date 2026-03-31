#!/usr/bin/env python
"""Quick test of validation."""

import sys

sys.path.insert(0, '.')

import pandas as pd

from src.data.validate import DataValidator

# Load test data
df = pd.read_csv('data/raw/train.csv')
print(f'✓ Loaded {len(df)} rows from training data')
print(f'Columns: {len(df.columns)}')

# Validate
validator = DataValidator()
is_valid, report = validator.validate(df)

print(f'\n✓ Validation Result: {"PASS" if is_valid else "FAIL"}')
print(f'Errors: {len(report["errors"])}')
print(f'Warnings: {len(report["warnings"])}')

if report['errors']:
    print('\n❌ Errors:')
    for error in report['errors'][:5]:
        print(f'  - {error}')

if report['warnings']:
    print('\n⚠️ Warnings:')
    for warning in report['warnings'][:5]:
        print(f'  - {warning}')

# Check data summary
if 'stats' in report:
    stats = report['stats']
    print('\n📊 Data Stats:')
    print(f'  Rows: {stats.get("n_rows")}')
    print(f'  Columns: {stats.get("n_columns")}')

print('\n✅ Validation test complete!')
