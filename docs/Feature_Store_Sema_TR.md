# Feature Store Şeması - Point-in-Time Veri Tutarlılığı

## 1. Feature Store Genel Bakış

### 1.1 Amaç
- Zaman damgalı özellik depolama (point-in-time consistency)
- Backtest ve canlı trading arasında veri sızıntısı önleme
- Yüksek performanslı özellik servisi
- Özellik versiyonlama ve A/B test desteği

### 1.2 Temel Prensipler
```python
# Point-in-time principle
# Herhangi bir T zamanında, sadece T öncesi bilinen veriler kullanılır
def get_features_at_time(symbol: str, timestamp: datetime) -> dict:
    """T zamanındaki özellikler - sadece T öncesi veriler"""
    return features_store.as_of(symbol, timestamp)
```

## 2. Veri Modeli

### 2.1 Ana Tablolar

#### 2.1.1 Raw Market Data
```sql
-- Temel piyasa verileri
CREATE TABLE market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '1m', '5m', '1h', etc.
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    close_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    quote_volume DECIMAL(20,8),
    trades_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexing for time-series queries
CREATE INDEX idx_market_data_symbol_time ON market_data (symbol, timestamp DESC);
CREATE INDEX idx_market_data_timeframe ON market_data (timeframe, timestamp DESC);
```

#### 2.1.2 Order Book Data
```sql
-- Order book snapshots
CREATE TABLE orderbook_snapshots (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    bids JSONB NOT NULL, -- [[price, size], [price, size], ...]
    asks JSONB NOT NULL, -- [[price, size], [price, size], ...]
    best_bid DECIMAL(20,8),
    best_ask DECIMAL(20,8),
    mid_price DECIMAL(20,8),
    spread DECIMAL(20,8),
    total_bid_volume DECIMAL(20,8),
    total_ask_volume DECIMAL(20,8),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_orderbook_symbol_time ON orderbook_snapshots (symbol, timestamp DESC);
```

#### 2.1.3 Trade Data
```sql
-- Individual trades
CREATE TABLE trades (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    trade_id VARCHAR(50),
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    side VARCHAR(10), -- 'buy', 'sell'
    is_maker BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trades_symbol_time ON trades (symbol, timestamp DESC);
CREATE INDEX idx_trades_large ON trades (symbol, quantity DESC) WHERE quantity > 10000;
```

### 2.2 Feature Tables

#### 2.2.1 Technical Indicators
```sql
-- Teknik indikatörler
CREATE TABLE technical_indicators (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    
    -- Trend indicators
    sma_20 DECIMAL(20,8),
    sma_50 DECIMAL(20,8),
    ema_12 DECIMAL(20,8),
    ema_26 DECIMAL(20,8),
    macd DECIMAL(20,8),
    macd_signal DECIMAL(20,8),
    macd_histogram DECIMAL(20,8),
    adx DECIMAL(10,4),
    plus_di DECIMAL(10,4),
    minus_di DECIMAL(10,4),
    
    -- Momentum indicators
    rsi DECIMAL(10,4),
    stoch_k DECIMAL(10,4),
    stoch_d DECIMAL(10,4),
    williams_r DECIMAL(10,4),
    roc DECIMAL(10,4),
    
    -- Volatility indicators
    bb_upper DECIMAL(20,8),
    bb_middle DECIMAL(20,8),
    bb_lower DECIMAL(20,8),
    bb_width DECIMAL(10,4),
    atr DECIMAL(20,8),
    atr_normalized DECIMAL(10,4),
    
    -- Volume indicators
    obv DECIMAL(20,8),
    mfi DECIMAL(10,4),
    vwap DECIMAL(20,8),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_tech_indicators_unique ON technical_indicators (symbol, timestamp, timeframe);
```

