"""
Logging configuration and utilities
"""
 
import logging
import sys
from pathlib import Path
from datetime import datetime
 
 
def setup_logger(name: str, config=None) -> logging.Logger:
    """
    Setup a logger with both file and console handlers
    
    Args:
        name: Logger name (typically __name__)
        config: LogConfig object with logging settings
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    log_level = getattr(logging, 'INFO', logging.INFO)
    log_dir = None
    
    if config:
        log_level = getattr(logging, config.log_level, logging.INFO)
        log_dir = config.log_dir
    
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"vm_agent_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger