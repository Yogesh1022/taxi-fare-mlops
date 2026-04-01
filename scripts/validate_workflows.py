#!/usr/bin/env python
"""
GitHub Actions Workflow Validator
Validates all workflows in .github/workflows/
"""

import os
import sys
import yaml
from pathlib import Path


def validate_workflow(workflow_path):
    """Validate a single workflow file"""
    print(f"\n{'='*60}")
    print(f"Validating: {workflow_path.name}")
    print('='*60)
    
    try:
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        # Check required fields
        if 'name' not in workflow:
            print("❌ Missing 'name' field")
            return False
        
        print(f"✅ Workflow name: {workflow['name']}")
        
        if 'on' not in workflow:
            print("❌ Missing 'on' triggers")
            return False
        
        triggers = workflow['on']
        if isinstance(triggers, dict):
            print(f"✅ Triggers: {', '.join(triggers.keys())}")
        else:
            print(f"✅ Triggers: {triggers}")
        
        if 'jobs' not in workflow:
            print("❌ Missing 'jobs' section")
            return False
        
        jobs = workflow['jobs']
        print(f"✅ Jobs: {len(jobs)} found")
        for job_name, job_config in jobs.items():
            if 'runs-on' in job_config:
                print(f"   - {job_name}: {job_config['runs-on']}")
            else:
                print(f"   - {job_name}: ⚠️ No 'runs-on' specified")
        
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main validation function"""
    workflows_dir = Path('.github/workflows')
    
    if not workflows_dir.exists():
        print("❌ .github/workflows directory not found")
        return False
    
    print(f"🔍 Found {len(list(workflows_dir.glob('*.yml')))} workflow files")
    
    results = {}
    for workflow_path in sorted(workflows_dir.glob('*.yml')):
        results[workflow_path.name] = validate_workflow(workflow_path)
    
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print('='*60)
    
    for workflow_name, is_valid in results.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {workflow_name}")
    
    all_valid = all(results.values())
    print('='*60)
    
    if all_valid:
        print("✅ All workflows validated successfully!")
        return True
    else:
        print("❌ Some workflows have issues")
        return False


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
