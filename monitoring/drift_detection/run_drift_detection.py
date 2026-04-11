"""
Drift Detection Pipeline Runner
Generates reports and detects data/model drift
"""

import os
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.test_suite import TestSuite
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, RegressionPerformancePreset

from config import DRIFT_CONFIG, METRIC_PRESETS, TEST_SUITES


class DriftDetectionPipeline:
    """Main drift detection pipeline"""
    
    def __init__(self, output_dir: str = "drift_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def load_data(self, reference_path: str, current_path: str) -> tuple:
        """Load reference and current datasets"""
        print(f"Loading reference data from {reference_path}")
        reference_df = pd.read_csv(reference_path)
        
        print(f"Loading current data from {current_path}")
        current_df = pd.read_csv(current_path)
        
        return reference_df, current_df
    
    def generate_data_drift_report(self, reference_df: pd.DataFrame, current_df: pd.DataFrame):
        """Generate data drift detection report"""
        print("\n" + "="*60)
        print("GENERATING DATA DRIFT REPORT")
        print("="*60)
        
        report = Report(metrics=[
            METRIC_PRESETS["data_drift"]
        ])
        
        report.run(
            reference_data=reference_df,
            current_data=current_df
        )
        
        # Save HTML report
        report_path = self.output_dir / f"data_drift_report_{self.timestamp}.html"
        report.save_html(str(report_path))
        print(f"✅ Data drift report saved: {report_path}")
        
        # Save JSON report
        report_json = report.as_dict()
        json_path = self.output_dir / f"data_drift_report_{self.timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(report_json, f, indent=2, default=str)
        print(f"✅ Data drift JSON saved: {json_path}")
        
        return report_json
    
    def generate_quality_report(self, reference_df: pd.DataFrame, current_df: pd.DataFrame):
        """Generate data quality report"""
        print("\n" + "="*60)
        print("GENERATING DATA QUALITY REPORT")
        print("="*60)
        
        report = Report(metrics=[
            METRIC_PRESETS["data_quality"]
        ])
        
        report.run(
            reference_data=reference_df,
            current_data=current_df
        )
        
        # Save HTML report
        report_path = self.output_dir / f"data_quality_report_{self.timestamp}.html"
        report.save_html(str(report_path))
        print(f"✅ Data quality report saved: {report_path}")
        
        # Save JSON report
        report_json = report.as_dict()
        json_path = self.output_dir / f"data_quality_report_{self.timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(report_json, f, indent=2, default=str)
        print(f"✅ Data quality JSON saved: {json_path}")
        
        return report_json
    
    def run_quality_tests(self, reference_df: pd.DataFrame, current_df: pd.DataFrame):
        """Run data quality tests"""
        print("\n" + "="*60)
        print("RUNNING DATA QUALITY TESTS")
        print("="*60)
        
        suite = TestSuite(tests=TEST_SUITES["data_quality"])
        
        suite.run(
            reference_data=reference_df,
            current_data=current_df
        )
        
        # Save test results
        json_path = self.output_dir / f"quality_tests_{self.timestamp}.json"
        suite.save_json(str(json_path))
        print(f"✅ Quality tests saved: {json_path}")
        
        # Print summary
        for result in suite.results:
            status = "✅ PASS" if result.get("status") == "success" else "❌ FAIL"
            print(f"{status}: {result.get('test_name')}")
        
        return suite.as_dict()
    
    def run_drift_tests(self, reference_df: pd.DataFrame, current_df: pd.DataFrame):
        """Run drift detection tests"""
        print("\n" + "="*60)
        print("RUNNING DRIFT DETECTION TESTS")
        print("="*60)
        
        suite = TestSuite(tests=TEST_SUITES["drift_detection"])
        
        suite.run(
            reference_data=reference_df,
            current_data=current_df
        )
        
        # Save test results
        json_path = self.output_dir / f"drift_tests_{self.timestamp}.json"
        suite.save_json(str(json_path))
        print(f"✅ Drift tests saved: {json_path}")
        
        # Print summary
        for result in suite.results:
            status = "✅ PASS" if result.get("status") == "success" else "⚠️ DRIFT" 
            print(f"{status}: {result.get('test_name')}")
        
        return suite.as_dict()
    
    def generate_summary(self, drift_report: dict, quality_report: dict, 
                        quality_tests: dict, drift_tests: dict) -> dict:
        """Generate a summary of all findings"""
        print("\n" + "="*60)
        print("GENERATING SUMMARY")
        print("="*60)
        
        summary = {
            "timestamp": self.timestamp,
            "drift_detected": drift_report.get("status") == "DRIFT_DETECTED",
            "quality_issues": quality_report.get("status") == "QUALITY_ISSUES",
            "tests_passed": sum(1 for r in drift_tests.get("results", []) 
                               if r.get("status") == "success"),
            "tests_failed": sum(1 for r in drift_tests.get("results", []) 
                               if r.get("status") != "success"),
            "report_files": {
                "drift": f"data_drift_report_{self.timestamp}.json",
                "quality": f"data_quality_report_{self.timestamp}.json",
                "quality_tests": f"quality_tests_{self.timestamp}.json",
                "drift_tests": f"drift_tests_{self.timestamp}.json",
            }
        }
        
        # Save summary
        summary_path = self.output_dir / f"summary_{self.timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Summary saved: {summary_path}")
        
        # Print summary
        print(f"\n📊 Drift Detected: {summary['drift_detected']}")
        print(f"⚠️ Quality Issues: {summary['quality_issues']}")
        print(f"✅ Tests Passed: {summary['tests_passed']}")
        print(f"❌ Tests Failed: {summary['tests_failed']}")
        
        return summary
    
    def run(self, reference_path: str, current_path: str):
        """Run complete drift detection pipeline"""
        print("\n" + "="*70)
        print("STARTING DRIFT DETECTION PIPELINE")
        print("="*70)
        
        try:
            # Load data
            reference_df, current_df = self.load_data(reference_path, current_path)
            print(f"✅ Reference data shape: {reference_df.shape}")
            print(f"✅ Current data shape: {current_df.shape}")
            
            # Generate reports
            drift_report = self.generate_data_drift_report(reference_df, current_df)
            quality_report = self.generate_quality_report(reference_df, current_df)
            
            # Run tests
            quality_tests = self.run_quality_tests(reference_df, current_df)
            drift_tests = self.run_drift_tests(reference_df, current_df)
            
            # Generate summary
            summary = self.generate_summary(drift_report, quality_report, 
                                          quality_tests, drift_tests)
            
            print("\n" + "="*70)
            print("✅ DRIFT DETECTION PIPELINE COMPLETED SUCCESSFULLY")
            print("="*70)
            
            return summary
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            raise


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run drift detection pipeline")
    parser.add_argument("--reference", required=True, help="Path to reference dataset")
    parser.add_argument("--current", required=True, help="Path to current dataset")
    parser.add_argument("--output", default="drift_reports", help="Output directory")
    
    args = parser.parse_args()
    
    pipeline = DriftDetectionPipeline(output_dir=args.output)
    summary = pipeline.run(args.reference, args.current)
    
    return summary


if __name__ == "__main__":
    main()
