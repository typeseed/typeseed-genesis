from abc import ABC, abstractmethod
import re
from typing import Any, Callable

from src.models import ColumnDefinition, ColumnProfileDefinition, TableDefinition




class BaseProducer(ABC):
    """Base producer class."""

   

    def replace_placeholders(self, text: str, context: dict):
        # find all placeholders {{}}
        placeholders = re.findall(r"{{.*?}}", text)
        result = text

        for placeholder in placeholders:
            placeholder_split = placeholder[2:-2].split(".")

            if len(placeholder_split) == 1:
                result = result.replace(
                    placeholder,
                    str(context[context["__table_name__"]][placeholder_split[0]]),
                )

            elif len(placeholder_split) == 2:
                result = result.replace(
                    placeholder,
                    str(context[placeholder_split[0]][placeholder_split[1]]),
                )

        return result

    @abstractmethod
    def generate(
        self,
        table_definition: TableDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> Any:
        """Generate a value for the column."""
        pass
