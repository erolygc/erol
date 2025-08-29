"""
Configuration Management Module

This module handles loading and managing configuration settings
for the AI trading bot application.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig(BaseSettings):
    """Database configuration settings"""
    postgresql_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgresql_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgresql_database: str = Field(default="trading_bot", env="POSTGRES_DB")
    postgresql_username: str = Field(default="trading_user", env="POSTGRES_USER")
    postgresql_password: str = Field(default="trading_password", env="POSTGRES_PASSWORD")
    pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")
    
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")

class ExchangeConfig(BaseSettings):
    """Exchange API configuration settings"""
    binance_api_key: str = Field(default="", env="BINANCE_API_KEY")
    binance_api_secret: str = Field(default="", env="BINANCE_API_SECRET")
    binance_testnet: bool = Field(default=True, env="BINANCE_TESTNET")
    binance_rate_limit: int = Field(default=1200, env="BINANCE_RATE_LIMIT")
    
    gate_io_api_key: str = Field(default="", env="GATE_IO_API_KEY")
    gate_io_api_secret: str = Field(default="", env="GATE_IO_API_SECRET")
    gate_io_testnet: bool = Field(default=True, env="GATE_IO_TESTNET")
    gate_io_rate_limit: int = Field(default=1000, env="GATE_IO_RATE_LIMIT")

class TradingConfig(BaseSettings):
    """Trading configuration settings"""
    max_position_size: float = Field(default=0.1, env="MAX_POSITION_SIZE")
    max_daily_risk: float = Field(default=0.02, env="MAX_DAILY_RISK")
    stop_loss_multiplier: float = Field(default=2.0, env="STOP_LOSS_MULTIPLIER")
    take_profit_multiplier: float = Field(default=4.0, env="TAKE_PROFIT_MULTIPLIER")
    max_leverage: int = Field(default=5, env="MAX_LEVERAGE")
    default_leverage: int = Field(default=1, env="DEFAULT_LEVERAGE")
    
    symbols: list = Field(default=["BTCUSDT", "ETHUSDT", "BNBUSDT"], env="TRADING_SYMBOLS")
    timeframes: list = Field(default=["1m", "5m", "15m", "1h", "4h", "1d"], env="TRADING_TIMEFRAMES")

class MLConfig(BaseSettings):
    """Machine Learning configuration settings"""
    lstm_sequence_length: int = Field(default=60, env="LSTM_SEQUENCE_LENGTH")
    lstm_hidden_size: int = Field(default=128, env="LSTM_HIDDEN_SIZE")
    lstm_num_layers: int = Field(default=2, env="LSTM_NUM_LAYERS")
    lstm_dropout: float = Field(default=0.2, env="LSTM_DROPOUT")
    lstm_learning_rate: float = Field(default=0.001, env="LSTM_LEARNING_RATE")
    
    xgb_max_depth: int = Field(default=6, env="XGB_MAX_DEPTH")
    xgb_learning_rate: float = Field(default=0.1, env="XGB_LEARNING_RATE")
    xgb_n_estimators: int = Field(default=100, env="XGB_N_ESTIMATORS")
    xgb_subsample: float = Field(default=0.8, env="XGB_SUBSAMPLE")
    xgb_colsample_bytree: float = Field(default=0.8, env="XGB_COLSAMPLE_BYTREE")
    
    train_split: float = Field(default=0.7, env="TRAIN_SPLIT")
    validation_split: float = Field(default=0.15, env="VALIDATION_SPLIT")
    test_split: float = Field(default=0.15, env="TEST_SPLIT")
    batch_size: int = Field(default=32, env="BATCH_SIZE")
    epochs: int = Field(default=100, env="EPOCHS")
    early_stopping_patience: int = Field(default=10, env="EARLY_STOPPING_PATIENCE")

class DataCollectionConfig(BaseSettings):
    """Data collection configuration settings"""
    historical_start_date: str = Field(default="2020-01-01", env="HISTORICAL_START_DATE")
    historical_end_date: str = Field(default="2024-01-01", env="HISTORICAL_END_DATE")
    batch_size: int = Field(default=1000, env="BATCH_SIZE")
    
    websocket_enabled: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    reconnect_attempts: int = Field(default=5, env="RECONNECT_ATTEMPTS")
    heartbeat_interval: int = Field(default=30, env="HEARTBEAT_INTERVAL")

class NotificationConfig(BaseSettings):
    """Notification configuration settings"""
    telegram_enabled: bool = Field(default=True, env="TELEGRAM_ENABLED")
    telegram_bot_token: str = Field(default="", env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", env="TELEGRAM_CHAT_ID")
    
    email_enabled: bool = Field(default=False, env="EMAIL_ENABLED")
    email_smtp_server: str = Field(default="smtp.gmail.com", env="EMAIL_SMTP_SERVER")
    email_smtp_port: int = Field(default=587, env="EMAIL_SMTP_PORT")
    email_username: str = Field(default="", env="EMAIL_USERNAME")
    email_password: str = Field(default="", env="EMAIL_PASSWORD")

class DashboardConfig(BaseSettings):
    """Dashboard configuration settings"""
    host: str = Field(default="0.0.0.0", env="DASHBOARD_HOST")
    port: int = Field(default=8501, env="DASHBOARD_PORT")
    debug: bool = Field(default=False, env="DASHBOARD_DEBUG")
    theme: str = Field(default="dark", env="DASHBOARD_THEME")

class LoggingConfig(BaseSettings):
    """Logging configuration settings"""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    file: str = Field(default="logs/trading_bot.log", env="LOG_FILE")
    max_size: str = Field(default="100MB", env="LOG_MAX_SIZE")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

class MonitoringConfig(BaseSettings):
    """Monitoring configuration settings"""
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    metrics_interval: int = Field(default=60, env="METRICS_INTERVAL")
    
    health_checks_enabled: bool = Field(default=True, env="HEALTH_CHECKS_ENABLED")
    high_latency_threshold: int = Field(default=1000, env="HIGH_LATENCY_THRESHOLD")
    low_accuracy_threshold: float = Field(default=0.8, env="LOW_ACCURACY_THRESHOLD")
    data_delay_threshold: int = Field(default=300, env="DATA_DELAY_THRESHOLD")

class Config:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration"""
        self.config_file = config_file or "config/config.yaml"
        self._load_config()
        
        # Initialize sub-configs
        self.database = DatabaseConfig()
        self.exchange = ExchangeConfig()
        self.trading = TradingConfig()
        self.ml = MLConfig()
        self.data_collection = DataCollectionConfig()
        self.notifications = NotificationConfig()
        self.dashboard = DashboardConfig()
        self.logging = LoggingConfig()
        self.monitoring = MonitoringConfig()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as file:
                    self._raw_config = yaml.safe_load(file)
            except Exception as e:
                print(f"Warning: Could not load config file {config_path}: {e}")
                self._raw_config = {}
        else:
            print(f"Warning: Config file {config_path} not found, using defaults")
            self._raw_config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._raw_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self._raw_config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save configuration to file"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self._raw_config, file, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def validate(self) -> bool:
        """Validate configuration"""
        required_fields = [
            'database.postgresql_username',
            'database.postgresql_password',
            'exchange.binance_api_key',
            'exchange.binance_api_secret'
        ]
        
        for field in required_fields:
            if not self.get(field):
                print(f"Warning: Required configuration field '{field}' is not set")
                return False
        
        return True
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return (f"postgresql://{self.database.postgresql_username}:"
                f"{self.database.postgresql_password}@"
                f"{self.database.postgresql_host}:"
                f"{self.database.postgresql_port}/"
                f"{self.database.postgresql_database}")
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.database.redis_password:
            return (f"redis://:{self.database.redis_password}@"
                    f"{self.database.redis_host}:"
                    f"{self.database.redis_port}/{self.database.redis_db}")
        else:
            return f"redis://{self.database.redis_host}:{self.database.redis_port}/{self.database.redis_db}"
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'