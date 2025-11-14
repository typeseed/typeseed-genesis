import uuid
from src.models import ColumnDefinition, ColumnProfileDefinition, TableDefinition
from src.producers.base_producer import BaseProducer


class IdentifierProducer(BaseProducer):
    """Identifier producer class."""

    def __init__(self):
        self.id_counter = 0

    def generate(
        self,
        table_definition: TableDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        if column_definition.type.id_type == "id":
            self.id_counter += 1
            return self.id_counter

        elif column_definition.type.id_type == "uuid":
            return str(uuid.uuid4())
        else:
            raise ValueError(f"Invalid ID type: {column_definition.type.id_type}")
