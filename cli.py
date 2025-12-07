#!/usr/bin/env python3
"""
CLI application using transformers, numpy, and pandas.
"""

import argparse
import os
import shutil
import json
import sys
from pathlib import Path
from src.generator import Generator
from src.hierarchy import Hierarchy
from src.models import Configuration
from src.logging_config import init_default_logger, get_logger, log_performance
from src.profiler import Profiler
from src.utils import table_logger


@log_performance
def load_json_config(json_input) -> Configuration:
    """
    Load JSON configuration from file path or string.

    Args:
        json_input: Path to JSON file or JSON string

    Returns:
        Configuration: Validated configuration object
    """
    logger = get_logger()

    try:
        # Try to parse as JSON string first
        logger.debug("Attempting to parse config as JSON string")
        config = json.loads(json_input)
        logger.info("Successfully parsed config from JSON string")
        return Configuration.model_validate(config)
    except json.JSONDecodeError:
        # If that fails, try to read as file path
        try:
            config_path = Path(json_input)
            logger.debug(f"Attempting to load config from file: {config_path}")

            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                logger.info(f"Successfully loaded config from file: {config_path}")
                return Configuration.model_validate(config)
            else:
                logger.error(f"Configuration file not found: {json_input}")
                raise FileNotFoundError(f"Configuration file not found: {json_input}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ValueError(f"Invalid JSON input: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TypeSeed Genesis - Synthetic Data Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using JSON file
  python cli.py --config samples/basic1.json
  
  # With verbose output
  python cli.py --config samples/basic1.json --verbose
  
  # With debug logging
  python cli.py --config samples/basic1.json --log-level DEBUG
  
  # Save logs to file
  python cli.py --config samples/basic1.json --log-file app.log
        """,
    )

    parser.add_argument(
        "--config", type=str, required=True, help="JSON configuration file path"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (sets log level to DEBUG)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Log file name (logs saved to logs/ directory)",
    )

    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored console output"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for results (JSON format)",
    )

    args = parser.parse_args()

    # Initialize logging
    log_level = "DEBUG" if args.verbose else args.log_level
    logger = init_default_logger(
        level=log_level,
        log_file=args.log_file,
        use_color=not args.no_color,
        detailed=args.verbose,
    )

    logger.info("=" * 60)
    logger.info("TypeSeed Genesis - Synthetic Data Generation")
    logger.info("=" * 60)

    try:

        # make tempo
        temp_dir = "temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # Load configuration
        logger.info(f"Loading configuration from: {args.config}")
        config = load_json_config(args.config)
        logger.info("Configuration loaded and validated successfully")

        # if args.verbose:
            # logger.debug(f"Configuration details:\n{config.model_dump_json(indent=2)}")

        # Process data
        logger.info("Starting data generation...")

        hierarchy = Hierarchy(config)
        tables, roots, statics, dependency_tree = hierarchy.calculate_roots()
        processed_hierarchy = hierarchy.process_hierarchy(tables, dependency_tree)

        with open(os.path.join(temp_dir, "dependency_tree.txt"), "w") as f:
            f.write(" Processed Hierarchy\n\n")

            f.write("|" + "-" * 40 + "|\n")
            f.write(f"[{"Tables".center(40)}]\n")
            f.write("|" + "-" * 40 + "|\n")
            for table in tables:
                f.write(f"|{table.center(40)}|\n")
            f.write("|" + "-" * 40 + "|\n\n")

            f.write("|" + "-" * 40 + "|\n")
            f.write(f"|{"Roots".center(40)}|\n")
            f.write("|" + "-" * 40 + "|\n")
            for root in roots:
                f.write(f"| {root.center(38)} |\n")
            f.write("|" + "-" * 40 + "|\n\n")

            f.write("|" + "-" * 120 + "|\n")
            f.write(f"|{"Dependency Tree".center(120)}|\n")
            f.write("|" + "-" * 120 + "|\n")
            for dependency in dependency_tree:
                from_table, from_column, relation, to_table, to_column = dependency
                f.write(f"|{(from_table+"."+from_column).center(47)} | {relation.center(20)} | {(to_table+"."+to_column).center(47)}|\n")
            f.write("|" + "-" * 120 + "|\n\n")
           

        config_profiles = config.profiles

        if len(config_profiles) > 0:
            profile = config_profiles[0]
        else:
            profiler = Profiler(config, hierarchy)
            profile = profiler.build_profile()

        with open(os.path.join(temp_dir, "profile.json"), "w") as f:
            json.dump(profile.model_dump(), f, indent=2)

        with open(os.path.join(temp_dir, "profile.txt"), "w") as f:  
            f.write(" Processed Profile\n\n")  
            for key,value in profile.tables.items():

                if value.options:
                    f.write(table_logger([item.values["values"] for item in value.options], f"{key} [Static]"))
                    f.write("\n\n")
                else:
                    table = next((table for table in config.tables if table.name == key), None)
                    table_data = []
                    for column in table.columns:
                        row = {}
                        row["column"] = column.name
                        row["type"] = column.type
                        row["config"] = str(column.config)
                        if column.name in value.columns:
                            row["config"] = value.columns[column.name].root_prompt
                        table_data.append(row)
                    f.write(table_logger(table_data, f"{key}({value.count}) [Dynamic]"))
                    f.write("\n\n")

        generator = Generator()
        results =generator.generate(config, profile, processed_hierarchy)

        final = ""

        for key, value in results.items():
            if "values" in value[0]:
                value = [item["values"] for item in value]
            final += table_logger(value, key, ellipsis=True, max_column_width=40)
            final += "\n\n"


        with open("sample_tables.txt", "w") as f:
            f.write(final)


        # TODO: Add actual data generation logic here
        logger.warning("Data generation not yet implemented")

        # Save results if output path specified
        output_path = args.output if args.output else "results.json"
        logger.info(f"Saving results to: {output_path}")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved successfully")

        logger.info("✓ Processing completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Application error: {e}")
        if args.verbose:
            import traceback

            logger.error(f"Stack trace:\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
