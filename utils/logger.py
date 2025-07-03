#%%

# utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(name="scraper"):
    """
    Create and configure a logger with both file and console handlers.

    This function sets up a logger with the specified name. Log messages are
    written to a rotating log file in the 'logs' directory (named after the logger)
    and also output to the console. The log format includes the timestamp, log level,
    logger name, and message. Log files are rotated when they reach 5 MB, with up to
    5 backup files kept.

    Args:
        name (str): The name of the logger and the log file (default: "scraper").

    Returns:
        logging.Logger: A configured logger instance.

    Example:
        >>> logger = get_logger("my_module")
        >>> logger.info("This is an info message")
        # Logs to logs/my_module.log and prints to console
    """
            
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    file_handler = RotatingFileHandler(f"{log_dir}/{name}.log", maxBytes=5_000_000, backupCount=5)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
