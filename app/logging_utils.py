import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"


def setup_logger(name, log_file=None):
    """Create a logger that writes to a file in the logs/ directory."""
    if log_file is None:
        log_file = f"{LOG_DIR}/{name}.log"
    
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
