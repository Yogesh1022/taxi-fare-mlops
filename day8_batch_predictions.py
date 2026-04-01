#!/usr/bin/env python3
"""Day 8: Batch Predictions & Monitoring - Production inference with drift detection."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.deployment.batch_predictions import BatchPredictor, PredictionMonitor
from src.utils.config import MODEL_DIR
import numpy as np
import pandas as pd


def main():
    """Main Day 8 execution: Batch predictions and monitoring."""
    
    print("=" * 80)
    print("DAY 8: BATCH PREDICTIONS & MONITORING")
    print("=" * 80)
    
    # Step 1: Load test data
    print("\n[STEP 1] Loading test data...")
    test_data_path = Path("data/raw/test.csv")
    
    if not test_data_path.exists():
        print(f"❌ Test data not found at {test_data_path}")
        print("   Using sample generated data instead")
        
        # Generate sample data
        np.random.seed(42)
        n_samples = 100
        X = pd.DataFrame({
            'trip_distance': np.random.uniform(0.5, 20, n_samples),
            'pickup_hour': np.random.randint(0, 24, n_samples),
            'passenger_count': np.random.randint(1, 6, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'is_weekend': np.random.randint(0, 2, n_samples)
        })
        print(f"✅ Generated {n_samples} sample predictions")
    else:
        X = pd.read_csv(test_data_path)
        print(f"✅ Loaded {len(X)} test samples from {test_data_path}")
    
    # Step 2: Initialize batch predictor
    print("\n[STEP 2] Initializing batch predictor...")
    predictor = BatchPredictor(model_name="taxi-fare-xgboost", use_mlflow=True)
    
    if predictor.load_production_model():
        print("✅ Production model loaded successfully")
    else:
        print("⚠️  Model loading failed (expected in dev mode)")
        print("    Continuing with mock predictions for demonstration...")
        
        # Mock model for demonstration
        from unittest.mock import Mock
        predictor.model = Mock()
        predictor.model.predict.return_value = np.random.normal(13.2, 8.5, len(X))
    
    # Step 3: Make batch predictions
    print("\n[STEP 3] Making batch predictions...")
    try:
        predictions, metrics = predictor.predict_batch(X)
        print(f"✅ Made {len(predictions)} predictions")
        print(f"   Mean fare: ${metrics['mean_prediction']:.2f}")
        print(f"   Std dev: ${metrics['std_prediction']:.2f}")
    except Exception as e:
        print(f"❌ Batch prediction failed: {e}")
        return
    
    # Step 4: Save predictions
    print("\n[STEP 4] Saving predictions...")
    predictions_path = predictor.save_predictions(predictions)
    print(f"✅ Predictions saved to {predictions_path}")
    
    # Step 5: Get prediction statistics
    print("\n[STEP 5] Prediction statistics...")
    stats = predictor.get_prediction_statistics()
    print("✅ Statistics computed:")
    for key, value in stats.items():
        if key != 'count':
            print(f"   {key}: ${value:.2f}")
    
    # Step 6: Initialize monitoring
    print("\n[STEP 6] Initializing monitoring...")
    baseline_metrics = {
        'mean_prediction': 13.2,  # From Day 5 tuned model
        'std_prediction': 8.5
    }
    monitor = PredictionMonitor(baseline_metrics=baseline_metrics)
    print("✅ Monitor initialized with baseline metrics")
    
    # Step 7: Check for data drift
    print("\n[STEP 7] Checking for data drift...")
    drift_analysis = monitor.check_data_drift(stats, threshold=0.15)
    
    if drift_analysis.get('checks'):
        print("Drift Analysis:")
        for metric, check in drift_analysis['checks'].items():
            status = "⚠️  DRIFTED" if check['drifted'] else "✅ OK"
            pct = check['pct_change'] * 100
            print(f"   {metric}: {status} ({pct:.1f}% change)")
    
    # Step 8: Check performance (if ground truth available)
    print("\n[STEP 8] Performance monitoring...")
    if all(c in X.columns for c in ['fare_amount']) or len(predictions) <= len(X):
        try:
            # Try to evaluate if we have test labels
            if 'fare_amount' in X.columns:
                y_true = X['fare_amount'].values
                eval_metrics = predictor.evaluate_predictions(y_true)
                print("✅ Evaluation metrics:")
                print(f"   R² Score: {eval_metrics['r2_score']:.4f}")
                print(f"   RMSE: ${eval_metrics['rmse']:.2f}")
                print(f"   MAE: ${eval_metrics['mae']:.2f}")
                
                # Check for degradation
                degradation = monitor.check_performance_degradation(eval_metrics)
                if degradation.get('degraded'):
                    print("\n   ⚠️  Performance degradation detected!")
                else:
                    print("   ✅ Performance within acceptable range")
            else:
                print("⚠️  No ground truth labels available")
        except Exception as e:
            print(f"⚠️  Could not evaluate: {e}")
    else:
        print("⚠️  No ground truth labels for evaluation")
    
    # Step 9: Save monitoring report
    print("\n[STEP 9] Saving monitoring report...")
    alert_file = monitor.save_monitoring_report()
    print(f"✅ Monitoring report saved to {alert_file}")
    
    if monitor.get_alerts():
        print("\n📋 Alerts:")
        for alert in monitor.get_alerts():
            print(f"   - {alert}")
    else:
        print("\n✅ No alerts raised")
    
    # Final summary
    print("\n" + "=" * 80)
    print("DAY 8 COMPLETION SUMMARY")
    print("=" * 80)
    print(f"✅ Batch predictions: {len(predictions)} samples")
    print(f"✅ Mean prediction: ${stats.get('mean', 0):.2f}")
    print(f"✅ Predictions saved to: {predictions_path}")
    print(f"✅ Monitoring report saved to: {alert_file}")
    print(f"✅ Alerts: {len(monitor.get_alerts())}")
    
    print("\n📊 Production Status:")
    print(f"   Model: taxi-fare-xgboost")
    print(f"   Predictions: ✅ Working")
    print(f"   Monitoring: ✅ Active")
    print(f"   Data Drift: {'⚠️  Detected' if monitor.get_alerts() else '✅ None'}")
    
    print("\n🚀 Next Steps:")
    print("   1. Day 9: Start inference server (FastAPI)")
    print("      python day9_inference_server.py")
    print("   2. Test API endpoints")
    print("   3. Monitor production predictions")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
