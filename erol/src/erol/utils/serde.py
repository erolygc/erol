from __future__ import annotations

import orjson


def to_json(obj: object) -> bytes:
	return orjson.dumps(obj)


def from_json(data: bytes) -> object:
	return orjson.loads(data)

