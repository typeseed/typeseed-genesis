"""
Logging configuration for TypeSeed Genesis.

Provides structured logging with console and file output,
log rotation, and different log levels.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SIMPLE_FORMAT = "%(levelname)s - %(message)s"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def __init__(self, fmt: str = DEFAULT_FORMAT, use_color: bool = True):
        super().__init__(fmt)
        self.use_color = use_color
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional color."""
        if self.use_color and record.levelname in self.COLORS:
            # Create a copy of the record to avoid modifying the original
            colored_record = logging.LogRecord(
                name=record.name,
                level=record.levelno,
                pathname=record.pathname,
                lineno=record.lineno,
                msg=record.msg,
                args=record.args,
                exc_info=record.exc_info,
            )
            colored_record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )
            return super().format(colored_record)
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    use_color: bool = True,
    detailed: bool = False,
) -> logging.Logger:
    """
    Set up application logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name (without path)
        log_dir: Directory for log files (default: "logs")
        use_color: Whether to use colored output for console
        detailed: Whether to use detailed format with file/line info
        
    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger("typeseed")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if use_color:
        console_format = DETAILED_FORMAT if detailed else DEFAULT_FORMAT
        console_formatter = ColoredFormatter(console_format, use_color=True)
    else:
        console_format = DETAILED_FORMAT if detailed else DEFAULT_FORMAT
        console_formatter = logging.Formatter(console_format)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file is specified)
    if log_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        file_path = log_path / log_file
        
        # Use rotating file handler (max 10MB, keep 5 backup files)
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(DETAILED_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {file_path}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "typeseed") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (default: "typeseed")
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str):
    """
    Change the log level for all handlers.
    
    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = get_logger()
    log_level = getattr(logging, level.upper())
    logger.setLevel(log_level)
    
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(log_level)


def log_performance(func):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_performance
        def my_function():
            pass
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = time.time()
        logger.debug(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.debug(f"Completed {func.__name__} in {elapsed_time:.4f}s")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"Failed {func.__name__} after {elapsed_time:.4f}s: {str(e)}"
            )
            raise
    
    return wrapper


# Create a default logger instance
_default_logger: Optional[logging.Logger] = None


def init_default_logger(
    level: str = "INFO",
    log_file: Optional[str] = None,
    **kwargs
) -> logging.Logger:
    """
    Initialize the default logger (call this once at application start).
    
    Args:
        level: Log level
        log_file: Optional log file name
        **kwargs: Additional arguments for setup_logging
        
    Returns:
        Configured logger
    """
    global _default_logger
    _default_logger = setup_logging(level=level, log_file=log_file, **kwargs)
    return _default_logger


# Convenience functions
def debug(msg: str, *args, **kwargs):
    """Log debug message."""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Log info message."""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Log warning message."""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Log error message."""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """Log critical message."""
    get_logger().critical(msg, *args, **kwargs)

