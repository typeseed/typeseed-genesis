import random
import re
import json
import traceback
from src.models import (
    ColumnDefinition,
    ColumnProfileDefinition,
    Configuration,
    TableDefinition,
    TableProfileDefinition,
)
from src.logging_config import get_logger
from src.producers.options_producer import OptionsProducer
from src.producers.producer_factory import ProducerFactory

logger = get_logger()


class Generator:
    def __init__(self):
        self.producer_factory = ProducerFactory()

    """
    Process the hierarchy of the tables.
    We need to calculate the hierarchy in the data structure because we cannot start from a dependent table
    or a table that is referenced by another table.
    """

    def process_hierarchy(self, tables: list, dependency_tree: list):
        hierarchy = {}

        refs = {}

        for table in tables:
            table_obj = {"depends_on": []}
            hierarchy[table] = table_obj
            refs[table] = table_obj

        for dependency in dependency_tree:
            table, column, relation, foreign_table, foreign_column = dependency
            ref_table = refs[table]

            ref_table["depends_on"].append(foreign_table)
        return hierarchy

    """
    Generation roots are tables that are not dependent on any other table
    and are not referenced by any other table.
    We need to calculate the roots in the data structure because we cannot start from a dependent table
    or a table that is referenced by another table.
    """

    def calculate_roots(self):
        tables = []
        root = []
        statics = []
        dependency_tree = []
        dependency_regex = r"{{([a-zA-Z0-9]+).([a-zA-Z0-9]+)}}"

        for table in self.configuration.tables:
            tables.append(table.name)
            if table.name not in self.profile.tables:
                continue
            table_profile = self.profile.tables[table.name]
            if table_profile and table_profile.options:
                has_dependencies = False
                for option in table_profile.options:
                    for value in option.model_dump().values():
                        matches = re.findall(dependency_regex, str(value))
                        if len(matches) > 0:
                            has_dependencies = True
                            break
                    if has_dependencies:
                        break
                if not has_dependencies:
                    statics.append(table.name)

        for table in self.configuration.tables:
            is_dependent = False

            for column in table.columns:
                if column.foreign_key:
                    # extract the table and column from the foreign key
                    foreign_key_table, foreign_key_column = column.foreign_key.split(
                        "."
                    )

                    is_dependent = True
                    dependency_tree.append(
                        (
                            table.name,
                            column.name,
                            "depends on",
                            foreign_key_table,
                            foreign_key_column,
                        )
                    )

            if not is_dependent and table.name not in statics:
                root.append(table.name)

        return tables, root, statics, dependency_tree

    def get_producer(
        self,
        table_definition: TableDefinition,
        table_profile_configuration: TableProfileDefinition,
        column_definition: ColumnDefinition,
        profile_configuration: ColumnProfileDefinition,
    ):
        """Get a producer using the factory."""
        return self.producer_factory.get_producer(
            table_definition,
            table_profile_configuration,
            column_definition,
            profile_configuration,
        )

    def generate_data(
        self,
        table_definition: TableDefinition,
        profile_configuration: TableProfileDefinition,
        context: dict,
    ):
        # logger.info(f"Generating data for table: {table_definition.name}")

        if profile_configuration.options:
            producer = OptionsProducer()
            return producer.generate(
                table_definition, profile_configuration, None, None, context=context
            )

        row = {}
        for column in table_definition.columns:
            column_profile_configuration = (
                profile_configuration.columns[column.name]
                if profile_configuration.columns
                and column.name in profile_configuration.columns
                else None
            )

            producer = self.get_producer(
                table_definition,
                profile_configuration,
                column,
                column_profile_configuration,
            )
            try:
                value = producer.generate(
                    table_definition,
                    profile_configuration,
                    column,
                    column_profile_configuration,
                    context,
                )
            except Exception as e:
                logger.debug(json.dumps(context, indent=2))
                raise e
            row[column.name] = value
            context[table_definition.name] = row

        return row, True

    def get_table_configuration(self, table_name: str):
        table_definition = None
        table_profile_configuration = None
        for table in self.configuration.tables:
            if table.name == table_name:
                table_definition = table
                table_profile_configuration = self.profile.tables[table_name]
                break

        return table_definition, table_profile_configuration

    def generate_entity(
        self, hierarchy: dict, table_name: str, context: dict, traceback: list = []
    ):
        table_definition, table_profile_configuration = self.get_table_configuration(
            table_name
        )

        if table_name in traceback:
            return

        if "__tables__" not in context:
            context["__tables__"] = {}

        tables = context["__tables__"]

        local_traceback = traceback.copy()
        local_traceback.append(table_name)

        print(" [ " + table_name + " ] ")

        for i in range(
            table_profile_configuration.count
            if table_profile_configuration.count
            else 1
        ):
            for dependency in hierarchy[table_name]["depends_on"]:
                if dependency in local_traceback:
                    continue
                logger.info(
                    f"Generating dependency: {dependency} for table: {table_name}"
                )
                self.generate_entity(hierarchy, dependency, context, local_traceback)

            context["__table_name__"] = table_name
            if table_name not in tables:
                tables[table_name] = []
            logger.info(f"Generating data for table: {table_name}")
            row_data, append_to_list = self.generate_data(
                table_definition, table_profile_configuration, context
            )

            context[table_name] = row_data
            if append_to_list:
                tables[table_name].append(row_data)

            for key, value in hierarchy.items():
                if table_name in value["depends_on"]:
                    if key in local_traceback:
                        continue
                    self.generate_entity(hierarchy, key, context, local_traceback)

    def generate(self, configuration: Configuration, profile_name: str = "default"):
        self.configuration = configuration

        selected_profile = next(
            (
                profile
                for profile in self.configuration.profiles
                if profile.name == profile_name
            ),
            None,
        )
        if not selected_profile:
            raise ValueError(f"Profile {profile_name} not found")

        self.profile = selected_profile

        tables, roots, statics, dependency_tree = self.calculate_roots()

        hierarchy = self.process_hierarchy(tables, dependency_tree)

        print(json.dumps(hierarchy, indent=2))

        context = {}

        self.generate_entity(hierarchy, "organizations", context, [])

        print(json.dumps(context["__tables__"], indent=2))
