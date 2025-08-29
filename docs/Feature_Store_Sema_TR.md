# Feature Store Şeması - Point-in-Time Veri Yapısı

## 1. Genel Bakış

Bu doküman, AI trading bot projesi için point-in-time (PIT) feature store şemasını tanımlar. Bu yapı, veri sızıntısını (data leakage) önlemek ve backtest ile canlı trading arasında tutarlılık sağlamak için tasarlanmıştır.

## 2. Veri Katmanları

### 2.1 Ham Veri Katmanı (Raw Data Layer)

#### 2.1.1 OHLCV Verileri
```sql
CREATE TABLE raw_ohlcv (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, exchange, timeframe, timestamp)
);
```

#### 2.1.2 Order Book Verileri
```sql
CREATE TABLE raw_orderbook (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    side VARCHAR(4) NOT NULL, -- 'bid' or 'ask'
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.1.3 Trade Verileri
```sql
CREATE TABLE raw_trades (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    side VARCHAR(4) NOT NULL, -- 'buy' or 'sell'
    trade_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.1.4 Sosyal Medya Verileri
```sql
CREATE TABLE raw_social_media (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL, -- 'twitter', 'telegram', 'reddit'
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    content TEXT,
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    engagement_count INTEGER,
    author_id VARCHAR(100),
    post_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 Feature Katmanı (Feature Layer)

#### 2.2.1 Teknik İndikatörler
```sql
CREATE TABLE features_technical (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Momentum İndikatörleri
    rsi DECIMAL(10,4),
    macd DECIMAL(20,8),
    macd_signal DECIMAL(20,8),
    macd_histogram DECIMAL(20,8),
    stoch_k DECIMAL(10,4),
    stoch_d DECIMAL(10,4),
    williams_r DECIMAL(10,4),
    cci DECIMAL(10,4),
    
    -- Trend İndikatörleri
    sma_20 DECIMAL(20,8),
    sma_50 DECIMAL(20,8),
    sma_200 DECIMAL(20,8),
    ema_12 DECIMAL(20,8),
    ema_26 DECIMAL(20,8),
    bollinger_upper DECIMAL(20,8),
    bollinger_middle DECIMAL(20,8),
    bollinger_lower DECIMAL(20,8),
    bollinger_width DECIMAL(10,4),
    bollinger_position DECIMAL(10,4),
    
    -- Volatilite İndikatörleri
    atr DECIMAL(20,8),
    bbw DECIMAL(10,4),
    kc_upper DECIMAL(20,8),
    kc_lower DECIMAL(20,8),
    kc_middle DECIMAL(20,8),
    
    -- Hacim İndikatörleri
    obv DECIMAL(20,8),
    mfi DECIMAL(10,4),
    vwap DECIMAL(20,8),
    volume_sma_20 DECIMAL(20,8),
    
    -- Ichimoku Bileşenleri
    tenkan_sen DECIMAL(20,8),
    kijun_sen DECIMAL(20,8),
    senkou_span_a DECIMAL(20,8),
    senkou_span_b DECIMAL(20,8),
    chikou_span DECIMAL(20,8),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, exchange, timeframe, timestamp)
);
```

#### 2.2.2 Order Book Features
```sql
CREATE TABLE features_orderbook (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Derinlik Analizi
    bid_depth_1 DECIMAL(20,8),
    bid_depth_5 DECIMAL(20,8),
    bid_depth_10 DECIMAL(20,8),
    ask_depth_1 DECIMAL(20,8),
    ask_depth_5 DECIMAL(20,8),
    ask_depth_10 DECIMAL(20,8),
    
    -- Spread Analizi
    spread DECIMAL(20,8),
    spread_percentage DECIMAL(10,4),
    
    -- Imbalance
    bid_ask_imbalance DECIMAL(10,4),
    order_flow_imbalance DECIMAL(10,4),
    
    -- Whale Detection
    large_orders_count INTEGER,
    large_orders_volume DECIMAL(20,8),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, exchange, timestamp)
);
```

#### 2.2.3 Sentiment Features
```sql
CREATE TABLE features_sentiment (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Genel Sentiment
    overall_sentiment DECIMAL(3,2),
    sentiment_volume INTEGER,
    sentiment_momentum DECIMAL(10,4),
    
    -- Platform Bazlı
    twitter_sentiment DECIMAL(3,2),
    telegram_sentiment DECIMAL(3,2),
    reddit_sentiment DECIMAL(3,2),
    
    -- Engagement Metrics
    total_mentions INTEGER,
    positive_mentions INTEGER,
    negative_mentions INTEGER,
    neutral_mentions INTEGER,
    
    -- Trend Analysis
    sentiment_trend_1h DECIMAL(10,4),
    sentiment_trend_4h DECIMAL(10,4),
    sentiment_trend_1d DECIMAL(10,4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

#### 2.2.4 Market Microstructure Features
```sql
CREATE TABLE features_microstructure (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Trade Size Analysis
    avg_trade_size DECIMAL(20,8),
    large_trade_ratio DECIMAL(10,4),
    trade_size_std DECIMAL(20,8),
    
    -- Price Impact
    price_impact_1m DECIMAL(10,4),
    price_impact_5m DECIMAL(10,4),
    
    -- Liquidity Metrics
    bid_ask_spread DECIMAL(20,8),
    effective_spread DECIMAL(20,8),
    realized_spread DECIMAL(20,8),
    
    -- Market Efficiency
    hurst_exponent DECIMAL(10,4),
    fractal_dimension DECIMAL(10,4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, exchange, timestamp)
);
```

### 2.3 Label Katmanı (Label Layer)

#### 2.3.1 Triple Barrier Labels
```sql
CREATE TABLE labels_triple_barrier (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Barrier Parameters
    upper_barrier DECIMAL(20,8),
    lower_barrier DECIMAL(20,8),
    time_barrier TIMESTAMP,
    
    -- Label Information
    label INTEGER, -- 1: upper hit, -1: lower hit, 0: time hit
    label_time TIMESTAMP,
    return_value DECIMAL(10,4),
    
    -- Meta Information
    barrier_type VARCHAR(20), -- 'fixed', 'atr_based', 'volatility_based'
    confidence_score DECIMAL(3,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, exchange, timeframe, timestamp)
);
```

#### 2.3.2 Meta Labels
```sql
CREATE TABLE labels_meta (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Primary Signal
    primary_signal INTEGER, -- 1: long, -1: short, 0: neutral
    primary_confidence DECIMAL(3,2),
    
    -- Meta Label
    meta_label INTEGER, -- 1: high_confidence, 0: low_confidence
    meta_confidence DECIMAL(3,2),
    
    -- Combined Signal
    final_signal INTEGER,
    final_confidence DECIMAL(3,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, exchange, timeframe, timestamp)
);
```

## 3. Point-in-Time Sorgulama

### 3.1 Feature Join Fonksiyonu
```sql
CREATE OR REPLACE FUNCTION get_features_asof(
    p_symbol VARCHAR(20),
    p_exchange VARCHAR(20),
    p_timestamp TIMESTAMP,
    p_timeframe VARCHAR(10) DEFAULT '1h'
)
RETURNS TABLE (
    symbol VARCHAR(20),
    exchange VARCHAR(20),
    timestamp TIMESTAMP,
    rsi DECIMAL(10,4),
    macd DECIMAL(20,8),
    sentiment_score DECIMAL(3,2),
    orderbook_imbalance DECIMAL(10,4),
    label INTEGER,
    label_confidence DECIMAL(3,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.symbol,
        t.exchange,
        t.timestamp,
        t.rsi,
        t.macd,
        s.overall_sentiment as sentiment_score,
        ob.bid_ask_imbalance as orderbook_imbalance,
        ltb.label,
        ltb.confidence_score as label_confidence
    FROM features_technical t
    LEFT JOIN features_sentiment s 
        ON t.symbol = s.symbol 
        AND t.timestamp >= s.timestamp 
        AND t.timestamp < s.timestamp + INTERVAL '1 hour'
    LEFT JOIN features_orderbook ob 
        ON t.symbol = ob.symbol 
        AND t.exchange = ob.exchange
        AND t.timestamp >= ob.timestamp 
        AND t.timestamp < ob.timestamp + INTERVAL '1 minute'
    LEFT JOIN labels_triple_barrier ltb 
        ON t.symbol = ltb.symbol 
        AND t.exchange = ltb.exchange
        AND t.timeframe = ltb.timeframe
        AND t.timestamp = ltb.timestamp
    WHERE t.symbol = p_symbol 
        AND t.exchange = p_exchange
        AND t.timeframe = p_timeframe
        AND t.timestamp <= p_timestamp
    ORDER BY t.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 Feature Store Snapshot
```sql
CREATE TABLE feature_snapshots (
    id BIGSERIAL PRIMARY KEY,
    snapshot_time TIMESTAMP NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    
    -- Technical Features (JSON)
    technical_features JSONB,
    
    -- Order Book Features (JSON)
    orderbook_features JSONB,
    
    -- Sentiment Features (JSON)
    sentiment_features JSONB,
    
    -- Microstructure Features (JSON)
    microstructure_features JSONB,
    
    -- Labels (JSON)
    labels JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_time, symbol, exchange, timeframe)
);
```

## 4. Veri Kalitesi Kontrolleri

### 4.1 Data Quality Checks
```sql
-- Missing Data Detection
CREATE OR REPLACE FUNCTION check_missing_data(
    p_symbol VARCHAR(20),
    p_start_time TIMESTAMP,
    p_end_time TIMESTAMP
)
RETURNS TABLE (
    timestamp TIMESTAMP,
    missing_features TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.timestamp,
        ARRAY[
            CASE WHEN t.rsi IS NULL THEN 'rsi' END,
            CASE WHEN s.overall_sentiment IS NULL THEN 'sentiment' END,
            CASE WHEN ob.bid_ask_imbalance IS NULL THEN 'orderbook' END
        ] as missing_features
    FROM features_technical t
    LEFT JOIN features_sentiment s ON t.symbol = s.symbol AND t.timestamp = s.timestamp
    LEFT JOIN features_orderbook ob ON t.symbol = ob.symbol AND t.timestamp = ob.timestamp
    WHERE t.symbol = p_symbol 
        AND t.timestamp BETWEEN p_start_time AND p_end_time
        AND (t.rsi IS NULL OR s.overall_sentiment IS NULL OR ob.bid_ask_imbalance IS NULL);
END;
$$ LANGUAGE plpgsql;
```

### 4.2 Data Consistency Checks
```sql
-- Outlier Detection
CREATE OR REPLACE FUNCTION detect_outliers(
    p_symbol VARCHAR(20),
    p_feature VARCHAR(50),
    p_threshold DECIMAL(10,4) DEFAULT 3.0
)
RETURNS TABLE (
    timestamp TIMESTAMP,
    feature_value DECIMAL(20,8),
    z_score DECIMAL(10,4)
) AS $$
BEGIN
    RETURN QUERY
    EXECUTE format('
        SELECT 
            timestamp,
            %I as feature_value,
            ABS((%I - AVG(%I) OVER ()) / STDDEV(%I) OVER ())) as z_score
        FROM features_technical 
        WHERE symbol = %L 
            AND ABS((%I - AVG(%I) OVER ()) / STDDEV(%I) OVER ())) > %L
    ', p_feature, p_feature, p_feature, p_feature, p_symbol, p_feature, p_feature, p_feature, p_threshold);
END;
$$ LANGUAGE plpgsql;
```

## 5. Performans Optimizasyonu

### 5.1 İndeksler
```sql
-- Ana indeksler
CREATE INDEX idx_ohlcv_symbol_time ON raw_ohlcv(symbol, timestamp);
CREATE INDEX idx_orderbook_symbol_time ON raw_orderbook(symbol, timestamp);
CREATE INDEX idx_trades_symbol_time ON raw_trades(symbol, timestamp);
CREATE INDEX idx_social_symbol_time ON raw_social_media(symbol, timestamp);

-- Feature indeksleri
CREATE INDEX idx_technical_symbol_time ON features_technical(symbol, timestamp);
CREATE INDEX idx_orderbook_features_symbol_time ON features_orderbook(symbol, timestamp);
CREATE INDEX idx_sentiment_symbol_time ON features_sentiment(symbol, timestamp);
CREATE INDEX idx_microstructure_symbol_time ON features_microstructure(symbol, timestamp);

-- Label indeksleri
CREATE INDEX idx_labels_symbol_time ON labels_triple_barrier(symbol, timestamp);
CREATE INDEX idx_meta_labels_symbol_time ON labels_meta(symbol, timestamp);
```

### 5.2 Partitioning
```sql
-- Zaman bazlı partitioning
CREATE TABLE raw_ohlcv_partitioned (
    LIKE raw_ohlcv INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Aylık partitionlar
CREATE TABLE raw_ohlcv_2024_01 PARTITION OF raw_ohlcv_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## 6. Monitoring ve Alerting

### 6.1 Data Freshness Monitoring
```sql
CREATE OR REPLACE FUNCTION check_data_freshness()
RETURNS TABLE (
    table_name TEXT,
    last_update TIMESTAMP,
    freshness_minutes INTEGER,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'raw_ohlcv'::TEXT as table_name,
        MAX(timestamp) as last_update,
        EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 60 as freshness_minutes,
        CASE 
            WHEN EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 60 < 5 THEN 'OK'
            WHEN EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 60 < 15 THEN 'WARNING'
            ELSE 'CRITICAL'
        END as status
    FROM raw_ohlcv
    UNION ALL
    SELECT 
        'features_technical'::TEXT,
        MAX(timestamp),
        EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 60,
        CASE 
            WHEN EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 60 < 10 THEN 'OK'
            WHEN EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) / 60 < 30 THEN 'WARNING'
            ELSE 'CRITICAL'
        END
    FROM features_technical;
END;
$$ LANGUAGE plpgsql;
```

Bu şema, AI trading bot projesi için gerekli tüm veri yapılarını point-in-time prensibiyle tanımlar ve veri sızıntısını önler.