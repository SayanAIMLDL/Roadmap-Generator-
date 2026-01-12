"""
Centralized logging configuration for Shifu AI
Structured logging with proper error handling
"""
import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

class ShifuLogger:
    """Centralized logger with structured formatting"""
    
    def __init__(self, name: str = "shifu"):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with proper formatting"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_dir / f"shifu_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"Could not setup file logging: {e}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception and context"""
        if exception:
            message = f"{message} | Exception: {type(exception).__name__}: {str(exception)}"
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.error(message)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception and context"""
        if exception:
            message = f"{message} | Exception: {type(exception).__name__}: {str(exception)}"
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.critical(message)

# Global logger instance
shifu_logger = ShifuLogger()
