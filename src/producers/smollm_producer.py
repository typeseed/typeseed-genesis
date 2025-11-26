import uuid
import re
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

        # # return "```" + prompt + "```"

        # inputs = tokenizer(prompt, return_tensors="pt").to(device)
        # outputs = model.generate(**inputs, max_new_tokens=100)
        # return tokenizer.decode(outputs[0], skip_special_tokens=True)

        if column_profile_definition.config.list:
            table_name = table_definition.name
            column_name = column_definition.name
            options_key = f"{table_name}.{column_name}.{prompt}"

            if "__options__" not in context:
                context["__options__"] = {}

            if options_key not in context["__options__"] or len(context["__options__"][options_key]) == 0:
                context["__options__"][options_key] = []

                SYSTEM_PROMPT = """You are a mock data generator that generates mock data for testing purposes. Your sole task is to generate multiple options for a specific entity based on a user prompt.

## Guidelines:
1. Analyze the user's input to identify the core entity and the relevant items to list.
2. Output the items as a standard numbered list (e.g., 1. Item).
3. STRICTLY FORBIDDEN: Do not include any introductory text (e.g., "Here are the items..."), conversational filler, markdown titles, or concluding remarks.
4. If the input is ambiguous, list the most common items associated with the primary interpretation of the entity.
5. The output must contain *only* the list.

## Example:
Input: "Ingredients for a standard pancake batter"
Output:
1. All-purpose flour
2. Sugar
3. Baking powder
4. Salt
5. Milk
6. Butter
7. Eggs
"""
                PROMPT = f"""**User Input:** {prompt}"""

                output = self.llm.call(
                    PROMPT, SYSTEM_PROMPT, temperature=0, max_tokens=3000
                ).strip()


                list_of_options = output.split("\n")[1:]

                digit_regex = r"^\d+\."
                list_of_options = [
                    re.sub(digit_regex, "", option).strip()
                    for option in list_of_options
                ]

                # remove empty strings
                list_of_options = [
                    option for option in list_of_options if option.strip()
                ]

                context["__options__"][options_key] = list_of_options

            option = context["__options__"][options_key].pop()

            return option
        else:
            SYSTEM_PROMPT = """
You are a specialized Deterministic, Constrained Value Generator for mock data. Your sole, immutable function is to create a single, novel, maximally short, and unique value for the data type specified by the user.

**CRITICAL RULES & CONSTRAINTS:**
1.  **Output Format:** Must be a single, unformatted string value.
2.  **Content:** The generated value must not appear in the 'Already Generated Values' list. If a proposed value is a duplicate, you are strictly forbidden from outputting it and must immediately generate a different, valid value.
3.  **DO NOT ADD:** Do not output any introductory sentence, concluding remark, explanation, title, header, footer, or any text/characters *other than* the value itself (e.g., "value").
4.  **Value Integrity:** The generated value must be simple data point. You must NOT add any new properties, attributes, descriptions, explanations, or context to the value itself.
5.  **Termination:** Stop immediately after the value is generated.
6.  **Output Type:** Do not generate code, documentation, guides or data formats.

"""
            PROMPT = (
                f"""Generate a unique value for the following prompt:
{prompt}
""",
            )
        output = self.llm.call(
            PROMPT, SYSTEM_PROMPT, temperature=0, max_tokens=3000
        ).strip()

        print("--------------------------------")
        print(output)
        print("--------------------------------")

        return output
