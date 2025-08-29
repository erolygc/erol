from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import polars as pl
import ta


@dataclass
class IndicatorConfig:
    rsi_period: int = 14
    ema_fast: int = 12
    ema_slow: int = 26
    bb_period: int = 20
    bb_std: float = 2.0
    atr_period: int = 14
    adx_period: int = 14
    stoch_rsi_period: int = 14


def _to_pandas(bars: pl.DataFrame) -> pd.DataFrame:
    df = bars.select(
        ["datetime", "open", "high", "low", "close", "volume", "symbol", "timeframe"]
    ).to_pandas()
    df = df.set_index("datetime")
    return df


def _to_polars(df: pd.DataFrame) -> pl.DataFrame:
    df = df.reset_index()
    return pl.from_pandas(df)


def compute_core_indicators(bars: pl.DataFrame, cfg: IndicatorConfig | None = None) -> pl.DataFrame:
    if bars.height == 0:
        return bars
    cfg = cfg or IndicatorConfig()
    pdf = _to_pandas(bars)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # EMAs
        ema_fast = ta.trend.EMAIndicator(pdf["close"], window=cfg.ema_fast).ema_indicator()
        ema_slow = ta.trend.EMAIndicator(pdf["close"], window=cfg.ema_slow).ema_indicator()
        # RSI
        rsi = ta.momentum.RSIIndicator(pdf["close"], window=cfg.rsi_period).rsi()
        # MACD
        macd_ind = ta.trend.MACD(pdf["close"], window_slow=cfg.ema_slow, window_fast=cfg.ema_fast)
        macd = macd_ind.macd()
        macd_signal = macd_ind.macd_signal()
        macd_hist = macd_ind.macd_diff()
        # Bollinger
        bb = ta.volatility.BollingerBands(pdf["close"], window=cfg.bb_period, window_dev=cfg.bb_std)
        bb_high = bb.bollinger_hband()
        bb_low = bb.bollinger_lband()
        # ATR
        atr = ta.volatility.AverageTrueRange(pdf["high"], pdf["low"], pdf["close"], window=cfg.atr_period).average_true_range()
        # ADX
        adx = ta.trend.ADXIndicator(pdf["high"], pdf["low"], pdf["close"], window=cfg.adx_period).adx()
        # Stoch RSI
        stoch_rsi = ta.momentum.StochRSIIndicator(pdf["close"], window=cfg.stoch_rsi_period).stochrsi()
        # OBV
        obv = ta.volume.OnBalanceVolumeIndicator(pdf["close"], pdf["volume"]).on_balance_volume()
        # MFI
        mfi = ta.volume.MFIIndicator(pdf["high"], pdf["low"], pdf["close"], pdf["volume"], window=cfg.rsi_period).money_flow_index()

    out = pdf.copy()
    out["ema_fast"] = ema_fast
    out["ema_slow"] = ema_slow
    out["rsi"] = rsi
    out["macd"] = macd
    out["macd_signal"] = macd_signal
    out["macd_hist"] = macd_hist
    out["bb_high"] = bb_high
    out["bb_low"] = bb_low
    out["atr"] = atr
    out["adx"] = adx
    out["stoch_rsi"] = stoch_rsi
    out["obv"] = obv
    out["mfi"] = mfi
    out["ema_cross"] = (out["ema_fast"] > out["ema_slow"]).astype(int)

    return _to_polars(out)


def select_columns(df: pl.DataFrame, include: Iterable[str]) -> pl.DataFrame:
    keep = [c for c in include if c in df.columns]
    return df.select(keep)

