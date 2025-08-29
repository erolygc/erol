#!/usr/bin/env python3
"""
AI Trading Bot - Main Application Entry Point

This is the main entry point for the AI trading bot application.
It initializes all components and starts the trading system.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from utils.config import Config
from utils.logger import setup_logging
from data_collection.data_collector import DataCollector
from ml_models.model_manager import ModelManager
from trading_engine.trading_bot import TradingBot
from api.fastapi_app import create_app
from dashboard.streamlit_app import run_dashboard

# Global variables for graceful shutdown
data_collector = None
model_manager = None
trading_bot = None
api_app = None

async def main():
    """Main application function"""
    global data_collector, model_manager, trading_bot, api_app
    
    try:
        # Load configuration
        config = Config()
        
        # Setup logging
        logger = setup_logging(config.logging)
        logger.info("Starting AI Trading Bot...")
        
        # Initialize components
        logger.info("Initializing data collector...")
        data_collector = DataCollector(config)
        
        logger.info("Initializing model manager...")
        model_manager = ModelManager(config)
        
        logger.info("Initializing trading bot...")
        trading_bot = TradingBot(config, data_collector, model_manager)
        
        # Start components
        logger.info("Starting data collection...")
        await data_collector.start()
        
        logger.info("Starting model manager...")
        await model_manager.start()
        
        logger.info("Starting trading bot...")
        await trading_bot.start()
        
        # Create and start FastAPI
        logger.info("Starting API server...")
        api_app = create_app(trading_bot)
        
        # Start dashboard in a separate thread
        logger.info("Starting dashboard...")
        import threading
        dashboard_thread = threading.Thread(target=run_dashboard, args=(config,))
        dashboard_thread.daemon = True
        dashboard_thread.start()
        
        logger.info("AI Trading Bot started successfully!")
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    except Exception as e:
        logger.error(f"Error in main application: {e}")
        raise
    finally:
        await shutdown()

async def shutdown():
    """Graceful shutdown of all components"""
    logger = logging.getLogger(__name__)
    logger.info("Shutting down AI Trading Bot...")
    
    try:
        if trading_bot:
            await trading_bot.stop()
            logger.info("Trading bot stopped")
        
        if model_manager:
            await model_manager.stop()
            logger.info("Model manager stopped")
        
        if data_collector:
            await data_collector.stop()
            logger.info("Data collector stopped")
        
        logger.info("AI Trading Bot shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the main application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)