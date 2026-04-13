#!/usr/bin/env python3
"""Day 7: Model Registry Setup - Register and manage production models."""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from deployment.model_registry import ModelRegistry, setup_production_models
from utils.logger import logger
from utils.config import MODEL_DIR


def main():
    """Main Day 7 execution: Setup production models in MLflow Model Registry."""
    
    print("=" * 80)
    print("DAY 7: MODEL REGISTRY & PRODUCTION DEPLOYMENT")
    print("=" * 80)
    
    # Step 1: Setup production models from tuning results
    print("\n[STEP 1] Setting up production models...")
    tuning_results_path = MODEL_DIR / "tuning_comparison.json"
    
    if not tuning_results_path.exists():
        print(f"❌ Tuning results not found at {tuning_results_path}")
        print("Please run Day 5 first to generate tuning results")
        return
    
    try:
        setup_results = setup_production_models(
            tuning_results_path=tuning_results_path,
            use_mlflow=True
        )
        
        if setup_results:
            print(f"✅ Registered {len(setup_results)} models")
            for model, result in setup_results.items():
                if 'version' in result:
                    print(f"   - {model}: Version {result['version']}")
    except Exception as e:
        print(f"⚠️  Setup error: {str(e)}")
        print("\n💡 Info: This is normal if no tuning run exists yet.")
        print("   You can still explore the Model Registry functionality manually.")
    
    # Step 2: Get registry and list models
    print("\n[STEP 2] Checking registered models...")
    registry = ModelRegistry(use_mlflow=True)
    
    try:
        models = registry.list_registered_models()
        if models:
            print(f"✅ Found {len(models)} registered models:")
            for model in models:
                print(f"   - {model}")
        else:
            print("⚠️  No registered models yet (this is expected for first run)")
    except Exception as e:
        print(f"⚠️  Could not list models: {str(e)}")
    
    # Step 3: Save registry summary
    print("\n[STEP 3] Saving model registry summary...")
    
    try:
        summary_path = registry.save_registry_summary()
        print(f"✅ Registry summary saved to {summary_path}")
    except Exception as e:
        print(f"⚠️  Could not save summary: {str(e)}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("DAY 7 COMPLETION SUMMARY")
    print("=" * 80)
    print("\n✅ Model Registry Infrastructure:")
    print("   - ModelRegistry class implemented")
    print("   - Registration, versioning, and aliasing support")
    print("   - Stage transitions (None → Staging → Production → Archived)")
    print("   - Metadata management with performance metrics")
    
    print("\n📊 When tuning runs are available:")
    print("   - Models auto-registered from tuning results")
    print("   - XGBoost (best) → Production")
    print("   - LightGBM (backup) → Staging")
    print("   - SVM → None (for reference)")
    
    print("\n🚀 Next Steps:")
    print("   1. Run Day 5 tuning first if not done")
    print("   2. Check MLflow UI at http://127.0.0.1:5000")
    print("   3. Navigate to Models section to see registry")
    print("   4. Day 8: Batch predictions and monitoring")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

