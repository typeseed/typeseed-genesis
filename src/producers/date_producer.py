from datetime import datetime
import random
from src.models import (
    ColumnDefinition,
    ColumnProfileDefinition,
    DateTimeProducerConfig,
    TableDefinition,
    TableProfileDefinition,
)
from src.producers.base_producer import BaseProducer


class DateTimeProducer(BaseProducer):
    """Identifier producer class."""

    def generate(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        

        config: DateTimeProducerConfig = column_definition.config
        

        return datetime.now()


