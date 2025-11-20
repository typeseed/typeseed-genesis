"""
Pydantic models for configuration validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class CLIConfig(BaseModel):
    """
    Configuration model for CLI application.

    This uses Pydantic for automatic validation and serialization.
    """

    task: str = Field(..., description="The task to perform", min_length=1)
    text: Optional[str] = Field(None, description="Input text for processing")
    model_name: Optional[str] = Field("default", description="Model to use")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters"
    )
    verbose: bool = Field(False, description="Enable verbose output")
    output_format: str = Field("json", description="Output format (json, csv, etc.)")

    @field_validator("task")
    @classmethod
    def validate_task(cls, v: str) -> str:
        """Validate that task is not empty and is lowercase."""
        if not v or not v.strip():
            raise ValueError("Task cannot be empty")
        return v.strip().lower()

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """Validate output format."""
        valid_formats = ["json", "csv", "txt", "xml"]
        if v.lower() not in valid_formats:
            raise ValueError(
                f"Output format must be one of: {', '.join(valid_formats)}"
            )
        return v.lower()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task": "sentiment-analysis",
                    "text": "I love this product!",
                    "model_name": "distilbert-base",
                    "parameters": {"max_length": 512},
                    "verbose": False,
                    "output_format": "json",
                }
            ]
        }
    }


class TaskResult(BaseModel):
    """Model for task execution results."""

    task: str
    status: str = Field(..., pattern="^(success|error|pending)$")
    result: Optional[Any] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task": "sentiment-analysis",
                    "status": "success",
                    "result": {"sentiment": "positive", "score": 0.95},
                    "error_message": None,
                    "metadata": {"processing_time": 0.42},
                }
            ]
        }
    }


class NumericType(BaseModel):
    """Model for numeric type."""

    precision: int = Field(..., description="The precision of the numeric type")
    rounding: Optional[int] = Field(
        None, description="The rounding of the numeric type"
    )
    max_value: Optional[float] = Field(
        None, description="The max value of the numeric type"
    )
    min_value: Optional[float] = Field(
        None, description="The min value of the numeric type"
    )


class DateType(BaseModel):
    """Model for date type."""

    date_format: str = Field(..., description="The format of the date type")


class StringType(BaseModel):
    """Model for string type."""

    max_length: Optional[int] = Field(
        None, description="The max length of the string type"
    )
    min_length: Optional[int] = Field(
        None, description="The min length of the string type"
    )


class BooleanType(BaseModel):
    """Model for boolean type."""

    boolean_type: bool = Field(options=["TrueFalse", "YesNo", "10"])


class EnumType(BaseModel):
    """Model for enum type."""

    values: List[str] = Field(..., description="The values of the enum type")
    default: Optional[str] = Field(
        None, description="The default value of the enum type"
    )


class IDType(BaseModel):
    id_type: str = Field(options=["id", "uuid"])


class ColumnDefinition(BaseModel):
    """Model for column definition."""

    name: str = Field(..., description="The name of the column")
    is_nullable: bool = Field(..., description="Whether the column is nullable")
    type: Union[NumericType, DateType, StringType, BooleanType, EnumType, IDType] = (
        Field(..., description="The type of the column")
    )
    foreign_key: Optional[str] = Field(
        None, description="The foreign key of the column"
    )


class TableDefinition(BaseModel):
    """Model for table definition."""

    name: str = Field(..., description="The name of the table")
    columns: List[ColumnDefinition] = Field(..., description="The columns of the table")


"""
Producer configs
"""


class SMOLLMProducerConfig(BaseModel):
    """Model for SMOLLM producer config."""

    list: Optional[bool] = Field(
        default=False, description="Whether to use a list of options"
    )

    prompt: str = Field(..., description="The prompt of the SMOLLM producer")


class DateTimeProducerConfig(BaseModel):
    """Model for DateTime producer config."""

    date_format: str = Field(..., description="The format of the date")
    start_date: Optional[datetime] = Field(
        ..., description="The start date of the date"
    )
    end_date: Optional[datetime] = Field(..., description="The end date of the date")


class RandomNumberProducerConfig(BaseModel):
    """Model for Random producer config."""

    min: Optional[int] = Field(..., description="The min value of the random")
    max: Optional[int] = Field(..., description="The max value of the random")


class ChoiceOption(BaseModel):
    """Model for Choice option."""

    name: str = Field(..., description="The name of the option")
    probability: Optional[float] = Field(
        ..., description="The probability of the option"
    )


class ChoiceProducerConfig(BaseModel):
    """Model for Choice producer config."""

    options: List[ChoiceOption] = Field(..., description="The options of the choice")


class ColumnProfileDefinition(BaseModel):
    """Model for column profile definition."""

    producer: str = Field(..., description="The producer of the column")
    config: Union[
        SMOLLMProducerConfig,
        DateTimeProducerConfig,
        RandomNumberProducerConfig,
        ChoiceProducerConfig,
    ] = Field(default=None, description="The config of the column")


class TableOptions(BaseModel):
    count: Optional[int] = Field(default=None, description="The count of the table")
    probability: Optional[float] = Field(
        default=None, description="The probability of the table"
    )
    values: Optional[Dict[str, Any]] = Field(
        default=None, description="The values of the table"
    )


class TableProfileDefinition(BaseModel):
    """Model for table profile definition."""

    count: Optional[int] = Field(default=None, description="The count of the table")
    forEach: Optional[str] = Field(default=None, description="The forEach of the table")
    min_count: Optional[int] = Field(
        default=None, description="The min count of the table"
    )
    max_count: Optional[int] = Field(
        default=None, description="The max count of the table"
    )
    columns: Optional[Dict[str, ColumnProfileDefinition]] = Field(
        default=None, description="The columns of the table"
    )

    options: Optional[List[TableOptions]] = Field(
        default=None, description="Static options for the table"
    )


class ProfileDefinition(BaseModel):
    """Model for profile definition."""

    name: str = Field(..., description="The name of the profile")
    root: Optional[str] = Field(
        default=None, description="The root table of the profile"
    )
    tables: Dict[str, TableProfileDefinition] = Field(
        ..., description="The tables of the profile"
    )


class Configuration(BaseModel):
    """Model for configuration."""

    product_description: Optional[str] = Field(
        default="No product description provided",
        description="The product description of the configuration",
    )
    tables: List[TableDefinition] = Field(
        ..., description="The tables of the configuration"
    )

    profiles: List[ProfileDefinition] = Field(
        ..., description="The profiles of the configuration"
    )
