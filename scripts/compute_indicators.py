#!/usr/bin/env python3
from __future__ import annotations

import polars as pl

from src.config import EXCHANGE
from src.feature_store.store import FeatureStore
from src.features.indicators import IndicatorConfig, compute_core_indicators
from src.utils import ensure_dirs


def main() -> None:
    symbol_safe = EXCHANGE.symbol.replace("/", "_")
    in_path = f"{EXCHANGE.data_dir}/{symbol_safe}/ohlcv.parquet"
    df = pl.read_parquet(in_path)
    features = compute_core_indicators(df)
    fs = FeatureStore()
    out = fs.save_snapshot(features, dataset="indicators", symbol=EXCHANGE.symbol, timeframe="mixed")
    print(f"Saved indicators snapshot: {out}")


if __name__ == "__main__":
    main()

