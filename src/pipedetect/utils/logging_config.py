"""Logging configuration using loguru."""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    format_string: Optional[str] = None
) -> None:
    """Setup logging configuration using loguru.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_console: Whether to enable console logging
        format_string: Custom format string (optional)
    """
    # Remove default logger
    logger.remove()
    
    # Default format
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    # Add console handler if enabled
    if enable_console:
        logger.add(
            sys.stderr,
            format=format_string,
            level=log_level.upper(),
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            format=format_string,
            level=log_level.upper(),
            rotation="10 MB",
            retention="1 week",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        logger.info(f"Logging to file: {log_file}")
    
    logger.info(f"Logging configured at {log_level.upper()} level")


def get_log_level_from_verbosity(verbose_count: int) -> str:
    """Convert verbosity count to log level.
    
    Args:
        verbose_count: Number of -v flags
        
    Returns:
        Log level string
    """
    if verbose_count >= 2:
        return "DEBUG"
    elif verbose_count == 1:
        return "INFO" 
    else:
        return "WARNING" 