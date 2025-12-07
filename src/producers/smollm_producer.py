import uuid
import re

from torch._inductor import list_options
from src.llm import LLMCaller
from src.models import (
    ColumnDefinition,
    ColumnProfileDefinition,
    TableDefinition,
    TableProfileDefinition,
)
from src.producers.base_producer import BaseProducer
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.logging_config import get_logger

logger = get_logger()


class SMOLLMProducer(BaseProducer):
    """Identifier producer class."""

    def generate(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        self.llm = LLMCaller(local=True)
        prompt = self.replace_placeholders(
            column_profile_definition.config.prompt, context
        )

        has_dependency = prompt != column_profile_definition.config.prompt

        table_name = table_definition.name
        column_name = column_definition.name
        options_key = f"{table_name}.{column_name}.{prompt}"

        if "__options__" not in context:
            context["__options__"] = {}

        if (
            options_key not in context["__options__"]
            or len(context["__options__"][options_key]) == 0
        ):
            context["__options__"][options_key] = []

        if len(context["__options__"][options_key]) > 0:
            return context["__options__"][options_key].pop()

        SYSTEM_PROMPT = """You are a strict synthetic data generator for software testing. Your task is to generate mock data for a single spreadsheet cell based on a column description provided by the user.

You must analyze the user input and choose exactly one of two output formats based on the following logic:

**CONDITION 1: Independent Data**
IF the description is for a name, short description, category, or static value AND contains no variable placeholders (like `{name}` or `<id>`), YOU MUST generate a numbered list of 10 unique samples.

**CONDITION 2: Dependent or Complex Data**
IF the description implies a dependency on another column (e.g., "matches the ID"), contains placeholders (e.g., "email for {name}"), or asks for a formula, YOU MUST generate only a single text output example.

**STRICT OUTPUT CONSTRAINTS:**
- Do NOT provide explanations, introductory text, or markdown code blocks (```).
- Do NOT say "Here is the list" or "Condition met".
- Output ONLY the raw data.
- Output only the data, no other text or alternatives.

### EXAMPLES

Input: "A random first name"
Output:
1. James
2. Sarah
3. Michael
4. Elena
5. David
6. Aiko
7. Robert
8. Wei
9. Emily
10. Carlos

Input: "An email address generated from {First Name} and {Last Name}"
Output:
james.smith@example.com

Input: "A status for a delivery order"
Output:
1. Pending
2. Shipped
3. Delivered
4. Cancelled
5. Returned
6. Processing
7. Out for Delivery
8. Failed Attempt
9. Awaiting Pickup
10. In Transit

Input: "Description of the tenant"
Output:
A large, multinational corporation specializing in advanced technology solutions and cloud infrastructure.

"""
        
        # table length
        table_data = context["__tables__"][table_name]
        if table_data:
            table_length = len(table_data)
        else:
            table_length = 0


        SYSTEM_PROMPT += f"Table length: {table_length}"

        print(table_length)


        PROMPT = f"""### CURRENT REQUEST

Input: {prompt} (has_dependency: {has_dependency})
Output:"""
        output = self.llm.call(
            PROMPT,
            SYSTEM_PROMPT,
            temperature=1.8,
            max_tokens=3000,
            allow_cache=True,
        ).strip()

        print("-" * 100)
        print(output)
        print("-" * 100)

        # regex to extract all the items from the numbered list
        pattern = r"^\d+\.\s+(.*)"
        matches = re.findall(pattern, output, re.MULTILINE)
        if matches:
            print("-" * 100)
            print(matches)
            print("-" * 100)
            list_of_options = matches
            context["__options__"][options_key] = list_of_options
            return list_of_options.pop()
        else:
            print("-" * 100)
            print(output)
            print("-" * 100)
            return output