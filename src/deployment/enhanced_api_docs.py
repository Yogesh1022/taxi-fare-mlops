"""
Enhanced API Documentation

ExtendedFastAPI documentation with:
1. Custom OpenAPI schema
2. Interactive webhook documentation
3. Example requests/responses
4. Error code glossary
5. API versioning helpers

Author: MLOps Team
Date: 2026-04-08
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class OpenAPISchemaCustomizer:
    """
    Customize FastAPI OpenAPI schema for better documentation.

    Features:
    - Custom tags and descriptions
    - Example payloads and responses
    - Error code documentation
    - Security scheme documentation
    """

    def __init__(self, app_title: str = "Taxi Fare Prediction API"):
        """Initialize customizer."""
        self.app_title = app_title
        self.schema = {}
        self.examples = {}
        self.error_codes = {}
        logger.info(f"[API_DOCS] OpenAPISchemaCustomizer initialized for {app_title}")

    def add_tag(self, name: str, description: str, external_docs: Optional[Dict[str, str]] = None):
        """Add custom tag to API."""
        if "tags" not in self.schema:
            self.schema["tags"] = []

        tag = {"name": name, "description": description}

        if external_docs:
            tag["externalDocs"] = external_docs

        self.schema["tags"].append(tag)
        logger.info(f"[API_DOCS] Tag added: {name}")

    def add_error_code(
        self, code: int, name: str, description: str, example_response: Dict[str, Any]
    ):
        """Add error code documentation."""
        self.error_codes[code] = {
            "name": name,
            "description": description,
            "example": example_response,
        }
        logger.info(f"[API_DOCS] Error code added: {code} ({name})")

    def add_example_request_response(
        self,
        endpoint: str,
        method: str,
        request_example: Dict[str, Any],
        response_example: Dict[str, Any],
    ):
        """Add example request/response for endpoint."""
        key = f"{method.upper()} {endpoint}"
        self.examples[key] = {"request": request_example, "response": response_example}
        logger.info(f"[API_DOCS] Example added: {key}")

    def generate_custom_schema(self) -> Dict[str, Any]:
        """Generate customized OpenAPI schema."""
        openapi_schema = {
            "openapi": "3.0.2",
            "info": {
                "title": self.app_title,
                "version": "2.0.0",
                "description": "Advanced taxi fare prediction API with real-time inference, batch processing, and model monitoring.",
                "contact": {
                    "name": "MLOps Team",
                    "url": "https://github.com/your-org/taxi-fare-prediction",
                },
                "license": {"name": "MIT"},
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "Development server"},
                {"url": "https://api.taxi-fare.com", "description": "Production server"},
            ],
            "tags": self.schema.get("tags", []),
        }

        self.schema = openapi_schema
        return openapi_schema


class APIEndpointDocumenter:
    """Document API endpoints with schemas and examples."""

    def __init__(self):
        """Initialize documenter."""
        self.endpoints = {}
        logger.info("[API_DOCS] APIEndpointDocumenter initialized")

    def document_endpoint(
        self,
        path: str,
        method: str,
        summary: str,
        description: str,
        tags: List[str],
        request_schema: Dict[str, Any],
        response_schema: Dict[str, Any],
        parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Document an API endpoint."""
        key = f"{method.upper()} {path}"

        endpoint_doc = {
            "path": path,
            "method": method.upper(),
            "summary": summary,
            "description": description,
            "tags": tags,
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": request_schema}},
            },
            "responses": {
                "200": {
                    "description": "Successful inference",
                    "content": {"application/json": {"schema": response_schema}},
                },
                "400": {"description": "Invalid input"},
                "500": {"description": "Server error"},
            },
        }

        if parameters:
            endpoint_doc["parameters"] = parameters

        self.endpoints[key] = endpoint_doc
        logger.info(f"[API_DOCS] Endpoint documented: {key}")

        return endpoint_doc

    def get_documentation(self) -> Dict[str, Any]:
        """Get all endpoint documentation."""
        return self.endpoints


