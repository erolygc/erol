import asyncio
import typer
from rich.console import Console

from .__version__ import __version__
from .core.bus import InMemoryEventBus
from .ingestion.binance import stream_trades, stream_order_book, stream_klines
from .utils.logging import setup_logging


@app.callback()
def cli() -> None:
	"""Erol AI trading bot CLI."""
	return None


@app.command()
def version() -> None:
	"""Show package version."""
	console.print(f"Erol version: {__version__}")


def _install_uvloop_if_available() -> None:
	try:
		import uvloop  # type: ignore

		uvloop.install()
	except Exception:
		# Fallback to default event loop on unsupported platforms
		pass


@app.command()
def ingest(
	symbol: str = typer.Option("BTCUSDT", help="Trading symbol, e.g., BTCUSDT"),
	interval: str = typer.Option("1m", help="Kline interval, e.g., 1m, 5m, 1h"),
	orderbook: bool = typer.Option(True, help="Stream order book snapshots"),
	trades: bool = typer.Option(True, help="Stream trades"),
	klines: bool = typer.Option(True, help="Stream klines"),
) -> None:
	"""Run simple ingestion streams and print event counts."""
	setup_logging()
	bus = InMemoryEventBus()

	async def _run() -> None:
		consumed = {"trades": 0, "orderbook": 0, "klines": 0}

		async def consume(name: str, channel: str) -> None:
			async for _ in bus.subscribe(channel):
				consumed[name] += 1
				if consumed[name] % 50 == 0:
					console.print(f"[{name}] events: {consumed[name]}")

		producers = []
		consumers = []
		if trades:
			producers.append(asyncio.create_task(stream_trades(symbol, bus)))
			consumers.append(asyncio.create_task(consume("trades", f"binance:{symbol.lower()}:trades")))
		if orderbook:
			producers.append(asyncio.create_task(stream_order_book(symbol, bus)))
			consumers.append(asyncio.create_task(consume("orderbook", f"binance:{symbol.lower()}:orderbook")))
		if klines:
			producers.append(asyncio.create_task(stream_klines(symbol, interval, bus)))
			consumers.append(asyncio.create_task(consume("klines", f"binance:{symbol.lower()}:kline:{interval}")))

		await asyncio.gather(*producers, *consumers)

	asyncio.run(_run())


if __name__ == "__main__":
	_install_uvloop_if_available()
	app()

