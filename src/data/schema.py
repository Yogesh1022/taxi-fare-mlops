"""Data schema and contracts for taxi fare prediction.

This module defines the expected data structure, types, and validation rules
for all data in the pipeline.
"""

from dataclasses import dataclass
from enum import Enum


class DataType(str, Enum):
    """Supported data types."""

    FLOAT = "float"
    INT = "int"
    STRING = "string"
    DATETIME = "datetime"
    BOOL = "bool"


@dataclass
class ColumnSpec:
    """Specification for a single column."""

    name: str
    dtype: DataType
    nullable: bool = False
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: list | None = None
    description: str = ""


class DataSchema:
    """Define the data contract for taxi fare data."""

    # Input features
    pickup_datetime = ColumnSpec(
        name="tpep_pickup_datetime",
        dtype=DataType.DATETIME,
        nullable=False,
        description="Pickup date and time",
    )

    dropoff_datetime = ColumnSpec(
        name="tpep_dropoff_datetime",
        dtype=DataType.DATETIME,
        nullable=False,
        description="Dropoff date and time",
    )

    passenger_count = ColumnSpec(
        name="passenger_count",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=1.0,
        max_value=6.0,
        description="Number of passengers (1-6)",
    )

    trip_distance = ColumnSpec(
        name="trip_distance",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=0.0,
        max_value=500.0,
        description="Trip distance in miles",
    )

    ratecode_id = ColumnSpec(
        name="RatecodeID",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=1.0,
        max_value=5.0,
        description="Rate code type",
    )

    store_and_fwd_flag = ColumnSpec(
        name="store_and_fwd_flag",
        dtype=DataType.STRING,
        nullable=False,
        allowed_values=["Y", "N"],
        description="Store and forward flag",
    )

    pu_location_id = ColumnSpec(
        name="PULocationID",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=1.0,
        max_value=265.0,
        description="Pickup location ID",
    )

    do_location_id = ColumnSpec(
        name="DOLocationID",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=1.0,
        max_value=265.0,
        description="Dropoff location ID",
    )

    payment_type = ColumnSpec(
        name="payment_type",
        dtype=DataType.STRING,
        nullable=False,
        allowed_values=["Credit Card", "Cash", "other"],
        description="Payment method",
    )

    vendor_id = ColumnSpec(
        name="VendorID",
        dtype=DataType.FLOAT,
        nullable=False,
        allowed_values=[0.0, 1.0],
        description="Taxi vendor ID",
    )

    extra = ColumnSpec(
        name="extra",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=0.0,
        max_value=100.0,
        description="Extra charges",
    )

    tip_amount = ColumnSpec(
        name="tip_amount",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=0.0,
        max_value=200.0,
        description="Tip amount",
    )

    tolls_amount = ColumnSpec(
        name="tolls_amount",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=0.0,
        max_value=100.0,
        description="Tolls paid",
    )

    improvement_surcharge = ColumnSpec(
        name="improvement_surcharge",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=0.0,
        max_value=2.0,
        description="Improvement surcharge",
    )

    congestion_surcharge = ColumnSpec(
        name="congestion_surcharge",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=0.0,
        max_value=5.0,
        description="Congestion surcharge",
    )

    airport_fee = ColumnSpec(
        name="Airport_fee",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=0.0,
        max_value=10.0,
        description="Airport fee",
    )

    # Target variable
    total_amount = ColumnSpec(
        name="total_amount",
        dtype=DataType.FLOAT,
        nullable=False,
        min_value=0.0,
        max_value=500.0,
        description="Total fare amount (TARGET)",
    )

    @classmethod
    def get_input_schema(cls) -> dict[str, ColumnSpec]:
        """Get schema for input features (excluding target)."""
        return {
            "tpep_pickup_datetime": cls.pickup_datetime,
            "tpep_dropoff_datetime": cls.dropoff_datetime,
            "passenger_count": cls.passenger_count,
            "trip_distance": cls.trip_distance,
            "RatecodeID": cls.ratecode_id,
            "store_and_fwd_flag": cls.store_and_fwd_flag,
            "PULocationID": cls.pu_location_id,
            "DOLocationID": cls.do_location_id,
            "payment_type": cls.payment_type,
            "VendorID": cls.vendor_id,
            "extra": cls.extra,
            "tip_amount": cls.tip_amount,
            "tolls_amount": cls.tolls_amount,
            "improvement_surcharge": cls.improvement_surcharge,
            "congestion_surcharge": cls.congestion_surcharge,
            "Airport_fee": cls.airport_fee,
        }

    @classmethod
    def get_full_schema(cls) -> dict[str, ColumnSpec]:
        """Get schema for all columns including target."""
        schema = cls.get_input_schema()
        schema["total_amount"] = cls.total_amount
        return schema

    @classmethod
    def get_required_columns(cls) -> list[str]:
        """Get list of required column names."""
        return list(cls.get_full_schema().keys())

    @classmethod
    def get_numeric_columns(cls) -> list[str]:
        """Get numeric column names."""
        schema = cls.get_full_schema()
        return [
            name for name, spec in schema.items() if spec.dtype in [DataType.FLOAT, DataType.INT]
        ]

    @classmethod
    def get_categorical_columns(cls) -> list[str]:
        """Get categorical column names."""
        schema = cls.get_full_schema()
        return [name for name, spec in schema.items() if spec.dtype == DataType.STRING]

    @classmethod
    def get_datetime_columns(cls) -> list[str]:
        """Get datetime column names."""
        schema = cls.get_full_schema()
        return [name for name, spec in schema.items() if spec.dtype == DataType.DATETIME]


# Critical fields for data drift monitoring
CRITICAL_FIELDS = ["trip_distance", "tip_amount", "total_amount", "fare_amount", "passenger_count"]

# Outlier detection thresholds (as multipliers of IQR)
OUTLIER_IQR_MULTIPLIER = 1.5

# Missing data tolerance (%)
MISSING_DATA_TOLERANCE = 0.05  # 5%
