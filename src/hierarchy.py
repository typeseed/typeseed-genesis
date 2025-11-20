from src.models import Configuration, ProfileDefinition
import re


class Hierarchy:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    """
    Generation roots are tables that are not dependent on any other table
    and are not referenced by any other table.
    We need to calculate the roots in the data structure because we cannot start from a dependent table
    or a table that is referenced by another table.
    """

    def calculate_roots(self, profile: ProfileDefinition = None):
        tables = []
        root = []
        statics = []
        dependency_tree = []
        dependency_regex = r"{{([a-zA-Z0-9]+).([a-zA-Z0-9]+)}}"

        for table in self.configuration.tables:
            tables.append(table.name)
            if profile is None or table.name not in profile.tables:
                continue
            table_profile = profile.tables[table.name]
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
