from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import AsyncIterator

from .events import Event


class EventBus(ABC):
	@abstractmethod
	async def publish(self, channel: str, event: Event) -> None:
		...

	@abstractmethod
	async def subscribe(self, channel: str) -> AsyncIterator[Event]:
		...


class InMemoryEventBus(EventBus):
	def __init__(self) -> None:
		self._channels: dict[str, asyncio.Queue[Event]] = {}

	def _get_queue(self, channel: str) -> asyncio.Queue[Event]:
		if channel not in self._channels:
			self._channels[channel] = asyncio.Queue()
		return self._channels[channel]

	async def publish(self, channel: str, event: Event) -> None:
		await self._get_queue(channel).put(event)

	async def subscribe(self, channel: str) -> AsyncIterator[Event]:
		queue = self._get_queue(channel)
		while True:
			yield await queue.get()

