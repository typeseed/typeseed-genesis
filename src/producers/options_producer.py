import random
from src.models import (
    ColumnDefinition,
    ColumnProfileDefinition,
    TableDefinition,
    TableProfileDefinition,
)
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
        tables = context["__tables__"]
        state = context["__state__"]

        if table_definition.name not in state:
            state[table_definition.name] = []

            for index, option in enumerate(table_profile_configuration.options):
                if option.count:
                    for i in range(option.count):
                        state[table_definition.name].append(index)

        
        queue = state[table_definition.name]

        if (
            table_definition.name not in tables
            or len(tables[table_definition.name]) == 0
        ):
            tables[table_definition.name] = [
                item.values for item in table_profile_configuration.options
            ]

        if len(queue) > 0:
            selected_option = table_profile_configuration.options[queue.pop(0)].values
        else:
            filtered_list = [option for option in table_profile_configuration.options if option.count is None]  
            print(f"Filtered list: {filtered_list}")  
            selected_option = random.choices(filtered_list, weights=[option.probability if option.probability else 1 for option in filtered_list], k=1)[0].values
            if "values" in selected_option:
                selected_option = selected_option["values"]
        return selected_option, False
