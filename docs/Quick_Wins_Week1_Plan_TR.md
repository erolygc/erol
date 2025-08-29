## Quick Wins – 1. Hafta Uygulama Planı

### Hedef (7 gün)
Gerçek zamanlı veri akışını, point-in-time feature iskeletini ve temel sinyal altyapısını çalışır hale getirmek; küçük sermaye olmadan dry-run’da uçtan uca test etmek.

### Gün 1–2: Veri Toplama ve Önbellek
- WebSocket kolektörleri: `ohlcv`, `trades`, `orderbook` (Binance Futures, 1–3 sembol: BTCUSDT, ETHUSDT).
- Redis: son N bar, son N trade, son order book özetini tut.
- S3/MinIO: ham akışları Parquet’e dök (saatlik dosyalar).
- Telemetri: p95 gecikme, event/drop sayacı, reconnect oranı.

### Gün 2–3: Feature Store İskeleti
- Bronze → Silver dönüşümleri (temizlik, hizalama).
- İlk feature view’lar: `fv_ta_1m` (RSI, MACD, BB, ATR, ADX), `fv_micro` (spread, ob_imbalance, mid_mom), `fv_deriv` (funding, dOI), `fv_sent` (mock skor).
- Asof join helper fonksiyonları (DuckDB/Polars) + snapshot meta alanları.

### Gün 3–4: Rejim Sınıflayıcı ve Etiket Hattı
- Basit kural tabanlı rejim sınıflayıcı (vola, ADX, likidite).
- Triple-barrier etiketleme (ATR tabanlı bariyerler, T=50–200 bar aralığı denemesi).
- Veri sızıntısı kontrolleri, purged split örnekleri.

### Gün 4–5: Basit Ensemble ve Meta-Label İskeleti
- LSTM (sekans) + XGBoost (tabular) minimal eğitim setup (küçük örnekleme).
- Meta-label için pipeline iskeleti; kalibrasyon (isotonic) örneği.
- Inference servisi: REST (FastAPI) veya gRPC; TorchScript/ONNX export denemesi.

### Gün 5–6: Trade Şablonları ve Risk Kuralları (Dry-run)
- Emir şablonları: market/limit, post-only, reduce-only, TWAP giriş denemesi (simülasyon).
- Risk: VaR tabanlı pozisyon boyutlandırma, günlük DD valfi, slipaj guard (simülasyon parametreleriyle).
- Telegram: sinyal/pozisyon bildirimleri (test kanalı).

### Gün 7: Uçtan Uca Dry-Run ve Rapor
- Canlı akış → feature → sinyal → risk → emir-sim → bildirim hattını uçtan uca çalıştır.
- Metrikler: hit-rate (sim), avg R, p95 latency, drop ratio, feature tazelik.
- Sonuç raporu ve sonraki hafta backlog’u.

### Teslimatlar
- Çalışan collector’lar (BTCUSDT/ETHUSDT), Redis cache, S3/Parquet yazımı.
- Feature Store iskeleti ve ilk feature view’lar.
- Rejim + triple-barrier + meta-label iskeletleri.
- Inference servisi (beta) ve risk/şablonlar (dry-run).
- Telemetri dashboard ve Telegram test bildirimleri.

