import random
from src.models import ColumnDefinition, ColumnProfileDefinition, TableDefinition, TableProfileDefinition
from src.producers.base_producer import BaseProducer


class ChoiceProducer(BaseProducer):
    """Choice producer class."""

    def generate(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        
        # selected_option = random.choice(column_profile_definition.config.options)
        selected_option = random.choices(column_profile_definition.config.options, weights=[option.probability if option.probability else 1 for option in column_profile_definition.config.options], k=1)[0]

        return selected_option.name