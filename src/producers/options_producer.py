import random
from src.models import ColumnDefinition, ColumnProfileDefinition, TableDefinition, TableProfileDefinition
from src.producers.base_producer import BaseProducer


class OptionsProducer(BaseProducer):
    """Options producer class."""

    def generate(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        
        selected_option = random.choice(table_profile_configuration.options)

        return selected_option.values