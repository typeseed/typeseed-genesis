import random
from src.models import ColumnDefinition, ColumnProfileDefinition, TableDefinition, TableProfileDefinition
from src.producers.base_producer import BaseProducer
from src.logging_config import get_logger

logger = get_logger()

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
        try:
            split = column_definition.foreign_key.split(".")
            return context[split[0]][split[1]]
        except Exception as e:
            logger.error("Unable to reference table based on configuration")
            logger.error(f"Reference key: {column_definition.foreign_key}")
            logger.error(f"Split {split}")
            logger.error("Reference table:")
            logger.error(context[split[0]])
            raise e