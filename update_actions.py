#!/usr/bin/env python3
"""Update deprecated GitHub Actions versions in all workflow files."""
import re
import os
from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")

# Define replacements
REPLACEMENTS = [
    ("actions/checkout@v4", "actions/checkout@v4.1.0"),
    ("actions/setup-python@v4", "actions/setup-python@v5"),
    ("actions/upload-artifact@v3", "actions/upload-artifact@v4"),
    ("codecov/codecov-action@v3", "codecov/codecov-action@v4"),
    ("actions/github-script@v7", "actions/github-script@v7.0.1"),
    ("docker/setup-buildx-action@v2", "docker/setup-buildx-action@v3"),
    ("docker/build-push-action@v4", "docker/build-push-action@v5"),
]

def update_workflow_file(filepath):
    """Update deprecated versions in a workflow file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in REPLACEMENTS:
            content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Count replacements
            count = sum(original_content.count(old) for old, _ in REPLACEMENTS)
            print(f"✓ {filepath.name:30} - Updated {count} deprecated versions")
            return count
        else:
            print(f"• {filepath.name:30} - No changes needed")
            return 0
    except Exception as e:
        print(f"✗ {filepath.name:30} - Error: {str(e)}")
        return -1

def main():
    """Update all workflow files."""
    print("Updating deprecated GitHub Actions versions...")
    print("=" * 70)
    
    total_updates = 0
    for workflow_file in sorted(WORKFLOWS_DIR.glob("*.yml")):
        updates = update_workflow_file(workflow_file)
        if updates > 0:
            total_updates += updates
    
    print("=" * 70)
    if total_updates > 0:
        print(f"✓ Total updates: {total_updates} deprecated versions replaced")
    else:
        print("✓ All workflow files up to date!")

if __name__ == "__main__":
    main()
