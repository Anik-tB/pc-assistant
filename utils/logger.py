"""
Logger Utility
Sets up logging for the application
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "pc_assistant", log_file: str = "./logs/assistant.log") -> logging.Logger:
    """
    Set up application logger

    Args:
        name: Logger name
        log_file: Path to log file

    Returns:
        Configured logger
    """
    # Create logs directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
