"""
Business KPI Metrics Collection
Day 13: Advanced Monitoring & Drift Detection

Tracks domain-specific KPIs for taxi fare prediction system:
- Revenue impact estimates
- Prediction accuracy by geographic region (borough)
- Demand forecasting accuracy
- Customer satisfaction proxy metrics
- Model value metrics (cost savings, efficiency)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class FarePredictionKPI:
    """Data class for fare prediction KPI metrics."""
    timestamp: str
    borough: str
    prediction_count: int
    mae: float  # Mean Absolute Error
    mape: float  # Mean Absolute Percentage Error
    accuracy: float  # Accuracy rate
    avg_prediction_time_ms: float
    revenue_impact: float  # Estimated revenue impact in dollars


class TaxiFarePredictionKPIs:
    """Monitor business KPIs for taxi fare prediction system."""
    
    def __init__(self, lookback_hours: int = 24):
        """
        Initialize KPI monitor.
        
        Args:
            lookback_hours: Historical window for KPI calculations
        """
        self.lookback_hours = lookback_hours
        self.boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']
        self.metrics_history: List[FarePredictionKPI] = []
        
    def calculate_mae(self, actuals: np.ndarray, predictions: np.ndarray) -> float:
        """Calculate Mean Absolute Error."""
        return np.mean(np.abs(actuals - predictions))
    
    def calculate_mape(self, actuals: np.ndarray, predictions: np.ndarray) -> float:
        """Calculate Mean Absolute Percentage Error."""
        mask = actuals != 0
        if not mask.any():
            return 0.0
        return np.mean(np.abs((actuals[mask] - predictions[mask]) / actuals[mask])) * 100
    
    def calculate_accuracy(self, actuals: np.ndarray, predictions: np.ndarray, 
                          tolerance_pct: float = 0.1) -> float:
        """
        Calculate accuracy as percentage of predictions within tolerance.
        
        Args:
            tolerance_pct: Acceptable error as percentage of actual value
        """
        threshold = np.abs(actuals * tolerance_pct)
        correct = np.abs(actuals - predictions) <= threshold
        return np.mean(correct) * 100 if len(correct) > 0 else 0.0
    
    def estimate_revenue_impact(self, actuals: np.ndarray, predictions: np.ndarray,
                               accuracy_weight: float = 0.7, 
                               efficiency_weight: float = 0.3) -> float:
        """
        Estimate revenue impact in dollars.
        
        Considers:
        - Prediction accuracy improvement
        - Operational efficiency
        - Reduced empty rides and dead mileage
        
        Args:
            accuracy_weight: Weight for accuracy component
            efficiency_weight: Weight for efficiency component
            
        Returns:
            Estimated revenue impact in dollars
        """
        mae = self.calculate_mae(actuals, predictions)
        
        # Accuracy component: each $0.50 improvement in MAE ≈ $10-15 revenue impact
        accuracy_impact = (1 - min(mae / 50, 1.0)) * 100  # Normalized to 100
        
        # Efficiency component: improved prediction efficiency saves ~5% dead mileage
        efficiency_impact = 50  # Baseline efficiency improvement
        
        # Combine components (typical daily volume: 500 rides, avg fare: $15)
        daily_rides = 500
        avg_fare = 15
        base_revenue = daily_rides * avg_fare
        
        # Total impact percentage
        impact_pct = (accuracy_weight * accuracy_impact + efficiency_weight * efficiency_impact) / 100
        revenue_impact = base_revenue * impact_pct
        
        return revenue_impact
    
    def calculate_by_borough(self, df: pd.DataFrame, 
                            predictions_col: str = 'predicted_fare',
                            actual_col: str = 'actual_fare',
                            borough_col: str = 'borough',
                            time_col: str = 'timestamp') -> Dict[str, FarePredictionKPI]:
        """
        Calculate KPIs by geographic borough.
        
        Args:
            df: DataFrame with predictions and actuals
            predictions_col: Column name for predictions
            actual_col: Column name for actuals
            borough_col: Column name for borough identifier
            time_col: Column name for timestamp
            
        Returns:
            Dict mapping borough -> FarePredictionKPI
        """
        borough_kpis = {}
        
        for borough in self.boroughs:
            # Filter data for this borough
            borough_data = df[df[borough_col] == borough]
            
            if len(borough_data) == 0:
                logger.warning(f"No data for borough: {borough}")
                continue
            
            actuals = borough_data[actual_col].values
            predictions = borough_data[predictions_col].values
            
            # Filter out invalid values
            valid_mask = (actuals > 0) & (predictions > 0) & ~np.isnan(actuals) & ~np.isnan(predictions)
            actuals = actuals[valid_mask]
            predictions = predictions[valid_mask]
            
            if len(actuals) == 0:
                continue
            
            # Calculate metrics
            mae = self.calculate_mae(actuals, predictions)
            mape = self.calculate_mape(actuals, predictions)
            accuracy = self.calculate_accuracy(actuals, predictions)
            avg_time_ms = borough_data['inference_time_ms'].mean() if 'inference_time_ms' in borough_data.columns else 10.0
            revenue_impact = self.estimate_revenue_impact(actuals, predictions)
            
            kpi = FarePredictionKPI(
                timestamp=datetime.utcnow().isoformat(),
                borough=borough,
                prediction_count=len(actuals),
                mae=mae,
                mape=mape,
                accuracy=accuracy,
                avg_prediction_time_ms=avg_time_ms,
                revenue_impact=revenue_impact
            )
            
            borough_kpis[borough] = kpi
            self.metrics_history.append(kpi)
        
        return borough_kpis
    
    def calculate_demand_forecast_accuracy(self, actual_demand: np.ndarray,
                                          predicted_demand: np.ndarray) -> Dict[str, float]:
        """
        Calculate demand forecasting accuracy metrics.
        
        Args:
            actual_demand: Actual ride demand per time period
            predicted_demand: Predicted ride demand per time period
            
        Returns:
            Dict with forecast accuracy metrics
        """
        mae = np.mean(np.abs(actual_demand - predicted_demand))
        rmse = np.sqrt(np.mean((actual_demand - predicted_demand) ** 2))
        mape = np.mean(np.abs((actual_demand - predicted_demand) / (actual_demand + 1))) * 100
        
        # Directional accuracy (forecast direction matches actual)
        actual_direction = np.sign(np.diff(actual_demand))
        pred_direction = np.sign(np.diff(predicted_demand))
        direction_accuracy = np.mean(actual_direction == pred_direction) * 100
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'direction_accuracy': direction_accuracy,
        }
    
    def calculate_model_value_metrics(self, 
                                     daily_predictions: int = 500,
                                     avg_prediction_accuracy: float = 0.92,
                                     operational_cost_per_prediction: float = 0.01,
                                     baseline_accuracy: float = 0.75) -> Dict[str, float]:
        """
        Calculate business value metrics for the model.
        
        Args:
            daily_predictions: Number of predictions per day
            avg_prediction_accuracy: Current model accuracy
            operational_cost_per_prediction: Cost to run prediction
            baseline_accuracy: Baseline accuracy (rule-based system)
            
        Returns:
            Dict with value metrics
        """
        # Accuracy improvement
        accuracy_improvement = (avg_prediction_accuracy - baseline_accuracy) * 100
        
        # Cost savings: improved accuracy reduces need for correction/reruns
        daily_corrections_baseline = daily_predictions * (1 - baseline_accuracy) * 0.3  # 30% need correction
        daily_corrections_current = daily_predictions * (1 - avg_prediction_accuracy) * 0.3
        daily_cost_savings = (daily_corrections_baseline - daily_corrections_current) * operational_cost_per_prediction
        annual_cost_savings = daily_cost_savings * 365
        
        # Revenue impact: better predictions lead to better pricing, more satisfied customers
        revenue_per_prediction = 15  # Average fare
        conversion_improvement = 0.03  # 3% improvement in customer satisfaction/retention
        daily_revenue_lift = daily_predictions * revenue_per_prediction * conversion_improvement
        annual_revenue_lift = daily_revenue_lift * 365
        
        # ROI calculation
        annual_model_cost = daily_predictions * operational_cost_per_prediction * 365
        total_value = annual_cost_savings + annual_revenue_lift
        roi_pct = (total_value / annual_model_cost) * 100 if annual_model_cost > 0 else 0
        
        return {
            'accuracy_improvement_pct': accuracy_improvement,
            'daily_cost_savings': daily_cost_savings,
            'annual_cost_savings': annual_cost_savings,
            'daily_revenue_lift': daily_revenue_lift,
            'annual_revenue_lift': annual_revenue_lift,
            'annual_model_cost': annual_model_cost,
            'total_annual_value': total_value,
            'roi_pct': roi_pct,
        }
    
    def get_prometheus_metrics(self, kpis: Dict[str, FarePredictionKPI]) -> Dict[str, float]:
        """
        Convert KPIs to Prometheus metrics format.
        
        Returns:
            Dict of metric_name -> value
        """
        metrics = {}
        
        # Overall metrics (aggregated across all boroughs)
        if kpis:
            avg_accuracy = np.mean([kpi.accuracy for kpi in kpis.values()])
            avg_mae = np.mean([kpi.mae for kpi in kpis.values()])
            total_predictions = sum([kpi.prediction_count for kpi in kpis.values()])
            total_revenue_impact = sum([kpi.revenue_impact for kpi in kpis.values()])
            
            metrics['taxi_model_accuracy'] = avg_accuracy
            metrics['taxi_model_mae'] = avg_mae
            metrics['taxi_predictions_total'] = total_predictions
            metrics['taxi_revenue_impact'] = total_revenue_impact
            
            # Per-borough metrics
            for borough, kpi in kpis.items():
                borough_label = borough.lower().replace(' ', '_')
                metrics[f'taxi_accuracy_borough_{borough_label}'] = kpi.accuracy
                metrics[f'taxi_mae_borough_{borough_label}'] = kpi.mae
                metrics[f'taxi_inference_time_ms_borough_{borough_label}'] = kpi.avg_prediction_time_ms
        
        return metrics
    
    def generate_kpi_report(self, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict:
        """
        Generate comprehensive KPI report.
        
        Args:
            start_date: Report start date (default: lookback_hours ago)
            end_date: Report end date (default: now)
            
        Returns:
            Dict with detailed KPI report
        """
        if not self.metrics_history:
            return {'error': 'No metrics history available'}
        
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(hours=self.lookback_hours)
        
        # Filter metrics in time range
        recent_metrics = [m for m in self.metrics_history 
                         if datetime.fromisoformat(m.timestamp) >= start_date]
        
        if not recent_metrics:
            return {'error': 'No metrics in specified time range'}
        
        # Aggregate metrics
        report = {
            'report_generated': datetime.utcnow().isoformat(),
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'metrics_count': len(recent_metrics),
            'summary': {
                'avg_accuracy': np.mean([m.accuracy for m in recent_metrics]),
                'min_accuracy': np.min([m.accuracy for m in recent_metrics]),
                'max_accuracy': np.max([m.accuracy for m in recent_metrics]),
                'avg_mae': np.mean([m.mae for m in recent_metrics]),
                'avg_mape': np.mean([m.mape for m in recent_metrics]),
                'avg_inference_time_ms': np.mean([m.avg_prediction_time_ms for m in recent_metrics]),
                'total_predictions': sum([m.prediction_count for m in recent_metrics]),
                'total_revenue_impact': sum([m.revenue_impact for m in recent_metrics]),
            },
            'by_borough': {}
        }
        
        # Borough breakdown
        for borough in self.boroughs:
            borough_metrics = [m for m in recent_metrics if m.borough == borough]
            if borough_metrics:
                report['by_borough'][borough] = {
                    'avg_accuracy': np.mean([m.accuracy for m in borough_metrics]),
                    'avg_mae': np.mean([m.mae for m in borough_metrics]),
                    'prediction_count': sum([m.prediction_count for m in borough_metrics]),
                    'revenue_impact': sum([m.revenue_impact for m in borough_metrics]),
                }
        
        return report
