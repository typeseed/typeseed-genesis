from typing import Dict, Type
from src.models import (
    ColumnDefinition,
    ColumnProfileDefinition,
    SMOLLMProducerConfig,
    TableDefinition,
    IDType,
    ChoiceProducerConfig,
    TableProfileDefinition,
)
from src.producers.base_producer import BaseProducer
from src.producers.bool_producer import BoolProducer
from src.producers.identifier_producer import IdentifierProducer
from src.producers.choice_producer import ChoiceProducer
from src.producers.random_number_producer import RandomNumberProducer
from src.producers.smollm_producer import SMOLLMProducer
from src.producers.fk_producer import FKProducer
from src.producers.options_producer import OptionsProducer
from src.logging_config import get_logger

logger = get_logger()


class ProducerFactory:
    """Factory class for creating and managing producers."""

    def __init__(self):
        self._producers: Dict[str, BaseProducer] = {}
        self._producer_types: Dict[str, Type[BaseProducer]] = {
            "identifier": IdentifierProducer,
            "choice": ChoiceProducer,
            "smollm": SMOLLMProducer,
            "fk": FKProducer,
            "options": OptionsProducer,
            "bool": BoolProducer,
            "numeric": RandomNumberProducer
        }

    def register_producer_type(self, name: str, producer_class: Type[BaseProducer]):
        """Register a new producer type."""
        self._producer_types[name] = producer_class
        logger.debug(f"Registered producer type: {name}")

    def get_producer(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        profile_configuration: ColumnProfileDefinition,
    ) -> BaseProducer:
        """Get or create a producer for the given column."""
        table_name = table_definition.name
        column_name = column_definition.name
        key = f"{table_name}.{column_name}"

        # Return cached producer if exists
        if key in self._producers:
            return self._producers[key]

        # Determine which producer to create
        producer = self._create_producer(column_definition, profile_configuration, key)

        # Cache the producer
        self._producers[key] = producer
        return producer

    def _create_producer(
        self,
        column_definition: ColumnDefinition,
        profile_configuration: ColumnProfileDefinition,
        key: str,
    ) -> BaseProducer:
        """Create a new producer based on column definition and profile."""
        # Check for ID type

        if column_definition.foreign_key:
            return self._producer_types["fk"]()

        if column_definition.type == "identifier":
            return self._producer_types["identifier"]()

        if column_definition.type == "numeric":
            return self._producer_types["numeric"]()

        if column_definition.type == "boolean":
            return self._producer_types["bool"]()

        if profile_configuration and isinstance(
            profile_configuration.config, ChoiceProducerConfig
        ):
            return self._producer_types["choice"]()

        if profile_configuration and isinstance(
            profile_configuration.config, SMOLLMProducerConfig
        ):
            return self._producer_types["smollm"]()

        logger.debug(f"No suitable producer found for {key}")
        logger.debug(column_definition.model_dump_json())
        raise ValueError(f"No suitable producer found for {key}")

    def clear_cache(self):
        """Clear all cached producers."""
        self._producers.clear()
        logger.debug("Cleared producer cache")

    def get_producer_count(self) -> int:
        """Get the number of cached producers."""
        return len(self._producers)