#### 2.2.2 Market Microstructure Features
```sql
-- Piyasa mikro yapısı özellikleri
CREATE TABLE microstructure_features (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Order book features
    order_imbalance DECIMAL(10,4), -- (bid_vol - ask_vol) / (bid_vol + ask_vol)
    depth_imbalance DECIMAL(10,4),
    spread_bps DECIMAL(10,4), -- Spread in basis points
    bid_ask_ratio DECIMAL(10,4),
    
    -- Trade features
    buy_volume DECIMAL(20,8),
    sell_volume DECIMAL(20,8),
    trade_imbalance DECIMAL(10,4), -- (buy_vol - sell_vol) / total_vol
    avg_trade_size DECIMAL(20,8),
    large_trade_ratio DECIMAL(10,4), -- % of volume from large trades
    
    -- Price impact
    price_impact_1min DECIMAL(10,6),
    price_impact_5min DECIMAL(10,6),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_microstructure_unique ON microstructure_features (symbol, timestamp);
```

#### 2.2.3 Regime Features
```sql
-- Piyasa rejimi özellikleri
CREATE TABLE regime_features (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Volatility regime
    realized_vol_1h DECIMAL(10,6),
    realized_vol_4h DECIMAL(10,6),
    realized_vol_1d DECIMAL(10,6),
    vol_regime VARCHAR(20), -- 'low', 'medium', 'high'
    
    -- Trend regime
    trend_strength DECIMAL(10,4),
    trend_direction DECIMAL(10,4),
    trend_regime VARCHAR(20), -- 'trending_up', 'trending_down', 'sideways'
    
    -- Liquidity regime
    liquidity_score DECIMAL(10,4),
    liquidity_regime VARCHAR(20), -- 'high', 'medium', 'low'
    
    -- Combined regime
    market_regime VARCHAR(30),
    regime_confidence DECIMAL(10,4),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_regime_unique ON regime_features (symbol, timestamp);
```

#### 2.2.4 Sentiment Features
```sql
-- Sosyal medya ve sentiment
CREATE TABLE sentiment_features (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Social media metrics
    twitter_mentions INTEGER,
    twitter_sentiment DECIMAL(10,4), -- -1 to 1
    reddit_posts INTEGER,
    reddit_sentiment DECIMAL(10,4),
    telegram_messages INTEGER,
    
    -- News sentiment
    news_count INTEGER,
    news_sentiment DECIMAL(10,4),
    news_impact_score DECIMAL(10,4),
    
    -- Fear & Greed
    fear_greed_index INTEGER, -- 0-100
    
    -- Whale movements
    whale_net_flow DECIMAL(20,8),
    whale_transaction_count INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_sentiment_unique ON sentiment_features (symbol, timestamp);
```

### 2.3 Aggregate Feature Views

#### 2.3.1 Point-in-Time Feature View
```sql
-- Point-in-time tüm özellikler
CREATE VIEW features_pit AS
SELECT 
    md.symbol,
    md.timestamp,
    md.timeframe,
    
    -- Price features
    md.open_price,
    md.high_price,
    md.low_price,
    md.close_price,
    md.volume,
    
    -- Technical indicators
    ti.sma_20, ti.sma_50, ti.ema_12, ti.ema_26,
    ti.macd, ti.macd_signal, ti.macd_histogram,
    ti.rsi, ti.stoch_k, ti.stoch_d,
    ti.bb_upper, ti.bb_lower, ti.bb_width,
    ti.atr, ti.atr_normalized,
    ti.obv, ti.mfi, ti.vwap,
    
    -- Microstructure
    mf.order_imbalance, mf.spread_bps,
    mf.trade_imbalance, mf.large_trade_ratio,
    mf.price_impact_1min, mf.price_impact_5min,
    
    -- Regime
    rf.realized_vol_1h, rf.trend_strength,
    rf.market_regime, rf.regime_confidence,
    
    -- Sentiment
    sf.twitter_sentiment, sf.news_sentiment,
    sf.fear_greed_index, sf.whale_net_flow

FROM market_data md
LEFT JOIN technical_indicators ti ON (
    ti.symbol = md.symbol 
    AND ti.timestamp = md.timestamp 
    AND ti.timeframe = md.timeframe
)
LEFT JOIN microstructure_features mf ON (
    mf.symbol = md.symbol 
    AND mf.timestamp <= md.timestamp
    AND mf.timestamp > md.timestamp - INTERVAL '5 minutes'
)
LEFT JOIN regime_features rf ON (
    rf.symbol = md.symbol 
    AND rf.timestamp <= md.timestamp
    AND rf.timestamp > rf.timestamp - INTERVAL '1 hour'
)
LEFT JOIN sentiment_features sf ON (
    sf.symbol = md.symbol 
    AND sf.timestamp <= md.timestamp
    AND sf.timestamp > sf.timestamp - INTERVAL '1 hour'
);
```

