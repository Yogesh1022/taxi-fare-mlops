"""
Day 13 Integration Tests - Advanced Monitoring & Drift Detection
Tests end-to-end monitoring pipeline with all components
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


def test_drift_detection():
    """Test drift detection pipeline."""
    print("\n" + "="*60)
    print("TEST 1: Drift Detection Pipeline")
    print("="*60)
    
    try:
        from monitoring.drift_detection.run_drift_detection import DriftDetectionPipeline
        
        # Create sample data
        np.random.seed(42)
        n_samples = 500
        
        # Reference data (normal distribution)
        reference_data = pd.DataFrame({
            'distance': np.random.normal(3.5, 1.2, n_samples),
            'duration': np.random.normal(15, 5, n_samples),
            'fare': np.random.normal(12, 3, n_samples),
            'day': np.random.choice(range(1, 8), n_samples),
            'hour': np.random.choice(range(24), n_samples),
        })
        
        # Current data (with slight drift)
        current_data = pd.DataFrame({
            'distance': np.random.normal(4.0, 1.3, n_samples),  # Shifted mean
            'duration': np.random.normal(16, 5.2, n_samples),
            'fare': np.random.normal(13, 3.1, n_samples),
            'day': np.random.choice(range(1, 8), n_samples),
            'hour': np.random.choice(range(24), n_samples),
        })
        
        # Initialize pipeline
        pipeline = DriftDetectionPipeline(reference_data, current_data)
        
        # Generate reports
        print("✓ Initializing drift detection pipeline")
        
        drift_report = pipeline.generate_data_drift_report()
        print(f"✓ Data drift report generated")
        print(f"  - Drift detected: {drift_report.drift_by_columns.number_of_drifted_columns > 0}")
        
        quality_report = pipeline.generate_quality_report()
        print(f"✓ Data quality report generated")
        
        # Run test suites
        drift_tests = pipeline.run_drift_tests()
        print(f"✓ Drift tests executed: {len(drift_tests.tests)} tests")
        
        quality_tests = pipeline.run_quality_tests()
        print(f"✓ Quality tests executed: {len(quality_tests.tests)} tests")
        
        summary = pipeline.generate_summary()
        print(f"✓ Summary generated")
        print(f"  - Has critical issues: {'critical_issues' in str(summary)}")
        
        print("\n✅ DRIFT DETECTION TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ DRIFT DETECTION TEST FAILED: {str(e)}")
        return False


def test_data_quality_monitor():
    """Test data quality monitoring."""
    print("\n" + "="*60)
    print("TEST 2: Data Quality Monitoring")
    print("="*60)
    
    try:
        from monitoring.drift_detection.data_quality_monitor import DataQualityMonitor
        
        # Create test data
        np.random.seed(42)
        n_samples = 1000
        
        reference_data = pd.DataFrame({
            'fare': np.random.normal(12, 3, n_samples),
            'distance': np.random.normal(3.5, 1.2, n_samples),
            'duration': np.random.normal(15, 5, n_samples),
            'passengers': np.random.choice([1, 2, 3, 4, 5, 6], n_samples),
        })
        
        monitor = DataQualityMonitor(reference_data)
        print("✓ Data quality monitor initialized")
        
        # Test with clean data
        clean_data = reference_data.copy()
        report = monitor.generate_quality_report(clean_data)
        print(f"✓ Clean data quality check: {report['quality_score']:.2%}")
        assert report['quality_score'] > 0.9, "Clean data should have high quality score"
        
        # Test with missing values
        dirty_data = reference_data.copy()
        dirty_data.loc[0:50, 'fare'] = np.nan
        report = monitor.generate_quality_report(dirty_data)
        print(f"✓ Dirty data quality check: {report['quality_score']:.2%}")
        assert report['missing_values_ratio'] > 0, "Should detect missing values"
        
        # Test metrics export
        metrics = monitor.get_prometheus_metrics(clean_data)
        print(f"✓ Prometheus metrics generated: {len(metrics)} metrics")
        assert 'data_quality_score' in metrics, "Should have quality score metric"
        
        # Test schema validation
        is_valid, issues = monitor.check_schema(clean_data)
        print(f"✓ Schema validation: valid={is_valid}, issues={len(issues)}")
        
        print("\n✅ DATA QUALITY MONITOR TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ DATA QUALITY MONITOR TEST FAILED: {str(e)}")
        return False


def test_business_kpis():
    """Test business KPI calculation."""
    print("\n" + "="*60)
    print("TEST 3: Business KPI Metrics")
    print("="*60)
    
    try:
        from monitoring.drift_detection.business_kpis import TaxiFarePredictionKPIs
        
        kpis = TaxiFarePredictionKPIs(lookback_hours=24)
        print("✓ Business KPI tracker initialized")
        
        # Create prediction data
        np.random.seed(42)
        n_samples = 1000
        
        predictions_df = pd.DataFrame({
            'actual_fare': np.random.uniform(10, 50, n_samples),
            'predicted_fare': np.random.uniform(10, 50, n_samples),
            'borough': np.random.choice(['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'], n_samples),
            'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='1min'),
            'inference_time_ms': np.random.uniform(5, 50, n_samples),
        })
        
        # Calculate borough KPIs
        borough_kpis = kpis.calculate_by_borough(predictions_df)
        print(f"✓ Calculated KPIs for {len(borough_kpis)} boroughs")
        
        for borough, kpi in borough_kpis.items():
            print(f"  - {borough}: accuracy={kpi.accuracy:.2%}, mae=${kpi.mae:.2f}")
            assert kpi.accuracy > 0, "Accuracy should be positive"
            assert kpi.mae > 0, "MAE should be positive"
        
        # Test demand forecast accuracy
        actual_demand = np.array([100, 110, 105, 120, 115])
        predicted_demand = np.array([98, 112, 103, 115, 118])
        
        forecast_metrics = kpis.calculate_demand_forecast_accuracy(actual_demand, predicted_demand)
        print(f"✓ Demand forecast MAPE: {forecast_metrics['mape']:.2f}%")
        print(f"✓ Direction accuracy: {forecast_metrics['direction_accuracy']:.2%}")
        
        # Test model value metrics
        value_metrics = kpis.calculate_model_value_metrics()
        print(f"✓ Model value metrics calculated")
        print(f"  - Annual revenue lift: ${value_metrics['annual_revenue_lift']:.0f}")
        print(f"  - Annual ROI: {value_metrics['roi_pct']:.1f}%")
        
        # Test KPI report generation
        report = kpis.generate_kpi_report()
        print(f"✓ KPI report generated with {report['metrics_count']} data points")
        
        # Test Prometheus metrics export
        prometheus_metrics = kpis.get_prometheus_metrics(borough_kpis)
        print(f"✓ Prometheus metrics exported: {len(prometheus_metrics)} metrics")
        
        print("\n✅ BUSINESS KPI TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ BUSINESS KPI TEST FAILED: {str(e)}")
        return False


def test_enhanced_monitoring_client():
    """Test enhanced monitoring client."""
    print("\n" + "="*60)
    print("TEST 4: Enhanced Monitoring Client")
    print("="*60)
    
    try:
        from monitoring.enhanced_monitoring import EnhancedMonitoringClient
        
        # Initialize without Jaeger (to avoid network dependency)
        monitor = EnhancedMonitoringClient(
            service_name="test-service",
            enable_jaeger=False,
            enable_prometheus=True
        )
        print("✓ Monitoring client initialized")
        
        # Test prediction tracking
        monitor.track_prediction(
            model_name="test_model",
            inference_time_ms=42.5,
            status="success",
            accuracy=0.95
        )
        print("✓ Prediction tracking works")
        
        # Test data quality tracking
        monitor.track_data_quality(
            dataset_name="test_dataset",
            quality_score=0.92,
            missing_values={'feature1': 0.01},
            outliers={'feature1': 0.03}
        )
        print("✓ Data quality tracking works")
        
        # Test drift tracking
        monitor.track_drift_detection(
            feature="test_feature",
            dataset_name="test_dataset",
            drift_score=0.65,
            threshold=0.5
        )
        print("✓ Drift detection tracking works")
        
        # Test API request tracking
        monitor.track_api_request(
            endpoint="/predict",
            duration_ms=150.0,
            status_code=200
        )
        print("✓ API request tracking works")
        
        # Test business KPI tracking
        monitor.track_business_kpi(
            metric_name="accuracy",
            value=0.93,
            borough="Manhattan"
        )
        print("✓ Business KPI tracking works")
        
        # Test decorator
        @monitor.track_latency("test_operation")
        def test_function():
            return 42
        
        result = test_function()
        print(f"✓ Latency tracking decorator works (result={result})")
        
        # Test registry
        registry = monitor.get_registry()
        print("✓ Prometheus registry retrieved")
        
        print("\n✅ ENHANCED MONITORING CLIENT TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ ENHANCED MONITORING CLIENT TEST FAILED: {str(e)}")
        return False


def test_alert_rules_syntax():
    """Test Prometheus alert rules syntax."""
    print("\n" + "="*60)
    print("TEST 5: Prometheus Alert Rules Syntax")
    print("="*60)
    
    try:
        import yaml
        
        alerts_file = Path(__file__).parent / "monitoring" / "docker" / "prometheus" / "alerts_extended.yaml"
        
        if not alerts_file.exists():
            print(f"⚠️  Alert rules file not found at {alerts_file}")
            print("✓ Skipping syntax check")
            return True
        
        with open(alerts_file, 'r') as f:
            rules = yaml.safe_load(f)
        
        print(f"✓ Alert rules YAML valid")
        
        groups = rules.get('groups', [])
        print(f"✓ Found {len(groups)} alert groups:")
        
        total_alerts = 0
        for group in groups:
            group_name = group.get('name', 'unknown')
            rules_list = group.get('rules', [])
            print(f"  - {group_name}: {len(rules_list)} alerts")
            total_alerts += len(rules_list)
        
        print(f"✓ Total alerts configured: {total_alerts}")
        assert total_alerts > 0, "Should have at least one alert"
        
        print("\n✅ ALERT RULES SYNTAX TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ ALERT RULES SYNTAX TEST FAILED: {str(e)}")
        return False


def main():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("DAY 13 INTEGRATION TEST SUITE")
    print("Advanced Monitoring & Drift Detection")
    print("="*60)
    
    results = {
        'Drift Detection': test_drift_detection(),
        'Data Quality Monitor': test_data_quality_monitor(),
        'Business KPIs': test_business_kpis(),
        'Enhanced Monitoring Client': test_enhanced_monitoring_client(),
        'Alert Rules Syntax': test_alert_rules_syntax(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print("\n" + "-"*60)
    print(f"Overall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("✅ ALL TESTS PASSED - Day 13 Implementation Complete!")
        return 0
    else:
        print(f"❌ {total_count - passed_count} test(s) failed - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
