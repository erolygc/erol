## Feature Store Şeması (Point-in-Time)

### Hedef
Tüm özniteliklerin zaman damgalı, ileriye sızmasız, backtest-canlı uyumlu tutulduğu bir yapı. "asof join" prensibi ile kesit anında yalnızca o ana kadar bilinen veriler erişilir.

### Mantıksal Bileşenler
- **Raw Topics/Streams** (event bus):
  - `ohlcv.{symbol}.{interval}`
  - `orderbook.{symbol}.l2`
  - `trades.{symbol}`
  - `derivatives.{symbol}` (funding, OI, L/S, liquidation)
  - `sentiment.{symbol}` (tweet_count, score, source_weight, shock_flag)
  - `cross.market` (BTC.D, DXY, NQ futures vb.)

- **Bronze (Landing) Tables**: Raw event’lerin sıkıştırılmış Parquet/S3 deposu; şema versiyonlu.
  - `bronze_ohlcv(symbol, interval, ts, open, high, low, close, volume, vendor_ts, ingest_ts)`
  - `bronze_orderbook(symbol, ts, bids[topk], asks[topk], mid, spread_bps, vendor_ts, ingest_ts)`
  - `bronze_trades(symbol, ts, price, qty, side, taker, vendor_ts, ingest_ts)`
  - `bronze_deriv(symbol, ts, funding_rate, open_interest, ls_ratio, liquidation_buy, liquidation_sell, vendor_ts, ingest_ts)`
  - `bronze_sentiment(symbol, ts, msg_count, pos_score, neg_score, source_weight, shock_flag, vendor_ts, ingest_ts)`
  - `bronze_cross(ts, btc_d, dxy, nq, vendor_ts, ingest_ts)`

- **Silver (Cleaned/Aligned)**: Zaman hizalı, outlier temizliği, null doldurma kuralları.
  - `silver_ohlcv(symbol, interval, ts, o,h,l,c,v)`
  - `silver_orderbook(symbol, ts, mid, spread_bps, ob_imbalance_k1..kN, spoof_ratio)`
  - `silver_trades(symbol, ts, buy_vol, sell_vol, big_trade_flag)`
  - `silver_deriv(symbol, ts, funding_rate, d_oi, ls_ratio, liq_intensity)`
  - `silver_sentiment(symbol, ts, sent_score, shock_flag)`
  - `silver_cross(ts, btc_d, dxy, nq)`

- **Feature Views (Gold)**: Point-in-time snapshot + asof join ile oluşturulmuş öznitelik setleri.
  - `fv_ta_{interval}(symbol, ts, rsi_14, macd_12_26_9, bb_up, bb_mid, bb_low, atr_14, adx_14, ...)`
  - `fv_micro(symbol, ts, ob_imb_k1..kN, spread_bps, mid_mom_1s..5s, spoof_ratio, vola_1m)`
  - `fv_deriv(symbol, ts, funding_rate, d_oi, ls_ratio, liq_intensity, basis)`
  - `fv_sent(symbol, ts, sent_score, shock_flag, src_weighted)`
  - `fv_cross(ts, btc_d, dxy, nq)`
  - `fv_regime(symbol, ts, regime_label, regime_conf)`

### Point-in-Time Kuralları
- Her feature view, **valid_from, valid_to** aralığı ile snapshot’lanır.
- Model eğitiminde hedef zaman damgası \(t_0\) için yalnızca **ts ≤ t_0** olan veriler asof join ile birleştirilir.
- Gecikmesi olan kaynaklar (ör. funding) için **availability_lag** alanı tutulur ve \(t_0 - lag\) kısıtı uygulanır.

### Örnek Asof Join (SQL benzeri)
```sql
SELECT 
  target.symbol, target.ts,
  ta.*, micro.*, deriv.*, sent.*, cross.*
FROM targets AS target
LEFT JOIN fv_ta_1m   ta    ON ta.symbol=target.symbol   AND ta.ts   <= target.ts
LEFT JOIN fv_micro   micro ON micro.symbol=target.symbol AND micro.ts<= target.ts
LEFT JOIN fv_deriv   deriv ON deriv.symbol=target.symbol AND deriv.ts<= target.ts - deriv.availability_lag
LEFT JOIN fv_sent    sent  ON sent.symbol=target.symbol  AND sent.ts <= target.ts
LEFT JOIN fv_cross   cross ON cross.ts <= target.ts
QUALIFY ROW_NUMBER() OVER (PARTITION BY target.ts ORDER BY ta.ts DESC) = 1
```

### Saklama ve Erişim
- S3/MinIO + Parquet (büyük tarihsel veri), DuckDB/Polars (analitik), ClickHouse (opsiyonel düşük gecikme).
- Online özellik önbelleği: Redis (son N pencere), Kafka Streams state store.

### Kalite ve Gözlemlenebilirlik
- Şema versiyonlama, veri tazelik metrikleri, boşluk/aykırı kontrol raporları.
- Feature drift ve kalibrasyon izleme (Prometheus/Grafana + MLflow/W&B).

