"""
Example script demonstrating MLflow + Optuna nested runs integration.

This script shows how to:
1. Initialize HyperparameterTuner with MLflow enabled
2. Run hyperparameter tuning with automatic MLflow logging
3. View results in MLflow UI
4. Export results for analysis
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# MLflow configuration
os.environ['MLFLOW_TRACKING_URI'] = 'file:./mlruns'
os.environ['MLFLOW_EXPERIMENT_NAME'] = 'taxi-fare-prediction'

import mlflow

# Project imports
from src.models.tune import HyperparameterTuner, tune_top_3_models
from src.utils.logger import logger
from src.utils.config import MODEL_DIR


def example_1_basic_tuning():
    """Example 1: Basic tuning with MLflow enabled."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Tuning with MLflow Enabled")
    print("="*80)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)]
    )
    y = pd.Series(
        X.iloc[:, 0] * 2 + X.iloc[:, 1] * 3 + np.random.randn(n_samples) * 0.5,
        name='target'
    )
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
    print(f"\nData shapes:")
    print(f"  Train: {X_train.shape}")
    print(f"  Val:   {X_val.shape}")
    print(f"  Test:  {X_test.shape}")
    
    # Create tuner with MLflow enabled
    print("\nInitializing HyperparameterTuner with MLflow enabled...")
    tuner = HyperparameterTuner(
        X_train, X_val, y_train, y_val, X_test, y_test,
        n_trials=5,  # Small number for demonstration
        use_mlflow=True  # Enable MLflow
    )
    
    # Run tuning
    print("Starting hyperparameter tuning...")
    print("This will create MLflow runs and nested trials...")
    results = tuner.tune_all()
    
    # Save results
    tuner.save_results()
    
    print("\nTuning complete!")
    print("\nResults summary:")
    for model_name, result in results.items():
        if result['status'] == 'success':
            r2 = result['test_metrics']['r2_score']
            rmse = result['test_metrics']['rmse']
            print(f"  {model_name:12} - R²: {r2:.4f}, RMSE: {rmse:.4f}")
    
    return tuner, results


def example_2_mlflow_navigation():
    """Example 2: Show MLflow structure and how to navigate."""
    print("\n" + "="*80)
    print("EXAMPLE 2: MLflow Structure Navigation")
    print("="*80)
    
    # Get active MLflow experiment
    experiment = mlflow.get_experiment_by_name('taxi-fare-prediction')
    if experiment:
        print(f"\nExperiment: {experiment.name}")
        print(f"Experiment ID: {experiment.experiment_id}")
        print(f"Location: {experiment.artifact_location}")
        
        # Search for runs
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        print(f"\nTotal runs found: {len(runs)}")
        
        print("\nRun hierarchy:")
        for i, run in runs.iterrows():
            run_name = run['tags.mlflow.runName']
            model = run['tags.model']
            status = run['status']
            print(f"  - {run_name} ({model}) [Status: {status}]")
    
    print("\nTo view runs in MLflow UI:")
    print("  1. Open terminal")
    print("  2. Run: mlflow ui")
    print("  3. Open browser: http://localhost:5000")
    print("  4. Navigate to 'taxi-fare-prediction' experiment")


def example_3_compare_with_without_mlflow():
    """Example 3: Show performance difference."""
    print("\n" + "="*80)
    print("EXAMPLE 3: MLflow Overhead Analysis")
    print("="*80)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 500
    n_features = 10
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)]
    )
    y = pd.Series(np.random.randn(n_samples) * 10, name='target')
    
    from sklearn.model_selection import train_test_split
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
    import time
    
    # Test 1: With MLflow
    print("\nTest 1: WITH MLflow enabled")
    start = time.time()
    tuner_with_mlflow = HyperparameterTuner(
        X_train, X_val, y_train, y_val, X_test, y_test,
        n_trials=3,
        use_mlflow=True
    )
    tuner_with_mlflow.tune_svm()
    time_with_mlflow = time.time() - start
    print(f"  Time: {time_with_mlflow:.2f} seconds")
    
    # Test 2: Without MLflow
    print("\nTest 2: WITHOUT MLflow (use_mlflow=False)")
    start = time.time()
    tuner_without_mlflow = HyperparameterTuner(
        X_train, X_val, y_train, y_val, X_test, y_test,
        n_trials=3,
        use_mlflow=False
    )
    tuner_without_mlflow.tune_svm()
    time_without_mlflow = time.time() - start
    print(f"  Time: {time_without_mlflow:.2f} seconds")
    
    overhead = (time_with_mlflow - time_without_mlflow) / time_without_mlflow * 100
    print(f"\nMLflow overhead: {overhead:.1f}%")
    print(f"Recommendation: MLflow overhead is minimal (<5% typical)")
    print(f"  → Enable MLflow in production for tracking")
    print(f"  → Disable MLflow in tests for speed")


def example_4_export_results():
    """Example 4: Export MLflow results for analysis."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Export MLflow Results")
    print("="*80)
    
    experiment = mlflow.get_experiment_by_name('taxi-fare-prediction')
    if experiment:
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        # Export to DataFrame
        export_data = {
            'run_name': [],
            'run_id': [],
            'model': [],
            'status': [],
            'best_r2': [],
            'completed_trials': []
        }
        
        for i, run in runs.iterrows():
            export_data['run_name'].append(run['tags.mlflow.runName'])
            export_data['run_id'].append(run['run_id'])
            export_data['model'].append(run['tags.model'])
            export_data['status'].append(run['status'])
            export_data['best_r2'].append(run['metrics.best_val_r2'])
            export_data['completed_trials'].append(int(run['metrics.n_completed_trials']))
        
        df = pd.DataFrame(export_data)
        
        print("\nExported MLflow runs:")
        print(df.to_string(index=False))
        
        # Save to CSV
        export_path = Path('mlflow_runs_export.csv')
        df.to_csv(export_path, index=False)
        print(f"\nExported to: {export_path}")


def main():
    """Run all examples."""
    print("\n")
    print("#" * 80)
    print("# MLflow + Optuna Nested Runs Integration Examples")
    print("#" * 80)
    
    try:
        # Example 1: Basic tuning
        tuner, results = example_1_basic_tuning()
        
        # Example 2: MLflow navigation
        example_2_mlflow_navigation()
        
        # Example 3: Performance comparison
        example_3_compare_with_without_mlflow()
        
        # Example 4: Export results
        example_4_export_results()
        
        print("\n" + "#" * 80)
        print("# All examples completed successfully!")
        print("# ")
        print("# Next steps:")
        print("#   1. Start MLflow UI: mlflow ui")
        print("#   2. Open http://localhost:5000")
        print("#   3. Navigate to 'taxi-fare-prediction' experiment")
        print("#   4. Explore runs and trials")
        print("#" * 80)
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
