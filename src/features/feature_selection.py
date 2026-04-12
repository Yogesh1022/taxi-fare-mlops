"""
Advanced Feature Selection Techniques

Implements multiple feature selection strategies:
1. Recursive Feature Elimination (RFE)
2. L1-based Feature Selection (Lasso)
3. Feature Importance-based Selection
4. Correlation-based Feature Selection
5. Combined ensemble voting

Author: MLOps Team
Date: 2026-04-08
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.feature_selection import RFE, SelectFromModel, mutual_info_regression
from sklearn.lightgbm import LGBMRegressor
from sklearn.linear_model import LassoCV, LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.xgboost import XGBRegressor

logger = logging.getLogger(__name__)


class FeatureSelector:
    """
    Advanced feature selection with multiple strategies.

    Strategies:
    1. RFE (Recursive Feature Elimination) - Iteratively removes features
    2. L1 (Lasso) - Zeros out less important features
    3. Tree-based Importance - Uses model importance scores
    4. Correlation-based - Removes highly correlated features
    5. Mutual Information - Measures feature-target dependency
    6. Ensemble - Voting from multiple methods
    """

    def __init__(self, feature_names: List[str] = None):
        """
        Initialize feature selector.

        Args:
            feature_names: List of feature names
        """
        self.feature_names = feature_names
        self.selection_results = {}
        self.selected_features = {}
        self.importance_scores = {}
        logger.info("[SELECTION] FeatureSelector initialized")

    def _set_feature_names(self, n_features: int):
        """Set default feature names if not provided."""
        if self.feature_names is None:
            self.feature_names = [f"feature_{i}" for i in range(n_features)]

    def select_rfe(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        n_features: int = None,
        estimator_name: str = "svm",
    ) -> Dict[str, Any]:
        """
        Recursive Feature Elimination (RFE).

        Recursively removes features and trains model until desired number remains.

        Args:
            X_train: Training features
            y_train: Training target
            n_features: Number of features to select (default: sqrt(n_features))
            estimator_name: Estimator to use for RFE

        Returns:
            Dictionary with selected features and scores
        """
        logger.info("[SELECTION] Starting RFE feature selection...")

        self._set_feature_names(X_train.shape[1])

        if n_features is None:
            n_features = int(np.sqrt(X_train.shape[1]))

        # Estimator for RFE
        if estimator_name == "svm":
            estimator = SVR(kernel="rbf", C=100)
        elif estimator_name == "xgboost":
            estimator = XGBRegressor(n_estimators=100, max_depth=7, random_state=42)
        else:
            estimator = LGBMRegressor(n_estimators=100, max_depth=7, random_state=42)

        logger.info(f"[SELECTION] RFE with {estimator_name}, selecting {n_features} features")

        rfe = RFE(estimator=estimator, n_features_to_select=n_features, step=1)
        rfe.fit(X_train, y_train)

        # Get selected features
        selected_mask = rfe.support_
        selected_features = [
            self.feature_names[i] for i in range(len(self.feature_names)) if selected_mask[i]
        ]

        # Compute cross-validation score with selected features
        cv_score = cross_val_score(
            estimator, X_train[:, selected_mask], y_train, cv=5, scoring="r2"
        ).mean()

        result = {
            "selected_features": selected_features,
            "n_features_selected": len(selected_features),
            "cv_r2_score": cv_score,
            "feature_ranking": rfe.ranking_,
        }

        self.selection_results["rfe"] = result
        self.selected_features["rfe"] = selected_features

        logger.info(f"[SELECTION] RFE selected {len(selected_features)} features")
        logger.info(f"[SELECTION] RFE CV R² Score: {cv_score:.4f}")

        return result

    def select_lasso(
        self, X_train: np.ndarray, y_train: np.ndarray, threshold: float = 0.01
    ) -> Dict[str, Any]:
        """
        L1-based Feature Selection (Lasso).

        Uses LassoCV to select features with non-zero coefficients.

        Args:
            X_train: Training features
            y_train: Training target
            threshold: Minimum coefficient magnitude to select feature

        Returns:
            Dictionary with selected features and scores
        """
        logger.info("[SELECTION] Starting Lasso feature selection...")

        self._set_feature_names(X_train.shape[1])

        # Standardize features (required for Lasso)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)

        # LassoCV to find optimal alpha
        lasso = LassoCV(cv=5, random_state=42, max_iter=10000)
        lasso.fit(X_scaled, y_train)

        logger.info(f"[SELECTION] Optimal Lasso alpha: {lasso.alpha_:.4f}")

        # Get features with non-zero coefficients
        coef_mask = np.abs(lasso.coef_) > threshold
        selected_features = [
            self.feature_names[i] for i in range(len(self.feature_names)) if coef_mask[i]
        ]

        # CV score with selected features
        cv_score = cross_val_score(
            lasso, X_scaled[:, coef_mask], y_train, cv=5, scoring="r2"
        ).mean()

        result = {
            "selected_features": selected_features,
            "n_features_selected": len(selected_features),
            "cv_r2_score": cv_score,
            "coefficients": dict(zip(self.feature_names, lasso.coef_)),
            "alpha": lasso.alpha_,
        }

        self.selection_results["lasso"] = result
        self.selected_features["lasso"] = selected_features

        logger.info(f"[SELECTION] Lasso selected {len(selected_features)} features")
        logger.info(f"[SELECTION] Lasso CV R² Score: {cv_score:.4f}")

        return result

    def select_tree_importance(
        self, X_train: np.ndarray, y_train: np.ndarray, percentile: int = 80
    ) -> Dict[str, Any]:
        """
        Tree-based Feature Importance Selection.

        Uses XGBoost/LightGBM importance scores to select top features.

        Args:
            X_train: Training features
            y_train: Training target
            percentile: Percentile threshold for feature importance

        Returns:
            Dictionary with selected features and scores
        """
        logger.info("[SELECTION] Starting Tree-based Importance selection...")

        self._set_feature_names(X_train.shape[1])

        # Train XGBoost to get feature importance
        xgb = XGBRegressor(n_estimators=100, max_depth=7, random_state=42)
        xgb.fit(X_train, y_train)

        # Get feature importance
        importance = xgb.feature_importances_
        importance_threshold = np.percentile(importance, percentile)

        logger.info(
            f"[SELECTION] Importance threshold (percentile {percentile}): {importance_threshold:.4f}"
        )

        # Select features above threshold
        importance_mask = importance >= importance_threshold
        selected_features = [
            self.feature_names[i] for i in range(len(self.feature_names)) if importance_mask[i]
        ]

        # CV score with selected features
        cv_score = cross_val_score(
            xgb, X_train[:, importance_mask], y_train, cv=5, scoring="r2"
        ).mean()

        # Store importance scores
        for fname, imp in zip(self.feature_names, importance):
            self.importance_scores[fname] = imp

        result = {
            "selected_features": selected_features,
            "n_features_selected": len(selected_features),
            "cv_r2_score": cv_score,
            "importance_scores": dict(zip(self.feature_names, importance.tolist())),
        }

        self.selection_results["tree_importance"] = result
        self.selected_features["tree_importance"] = selected_features

        logger.info(f"[SELECTION] Tree Importance selected {len(selected_features)} features")
        logger.info(f"[SELECTION] Tree Importance CV R² Score: {cv_score:.4f}")

        return result

    def select_correlation_based(
        self, X_train: np.ndarray, y_train: np.ndarray, correlation_threshold: float = 0.95
    ) -> Dict[str, Any]:
        """
        Correlation-based Feature Selection.

        Removes highly correlated features, keeps one from each pair.

        Args:
            X_train: Training features
            y_train: Training target
            correlation_threshold: Threshold for feature correlation

        Returns:
            Dictionary with selected features
        """
        logger.info("[SELECTION] Starting Correlation-based selection...")

        self._set_feature_names(X_train.shape[1])

        # Compute correlation matrix
        df = pd.DataFrame(X_train, columns=self.feature_names)
        corr_matrix = df.corr().abs()

        # Select upper triangle of correlation matrix
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

        # Find features with correlation greater than threshold
        to_drop = [column for column in upper.columns if any(upper[column] > correlation_threshold)]

        selected_features = [f for f in self.feature_names if f not in to_drop]

        # CV score with selected features
        selected_indices = [i for i, f in enumerate(self.feature_names) if f in selected_features]
        X_selected = X_train[:, selected_indices]

        xgb = XGBRegressor(n_estimators=100, max_depth=7, random_state=42)
        cv_score = cross_val_score(xgb, X_selected, y_train, cv=5, scoring="r2").mean()

        result = {
            "selected_features": selected_features,
            "n_features_selected": len(selected_features),
            "cv_r2_score": cv_score,
            "dropped_features": to_drop,
            "correlation_threshold": correlation_threshold,
        }

        self.selection_results["correlation"] = result
        self.selected_features["correlation"] = selected_features

        logger.info(f"[SELECTION] Correlation-based selected {len(selected_features)} features")
        logger.info(f"[SELECTION] Dropped {len(to_drop)} highly correlated features")
        logger.info(f"[SELECTION] CV R² Score: {cv_score:.4f}")

        return result

    def select_mutual_information(
        self, X_train: np.ndarray, y_train: np.ndarray, n_features: int = None
    ) -> Dict[str, Any]:
        """
        Mutual Information-based Feature Selection.

        Selects features with highest mutual information with target.

        Args:
            X_train: Training features
            y_train: Training target
            n_features: Number of features to select

        Returns:
            Dictionary with selected features
        """
        logger.info("[SELECTION] Starting Mutual Information selection...")

        self._set_feature_names(X_train.shape[1])

        if n_features is None:
            n_features = int(np.sqrt(X_train.shape[1]))

        # Compute mutual information
        mi = mutual_info_regression(X_train, y_train, random_state=42)

        # Get top features by MI
        top_indices = np.argsort(mi)[-n_features:]
        selected_features = [self.feature_names[i] for i in top_indices]

        # CV score with selected features
        X_selected = X_train[:, top_indices]
        xgb = XGBRegressor(n_estimators=100, max_depth=7, random_state=42)
        cv_score = cross_val_score(xgb, X_selected, y_train, cv=5, scoring="r2").mean()

        result = {
            "selected_features": selected_features,
            "n_features_selected": len(selected_features),
            "cv_r2_score": cv_score,
            "mutual_information_scores": dict(zip(self.feature_names, mi.tolist())),
        }

        self.selection_results["mutual_information"] = result
        self.selected_features["mutual_information"] = selected_features

        logger.info(f"[SELECTION] MI-based selected {len(selected_features)} features")
        logger.info(f"[SELECTION] MI CV R² Score: {cv_score:.4f}")

        return result

    def select_ensemble(
        self, X_train: np.ndarray, y_train: np.ndarray, voting_threshold: int = 3
    ) -> Dict[str, Any]:
        """
        Ensemble Feature Selection using voting.

        Feature is selected if it's chosen by at least voting_threshold methods.

        Args:
            X_train: Training features
            y_train: Training target
            voting_threshold: Minimum votes to select feature

        Returns:
            Dictionary with ensemble-selected features
        """
        logger.info("[SELECTION] Starting Ensemble feature selection...")

        # Run all selection methods
        self.select_rfe(X_train, y_train)
        self.select_lasso(X_train, y_train)
        self.select_tree_importance(X_train, y_train)
        self.select_correlation_based(X_train, y_train)

        # Count votes for each feature
        feature_votes = {}
        for method_name, features in self.selected_features.items():
            for feature in features:
                feature_votes[feature] = feature_votes.get(feature, 0) + 1

        # Select features that meet voting threshold
        ensemble_selected = [
            feature for feature, votes in feature_votes.items() if votes >= voting_threshold
        ]

        # CV score with ensemble-selected features
        selected_indices = [i for i, f in enumerate(self.feature_names) if f in ensemble_selected]
        X_selected = X_train[:, selected_indices]

        xgb = XGBRegressor(n_estimators=100, max_depth=7, random_state=42)
        cv_score = cross_val_score(xgb, X_selected, y_train, cv=5, scoring="r2").mean()

        result = {
            "selected_features": ensemble_selected,
            "n_features_selected": len(ensemble_selected),
            "cv_r2_score": cv_score,
            "feature_votes": feature_votes,
            "voting_threshold": voting_threshold,
        }

        self.selection_results["ensemble"] = result
        self.selected_features["ensemble"] = ensemble_selected

        logger.info(f"[SELECTION] Ensemble selected {len(ensemble_selected)} features")
        logger.info(f"[SELECTION] Ensemble CV R² Score: {cv_score:.4f}")

        return result

    def run_all_methods(
        self, X_train: np.ndarray, y_train: np.ndarray
    ) -> Dict[str, Dict[str, Any]]:
        """
        Run all feature selection methods.

        Args:
            X_train: Training features
            y_train: Training target

        Returns:
            Dictionary with results from all methods
        """
        logger.info("[SELECTION] Running all feature selection methods...")

        results = {}

        logger.info("\n[SELECTION] Method 1: RFE")
        results["rfe"] = self.select_rfe(X_train, y_train)

        logger.info("\n[SELECTION] Method 2: Lasso")
        results["lasso"] = self.select_lasso(X_train, y_train)

        logger.info("\n[SELECTION] Method 3: Tree Importance")
        results["tree_importance"] = self.select_tree_importance(X_train, y_train)

        logger.info("\n[SELECTION] Method 4: Correlation-based")
        results["correlation"] = self.select_correlation_based(X_train, y_train)

        logger.info("\n[SELECTION] Method 5: Mutual Information")
        results["mutual_information"] = self.select_mutual_information(X_train, y_train)

        logger.info("\n[SELECTION] Method 6: Ensemble (Voting)")
        results["ensemble"] = self.select_ensemble(X_train, y_train)

        return results

    def get_best_selection(self) -> Tuple[str, List[str]]:
        """
        Get the best feature selection method by CV R² score.

        Returns:
            Tuple of (method_name, selected_features)
        """
        best_method = max(
            self.selection_results.keys(), key=lambda x: self.selection_results[x]["cv_r2_score"]
        )

        features = self.selected_features[best_method]
        logger.info(f"\n[SELECTION] Best method: {best_method}")
        logger.info(f"[SELECTION] Selected {len(features)} features")

        return best_method, features

    def save_results(self, output_dir: str = "models"):
        """Save feature selection results to JSON."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results_file = output_path / "feature_selection_results.json"

        # Convert results to JSON-serializable format
        results_to_save = {}
        for method, result in self.selection_results.items():
            results_to_save[method] = {
                "selected_features": result["selected_features"],
                "n_features_selected": result["n_features_selected"],
                "cv_r2_score": result["cv_r2_score"],
            }

        with open(results_file, "w") as f:
            json.dump(results_to_save, f, indent=2)

        logger.info(f"[SELECTION] Results saved to {results_file}")

        # Generate summary report
        self._generate_summary_report(output_dir)

    def _generate_summary_report(self, output_dir: str = "models"):
        """Generate feature selection summary report."""
        data = []
        for method, result in self.selection_results.items():
            data.append(
                {
                    "Method": method.replace("_", " ").title(),
                    "Features Selected": result["n_features_selected"],
                    "CV R² Score": f"{result['cv_r2_score']:.4f}",
                }
            )

        df = pd.DataFrame(data).sort_values("CV R² Score", ascending=False)

        report_file = Path(output_dir) / "feature_selection_summary.csv"
        df.to_csv(report_file, index=False)

        logger.info("\n[SELECTION] FEATURE SELECTION SUMMARY")
        logger.info("=" * 80)
        logger.info(df.to_string(index=False))
        logger.info("=" * 80)