## 3. Feature Store API

### 3.1 Python Interface

```python
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import asyncio
import asyncpg

class FeatureStore:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection_pool = None
        
    async def initialize(self):
        """Connection pool başlat"""
        self.connection_pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20
        )
        
    async def get_features_at_time(
        self, 
        symbol: str, 
        timestamp: datetime,
        timeframe: str = '1m'
    ) -> Dict:
        """Belirli bir zamandaki özellikleri getir (point-in-time)"""
        
        query = """
        SELECT * FROM features_pit 
        WHERE symbol = $1 
        AND timestamp <= $2 
        AND timeframe = $3
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        
        async with self.connection_pool.acquire() as conn:
            row = await conn.fetchrow(query, symbol, timestamp, timeframe)
            
        return dict(row) if row else None
        
    async def get_features_range(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        timeframe: str = '1m'
    ) -> pd.DataFrame:
        """Zaman aralığındaki özellikleri getir"""
        
        query = """
        SELECT * FROM features_pit 
        WHERE symbol = $1 
        AND timestamp BETWEEN $2 AND $3
        AND timeframe = $4
        ORDER BY timestamp ASC
        """
        
        async with self.connection_pool.acquire() as conn:
            rows = await conn.fetch(query, symbol, start_time, end_time, timeframe)
            
        return pd.DataFrame([dict(row) for row in rows])
        
    async def get_latest_features(
        self, 
        symbol: str, 
        timeframe: str = '1m'
    ) -> Dict:
        """En güncel özellikleri getir"""
        
        latest_time = datetime.utcnow()
        return await self.get_features_at_time(symbol, latest_time, timeframe)
        
    async def store_market_data(self, data: Dict):
        """Piyasa verisi kaydet"""
        
        query = """
        INSERT INTO market_data 
        (symbol, timestamp, timeframe, open_price, high_price, 
         low_price, close_price, volume, quote_volume, trades_count)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (symbol, timestamp, timeframe) DO UPDATE SET
        open_price = EXCLUDED.open_price,
        high_price = EXCLUDED.high_price,
        low_price = EXCLUDED.low_price,
        close_price = EXCLUDED.close_price,
        volume = EXCLUDED.volume
        """
        
        async with self.connection_pool.acquire() as conn:
            await conn.execute(
                query,
                data['symbol'], data['timestamp'], data['timeframe'],
                data['open'], data['high'], data['low'], data['close'],
                data['volume'], data.get('quote_volume'), data.get('trades_count')
            )
            
    async def store_features(self, table: str, features: Dict):
        """Özellik verilerini kaydet"""
        
        # Dynamic insert based on table schema
        columns = list(features.keys())
        values = list(features.values())
        placeholders = ', '.join([f'${i+1}' for i in range(len(values))])
        
        query = f"""
        INSERT INTO {table} ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT (symbol, timestamp) DO UPDATE SET
        {', '.join([f'{col} = EXCLUDED.{col}' for col in columns if col not in ['symbol', 'timestamp']])}
        """
        
        async with self.connection_pool.acquire() as conn:
            await conn.execute(query, *values)
```

### 3.2 Feature Computation Pipeline

