from __future__ import annotations

import asyncio
import json
import time
from typing import AsyncIterator

import httpx
import websockets

from ..core.models import Trade, OrderBookSnapshot, OrderBookLevel, Kline
from ..core.events import Event, EventType
from ..core.bus import EventBus
from ..utils.logging import get_logger


BINANCE_WS = "wss://stream.binance.com:9443/stream"
BINANCE_REST = "https://api.binance.com"


logger = get_logger(__name__)


def _topic(symbol: str, kind: str) -> str:
	return f"binance:{symbol.lower()}:{kind}"


async def stream_trades(symbol: str, bus: EventBus) -> None:
\tparams = {"streams": f"{symbol.lower()}@trade"}
	url = f"{BINANCE_WS}?streams={symbol.lower()}@trade"
	while True:
		try:
			async with websockets.connect(url, ping_interval=15, ping_timeout=20) as ws:
				async for raw in ws:
					msg = json.loads(raw)
					data = msg.get("data", {})
					trade = Trade(
						exchange="binance",
						symbol=symbol.upper(),
						trade_id=int(data.get("t", 0)),
						price=float(data.get("p", 0.0)),
						quantity=float(data.get("q", 0.0)),
						is_buyer_maker=bool(data.get("m", False)),
						timestamp=int(data.get("T", int(time.time() * 1000))),
					)
					event = Event(
						type=EventType.TRADE,
						payload=trade.model_dump(),
						topic=_topic(symbol, "trades"),
						timestamp=trade.timestamp,
					)
					await bus.publish(event.topic, event)
		except Exception as exc:
			logger.warning("trade stream error: %s; reconnecting in 2s", exc)
			await asyncio.sleep(2)


async def stream_order_book(symbol: str, bus: EventBus, depth: int = 20) -> None:
	# Binance offers diff depth streams; here we keep it simple with bookTicker snapshot polling as placeholder
	client = httpx.AsyncClient(base_url=BINANCE_REST, timeout=10)
	endpoint = "/api/v3/depth"
	params = {"symbol": symbol.upper(), "limit": depth}
	while True:
		try:
			resp = await client.get(endpoint, params=params)
			resp.raise_for_status()
			js = resp.json()
			snapshot = OrderBookSnapshot(
				exchange="binance",
				symbol=symbol.upper(),
				bids=[OrderBookLevel(price=float(p), quantity=float(q)) for p, q in js.get("bids", [])],
				asks=[OrderBookLevel(price=float(p), quantity=float(q)) for p, q in js.get("asks", [])],
				last_update_id=int(js.get("lastUpdateId", 0)),
				timestamp=int(time.time() * 1000),
			)
			event = Event(
				type=EventType.ORDER_BOOK,
				payload=snapshot.model_dump(),
				topic=_topic(symbol, "orderbook"),
				timestamp=snapshot.timestamp,
			)
			await bus.publish(event.topic, event)
			await asyncio.sleep(0.5)
		except Exception as exc:
			logger.warning("order book fetch error: %s", exc)
			await asyncio.sleep(2)


async def stream_klines(symbol: str, interval: str, bus: EventBus) -> None:
	url = f"{BINANCE_WS}?streams={symbol.lower()}@kline_{interval}"
	while True:
		try:
			async with websockets.connect(url, ping_interval=15, ping_timeout=20) as ws:
				async for raw in ws:
					msg = json.loads(raw).get("data", {}).get("k", {})
					k = Kline(
						exchange="binance",
						symbol=symbol.upper(),
						interval=interval,
						open_time=int(msg.get("t", 0)),
						open=float(msg.get("o", 0.0)),
						high=float(msg.get("h", 0.0)),
						low=float(msg.get("l", 0.0)),
						close=float(msg.get("c", 0.0)),
						volume=float(msg.get("v", 0.0)),
						close_time=int(msg.get("T", 0)),
						num_trades=int(msg.get("n", 0)),
					)
					event = Event(
						type=EventType.KLINE,
						payload=k.model_dump(),
						topic=_topic(symbol, f"kline:{interval}"),
						timestamp=k.close_time or k.open_time,
					)
					await bus.publish(event.topic, event)
		except Exception as exc:
			logger.warning("kline stream error: %s; reconnecting in 2s", exc)
			await asyncio.sleep(2)

