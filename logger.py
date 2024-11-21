# app/utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
from app.config import Config
import sys


def setup_logger(config: Config, logger_name: str = 'app_logger') -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    if "console" in config.logging.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File Handler with Rotation
    if "file" in config.logging.handlers and config.logging.file:
        file_handler = RotatingFileHandler(
            filename=config.logging.file.filename,
            maxBytes=config.logging.file.max_size,
            backupCount=config.logging.file.backup_count
        )
        file_handler.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Avoid duplicate logs
    logger.propagate = False

    logger.info("Logger has been configured.")
    return logger
