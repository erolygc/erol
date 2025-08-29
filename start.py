#!/usr/bin/env python3
"""
AI Trading Bot - Startup Script

This script provides a simple way to start the AI trading bot
with different configurations and modes.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="AI Trading Bot Startup")
    parser.add_argument(
        "--mode", 
        choices=["development", "production", "backtest", "data-collection"],
        default="development",
        help="Running mode"
    )
    parser.add_argument(
        "--config", 
        type=str,
        default="config/config.yaml",
        help="Configuration file path"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["BTCUSDT", "ETHUSDT"],
        help="Trading symbols"
    )
    parser.add_argument(
        "--timeframes",
        nargs="+",
        default=["1h", "4h"],
        help="Trading timeframes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual trading)"
    )
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["ENVIRONMENT"] = args.mode
    os.environ["CONFIG_FILE"] = args.config
    os.environ["DRY_RUN"] = str(args.dry_run).lower()
    
    print(f"Starting AI Trading Bot in {args.mode} mode...")
    print(f"Configuration: {args.config}")
    print(f"Symbols: {args.symbols}")
    print(f"Timeframes: {args.timeframes}")
    print(f"Dry run: {args.dry_run}")
    
    try:
        # Import and run main application
        from src.main import main as app_main
        import asyncio
        
        asyncio.run(app_main())
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()