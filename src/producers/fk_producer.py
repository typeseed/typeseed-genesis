import random
from src.models import ColumnDefinition, ColumnProfileDefinition, TableDefinition, TableProfileDefinition
from src.producers.base_producer import BaseProducer


class FKProducer(BaseProducer):
    """FK producer class."""

    def generate(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        
        split = column_definition.foreign_key.split(".")
        return context[split[0]][split[1]]