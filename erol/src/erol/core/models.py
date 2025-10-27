from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


TimestampMs = int


class Trade(BaseModel):
	exchange: Literal["binance"]
	symbol: str
	trade_id: int
	price: float
	quantity: float
	is_buyer_maker: bool
	timestamp: TimestampMs


class OrderBookLevel(BaseModel):
	price: float
	quantity: float


class OrderBookSnapshot(BaseModel):
	exchange: Literal["binance"]
	symbol: str
	bids: list[OrderBookLevel]
	asks: list[OrderBookLevel]
	last_update_id: int
	timestamp: TimestampMs


class Kline(BaseModel):
	exchange: Literal["binance"]
	symbol: str
	interval: str
	open_time: TimestampMs
	open: float
	high: float
	low: float
	close: float
	volume: float
	close_time: TimestampMs
	num_trades: int = Field(default=0)