class ErrorCodeDocumentation:
    """Complete error code documentation."""

    ERROR_CODES = {
        400: {
            "name": "Bad Request",
            "description": "Invalid input parameters",
            "examples": {
                "missing_field": {
                    "error": "Missing required field: trip_distance",
                    "code": "MISSING_FIELD",
                },
                "invalid_type": {"error": "fare_amount must be a number", "code": "INVALID_TYPE"},
                "invalid_range": {
                    "error": "trip_distance must be between 0.1 and 50",
                    "code": "INVALID_RANGE",
                },
            },
        },
        401: {
            "name": "Unauthorized",
            "description": "Invalid or missing API key",
            "examples": {
                "missing_auth": {"error": "API key is missing", "code": "MISSING_AUTH"},
                "invalid_auth": {"error": "Invalid API key provided", "code": "INVALID_AUTH"},
            },
        },
        403: {
            "name": "Forbidden",
            "description": "Insufficient permissions",
            "examples": {
                "insufficient_plan": {
                    "error": "API limit exceeded for your plan",
                    "code": "INSUFFICIENT_PLAN",
                }
            },
        },
        404: {
            "name": "Not Found",
            "description": "Resource not found",
            "examples": {
                "model_not_found": {
                    "error": "Model version 1.0.0 not found",
                    "code": "MODEL_NOT_FOUND",
                }
            },
        },
        422: {
            "name": "Validation Error",
            "description": "Request validation failed",
            "examples": {
                "validation_error": {
                    "detail": [
                        {
                            "loc": ["body", "fare_amount"],
                            "msg": "ensure this value is greater than 2.5",
                            "type": "value_error",
                        }
                    ]
                }
            },
        },
        429: {
            "name": "Too Many Requests",
            "description": "Rate limit exceeded",
            "examples": {
                "rate_limit": {
                    "error": "Rate limit exceeded: 100 requests per minute",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "retry_after_seconds": 60,
                }
            },
        },
        500: {
            "name": "Internal Server Error",
            "description": "Server error during processing",
            "examples": {
                "model_error": {
                    "error": "Model inference failed",
                    "code": "MODEL_ERROR",
                    "request_id": "req_123456789",
                }
            },
        },
        503: {
            "name": "Service Unavailable",
            "description": "Service is temporarily unavailable",
            "examples": {
                "maintenance": {
                    "error": "Service undergoing maintenance",
                    "code": "SERVICE_MAINTENANCE",
                    "estimated_downtime_minutes": 30,
                }
            },
        },
    }

    @classmethod
    def get_status_code_docs(cls) -> Dict[str, Any]:
        """Get documentation for all HTTP status codes."""
        return cls.ERROR_CODES

    @classmethod
    def get_error_code_doc(cls, status_code: int) -> Optional[Dict[str, Any]]:
        """Get documentation for specific status code."""
        return cls.ERROR_CODES.get(status_code)


