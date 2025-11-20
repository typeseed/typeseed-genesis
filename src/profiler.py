import json
from src.hierarchy import Hierarchy
from src.llm import LLMCaller
from src.llm.prompts import (
    get_column_descriptions_prompt,
    get_profiler_prompt,
    get_static_data_generation_prompt,
)
from src.logging_config import get_logger
from src.models import Configuration, StringType

logger = get_logger()


class Profiler:
    def __init__(self, configuration: Configuration, hierarchy: Hierarchy):
        self.hierarchy = hierarchy
        self.configuration = configuration

        self.llm = LLMCaller(local=True)

    def get_table(self, table_name: str):
        return next(
            (table for table in self.configuration.tables if table.name == table_name),
            None,
        )

    def get_schema(self, table_name: str):
        table = self.get_table(table_name)
        return json.dumps(table.model_dump()["columns"], indent=2)

    def get_table_type(self, table_name: str):
        schema = self.get_schema(table_name)

        system_prompt, prompt = get_profiler_prompt(
            self.configuration.product_description, table_name, schema
        )
        return self.llm.call(
            prompt, system_prompt, temperature=0, max_tokens=3000
        ).strip()

    def get_column_descriptions(self, table_name: str):
        model_schema = self.get_schema(table_name)

        SYSTEM_PROMPT = """
You are a Contextual Column Describer. Your task is to analyze the provided database table schema and write a concise, professional, and entity-aware description for every column. You MUST use the table_name (which represents the entity) to ground the description of each column.
You MUST return the output as a clean, continuous Markdown dash list. Do NOT include any explanatory text, greetings, code blocks, or reasoning. The response must be ONLY the dash list.
Format: - column_name: A descriptive sentence for the column, specifically referencing the table_name entity.
"""
        PROMPT = f"""
TASK:
Analyze the provided table schema (including column names and data types/descriptions) and output a descriptive entry for every column, ensuring the table entity is incorporated into the description.

Input Table Schema:
{model_schema}
"""
        return self.llm.call(PROMPT, SYSTEM_PROMPT, temperature=0, max_tokens=3000)

    def build_profile(self):
        logger.info("Building profile...")

        tables, root, statics, dependency_tree = self.hierarchy.calculate_roots()

        hierarchy = self.hierarchy.process_hierarchy(tables, dependency_tree)

        table_types = {}

        for table_name in tables:
            table = self.get_table(table_name)

            logger.info(f"--------[ {table_name} ]--------")

            table_type = self.get_table_type(table_name)

            # extract everything between ```json and ``` and convert to json
            try:
                table_type = json.loads(table_type.split("```json")[1].split("```")[0])
            except Exception as e:
                table_type = {
                    "classification": "DYNAMIC",
                    "confidence": 0.0,
                    "reasoning": "Error parsing table type",
                }

            table_types[table_name] = table_type

        for table_name in tables:
            table_schema = self.get_schema(table_name)
            dependent_tables = hierarchy[table_name]["depends_on"]
            dependent_tables_schema = [
                self.get_schema(table) for table in dependent_tables
            ]

            dependent_tables_schema = "\n".join(dependent_tables_schema)

            table_type = table_types[table_name]

            is_static = table_type["classification"] == "STATIC"

            column_description = ""

            if is_static:
                system_prompt, prompt = get_static_data_generation_prompt(
                    self.configuration.product_description,
                    table_name,
                    table_schema,                
                )

                column_description = self.llm.call(
                    prompt, system_prompt, temperature=0, max_tokens=6000
                ).strip()
            else:
                system_prompt, prompt = get_column_descriptions_prompt(
                    self.configuration.product_description,
                    table_name,
                    table_schema,
                    dependent_tables_schema,
                )

                column_description = self.llm.call(
                    prompt, system_prompt, temperature=0, max_tokens=3000
                ).strip()

            try:
                column_description_json = json.loads(
                    column_description.split("```json")[1].split("```")[0]
                )
            except Exception as e:
                print(column_description)
                column_description_json = {"error": "Error parsing column descriptions"}

            print(f"---- {table_name} ----")
            print(json.dumps(column_description_json, indent=2))
            print("--------------------------------")

