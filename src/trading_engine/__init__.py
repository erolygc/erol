"""
Trading Engine Package

This package contains the core trading engine functionality:
- Signal generation and processing
- Order management
- Position tracking
- Risk management integration
- Portfolio management
"""

from .trading_bot import TradingBot
from .signal_generator import SignalGenerator
from .order_manager import OrderManager
from .position_manager import PositionManager

__all__ = [
    'TradingBot',
    'SignalGenerator',
    'OrderManager',
    'PositionManager'
]