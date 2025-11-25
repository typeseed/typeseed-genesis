import random
from src.models import (
    ColumnDefinition,
    ColumnProfileDefinition,
    TableDefinition,
    TableProfileDefinition,
)
from src.producers.base_producer import BaseProducer


class BoolProducer(BaseProducer):
    """Identifier producer class."""

    def generate(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        return random.random() < 0.5
