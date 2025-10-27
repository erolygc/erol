from __future__ import annotations

from pathlib import Path
from typing import Iterable

import polars as pl


class FeatureStore:
	"""Simple point-in-time feature store using Parquet snapshots.

	Append-only writes, partitioned by symbol and feature group.
	"""

	def __init__(self, root: str | Path) -> None:
		self.root = Path(root)
		self.root.mkdir(parents=True, exist_ok=True)

	def _path(self, symbol: str, group: str) -> Path:
		return self.root / symbol.upper() / f"{group}.parquet"

	def write_snapshot(self, symbol: str, group: str, frame: pl.DataFrame) -> None:
		path = self._path(symbol, group)
		path.parent.mkdir(parents=True, exist_ok=True)
		frame.write_parquet(path)

	def read_asof(
		self, symbol: str, group: str, asof_ts: int, ts_col: str = "timestamp"
	) -> pl.DataFrame:
		path = self._path(symbol, group)
		if not path.exists():
			return pl.DataFrame()
		df = pl.read_parquet(path)
		return (
			df.filter(pl.col(ts_col) <= asof_ts)
			.sort(ts_col)
		)

