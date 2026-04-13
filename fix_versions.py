#!/usr/bin/env python3
"""Fix malformed GitHub Actions versions."""
import re
from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")

# Fix patterns
FIXES = [
    ("v4.1.0.1.0", "v4.1.0"),  # Duplicate version suffix
]

def fix_workflow_file(filepath):
    """Fix malformed versions in a workflow file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in FIXES:
            if old in content:
                content = content.replace(old, new)
                count = original_content.count(old)
                print(f"✓ {filepath.name:30} - Fixed {count} instances of {old}")
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    except Exception as e:
        print(f"✗ {filepath.name:30} - Error: {str(e)}")

def main():
    """Fix all workflow files."""
    print("Fixing malformed GitHub Actions versions...")
    print("=" * 70)
    
    for workflow_file in sorted(WORKFLOWS_DIR.glob("*.yml")):
        fix_workflow_file(workflow_file)
    
    print("=" * 70)
    print("✓ All workflow files fixed!")

if __name__ == "__main__":
    main()
