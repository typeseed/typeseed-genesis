import random
from src.models import (
    ColumnDefinition,
    ColumnProfileDefinition,
    RandomNumberProducerConfig,
    TableDefinition,
    TableProfileDefinition,
)
from src.producers.base_producer import BaseProducer


class RandomNumberProducer(BaseProducer):
    """Identifier producer class."""

    def generate(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        config: RandomNumberProducerConfig = column_profile_definition.config
        min = config.min_value if config.min_value else 0
        max = config.max_value if config.max_value else 1
        precision = config.precision if config.precision is not None else 2

        print(f"Generating random number between {min} and {max} with precision {precision}")
        value = min + (random.random() * (max-min))

        return round(value, precision)