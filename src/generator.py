import random
from src.hierarchy import Hierarchy
from src.models import (
    ColumnDefinition,
    ColumnProfileDefinition,
    Configuration,
    ProfileDefinition,
    TableDefinition,
    TableProfileDefinition,
)
from src.logging_config import get_logger
from src.producers.options_producer import OptionsProducer
from src.producers.producer_factory import ProducerFactory
from src.utils import bcolors

logger = get_logger()


class Generator:
    def __init__(self):
        self.producer_factory = ProducerFactory()

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
                # logger.debug(json.dumps(context, indent=2))
                logger.error(f"Error generating data for column: {column.name}")
                # logger.debug(column_profile_configuration.model_dump_json())
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

    def generate(
        self,
        configuration: Configuration,
        selected_profile: ProfileDefinition,
        hierarchy: dict,
    ):

        logger.info(
            f"{bcolors.BOLD}{bcolors.HEADER} Started Generation ... {bcolors.ENDC}"
        )
        self.configuration = configuration
        self.profile = selected_profile

        context = {"__tables__": {}, "__satisfied_dependencies__": [], "__state__": {}}

        def generate():
            # get all the tables that have no dependencies or dependencies that have already been satisfied
            tables_to_generate = [
                table
                for table in hierarchy
                if (
                    table not in context["__satisfied_dependencies__"]
                    and (
                        len(hierarchy[table]["depends_on"]) == 0
                        or all(
                            dependency in context["__satisfied_dependencies__"]
                            for dependency in hierarchy[table]["depends_on"]
                        )
                    )
                )
            ]
            tables = context["__tables__"]
            for table_name in tables_to_generate:
                table_definition, table_profile_configuration = (
                    self.get_table_configuration(table_name)
                )

                count = (
                    table_profile_configuration.count
                    if table_profile_configuration.count
                    else 1
                )
                for i in range(count):
                    context["__table_name__"] = table_name
                    if table_name not in tables:
                        tables[table_name] = []
                    logger.info(
                        f"Generating data for table: {table_name} [{i}/{count}]"
                    )

                    # prepare dependencies
                    for dependency in hierarchy[table_name]["depends_on"]:
                        logger.info(
                            f"Preparing dependency: {dependency} for table: {table_name}"
                        )
                        print(tables)
                        context[dependency] = random.choice(tables[dependency])
                        logger.info(
                            f"Prepared dependency: {dependency} for table: {table_name}"
                        )
                        logger.info(f"Dependency: {context[dependency]}")

                    row_data, append_to_list = self.generate_data(
                        table_definition, table_profile_configuration, context
                    )

                    context[table_name] = row_data
                    if append_to_list:
                        tables[table_name].append(row_data)

                if table_name not in context["__satisfied_dependencies__"]:
                    context["__satisfied_dependencies__"].append(table_name)

        for table_name in hierarchy:
            table_definition, table_profile_configuration = (
                self.get_table_configuration(table_name)
            )

            if table_profile_configuration.options:
                context["__tables__"][table_name] = [
                    item.values["values"]
                    for item in table_profile_configuration.options
                ]
                context["__satisfied_dependencies__"].append(table_name)

        while len(context["__satisfied_dependencies__"]) < len(hierarchy):
            generate()
            logger.info(
                f"Satisfied dependencies: {context['__satisfied_dependencies__']}"
            )

        return context["__tables__"]