```python
class FeatureComputationPipeline:
    def __init__(self, feature_store: FeatureStore):
        self.feature_store = feature_store
        self.indicators = TechnicalIndicators()
        
    async def compute_and_store_features(self, symbol: str, timeframe: str):
        """Özellikleri hesapla ve kaydet"""
        
        # Son 200 bar veriyi al (indikatörler için yeterli)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=200)
        
        market_data = await self.feature_store.get_features_range(
            symbol, start_time, end_time, timeframe
        )
        
        if len(market_data) < 50:  # Minimum data requirement
            return
            
        # Technical indicators hesapla
        tech_indicators = self.indicators.calculate_all(market_data)
        
        # Microstructure features
        microstructure = await self._calculate_microstructure_features(symbol)
        
        # Regime features
        regime = await self._calculate_regime_features(market_data)
        
        # Store features
        latest_timestamp = market_data.iloc[-1]['timestamp']
        
        await self.feature_store.store_features('technical_indicators', {
            'symbol': symbol,
            'timestamp': latest_timestamp,
            'timeframe': timeframe,
            **tech_indicators
        })
        
        await self.feature_store.store_features('microstructure_features', {
            'symbol': symbol,
            'timestamp': latest_timestamp,
            **microstructure
        })
        
        await self.feature_store.store_features('regime_features', {
            'symbol': symbol,
            'timestamp': latest_timestamp,
            **regime
        })
```

## 4. Data Consistency & Quality

### 4.1 Point-in-Time Consistency

```python
class PointInTimeValidator:
    """Point-in-time veri tutarlılığını doğrula"""
    
    def __init__(self, feature_store: FeatureStore):
        self.feature_store = feature_store
        
    async def validate_no_future_leak(self, symbol: str, timestamp: datetime) -> bool:
        """Gelecek veri sızıntısı kontrolü"""
        
        features = await self.feature_store.get_features_at_time(symbol, timestamp)
        
        # Tüm feature'ların timestamp'i kontrol et
        for key, value in features.items():
            if 'timestamp' in key.lower() and isinstance(value, datetime):
                if value > timestamp:
                    print(f"Future leak detected: {key} = {value} > {timestamp}")
                    return False
                    
        return True
        
    async def validate_feature_availability(
        self, 
        symbol: str, 
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, float]:
        """Özellik kullanılabilirlik oranları"""
        
        data = await self.feature_store.get_features_range(
            symbol, start_time, end_time
        )
        
        availability = {}
        for column in data.columns:
            non_null_ratio = data[column].notna().mean()
            availability[column] = non_null_ratio
            
        return availability
```

### 4.2 Data Quality Monitoring

```python
class DataQualityMonitor:
    def __init__(self, feature_store: FeatureStore):
        self.feature_store = feature_store
        
    async def check_data_freshness(self, symbol: str, max_delay_minutes: int = 5) -> bool:
        """Veri güncellik kontrolü"""
        
        latest_data = await self.feature_store.get_latest_features(symbol)
        
        if not latest_data:
            return False
            
        latest_timestamp = latest_data['timestamp']
        current_time = datetime.utcnow()
        delay = (current_time - latest_timestamp).total_seconds() / 60
        
        return delay <= max_delay_minutes
        
    async def detect_anomalies(self, symbol: str, lookback_hours: int = 24) -> List[str]:
        """Veri anomalilerini tespit et"""
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=lookback_hours)
        
        data = await self.feature_store.get_features_range(
            symbol, start_time, end_time
        )
        
        anomalies = []
        
        # Price anomalies
        price_change = data['close_price'].pct_change().abs()
        if price_change.max() > 0.2:  # 20% price jump
            anomalies.append("Extreme price movement detected")
            
        # Volume anomalies
        volume_zscore = (data['volume'] - data['volume'].mean()) / data['volume'].std()
        if volume_zscore.abs().max() > 5:
            anomalies.append("Extreme volume detected")
            
        # Missing data
        missing_ratio = data.isnull().mean().mean()
        if missing_ratio > 0.1:  # 10% missing data
            anomalies.append(f"High missing data ratio: {missing_ratio:.2%}")
            
        return anomalies
```

## 5. Performance Optimization

### 5.1 Caching Strategy

