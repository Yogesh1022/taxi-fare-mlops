#!/usr/bin/env python3
"""Validate GitHub Actions workflow YAML files."""
import yaml
import os

workflows = [
    '.github/workflows/ci.yml',
    '.github/workflows/deployment-ready.yml',
    '.github/workflows/model-validation.yml',
    '.github/workflows/docker.yml',
    '.github/workflows/release.yml'
]

print("Validating GitHub Actions Workflows...")
print("=" * 60)

for workflow in workflows:
    try:
        with open(workflow, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print(f"✓ {os.path.basename(workflow):30} - VALID")
    except FileNotFoundError:
        print(f"✗ {os.path.basename(workflow):30} - NOT FOUND")
    except yaml.YAMLError as e:
        print(f"✗ {os.path.basename(workflow):30} - ERROR: {str(e)[:40]}")
    except Exception as e:
        print(f"✗ {os.path.basename(workflow):30} - ERROR: {str(e)[:40]}")

print("=" * 60)
print("Workflow validation complete!")
