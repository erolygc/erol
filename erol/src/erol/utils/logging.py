from __future__ import annotations

import logging
import sys
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(level: int = logging.INFO) -> None:
	"""Configure application-wide logging with Rich handler."""
	console = Console(stderr=True)
	handler = RichHandler(console=console, rich_tracebacks=True, show_time=False)
	logging.basicConfig(
		level=level,
		format="%(message)s",
		handlers=[handler],
	)
	for noisy in ("asyncio", "websockets", "httpx"):
		logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
	logger = logging.getLogger(name)
	if not logger.handlers:
		setup_logging()
	return logger