class RequestResponseExamples:
    """Request and response examples for common scenarios."""

    # Prediction Request/Response
    PREDICT_REQUEST = {
        "task_id": "task_12345",
        "trip_distance": 3.5,
        "passenger_count": 2,
        "pickup_hour": 14,
        "pickup_day": 3,
        "month": 6,
        "vendor_id": 2,
        "payment_type": 1,
    }

    PREDICT_RESPONSE = {
        "task_id": "task_12345",
        "prediction": 15.75,
        "confidence_interval": {"lower": 14.20, "upper": 17.30},
        "model_version": "2.1.0",
        "model_type": "xgboost",
        "inference_time_ms": 12.5,
        "timestamp": "2023-06-15T14:30:00.123Z",
    }

    # Batch Prediction Request/Response
    BATCH_PREDICT_REQUEST = {
        "batch_id": "batch_98765",
        "predictions": [
            {"trip_distance": 2.5, "passenger_count": 1, "pickup_hour": 9},
            {"trip_distance": 5.0, "passenger_count": 3, "pickup_hour": 19},
        ],
    }

    BATCH_PREDICT_RESPONSE = {
        "batch_id": "batch_98765",
        "predictions": [{"prediction": 12.50, "id": 0}, {"prediction": 18.75, "id": 1}],
        "total_processed": 2,
        "total_failed": 0,
        "batch_inference_time_ms": 45.0,
    }

    # Model Info Request/Response
    MODEL_INFO_RESPONSE = {
        "model_id": "taxi_fare_v2.1.0",
        "model_name": "Taxi Fare Prediction",
        "version": "2.1.0",
        "model_type": "xgboost",
        "created_date": "2023-05-15",
        "updated_date": "2023-06-10",
        "status": "active",
        "performance": {"r2_score": 0.875, "mae": 1.25, "rmse": 2.10},
        "features": ["trip_distance", "passenger_count", "pickup_hour", "day_of_week", "month"],
        "input_schema": {"trip_distance": "float", "passenger_count": "int", "pickup_hour": "int"},
    }

    # Explanation Request/Response
    EXPLAIN_REQUEST = {"prediction_id": "pred_789456", "trip_distance": 3.5, "passenger_count": 2}

    EXPLAIN_RESPONSE = {
        "prediction_id": "pred_789456",
        "prediction": 15.75,
        "feature_importance": {
            "trip_distance": 0.65,
            "passenger_count": 0.15,
            "pickup_hour": 0.12,
            "day_of_week": 0.03,
            "other": 0.05,
        },
        "shap_values": {"trip_distance": 5.2, "passenger_count": 2.1, "pickup_hour": 1.5},
        "force_plot_url": "/api/v2/explain/pred_789456/force_plot",
    }

    @classmethod
    def get_example(cls, endpoint: str, example_type: str = "basic") -> Dict[str, Any]:
        """Get example for endpoint."""
        examples_map = {
            "/predict": {"request": cls.PREDICT_REQUEST, "response": cls.PREDICT_RESPONSE},
            "/predict/batch": {
                "request": cls.BATCH_PREDICT_REQUEST,
                "response": cls.BATCH_PREDICT_RESPONSE,
            },
            "/models/info": {"response": cls.MODEL_INFO_RESPONSE},
            "/explain": {"request": cls.EXPLAIN_REQUEST, "response": cls.EXPLAIN_RESPONSE},
        }

        return examples_map.get(endpoint, {})


class WebhookDocumentation:
    """Document webhook events and payloads."""

    WEBHOOK_EVENTS = {
        "model.trained": {
            "name": "Model Trained",
            "description": "Triggered when a new model is trained and deployed",
            "payload": {
                "event_type": "model.trained",
                "timestamp": "2023-06-15T14:30:00Z",
                "model_id": "taxi_fare_v2.2.0",
                "model_version": "2.2.0",
                "performance": {"r2_score": 0.876, "mae": 1.24},
            },
        },
        "model.drift_detected": {
            "name": "Data Drift Detected",
            "description": "Triggered when significant data drift is detected",
            "payload": {
                "event_type": "model.drift_detected",
                "timestamp": "2023-06-15T15:45:00Z",
                "drift_score": 0.28,
                "threshold": 0.25,
                "affected_features": ["trip_distance", "pickup_hour"],
            },
        },
        "prediction.latency_alert": {
            "name": "Latency Alert",
            "description": "Triggered when prediction latency exceeds threshold",
            "payload": {
                "event_type": "prediction.latency_alert",
                "timestamp": "2023-06-15T14:35:00Z",
                "latency_ms": 850,
                "threshold_ms": 500,
                "severity": "warning",
            },
        },
        "model.error_rate_high": {
            "name": "High Error Rate",
            "description": "Triggered when error rate exceeds threshold",
            "payload": {
                "event_type": "model.error_rate_high",
                "timestamp": "2023-06-15T14:40:00Z",
                "error_rate_pct": 5.5,
                "threshold_pct": 5.0,
                "error_count": 55,
                "total_predictions": 1000,
            },
        },
    }

    @classmethod
    def get_webhook_documentation(cls) -> Dict[str, Any]:
        """Get webhook documentation."""
        return {
            "webhooks": cls.WEBHOOK_EVENTS,
            "delivery_method": "HTTP POST",
            "retry_policy": {
                "max_attempts": 5,
                "backoff_strategy": "exponential",
                "initial_delay_seconds": 1,
            },
            "authentication": {
                "method": "HMAC-SHA256",
                "header": "X-Webhook-Signature",
                "secret_header": "X-Webhook-Secret",  # nosec B105
            },
            "testing": {
                "webhook_url": "/webhooks/test",
                "sample_events_url": "/api/docs/webhook-samples",
            },
        }


