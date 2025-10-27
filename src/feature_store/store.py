from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import polars as pl

from src.config import EXCHANGE
from src.utils import ensure_dirs


@dataclass
class DatasetLocator:
    base_dir: str
    dataset: str
    symbol: str
    timeframe: str

    def dir_path(self) -> Path:
        safe_symbol = self.symbol.replace("/", "_")
        return Path(self.base_dir) / self.dataset / safe_symbol / self.timeframe

    def snapshot_path(self, dt: datetime) -> Path:
        fname = dt.strftime("%Y%m%dT%H%M%S.parquet")
        return self.dir_path() / fname


class FeatureStore:
    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = base_dir or EXCHANGE.feature_store_dir
        ensure_dirs(self.base_dir)

    def save_snapshot(
        self,
        df: pl.DataFrame,
        dataset: str,
        symbol: str,
        timeframe: str,
        snapshot_time: Optional[datetime] = None,
    ) -> str:
        if "datetime" not in df.columns:
            raise ValueError("DataFrame must contain 'datetime' column")
        snapshot_time = snapshot_time or datetime.utcnow()
        loc = DatasetLocator(self.base_dir, dataset, symbol, timeframe)
        ensure_dirs(str(loc.dir_path()))
        path = loc.snapshot_path(snapshot_time)
        df.write_parquet(path)
        return str(path)

    def load_range(
        self,
        dataset: str,
        symbol: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pl.DataFrame:
        loc = DatasetLocator(self.base_dir, dataset, symbol, timeframe)
        dir_path = loc.dir_path()
        if not dir_path.exists():
            return pl.DataFrame()
        files = sorted(p for p in dir_path.glob("*.parquet"))
        if not files:
            return pl.DataFrame()
        df = pl.concat([pl.read_parquet(p) for p in files])
        if start:
            df = df.filter(pl.col("datetime") >= pl.datetime(start.year, start.month, start.day, start.hour, start.minute, start.second))
        if end:
            df = df.filter(pl.col("datetime") <= pl.datetime(end.year, end.month, end.day, end.hour, end.minute, end.second))
        return df.sort("datetime")

    @staticmethod
    def asof_join(
        left: pl.DataFrame,
        right: pl.DataFrame,
        on: str = "datetime",
        by: list[str] | None = None,
        tolerance: Optional[str] = None,
    ) -> pl.DataFrame:
        joined = left.join_asof(
            right,
            left_on=on,
            right_on=on,
            by=by,
            strategy="backward",
            tolerance=tolerance,
        )
        return joined

