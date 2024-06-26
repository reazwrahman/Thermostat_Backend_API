# logging_config.py

import logging
from logging.handlers import RotatingFileHandler
import os

ERROR_LOG = "error.log"


def configure_logging():
    if os.path.exists(os.path.join(os.getcwd(), ERROR_LOG)):
        os.remove(ERROR_LOG)

    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.WARN)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("error.log")
    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.ERROR)

    # Create formatters and add it to handlers
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# Call the function to configure logging
configure_logging()
