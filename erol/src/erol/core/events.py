from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class EventType(str, Enum):
	TRADE = "trade"
	ORDER_BOOK = "order_book"
	KLINE = "kline"


class Event(BaseModel):
	type: EventType
	payload: dict
	topic: str
	timestamp: int

