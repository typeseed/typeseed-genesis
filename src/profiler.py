import json
import re
from src.hierarchy import Hierarchy
from src.llm import LLMCaller
from src.llm.prompts import (
    get_column_descriptions_prompt,
    get_profiler_prompt,
    get_static_data_generation_prompt,
    heal_dynamic_response_table,
)
from src.logging_config import get_logger
from src.models import (
    ColumnProfileDefinition,
    Configuration,
    ProfileDefinition,
    SMOLLMProducerConfig,
    StringType,
    TableOptions,
    TableProfileDefinition,
)
from src.utils import extract_nested_json, table_logger

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

    def build_profile(self):
        logger.info("Building profile...")

        tables, roots, statics, dependency_tree = self.hierarchy.calculate_roots()

        hierarchy = self.hierarchy.process_hierarchy(tables, dependency_tree)

        table_types = {}

        table_options = {}

        for table_name in tables:
            table_type = self.get_table_type(table_name)

            try:
                table_type = json.loads(table_type.split("```json")[1].split("```")[0])
            except Exception as e:
                table_type = {
                    "classification": "DYNAMIC",
                    "confidence": 0.0,
                    "reasoning": "Error parsing table type",
                }

            logger.info(
                f" {table_name} is {table_type['classification']} - [{table_type['confidence']}] - {table_type['reasoning']}"
            )
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

            column_description_json = None

            try:
                column_description_json = json.loads(
                    column_description.split("```json")[1].split("```")[0]
                )

            except Exception as e:
                json_object = extract_nested_json(column_description)
                if json_object:
                    column_description_json = json.loads(json_object)
                else:
                    system_prompt, prompt = heal_dynamic_response_table(
                        column_description
                    )
                    column_description_json = self.llm.call(
                        prompt, system_prompt, temperature=0, max_tokens=3000
                    ).strip()

                    try:
                        column_description_json = json.loads(
                            column_description_json.split("```json")[1].split("```")[0]
                        )
                    except Exception as e:
                        print(f"Error parsing column {table_name}: {e}")
                        column_description_json = {
                            "error": "Error parsing column {table_name}"
                        }

            if column_description_json:
                table_options[table_name] = column_description_json

        profile_tables = ProfileDefinition(name="default", tables={}, root=None)
        for table_name in tables:
            table = self.get_table(table_name)

            table_type = table_types[table_name]

            is_static = table_type["classification"] == "STATIC"

            if is_static:
                logger.info(f"Static table: {table_name}")
                options = table_options[table_name]

                table_profile = TableProfileDefinition(
                    count=None,
                    min_count=None,
                    max_count=None,
                    columns=None,
                    options=[
                        TableOptions(
                            count=None,
                            probability=1,
                            values={"values": option},
                        )
                        for option in options
                    ],
                )

                profile_tables.tables[table_name] = table_profile

            else:
                column_profile_definitions = {}
                table_profile = TableProfileDefinition(
                    count=1,
                    min_count=None,
                    max_count=None,
                    columns=None,
                    options=None,
                )

                for column in table.columns:
                    print("++++++")
                    print(column.name)
                    print(type(column.type))
                    if isinstance(column.type, StringType):
                        print(json.dumps(table_options, indent=2))
                        column_profile_definition = ColumnProfileDefinition(
                            producer="smollm",
                            config=SMOLLMProducerConfig(
                                list=True,
                                prompt=table_options[table_name][column.name],
                            ),
                        )

                        column_profile_definitions[column.name] = (
                            column_profile_definition
                        )

                table_profile.columns = column_profile_definitions

                profile_tables.tables[table_name] = table_profile

        logger.info(">>>>>>>>>>>>>>>")
        logger.info(json.dumps(profile_tables.model_dump(), indent=2))

        # table = self.get_table(table_name)
        # for column in table.columns:
        #     if isinstance(column.type, IDType):
