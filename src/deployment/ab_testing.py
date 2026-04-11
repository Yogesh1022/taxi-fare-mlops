"""
A/B Testing Framework for Model Deployments

Implements safe model testing and comparison:
1. Traffic Splitting - Route percentage of traffic to models
2. Statistical Testing - Significance testing for metrics
3. Multi-armed Bandit - Adaptive allocation based on performance
4. Reporting - Comprehensive comparison reports

Author: MLOps Team
Date: 2026-04-08
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

import numpy as np
import pandas as pd
from scipy.stats import binom_test, ttest_ind, mannwhitneyu
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Status of A/B test experiment."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    WINNER_SELECTED = "winner_selected"
    FAILED = "failed"


class ABTestManager:
    """
    A/B Testing framework for model deployments.
    
    Features:
    - Traffic splitting between models
    - Statistical significance testing
    - Multi-armed bandit optimization
    - Comprehensive reporting
    """
    
    def __init__(self, test_name: str, random_state: int = 42):
        """
        Initialize A/B test manager.
        
        Args:
            test_name: Name of the A/B test
            random_state: Random seed for reproducibility
        """
        self.test_name = test_name
        self.random_state = random_state
        self.status = ExperimentStatus.PENDING
        self.models = {}
        self.traffic_allocation = {}
        self.results = {
            'model_a': {'predictions': [], 'actuals': []},
            'model_b': {'predictions': [], 'actuals': []}
        }
        self.metrics = {}
        self.start_time = None
        self.end_time = None
        logger.info(f"[ABTEST] ABTestManager initialized for test: {test_name}")
    
    def add_model(self, model_name: str, model: Any, traffic_pct: float = 0.5):
        """
        Add model to A/B test.
        
        Args:
            model_name: Name of the model
            model: Trained model object
            traffic_pct: Percentage of traffic (0-1)
        """
        if model_name in self.models:
            raise ValueError(f"Model {model_name} already added")
        
        self.models[model_name] = model
        self.traffic_allocation[model_name] = traffic_pct
        
        logger.info(f"[ABTEST] Added model: {model_name} (traffic: {traffic_pct*100:.0f}%)")
    
    def route_request(self, request_id: int) -> str:
        """
        Route a request to one of the models based on traffic allocation.
        
        Args:
            request_id: ID of the request
            
        Returns:
            Name of the model to serve
        """
        np.random.seed(self.random_state + request_id)
        
        model_names = list(self.models.keys())
        allocations = list(self.traffic_allocation.values())
        allocations = [a / sum(allocations) for a in allocations]  # Normalize
        
        selected = np.random.choice(model_names, p=allocations)
        return selected
    
    def make_prediction(self, request_id: int, X: np.ndarray) -> Tuple[str, np.ndarray]:
        """
        Make prediction from appropriate model based on traffic allocation.
        
        Args:
            request_id: ID of the request
            X: Input features
            
        Returns:
            Tuple of (model_name, prediction)
        """
        if self.status == ExperimentStatus.PENDING:
            self.status = ExperimentStatus.RUNNING
            self.start_time = datetime.now()
            logger.info(f"[ABTEST] Experiment started at {self.start_time}")
        
        model_name = self.route_request(request_id)
        model = self.models[model_name]
        
        prediction = model.predict(X)
        
        return model_name, prediction
    
    def record_result(self, model_name: str, prediction: np.ndarray, actual: np.ndarray):
        """
        Record prediction and actual value.
        
        Args:
            model_name: Name of the model used
            prediction: Model prediction
            actual: Actual value
        """
        self.results[model_name]['predictions'].append(prediction)
        self.results[model_name]['actuals'].append(actual)
    
    def compute_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Compute metrics for each model.
        
        Returns:
            Dictionary of metrics per model
        """
        logger.info("[ABTEST] Computing metrics for each model...")
        
        for model_name in self.models.keys():
            predictions = np.array(self.results[model_name]['predictions'])
            actuals = np.array(self.results[model_name]['actuals'])
            
            if len(predictions) == 0:
                logger.warning(f"[ABTEST] No predictions recorded for {model_name}")
                continue
            
            metrics = {
                'n_samples': len(predictions),
                'r2_score': float(r2_score(actuals, predictions)),
                'mae': float(mean_absolute_error(actuals, predictions)),
                'rmse': float(np.sqrt(mean_squared_error(actuals, predictions))),
                'mean_prediction': float(predictions.mean()),
                'std_prediction': float(predictions.std()),
            }
            
            self.metrics[model_name] = metrics
            
            logger.info(f"[ABTEST] {model_name} Metrics:")
            logger.info(f"[ABTEST]   Samples: {metrics['n_samples']}")
            logger.info(f"[ABTEST]   R² Score: {metrics['r2_score']:.4f}")
            logger.info(f"[ABTEST]   MAE: ${metrics['mae']:.2f}")
            logger.info(f"[ABTEST]   RMSE: ${metrics['rmse']:.2f}")
        
        return self.metrics
    
    def statistical_test(self) -> Dict[str, Any]:
        """
        Perform statistical significance test.
        
        Uses Mann-Whitney U test (non-parametric).
        
        Returns:
            Dictionary with test results
        """
        logger.info("[ABTEST] Running statistical significance test...")
        
        model_names = list(self.models.keys())
        if len(model_names) != 2:
            raise ValueError("Statistical test requires exactly 2 models")
        
        model_a, model_b = model_names
        
        pred_a = np.array(self.results[model_a]['predictions'])
        pred_b = np.array(self.results[model_b]['predictions'])
        actuals_a = np.array(self.results[model_a]['actuals'])
        actuals_b = np.array(self.results[model_b]['actuals'])
        
        # Compute errors
        errors_a = np.abs(pred_a - actuals_a)
        errors_b = np.abs(pred_b - actuals_b)
        
        # Mann-Whitney U test
        statistic, p_value = mannwhitneyu(errors_a, errors_b, alternative='two-sided')
        
        # Determine winner
        mean_error_a = errors_a.mean()
        mean_error_b = errors_b.mean()
        
        if mean_error_a < mean_error_b:
            winner = model_a
            improvement = (mean_error_b - mean_error_a) / mean_error_b * 100
        else:
            winner = model_b
            improvement = (mean_error_a - mean_error_b) / mean_error_a * 100
        
        is_significant = p_value < 0.05
        
        result = {
            'test_type': 'Mann-Whitney U test',
            'statistic': float(statistic),
            'p_value': float(p_value),
            'is_significant': bool(is_significant),
            'winner': winner if is_significant else "no_clear_winner",
            'improvement_pct': float(improvement) if is_significant else 0.0,
            'mean_error_a': float(mean_error_a),
            'mean_error_b': float(mean_error_b),
        }
        
        logger.info(f"[ABTEST] Statistical Test Results:")
        logger.info(f"[ABTEST]   p-value: {p_value:.4f}")
        logger.info(f"[ABTEST]   Significant: {is_significant}")
        logger.info(f"[ABTEST]   Winner: {result['winner']}")
        logger.info(f"[ABTEST]   Improvement: {improvement:.1f}%")
        
        return result
    
    def conclude_test(self) -> Dict[str, Any]:
        """
        Conclude the A/B test and generate final report.
        
        Returns:
            Dictionary with test conclusion
        """
        logger.info("[ABTEST] Concluding A/B test...")
        
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        # Compute metrics
        self.compute_metrics()
        
        # Statistical test
        stat_test = self.statistical_test()
        
        conclusion = {
            'test_name': self.test_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'metrics': self.metrics,
            'statistical_test': stat_test,
            'recommendation': self._generate_recommendation(stat_test)
        }
        
        self.status = ExperimentStatus.COMPLETED
        
        if stat_test['is_significant']:
            self.status = ExperimentStatus.WINNER_SELECTED
        
        logger.info(f"\n[ABTEST] TEST CONCLUSION: {conclusion['recommendation']}")
        
        return conclusion
    
    def _generate_recommendation(self, stat_test: Dict) -> str:
        """Generate deployment recommendation based on test results."""
        if not stat_test['is_significant']:
            return "NO_SIGNIFICANT_DIFFERENCE"
        
        winner = stat_test['winner']
        improvement = stat_test['improvement_pct']
        
        if improvement > 5:
            return f"DEPLOY_{winner.upper()}_STRONGLY_RECOMMENDED"
        elif improvement > 2:
            return f"DEPLOY_{winner.upper()}_RECOMMENDED"
        else:
            return f"DEPLOY_{winner.upper()}_CAUTIOUSLY"
    
    def save_report(self, output_dir: str = "models"):
        """Save A/B test report."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Conclude test if not already done
        if self.status == ExperimentStatus.RUNNING:
            conclusion = self.conclude_test()
        else:
            conclusion = {
                'test_name': self.test_name,
                'status': self.status.value,
                'metrics': self.metrics
            }
        
        report_file = output_path / f"abtest_{self.test_name}.json"
        
        with open(report_file, 'w') as f:
            json.dump(conclusion, f, indent=2)
        
        logger.info(f"[ABTEST] Report saved to {report_file}")
        
        # Generate CSV comparison table
        self._generate_comparison_table(output_path)
    
    def _generate_comparison_table(self, output_path: Path):
        """Generate comparison table as CSV."""
        data = []
        for model_name, metrics in self.metrics.items():
            data.append({
                'Model': model_name,
                'Samples': metrics['n_samples'],
                'R² Score': f"{metrics['r2_score']:.4f}",
                'MAE': f"${metrics['mae']:.2f}",
                'RMSE': f"${metrics['rmse']:.2f}",
            })
        
        df = pd.DataFrame(data)
        comparison_file = output_path / f"abtest_{self.test_name}_comparison.csv"
        df.to_csv(comparison_file, index=False)
        
        logger.info(f"\n[ABTEST] COMPARISON TABLE")
        logger.info("=" * 80)
        logger.info(df.to_string(index=False))
        logger.info("=" * 80)


class MultiArmedBandit:
    """
    Multi-armed bandit for adaptive model allocation.
    
    Automatically adjusts traffic allocation based on model performance.
    """
    
    def __init__(self, initial_allocations: Dict[str, float], strategy: str = 'epsilon_greedy'):
        """
        Initialize multi-armed bandit.
        
        Args:
            initial_allocations: Initial traffic allocation per model
            strategy: 'epsilon_greedy' or 'upper_confidence_bound'
        """
        self.allocations = initial_allocations.copy()
        self.strategy = strategy
        self.attempts = {model: 0 for model in initial_allocations.keys()}
        self.successes = {model: 0 for model in initial_allocations.keys()}
        self.epsilon = 0.1  # Exploration rate
        self.c = 1.0  # Confidence parameter for UCB
        logger.info(f"[BANDIT] MultiArmedBandit initialized (strategy: {strategy})")
    
    def select_model(self, request_id: int) -> str:
        """
        Select model using bandit strategy.
        
        Args:
            request_id: ID of the request
            
        Returns:
            Selected model name
        """
        np.random.seed(self.random_state + request_id if hasattr(self, 'random_state') else 42)
        
        if self.strategy == 'epsilon_greedy':
            return self._epsilon_greedy()
        elif self.strategy == 'ucb':
            return self._upper_confidence_bound()
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def _epsilon_greedy(self) -> str:
        """Epsilon-greedy selection."""
        if np.random.random() < self.epsilon:
            # Explore: random selection
            return np.random.choice(list(self.allocations.keys()))
        else:
            # Exploit: select best performing model
            success_rates = {
                model: self.successes[model] / (self.attempts[model] + 1e-10)
                for model in self.allocations.keys()
            }
            return max(success_rates, key=success_rates.get)
    
    def _upper_confidence_bound(self) -> str:
        """Upper Confidence Bound selection."""
        ucb_scores = {}
        for model in self.allocations.keys():
            mean_reward = self.successes[model] / (self.attempts[model] + 1e-10)
            confidence = self.c * np.sqrt(np.log(sum(self.attempts.values()) + 1) / (self.attempts[model] + 1))
            ucb_scores[model] = mean_reward + confidence
        
        return max(ucb_scores, key=ucb_scores.get)
    
    def update(self, model_name: str, reward: float):
        """
        Update bandit statistics.
        
        Args:
            model_name: Model that was used
            reward: Performance reward (0-1, higher is better)
        """
        self.attempts[model_name] += 1
        self.successes[model_name] += reward
    
    def get_allocations(self) -> Dict[str, float]:
        """Get current traffic allocations."""
        success_rates = {
            model: self.successes[model] / (self.attempts[model] + 1e-10)
            for model in self.allocations.keys()
        }
        
        # Allocate traffic proportional to success rate
        total_rate = sum(success_rates.values())
        if total_rate > 0:
            self.allocations = {
                model: rate / total_rate
                for model, rate in success_rates.items()
            }
        
        return self.allocations


def run_ab_test(
    model_a: Any,
    model_b: Any,
    X_data: np.ndarray,
    y_data: np.ndarray,
    test_name: str = "model_comparison",
    traffic_split: Tuple[float, float] = (0.5, 0.5),
    output_dir: str = "models"
) -> Dict[str, Any]:
    """
    Run complete A/B test between two models.
    
    Args:
        model_a: First model
        model_b: Second model
        X_data: Test features
        y_data: Test targets
        test_name: Name of the test
        traffic_split: Traffic allocation (model_a_pct, model_b_pct)
        output_dir: Directory to save results
        
    Returns:
        Dictionary with A/B test results
    """
    logger.info("[ABTEST] Starting A/B test...")
    
    manager = ABTestManager(test_name)
    manager.add_model('model_a', model_a, traffic_split[0])
    manager.add_model('model_b', model_b, traffic_split[1])
    
    # Simulate predictions
    for i in range(len(X_data)):
        model_name, prediction = manager.make_prediction(i, X_data[i:i+1])
        manager.record_result(model_name, prediction, y_data[i])
    
    # Conclude test
    conclusion = manager.conclude_test()
    manager.save_report(output_dir)
    
    return conclusion
