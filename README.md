# erol

End-to-end crypto AI bot MVP scaffolding.

Quick start:

1) Create and activate a virtual environment (Python 3.11+ recommended)
2) Install requirements
3) Configure `.env` (copy `.env.example`)
4) Collect OHLCV data

Commands:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
SYMBOL=BTC/USDT TIMEFRAMES=1m,5m,15m,1h,4h,1d LIMIT_PER_TF=500 python scripts/collect_ohlcv.py
```

Generated files:
- `data/<SYMBOL_REPLACED>/ohlcv.parquet`
- logs under `logs/`

Next steps (Quick Wins):
- WebSocket ingestion (trades & order book)
- Point-in-time Feature Store
- Core indicators and regime classifier
- Triple-barrier labeling and a minimal inference API