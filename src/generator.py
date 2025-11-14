import re
from src.models import (
    ChoiceProducerConfig,
    ColumnDefinition,
    ColumnProfileDefinition,
    Configuration,
    IDType,
    TableDefinition,
    TableProfileDefinition,
)
from src.logging_config import get_logger
from src.producers.identifier_producer import IdentifierProducer
from src.producers.smollm_producer import SMOLLMProducer

logger = get_logger()


class Generator:
    def __init__(self):
        self.producers = {}

    """
    Process the hierarchy of the tables.
    We need to calculate the hierarchy in the data structure because we cannot start from a dependent table
    or a table that is referenced by another table.
    """

    def process_hierarchy(self, root: str, dependency_tree: list, statics: list):
        hierarchy = {}

        for table in self.configuration.tables:
            if table.name in statics:
                continue

            hierarchy[table.name] = {
                "level": 0,
                "parent": None if root == table.name else root,
            }

        for dependency in dependency_tree:
            (to_table, to_field, _, from_table, from_field) = dependency

            parent = hierarchy[from_table]
            current = hierarchy[to_table]

            if parent["level"] + 1 > current["level"] and from_table != to_table:
                current["level"] = parent["level"] + 1
                current["parent"] = from_table

        transformed_hierarchy = {}

        for table_name, attributes in hierarchy.items():
            parent = attributes["parent"]

            if parent is None:
                parent = "root"

            if table_name not in transformed_hierarchy:
                transformed_hierarchy[table_name] = {}

            if parent not in transformed_hierarchy:
                transformed_hierarchy[parent] = {}

            transformed_hierarchy[parent][table_name] = transformed_hierarchy[
                table_name
            ]

        hierarchy = transformed_hierarchy[root]

        return hierarchy

    """
    Generation roots are tables that are not dependent on any other table
    and are not referenced by any other table.
    We need to calculate the roots in the data structure because we cannot start from a dependent table
    or a table that is referenced by another table.
    """

    def calculate_roots(self):
        root = []
        statics = []
        dependency_tree = []
        dependency_regex = r"{{([a-zA-Z0-9]+).([a-zA-Z0-9]+)}}"

        for table in self.configuration.tables:
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

                    if foreign_key_table not in statics:
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

            table_profile = self.profile.tables[table.name]
            if table_profile:
                if table_profile.columns:
                    profile_columns = table_profile.columns
                    if profile_columns and column.name in profile_columns.keys():
                        profile_column_config = profile_columns[column.name].config

                        for value in profile_column_config.model_dump().values():
                            # if re.search(r"{{[a-zA-Z0-9]+.[a-zA-Z0-9]+}}", str(value)):
                            #     is_dependent = True
                            matches = re.findall(dependency_regex, str(value))
                            for match in matches:
                                dependency_tree.append(
                                    (
                                        table.name,
                                        column.name,
                                        "depends on",
                                        match[0],
                                        match[1],
                                    )
                                )
                            if matches and len(matches) > 0:
                                for match in matches:
                                    if match[0] not in statics:
                                        is_dependent = True

            if not is_dependent and table.name not in statics:
                root.append(table.name)

        return root, statics, dependency_tree

    def get_producer(
        self,
        table_definition: TableDefinition,
        column_definition: ColumnDefinition,
        profile_configuration: ColumnProfileDefinition,
    ):
        table_name = table_definition.name
        column_name = column_definition.name

        key = f"{table_name}.{column_name}"

        if key in self.producers:
            return self.producers[key]

        producer = None

        if isinstance(column_definition.type, IDType):
            producer = IdentifierProducer()

        if producer is None:
            logger.debug(f"Key {key}")
            logger.info(type(column_definition.type))
            logger.debug(
                f"Column definition: {column_definition.model_dump_json(indent=2)}"
            )
            logger.debug(
                f"Profile configuration: {profile_configuration.model_dump_json(indent=2)}"
            )
            raise ValueError(f"Producer {key} not found")

        self.producers[key] = producer
        return producer

    def generate_data(
        self,
        table_definition: TableDefinition,
        profile_configuration: TableProfileDefinition,
        context: dict,
    ):
        logger.info(f"Generating data for table: {table_definition.name}")

        rows = []

        row = {}
        for column in table_definition.columns:
            producer = self.get_producer(
                table_definition, column, profile_configuration
            )
            value = producer.generate(
                table_definition, column, profile_configuration, context
            )
            row[column.name] = value
        rows.append(row)

        return rows

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

        roots, statics, dependency_tree = self.calculate_roots()

        if len(statics) > 0:
            logger.info("+--------------------------------+")
            logger.info("|         Static tables          |")
            logger.info("+--------------------------------+")
            for static in statics:
                logger.info(f"| \x1b[34;20m{static}\x1b[0m".ljust(45) + "|")
            logger.info("+--------------------------------+")

            logger.info("\n\n")

        logger.info("+--------------------------------+")
        logger.info("|        Possible roots          |")
        logger.info("+--------------------------------+")
        for root in roots:
            logger.info(f"| \x1b[32;20m{root}\x1b[0m".ljust(45) + "|")
        logger.info("+--------------------------------+")
        logger.info("\n\n")

        start_root = None
        if self.profile.root is None and len(roots) > 0:
            start_root = roots[0]
        elif self.profile.root is not None:
            start_root = self.profile.root
        elif self.profile.root not in roots:
            raise ValueError(f"Root table {self.profile.root} not found in roots")

        hierarchy = self.process_hierarchy(start_root, dependency_tree, statics)

        def go_into_hierarchy(hierarchy, level=0):
            for key in hierarchy.keys():
                logger.info(f"{'  ' * level}|-\x1b[32;20m{key}\x1b[0m")
                go_into_hierarchy(hierarchy[key], level + 1)

        logger.info("Dependency Tree:")
        logger.info(f"\x1b[32;20m{start_root}\x1b[0m")
        go_into_hierarchy(hierarchy)
        logger.info("\n")

        context = {
            "__availability__": {},
            "__tables__": {}
        }

        logger.info("Generating static data...")
        for static in statics:
            table = next(
                table for table in self.configuration.tables if table.name == static
            )

            table_name = table.name

            context["__tables__"][table_name] = []
            context["__availability__"][table_name] = []
            
            for index, option in enumerate(self.profile.tables[static].options):
                context["__tables__"][table_name].append(option.values)

                if option.count:
                    context["__availability__"][table_name].append({"type": "count", "value": option.count, "index": index})
                elif option.probability:
                    context["__availability__"][table_name].append({"type": "probability", "value": option.probability, "index": index})
                else:
                    context["__availability__"][table_name].append({"type": "default", "value": 1, "index": index})



        

               
