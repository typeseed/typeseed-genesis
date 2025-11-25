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
        max = config.min_value if config.min_value else 1
        precision = config.precision if config.precision else 2


        return min + (random.random() * (max-min))