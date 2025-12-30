import logging
import sys
import os
from config.settings import settings

def setup_logging(name):
    """
    Setup a logger with the given name using configuration settings.
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured to avoid duplicate logs
    if not logger.handlers:
        log_level = settings.get('logging.level', 'INFO')
        log_format = settings.get('logging.format', '%(asctime)s | %(levelname)s | %(name)s | %(message)s')

        formatter = logging.Formatter(log_format)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler (optional)
        log_file = settings.get('logging.file')
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"Failed to setup file logging: {e}")

        logger.setLevel(log_level)

    return logger
