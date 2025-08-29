from __future__ import annotations

import polars as pl


def rsi(df: pl.DataFrame, period: int = 14, close: str = "close") -> pl.Series:
	price = df[close]
	delta = price.diff()
	gain = pl.when(delta > 0).then(delta).otherwise(0)
	loss = (-pl.when(delta < 0).then(delta).otherwise(0))
	avg_gain = gain.ewm_mean(com=period - 1, adjust=False)
	avg_loss = loss.ewm_mean(com=period - 1, adjust=False)
	rs = avg_gain / (avg_loss + 1e-12)
	return 100 - (100 / (1 + rs))


def ema(s: pl.Series, period: int) -> pl.Series:
	return s.ewm_mean(com=period - 1, adjust=False)


def macd(
	df: pl.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, close: str = "close"
) -> tuple[pl.Series, pl.Series, pl.Series]:
	fast_ema = ema(df[close], fast)
	slow_ema = ema(df[close], slow)
	macd_line = fast_ema - slow_ema
	signal_line = ema(macd_line, signal)
	hist = macd_line - signal_line
	return macd_line, signal_line, hist


def bollinger_bands(
	df: pl.DataFrame, period: int = 20, std_mult: float = 2.0, close: str = "close"
) -> tuple[pl.Series, pl.Series, pl.Series]:
	ma = df[close].rolling_mean(window_size=period)
	std = df[close].rolling_std(window_size=period)
	upper = ma + std_mult * std
	lower = ma - std_mult * std
	return lower, ma, upper


def atr(df: pl.DataFrame, period: int = 14) -> pl.Series:
	true_range = (
		pl.concat(
			[
				(df["high"] - df["low"]).abs(),
				(df["high"] - df["close"].shift(1)).abs(),
				(df["low"] - df["close"].shift(1)).abs(),
			]
		)
		.max(axis=1)
	)
	return true_range.ewm_mean(com=period - 1, adjust=False)

