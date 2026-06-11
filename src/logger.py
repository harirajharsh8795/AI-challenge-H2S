import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


class PipelineLogger:
    """A singleton logger class for the Redrob Intelligent Candidate Discovery pipeline.

    Provides console and rotating file logging configurations.
    """

    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(
        cls,
        name: str = "redrob_pipeline",
        log_level: int = logging.INFO,
        log_file: Optional[str] = "logs/pipeline.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
    ) -> logging.Logger:
        """Configures and returns the singleton logger instance.

        Args:
            name (str): The namespace name for the logger.
            log_level (int): Logging level (e.g., logging.INFO).
            log_file (Optional[str]): Path to the output log file. Disabled if None.
            max_bytes (int): Maximum size of log file before rotation.
            backup_count (int): Number of rotated log files to retain.

        Returns:
            logging.Logger: The configured Logger instance.
        """
        if cls._instance is not None:
            return cls._instance

        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        logger.propagate = False

        # Define output log format
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 1. Setup Console Handler (Standard Output)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 2. Setup Rotating File Handler
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._instance = logger
        return cls._instance
