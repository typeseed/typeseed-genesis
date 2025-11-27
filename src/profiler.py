import json
import re
from src.hierarchy import Hierarchy
from src.llm import LLMCaller
from src.llm.prompts import (
    get_column_descriptions_prompt,
    get_profiler_prompt,
    get_static_data_generation_prompt,
    get_configuration_for_column,
    heal_dynamic_response_table,
)

from src.models import (
    ColumnProfileDefinition,
    Configuration,
    IDType,
    IntegerType,
    NumericType,
    ProfileDefinition,
    RandomNumberProducerConfig,
    SMOLLMProducerConfig,
    StringType,
    TableOptions,
    TableProfileDefinition,
)
from src.utils import extract_nested_json, table_logger, bcolors
from src.logging_config import get_logger

logger = get_logger()


class Profiler:
    def __init__(self, configuration: Configuration, hierarchy: Hierarchy):
        self.hierarchy = hierarchy
        self.configuration = configuration

        self.llm = LLMCaller(local=False)

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
        logger.info("-" * 60)
        logger.info("\033[94mBuilding profile...\033[0m")

        tables, roots, statics, dependency_tree = self.hierarchy.calculate_roots()

        hierarchy = self.hierarchy.process_hierarchy(tables, dependency_tree)

        for hierarchy_table in hierarchy:
            dependencies_str = ", ".join(hierarchy[hierarchy_table]["depends_on"])
            logger.info(
                f"{bcolors.HEADER} * {hierarchy_table} ({len(hierarchy[hierarchy_table]['depends_on'])}){bcolors.ENDC} {bcolors.OKCYAN}{': [' + dependencies_str + ' ]' if len(dependencies_str) > 0 else ''}{bcolors.ENDC}"
            )

        table_types = {}

        table_options = {}

        logger.info("-" * 60)
        logger.info("\033[94mEvaluating if tables are static or dynamic...\033[0m")
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
                f"{bcolors.HEADER} + {table_name.center(30)}[ {table_type['classification'].center(10)} ] {bcolors.ENDC}"
            )

            table_types[table_name] = table_type

        logger.info("-" * 60)
        logger.info(f"{bcolors.OKBLUE}Generating column descriptions ...{bcolors.ENDC}")
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
                column_description_json = extract_nested_json(column_description, True)
            except Exception as e:
                print(f"Error parsing column {table_name}: {e}")
                column_description_json = {"error": "Error parsing column {table_name}"}
            if isinstance(column_description_json, list):
                table_logger(column_description_json, table_name)
            else:
                logger.info("-" * 80)
                logger.info(
                    f"{bcolors.HEADER} {table_name} generation prompts... {bcolors.ENDC}"
                )
                for key, value in column_description_json.items():
                    replace_regex = r"(\{\{[a-zA-Z0-9_. ]+\}\})"
                    print_value = str(value).replace(
                        replace_regex,
                        rf"{bcolors.OKGREEN}$1{bcolors.ENDC}{bcolors.WARNING}",
                    )
                    logger.info(
                        f"{bcolors.HEADER} | {key[:20].center(20)}{bcolors.ENDC} | {bcolors.WARNING}{print_value}{bcolors.ENDC} "
                    )
                logger.info("-" * 80)
            if column_description_json:
                table_options[table_name] = column_description_json

        logger.info("#" * 60)
        logger.info(f"{bcolors.OKBLUE}Completing profile ...{bcolors.ENDC}")

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

                count = 1

                # if table.name == "medical_encounters":
                #     count = 3
                if table.name == "medical_facilities":
                    count = 1
                if table.name == "providers":
                    count = 1
                if table.name == "patients":
                    count = 6
                if table.name == "medical_encounters":
                    count = 2

                table_profile = TableProfileDefinition(
                    count=count,
                    min_count=None,
                    max_count=None,
                    columns=None,
                    options=None,
                )

                for column in table.columns:
                    column_profile_definition = None

                    if not column.foreign_key:
                        if column.type == "numeric":
                            schema_json = NumericType.model_json_schema()
                            system_prompt, prompt = get_configuration_for_column(
                                table_options[table_name][column.name],
                                schema_json,
                            )
                            column_configuration_output = self.llm.call(
                                prompt, system_prompt, temperature=0, max_tokens=3000
                            ).strip()
                            try:
                                column_configuration_json = extract_nested_json(
                                    column_configuration_output, True
                                )

                                column_profile_definition = ColumnProfileDefinition(
                                    producer="numeric",
                                    config=RandomNumberProducerConfig(
                                        **column_configuration_json
                                    ),
                                )

                            except Exception as e:
                                logger.error(
                                    f"Unable to generate the configuration for {table_name}.{column.name}"
                                )
                                logger.error(column_configuration_json)
                                raise e

                        elif column.type == "string":
                            column_profile_definition = ColumnProfileDefinition(
                                producer="smollm",
                                config=SMOLLMProducerConfig(
                                    list=False,
                                    prompt=table_options[table_name][column.name],
                                ),
                            )

                    if not column_profile_definition:
                        logger.error(
                            f"No column profile definition found for {column.name}"
                        )
                        continue

                    column_profile_definition.root_prompt = table_options[table_name][
                        column.name
                    ]

                    column_profile_definitions[column.name] = column_profile_definition

                table_profile.columns = column_profile_definitions

                profile_tables.tables[table_name] = table_profile

                ## dump profile json to a local file `temp-profile.json`
        with open("temp-profile.json", "w") as f:
            json.dump(profile_tables.model_dump(), f, indent=2)

        return profile_tables
