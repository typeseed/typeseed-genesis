#!/usr/bin/env python3
"""
Examples demonstrating logging usage in TypeSeed Genesis.

Run this file to see how logging works at different levels
and with different configurations.
"""

from src.logging_config import (
    setup_logging,
    get_logger,
    log_performance,
    debug, info, warning, error, critical
)
import time


def example_basic_logging():
    """Example: Basic logging at different levels."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Logging Levels")
    print("=" * 60 + "\n")
    
    # Setup logger
    logger = setup_logging(level="DEBUG", use_color=True)
    
    logger.debug("This is a DEBUG message - detailed information for developers")
    logger.info("This is an INFO message - general informational messages")
    logger.warning("This is a WARNING message - something unexpected but not critical")
    logger.error("This is an ERROR message - something went wrong")
    logger.critical("This is a CRITICAL message - serious error, app may not continue")


def example_log_levels():
    """Example: Different log levels filter messages."""
    print("\n" + "=" * 60)
    print("Example 2: Log Level Filtering")
    print("=" * 60 + "\n")
    
    print("Setting log level to WARNING (only WARNING and above will show):\n")
    logger = setup_logging(level="WARNING", use_color=True)
    
    logger.debug("This DEBUG message won't appear")
    logger.info("This INFO message won't appear")
    logger.warning("This WARNING message WILL appear")
    logger.error("This ERROR message WILL appear")


def example_file_logging():
    """Example: Logging to a file."""
    print("\n" + "=" * 60)
    print("Example 3: Logging to File")
    print("=" * 60 + "\n")
    
    logger = setup_logging(
        level="DEBUG",
        log_file="example.log",
        log_dir="logs",
        use_color=True
    )
    
    logger.info("This message goes to both console and file!")
    logger.debug("Debug messages are always saved to file")
    logger.warning("Check logs/example.log to see all messages")


def example_no_color():
    """Example: Logging without colors."""
    print("\n" + "=" * 60)
    print("Example 4: Logging Without Colors")
    print("=" * 60 + "\n")
    
    logger = setup_logging(level="INFO", use_color=False)
    
    logger.info("This message has no colors")
    logger.warning("This warning also has no colors")
    logger.error("Plain text output - good for log files or CI/CD")


def example_detailed_format():
    """Example: Detailed logging format with file/line info."""
    print("\n" + "=" * 60)
    print("Example 5: Detailed Format (shows file:line)")
    print("=" * 60 + "\n")
    
    logger = setup_logging(level="DEBUG", detailed=True, use_color=True)
    
    logger.debug("This shows which file and line number the log came from")
    logger.info("Useful for debugging and tracing")


@log_performance
def slow_function():
    """Example function that takes time."""
    logger = get_logger()
    logger.info("Doing some work...")
    time.sleep(0.5)
    logger.info("Work completed!")
    return "result"


def example_performance_logging():
    """Example: Performance logging decorator."""
    print("\n" + "=" * 60)
    print("Example 6: Performance Logging")
    print("=" * 60 + "\n")
    
    setup_logging(level="DEBUG", use_color=True)
    
    print("Calling a function with @log_performance decorator:\n")
    result = slow_function()
    print(f"\nFunction returned: {result}")


def example_convenience_functions():
    """Example: Using convenience functions."""
    print("\n" + "=" * 60)
    print("Example 7: Convenience Functions")
    print("=" * 60 + "\n")
    
    setup_logging(level="DEBUG", use_color=True)
    
    print("You can use module-level functions instead of logger.method():\n")
    
    debug("Direct debug() call")
    info("Direct info() call")
    warning("Direct warning() call")
    error("Direct error() call")


def example_structured_logging():
    """Example: Structured logging with context."""
    print("\n" + "=" * 60)
    print("Example 8: Structured Logging with Context")
    print("=" * 60 + "\n")
    
    logger = setup_logging(level="INFO", use_color=True)
    
    # Log with context
    user_id = 12345
    action = "login"
    logger.info(f"User action: {action}", extra={"user_id": user_id})
    
    # Log with formatted strings
    tables_generated = 5
    records_created = 1000
    logger.info(f"Generated {tables_generated} tables with {records_created} total records")
    
    # Log errors with details
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Math error occurred: {e}")


def example_production_setup():
    """Example: Typical production logging setup."""
    print("\n" + "=" * 60)
    print("Example 9: Production Setup")
    print("=" * 60 + "\n")
    
    # Production: INFO level, with file logging, no colors for file
    logger = setup_logging(
        level="INFO",
        log_file="production.log",
        log_dir="logs",
        use_color=True,  # Colors for console
        detailed=False   # Less verbose for production
    )
    
    logger.info("Application started")
    logger.info("Processing configuration...")
    logger.warning("Retrying connection (attempt 1/3)")
    logger.info("Connection established")
    logger.info("Application running normally")


def example_development_setup():
    """Example: Typical development logging setup."""
    print("\n" + "=" * 60)
    print("Example 10: Development Setup")
    print("=" * 60 + "\n")
    
    # Development: DEBUG level, with colors, detailed format
    logger = setup_logging(
        level="DEBUG",
        log_file="development.log",
        log_dir="logs",
        use_color=True,
        detailed=True
    )
    
    logger.debug("Starting initialization...")
    logger.debug("Loading configuration from file")
    logger.info("Configuration loaded")
    logger.debug("Connecting to database...")
    logger.info("Database connection established")
    logger.debug("Application ready")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "LOGGING EXAMPLES - TYPESEED GENESIS" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    
    examples = [
        example_basic_logging,
        example_log_levels,
        example_file_logging,
        example_no_color,
        example_detailed_format,
        example_performance_logging,
        example_convenience_functions,
        example_structured_logging,
        example_production_setup,
        example_development_setup,
    ]
    
    for example_func in examples:
        try:
            example_func()
            time.sleep(0.5)  # Pause between examples
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nCheck the logs/ directory for log files created by these examples.")
    print("Tip: Run 'python cli.py --help' to see logging options for the CLI.\n")


if __name__ == '__main__':
    main()