```python
import redis
import pickle
from typing import Optional

class FeatureCacheManager:
    def __init__(self, redis_client: redis.Redis, ttl_seconds: int = 300):
        self.redis = redis_client
        self.ttl = ttl_seconds
        
    def _make_key(self, symbol: str, timestamp: datetime, feature_type: str) -> str:
        """Cache key oluştur"""
        timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
        return f"features:{symbol}:{timestamp_str}:{feature_type}"
        
    async def get_cached_features(
        self, 
        symbol: str, 
        timestamp: datetime,
        feature_type: str = "all"
    ) -> Optional[Dict]:
        """Cache'den özellik getir"""
        
        key = self._make_key(symbol, timestamp, feature_type)
        cached_data = self.redis.get(key)
        
        if cached_data:
            return pickle.loads(cached_data)
        return None
        
    async def cache_features(
        self, 
        symbol: str, 
        timestamp: datetime,
        features: Dict,
        feature_type: str = "all"
    ):
        """Özellikleri cache'e kaydet"""
        
        key = self._make_key(symbol, timestamp, feature_type)
        serialized_data = pickle.dumps(features)
        
        self.redis.setex(key, self.ttl, serialized_data)
```

### 5.2 Batch Processing

```python
class BatchFeatureProcessor:
    def __init__(self, feature_store: FeatureStore, batch_size: int = 1000):
        self.feature_store = feature_store
        self.batch_size = batch_size
        
    async def process_historical_features(
        self, 
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ):
        """Geçmiş veriler için batch feature hesaplama"""
        
        current_date = start_date
        
        while current_date <= end_date:
            batch_end = min(
                current_date + timedelta(days=1), 
                end_date
            )
            
            # Process one day at a time
            await self._process_date_batch(symbol, current_date, batch_end)
            
            current_date = batch_end + timedelta(minutes=1)
            
    async def _process_date_batch(
        self, 
        symbol: str, 
        start_time: datetime, 
        end_time: datetime
    ):
        """Bir günlük batch işleme"""
        
        # Get raw data
        raw_data = await self.feature_store.get_features_range(
            symbol, start_time, end_time, '1m'
        )
        
        # Process in smaller chunks
        for i in range(0, len(raw_data), self.batch_size):
            chunk = raw_data.iloc[i:i+self.batch_size]
            
            # Calculate features for chunk
            features = self._calculate_features_batch(chunk)
            
            # Store features
            await self._store_features_batch(features)
```

## 6. Monitoring & Alerting

### 6.1 Feature Store Health Monitoring

```python
class FeatureStoreMonitor:
    def __init__(self, feature_store: FeatureStore):
        self.feature_store = feature_store
        
    async def health_check(self) -> Dict[str, Union[str, float]]:
        """Feature store sağlık kontrolü"""
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        try:
            # Database connection test
            await self.feature_store.connection_pool.fetchval('SELECT 1')
            health_status['checks']['database'] = 'ok'
            
            # Data freshness test
            latest_btc = await self.feature_store.get_latest_features('BTCUSDT')
            if latest_btc:
                delay_minutes = (datetime.utcnow() - latest_btc['timestamp']).total_seconds() / 60
                health_status['checks']['data_freshness'] = f'{delay_minutes:.1f}min'
                
                if delay_minutes > 10:
                    health_status['status'] = 'warning'
            else:
                health_status['checks']['data_freshness'] = 'no_data'
                health_status['status'] = 'critical'
                
            # Feature completeness
            if latest_btc:
                null_ratio = sum(1 for v in latest_btc.values() if v is None) / len(latest_btc)
                health_status['checks']['completeness'] = f'{(1-null_ratio)*100:.1f}%'
                
        except Exception as e:
            health_status['status'] = 'critical'
            health_status['error'] = str(e)
            
        return health_status
```

Bu Feature Store şeması, point-in-time veri tutarlılığını sağlayarak backtest ve canlı trading arasındaki tutarsızlıkları önler, yüksek performanslı veri erişimi sunar ve veri kalitesini sürekli izler.