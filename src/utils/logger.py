"""
Logging Configuration Module

This module handles logging setup and configuration for the AI trading bot.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from loguru import logger

class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to loguru"""
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging(config) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        config: Logging configuration object
        
    Returns:
        Configured logger instance
    """
    
    # Create logs directory if it doesn't exist
    log_file = Path(config.file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove default loguru handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=config.format,
        level=config.level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Add file handler with rotation
    logger.add(
        config.file,
        format=config.format,
        level=config.level,
        rotation=config.max_size,
        retention=config.backup_count,
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Configure specific loggers
    _configure_specific_loggers(config)
    
    return logger

def _configure_specific_loggers(config):
    """Configure specific loggers for different components"""
    
    # Trading logger
    trading_logger = logging.getLogger("trading")
    trading_logger.setLevel(getattr(logging, config.categories.get("trading", "INFO")))
    
    # Data collection logger
    data_logger = logging.getLogger("data_collection")
    data_logger.setLevel(getattr(logging, config.categories.get("data_collection", "INFO")))
    
    # ML models logger
    ml_logger = logging.getLogger("ml_models")
    ml_logger.setLevel(getattr(logging, config.categories.get("ml_models", "INFO")))
    
    # API calls logger
    api_logger = logging.getLogger("api_calls")
    api_logger.setLevel(getattr(logging, config.categories.get("api_calls", "WARNING")))
    
    # Errors logger
    error_logger = logging.getLogger("errors")
    error_logger.setLevel(getattr(logging, config.categories.get("errors", "ERROR")))

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific component
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class TradingLogger:
    """Custom logger for trading operations"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def signal_generated(self, symbol: str, signal: str, confidence: float, **kwargs):
        """Log signal generation"""
        self.logger.info(
            f"Signal generated - Symbol: {symbol}, Signal: {signal}, "
            f"Confidence: {confidence:.2f}, Details: {kwargs}"
        )
    
    def position_opened(self, symbol: str, side: str, size: float, price: float, **kwargs):
        """Log position opening"""
        self.logger.info(
            f"Position opened - Symbol: {symbol}, Side: {side}, "
            f"Size: {size}, Price: {price}, Details: {kwargs}"
        )
    
    def position_closed(self, symbol: str, side: str, size: float, price: float, pnl: float, **kwargs):
        """Log position closing"""
        self.logger.info(
            f"Position closed - Symbol: {symbol}, Side: {side}, "
            f"Size: {size}, Price: {price}, PnL: {pnl}, Details: {kwargs}"
        )
    
    def stop_loss_hit(self, symbol: str, side: str, price: float, loss: float):
        """Log stop loss hit"""
        self.logger.warning(
            f"Stop loss hit - Symbol: {symbol}, Side: {side}, "
            f"Price: {price}, Loss: {loss}"
        )
    
    def take_profit_hit(self, symbol: str, side: str, price: float, profit: float):
        """Log take profit hit"""
        self.logger.info(
            f"Take profit hit - Symbol: {symbol}, Side: {side}, "
            f"Price: {price}, Profit: {profit}"
        )
    
    def error_occurred(self, error: Exception, context: str = ""):
        """Log errors"""
        self.logger.error(
            f"Error occurred - Context: {context}, Error: {str(error)}",
            exc_info=True
        )
    
    def performance_metric(self, metric: str, value: float, **kwargs):
        """Log performance metrics"""
        self.logger.info(
            f"Performance metric - {metric}: {value}, Details: {kwargs}"
        )

class DataLogger:
    """Custom logger for data collection operations"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def data_received(self, source: str, symbol: str, data_type: str, count: int):
        """Log data reception"""
        self.logger.info(
            f"Data received - Source: {source}, Symbol: {symbol}, "
            f"Type: {data_type}, Count: {count}"
        )
    
    def data_processed(self, symbol: str, data_type: str, processing_time: float):
        """Log data processing"""
        self.logger.info(
            f"Data processed - Symbol: {symbol}, Type: {data_type}, "
            f"Time: {processing_time:.3f}s"
        )
    
    def data_error(self, source: str, error: Exception, **kwargs):
        """Log data errors"""
        self.logger.error(
            f"Data error - Source: {source}, Error: {str(error)}, Details: {kwargs}",
            exc_info=True
        )
    
    def connection_status(self, source: str, status: str, **kwargs):
        """Log connection status"""
        self.logger.info(
            f"Connection status - Source: {source}, Status: {status}, Details: {kwargs}"
        )

class MLLogger:
    """Custom logger for machine learning operations"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def model_training_started(self, model_name: str, dataset_size: int, **kwargs):
        """Log model training start"""
        self.logger.info(
            f"Model training started - Model: {model_name}, "
            f"Dataset size: {dataset_size}, Details: {kwargs}"
        )
    
    def model_training_completed(self, model_name: str, training_time: float, **kwargs):
        """Log model training completion"""
        self.logger.info(
            f"Model training completed - Model: {model_name}, "
            f"Training time: {training_time:.2f}s, Details: {kwargs}"
        )
    
    def model_prediction(self, model_name: str, symbol: str, prediction: float, confidence: float):
        """Log model predictions"""
        self.logger.info(
            f"Model prediction - Model: {model_name}, Symbol: {symbol}, "
            f"Prediction: {prediction:.4f}, Confidence: {confidence:.2f}"
        )
    
    def model_performance(self, model_name: str, metric: str, value: float, **kwargs):
        """Log model performance metrics"""
        self.logger.info(
            f"Model performance - Model: {model_name}, {metric}: {value:.4f}, Details: {kwargs}"
        )
    
    def model_error(self, model_name: str, error: Exception, **kwargs):
        """Log model errors"""
        self.logger.error(
            f"Model error - Model: {model_name}, Error: {str(error)}, Details: {kwargs}",
            exc_info=True
        )

# Create default loggers
trading_logger = TradingLogger("trading")
data_logger = DataLogger("data_collection")
ml_logger = MLLogger("ml_models")