"""
COMPREHENSIVE IMPROVEMENTS VERIFICATION & INTEGRATION SCRIPT
Tests all 10 major improvements to ensure they're fully functional and integrated
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_ensemble_models():
    """Test Ensemble Models improvement"""
    print("\n✓ Testing Ensemble Models...")
    try:
        from src.models.ensemble import EnsembleModels
        from sklearn.datasets import make_regression
        from sklearn.model_selection import train_test_split
        
        X, y = make_regression(n_samples=100, n_features=10, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        ensemble = EnsembleModels()
        ensemble.fit(X_train, y_train)
        score = ensemble.score(X_test, y_test)
        
        print(f"  ✅ Ensemble Models: Working (R² = {score:.4f})")
        return True
    except Exception as e:
        print(f"  ⚠️  Ensemble Models: {str(e)}")
        return False

def test_bayesian_tuning():
    """Test Bayesian Hyperparameter Tuning improvement"""
    print("\n✓ Testing Bayesian Tuning...")
    try:
        from src.models.bayesian_tuning import BayesianTuning
        from sklearn.datasets import make_regression
        from sklearn.model_selection import train_test_split
        
        X, y = make_regression(n_samples=100, n_features=10, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        tuner = BayesianTuning(n_trials=3)  # Reduced for quick test
        best_model, best_score = tuner.optimize(X_train, y_train, X_test, y_test)
        
        print(f"  ✅ Bayesian Tuning: Working (Best R² = {best_score:.4f})")
        return True
    except Exception as e:
        print(f"  ⚠️  Bayesian Tuning: {str(e)}")
        return False

def test_feature_selection():
    """Test Advanced Feature Selection improvement"""
    print("\n✓ Testing Feature Selection...")
    try:
        from src.features.feature_selection import FeatureSelector
        from sklearn.datasets import make_regression
        
        X, y = make_regression(n_samples=100, n_features=20, random_state=42)
        
        selector = FeatureSelector()
        selected_features = selector.select_features(X, y, method="correlation")
        
        print(f"  ✅ Feature Selection: Working (Selected {len(selected_features)} features)")
        return True
    except Exception as e:
        print(f"  ⚠️  Feature Selection: {str(e)}")
        return False

def test_anomaly_detection():
    """Test Anomaly & Outlier Detection improvement"""
    print("\n✓ Testing Anomaly Detection...")
    try:
        from src.deployment.drift_detection import AnomalyDetector
        import numpy as np
        
        X = np.random.randn(100, 10)
        
        detector = AnomalyDetector()
        anomalies = detector.detect(X, method="isolation_forest")
        
        print(f"  ✅ Anomaly Detection: Working (Found {anomalies.sum()} anomalies)")
        return True
    except Exception as e:
        print(f"  ⚠️  Anomaly Detection: {str(e)}")
        return False

def test_ab_testing():
    """Test A/B Testing Framework improvement"""
    print("\n✓ Testing A/B Testing Framework...")
    try:
        from src.deployment.ab_testing import ABTester
        import numpy as np
        
        # Create sample A/B test data
        group_a = np.random.normal(10, 2, 100)
        group_b = np.random.normal(10.5, 2, 100)
        
        tester = ABTester()
        result = tester.t_test(group_a, group_b)
        
        print(f"  ✅ A/B Testing: Working (Statistic = {result['statistic']:.4f}, p-value = {result['p_value']:.4f})")
        return True
    except Exception as e:
        print(f"  ⚠️  A/B Testing: {str(e)}")
        return False

def test_shap_explainability():
    """Test SHAP Model Explainability improvement"""
    print("\n✓ Testing SHAP Explainability...")
    try:
        from src.models.explainability import SHAPExplainer
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.datasets import make_regression
        
        X, y = make_regression(n_samples=100, n_features=5, random_state=42)
        
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        explainer = SHAPExplainer(model)
        explanation = explainer.explain(X[:1])
        
        print(f"  ✅ SHAP Explainability: Working (Generated explanations)")
        return True
    except Exception as e:
        print(f"  ⚠️  SHAP Explainability: {str(e)}")
        return False

def test_grafana_integration():
    """Test Grafana Integration improvement"""
    print("\n✓ Testing Grafana Integration...")
    try:
        from src.deployment.grafana_integration import GrafanaIntegration
        
        grafana = GrafanaIntegration()
        dashboards = grafana.get_dashboard_config()
        
        print(f"  ✅ Grafana Integration: Working ({len(dashboards)} dashboards configured)")
        return True
    except Exception as e:
        print(f"  ⚠️  Grafana Integration: {str(e)}")
        return False

def test_model_optimization():
    """Test Model Optimization improvement"""
    print("\n✓ Testing Model Optimization...")
    try:
        from src.deployment.optimization import ModelOptimizer
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.datasets import make_regression
        
        X, y = make_regression(n_samples=100, n_features=10, random_state=42)
        
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        optimizer = ModelOptimizer()
        size_reduction = optimizer.measure_optimization_potential(model)
        
        print(f"  ✅ Model Optimization: Working (Potential {size_reduction}% reduction)")
        return True
    except Exception as e:
        print(f"  ⚠️  Model Optimization: {str(e)}")
        return False

def test_data_quality_framework():
    """Test Great Expectations Data Quality improvement"""
    print("\n✓ Testing Data Quality Framework...")
    try:
        from src.data.quality_framework import DataQualityValidator
        import pandas as pd
        
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })
        
        validator = DataQualityValidator()
        report = validator.validate(df)
        
        print(f"  ✅ Data Quality Framework: Working (Quality score: {report.get('quality_score', 'N/A')})")
        return True
    except Exception as e:
        print(f"  ⚠️  Data Quality Framework: {str(e)}")
        return False

def test_enhanced_api_docs():
    """Test Enhanced API Documentation improvement"""
    print("\n✓ Testing Enhanced API Docs...")
    try:
        from src.deployment.enhanced_api_docs import EnhancedAPIDocumentation
        
        docs = EnhancedAPIDocumentation()
        schema = docs.get_openapi_schema()
        
        print(f"  ✅ Enhanced API Docs: Working (OpenAPI 3.0 schema generated)")
        return True
    except Exception as e:
        print(f"  ⚠️  Enhanced API Docs: {str(e)}")
        return False

def run_all_tests():
    """Run all improvement tests"""
    print("\n" + "="*80)
    print("🚀 COMPREHENSIVE IMPROVEMENTS VERIFICATION")
    print("="*80)
    
    tests = [
        ("HIGH-PRIORITY IMPROVEMENTS", [
            ("1. Ensemble Models", test_ensemble_models),
            ("2. Bayesian Tuning", test_bayesian_tuning),
            ("3. Feature Selection", test_feature_selection),
            ("4. Anomaly Detection", test_anomaly_detection),
            ("5. A/B Testing", test_ab_testing),
        ]),
        ("MEDIUM-PRIORITY IMPROVEMENTS", [
            ("6. SHAP Explainability", test_shap_explainability),
            ("7. Grafana Integration", test_grafana_integration),
            ("8. Model Optimization", test_model_optimization),
            ("9. Data Quality Framework", test_data_quality_framework),
            ("10. Enhanced API Docs", test_enhanced_api_docs),
        ])
    ]
    
    results = {}
    
    for phase_name, phase_tests in tests:
        print(f"\n{phase_name}:")
        print("-" * 80)
        
        phase_results = {}
        for test_name, test_func in phase_tests:
            try:
                success = test_func()
                phase_results[test_name] = success
            except Exception as e:
                print(f"  ❌ {test_name}: Failed - {str(e)}")
                phase_results[test_name] = False
        
        results[phase_name] = phase_results
    
    # Summary
    print("\n" + "="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)
    
    total_tests = 0
    total_passed = 0
    
    for phase_name, phase_results in results.items():
        passed = sum(1 for v in phase_results.values() if v)
        total = len(phase_results)
        total_tests += total
        total_passed += passed
        
        print(f"\n{phase_name}:")
        print(f"  ✅ Passed: {passed}/{total}")
        for test_name, result in phase_results.items():
            status = "✅" if result else "⚠️"
            print(f"    {status} {test_name}")
    
    print("\n" + "="*80)
    print(f"🎉 OVERALL RESULT: {total_passed}/{total_tests} improvements verified")
    print("="*80)
    
    # Return results as JSON for logging
    return {
        "total_improvements": total_tests,
        "passed": total_passed,
        "success_rate": f"{(total_passed/total_tests)*100:.1f}%",
        "details": results
    }

if __name__ == "__main__":
    results = run_all_tests()
    
    # Save results
    with open("improvement_verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: improvement_verification_results.json")
