"""MLflow Model Registry management for production deployment."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import mlflow

from src.utils.config import MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI, MODEL_DIR
from src.utils.logger import logger


class ModelRegistry:
    """Manage model registration, versioning, and staging in MLflow Model Registry."""

    def __init__(self, use_mlflow: bool = True):
        """
        Initialize model registry manager.

        Args:
            use_mlflow: Whether to use MLflow for registration
        """
        self.use_mlflow = use_mlflow
        self.registered_models = {}
        self.model_versions = {}

        if self.use_mlflow:
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
            logger.info(f"[REGISTRY] Initialized with MLflow: {MLFLOW_TRACKING_URI}")

    def register_model(
        self,
        model_name: str,
        model_uri: str,
        description: str = None,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Register a model in MLflow Model Registry.

        Args:
            model_name: Name of the model (e.g., 'taxi-fare-xgboost')
            model_uri: URI to the model artifact (e.g., 'runs:/run_id/model')
            description: Model description
            metadata: Additional metadata

        Returns:
            Registration details
        """
        logger.info(f"[REGISTRY] Registering model: {model_name}")

        try:
            if self.use_mlflow:
                # Register model
                model_version = mlflow.register_model(model_uri, model_name)
                version_number = model_version.version

                logger.info(f"[REGISTRY] Model registered: {model_name} v{version_number}")

                # Update registration info
                registration_info = {
                    "model_name": model_name,
                    "version": version_number,
                    "uri": model_uri,
                    "description": description,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat(),
                    "status": "Registered",
                }

                self.registered_models[model_name] = registration_info
                self.model_versions[f"{model_name}@v{version_number}"] = registration_info

                return registration_info
            else:
                logger.warning("[REGISTRY] MLflow disabled, skipping registration")
                return {}

        except Exception as e:
            logger.error(f"[REGISTRY] Error registering model {model_name}: {e}")
            raise

    def set_model_alias(self, model_name: str, alias: str, version: int) -> Dict[str, Any]:
        """
        Set an alias for a specific model version.

        Args:
            model_name: Name of the registered model
            alias: Alias name (e.g., 'production', 'staging')
            version: Model version number

        Returns:
            Alias details
        """
        logger.info(f"[REGISTRY] Setting alias '{alias}' for {model_name}@v{version}")

        try:
            if self.use_mlflow:
                from mlflow.tracking import MlflowClient

                client = MlflowClient()

                # Set alias
                client.set_registered_model_alias(model_name, alias, version)

                logger.info(f"[REGISTRY] Alias set: {model_name}@{alias} -> v{version}")

                alias_info = {
                    "model_name": model_name,
                    "alias": alias,
                    "version": version,
                    "timestamp": datetime.now().isoformat(),
                }

                return alias_info
            else:
                logger.warning("[REGISTRY] MLflow disabled, skipping alias")
                return {}

        except Exception as e:
            logger.error(f"[REGISTRY] Error setting alias: {e}")
            raise

    def transition_stage(self, model_name: str, version: int, stage: str) -> Dict[str, Any]:
        """
        Transition a model version to a new stage.

        Args:
            model_name: Name of the registered model
            version: Model version number
            stage: Target stage ('None', 'Staging', 'Production', 'Archived')

        Returns:
            Stage transition details
        """
        valid_stages = ["None", "Staging", "Production", "Archived"]
        if stage not in valid_stages:
            raise ValueError(f"Invalid stage {stage}. Must be one of {valid_stages}")

        logger.info(f"[REGISTRY] Transitioning {model_name}@v{version} to stage: {stage}")

        try:
            if self.use_mlflow:
                client = mlflow.tracking.MlflowClient()

                # Transition stage
                client.transition_model_version_stage(model_name, version, stage)

                logger.info(f"[REGISTRY] Stage transitioned: {model_name}@v{version} -> {stage}")

                transition_info = {
                    "model_name": model_name,
                    "version": version,
                    "stage": stage,
                    "timestamp": datetime.now().isoformat(),
                }

                return transition_info
            else:
                logger.warning("[REGISTRY] MLflow disabled, skipping stage transition")
                return {}

        except Exception as e:
            logger.error(f"[REGISTRY] Error transitioning stage: {e}")
            raise

    def update_model_description(self, model_name: str, description: str) -> Dict[str, Any]:
        """
        Update the description of a registered model.

        Args:
            model_name: Name of the registered model
            description: New description

        Returns:
            Update details
        """
        logger.info(f"[REGISTRY] Updating description for {model_name}")

        try:
            if self.use_mlflow:
                client = mlflow.tracking.MlflowClient()
                client.update_registered_model(model_name, description)

                logger.info(f"[REGISTRY] Description updated for {model_name}")

                return {
                    "model_name": model_name,
                    "description": description,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                logger.warning("[REGISTRY] MLflow disabled, skipping update")
                return {}

        except Exception as e:
            logger.error(f"[REGISTRY] Error updating description: {e}")
            raise

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a registered model.

        Args:
            model_name: Name of the registered model

        Returns:
            Model information
        """
        logger.info(f"[REGISTRY] Retrieving info for {model_name}")

        try:
            if self.use_mlflow:
                client = mlflow.tracking.MlflowClient()
                model = client.get_registered_model(model_name)

                model_info = {
                    "name": model.name,
                    "creation_timestamp": model.creation_timestamp,
                    "last_updated_timestamp": model.last_updated_timestamp,
                    "description": model.description,
                    "latest_versions": [],
                }

                # Get latest versions
                for version in model.latest_versions:
                    model_info["latest_versions"].append(
                        {
                            "version": version.version,
                            "stage": version.current_stage,
                            "run_id": version.run_id,
                            "source": version.source,
                        }
                    )

                logger.info(f"[REGISTRY] Retrieved info for {model_name}")
                return model_info
            else:
                logger.warning("[REGISTRY] MLflow disabled, cannot retrieve info")
                return {}

        except Exception as e:
            logger.error(f"[REGISTRY] Error retrieving model info: {e}")
            raise

    def list_registered_models(self) -> List[str]:
        """
        List all registered models.

        Returns:
            List of model names
        """
        logger.info("[REGISTRY] Listing all registered models")

        try:
            if self.use_mlflow:
                client = mlflow.tracking.MlflowClient()
                models = client.search_registered_models()

                model_list = [model.name for model in models]
                logger.info(f"[REGISTRY] Found {len(model_list)} registered models")
                return model_list
            else:
                logger.warning("[REGISTRY] MLflow disabled, cannot list models")
                return []

        except Exception as e:
            logger.error(f"[REGISTRY] Error listing models: {e}")
            return []

    def get_production_model(self, model_name: str) -> Dict[str, Any]:
        """
        Get the production stage model.

        Args:
            model_name: Name of the registered model

        Returns:
            Production model information
        """
        logger.info(f"[REGISTRY] Retrieving production model for {model_name}")

        try:
            if self.use_mlflow:
                client = mlflow.tracking.MlflowClient()
                model = client.get_registered_model(model_name)

                # Find production version
                for version in model.latest_versions:
                    if version.current_stage == "Production":
                        production_info = {
                            "model_name": model_name,
                            "version": version.version,
                            "stage": "Production",
                            "run_id": version.run_id,
                            "source": version.source,
                            "created_timestamp": version.creation_timestamp,
                        }
                        logger.info(f"[REGISTRY] Production model: {model_name}@v{version.version}")
                        return production_info

                logger.warning(f"[REGISTRY] No production model found for {model_name}")
                return {}
            else:
                logger.warning("[REGISTRY] MLflow disabled")
                return {}

        except Exception as e:
            logger.error(f"[REGISTRY] Error retrieving production model: {e}")
            return {}

    def save_registry_summary(self, output_path: Path = None) -> Path:
        """
        Save a summary of the model registry.

        Args:
            output_path: Path to save summary JSON

        Returns:
            Path to saved summary
        """
        if output_path is None:
            output_path = MODEL_DIR / "model_registry_summary.json"

        logger.info(f"[REGISTRY] Saving registry summary to {output_path}")

        summary = {
            "timestamp": datetime.now().isoformat(),
            "registered_models": self.registered_models,
            "model_versions": self.model_versions,
            "total_models": len(self.registered_models),
            "total_versions": len(self.model_versions),
        }

        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"[REGISTRY] Registry summary saved: {output_path}")
        return output_path


def setup_production_models(
    tuning_results_path: Path = None, use_mlflow: bool = True
) -> Dict[str, Any]:
    """
    Setup production models from tuning results.
    Uses the latest Hyperparameter-Tuning run data from MLflow.

    Args:
        tuning_results_path: Path to tuning results JSON
        use_mlflow: Whether to use MLflow

    Returns:
        Setup results
    """
    logger.info("[DAY7] Setting up production models...")

    if tuning_results_path is None:
        tuning_results_path = MODEL_DIR / "tuning_comparison.json"

    # Load tuning results
    if not tuning_results_path.exists():
        logger.warning(f"Tuning results not found at {tuning_results_path}")
        return {}

    with open(tuning_results_path, "r") as f:
        tuning_results = json.load(f)

    registry = ModelRegistry(use_mlflow=use_mlflow)
    setup_results = {}

    if not use_mlflow:
        logger.warning("[DAY7] MLflow disabled, skipping model registration")
        return setup_results

    # Get latest tuning runs from MLflow
    try:
        from mlflow.tracking import MlflowClient

        client = MlflowClient()

        # Get the latest Hyperparameter-Tuning run
        experiment = client.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
        if not experiment:
            logger.warning(f"[DAY7] Experiment {MLFLOW_EXPERIMENT_NAME} not found")
            return {}

        # Search for tuning runs
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="tags.`mlflow.runName` LIKE 'Hyperparameter-Tuning'",
            order_by=["start_time DESC"],
            max_results=1,
        )

        if not runs:
            logger.warning("[DAY7] No Hyperparameter-Tuning run found")
            return {}

        tuning_parent_run = runs[0]
        tuning_run_id = tuning_parent_run.info.run_id
        logger.info(f"[DAY7] Found latest tuning run: {tuning_run_id}")

        # Register each model with its run
        for model_name in ["SVM", "XGBoost", "LightGBM"]:
            if model_name in tuning_results:
                result = tuning_results[model_name]

                # Use runs:/ URI format pointing to the tuning run
                model_uri = f"runs:/{tuning_run_id}/models/{model_name.lower()}_model"

                # Prepare metadata
                metadata = {
                    "test_r2": result.get("tuned_r2"),
                    "test_rmse": result.get("tuned_metrics", {}).get("rmse"),
                    "test_mae": result.get("tuned_metrics", {}).get("mae"),
                    "improvement_pct": result.get("improvement_pct"),
                    "model_type": model_name,
                    "training_date": datetime.now().isoformat(),
                }

                # Register model
                try:
                    reg_result = registry.register_model(
                        model_name=f"taxi-fare-{model_name.lower()}",
                        model_uri=model_uri,
                        description=f"Tuned {model_name} model for taxi fare prediction (R²={metadata['test_r2']:.4f})",
                        metadata=metadata,
                    )
                    setup_results[model_name] = reg_result
                    logger.info(f"[DAY7] Registered: {model_name}")
                except Exception as e:
                    logger.warning(f"[DAY7] Could not register {model_name}: {str(e)[:100]}")

        # Set aliases for registered models
        if "XGBoost" in setup_results and setup_results["XGBoost"]:
            try:
                version = setup_results["XGBoost"].get("version", 1)
                registry.set_model_alias("taxi-fare-xgboost", "production", version)
                logger.info(f"[DAY7] Set XGBoost v{version} as production model")
            except Exception as e:
                logger.warning(f"[DAY7] Could not set XGBoost alias: {str(e)[:100]}")

        if "LightGBM" in setup_results and setup_results["LightGBM"]:
            try:
                version = setup_results["LightGBM"].get("version", 1)
                registry.set_model_alias("taxi-fare-lightgbm", "staging", version)
                logger.info(f"[DAY7] Set LightGBM v{version} as staging model")
            except Exception as e:
                logger.warning(f"[DAY7] Could not set LightGBM alias: {str(e)[:100]}")

    except Exception as e:
        logger.error(f"[DAY7] Error in model registration: {str(e)[:100]}")

    # Save summary
    registry.save_registry_summary()

    logger.info("[DAY7] Production models setup complete!")
    return setup_results