class APIDocumentationGenerator:
    """Generate comprehensive API documentation."""

    @staticmethod
    def generate_complete_documentation() -> Dict[str, Any]:
        """Generate complete API documentation."""
        logger.info("[API_DOCS] Generating complete API documentation...")

        schema_customizer = OpenAPISchemaCustomizer()

        # Add tags
        schema_customizer.add_tag(
            "Predictions",
            "Make single and batch predictions for taxi fares",
            {"url": "https://github.com/your-org/docs/predictions"},
        )
        schema_customizer.add_tag("Model Management", "Get model information and status")
        schema_customizer.add_tag("Explainability", "Get model predictions explanations using SHAP")
        schema_customizer.add_tag("Monitoring", "Model performance and system metrics")

        documentation = {
            "timestamp": datetime.now().isoformat(),
            "openapi_schema": schema_customizer.generate_custom_schema(),
            "error_codes": ErrorCodeDocumentation.get_status_code_docs(),
            "examples": {
                "/predict": RequestResponseExamples.get_example("/predict"),
                "/predict/batch": RequestResponseExamples.get_example("/predict/batch"),
                "/models/info": RequestResponseExamples.get_example("/models/info"),
                "/explain": RequestResponseExamples.get_example("/explain"),
            },
            "webhooks": WebhookDocumentation.get_webhook_documentation(),
        }

        logger.info("[API_DOCS] Documentation generation complete")

        return documentation

    @staticmethod
    def save_documentation(output_dir: str = "mlops/api_docs") -> str:
        """Save API documentation to file."""
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        docs = APIDocumentationGenerator.generate_complete_documentation()

        # Save as JSON
        json_file = output_path / "api_documentation.json"
        with open(json_file, "w") as f:
            json.dump(docs, f, indent=2)

        logger.info(f"[API_DOCS] JSON documentation saved to {json_file}")

        # Save as markdown
        APIDocumentationGenerator._save_markdown_documentation(output_path, docs)

        return str(json_file)

    @staticmethod
    def _save_markdown_documentation(output_path: Path, docs: Dict[str, Any]):
        """Save API documentation as markdown."""
        md_content = """# Taxi Fare Prediction API - Complete Documentation

## Overview

Comprehensive REST API for taxi fare prediction with real-time inference, batch processing, model monitoring, and explainability.

**Base URL**: `https://api.taxi-fare.com`  
**API Version**: 2.0.0

## Error Codes

"""

        for code, info in docs.get("error_codes", {}).items():
            md_content += f"### {code} - {info['name']}\n"
            md_content += f"{info['description']}\n\n"

        md_content += "\n## Endpoints\n\n"

        for endpoint, example in docs.get("examples", {}).items():
            md_content += f"### {endpoint}\n\n"
            md_content += "**Request**:\n```json\n"
            md_content += json.dumps(example.get("request", {}), indent=2)
            md_content += "\n```\n\n"
            md_content += "**Response**:\n```json\n"
            md_content += json.dumps(example.get("response", {}), indent=2)
            md_content += "\n```\n\n"

        md_content += "\n## Webhooks\n\n"
        webhooks = docs.get("webhooks", {})
        md_content += f"Webhook events are sent as POST requests to your registered endpoints.\n\n"

        for event_name, event_info in webhooks.get("webhooks", {}).items():
            md_content += f"### {event_info['name']}\n"
            md_content += f"{event_info['description']}\n\n"

        md_file = output_path / "API_DOCUMENTATION.md"
        with open(md_file, "w") as f:
            f.write(md_content)

        logger.info(f"[API_DOCS] Markdown documentation saved to {md_file}")
