## Bitwisers – Yapay Zekâ Tabanlı Kripto Algo Trade Botu (MVP Proje Dokümanı)

### 1) Amaç ve Başarı Kriterleri
- **Amaç**: Çoklu kaynaktan veri toplayan, özellik (feature) mühendisliği yapan, ML/AI ile rejime duyarlı sinyal üreten ve hedge modda otomatik alım/satım yapan, düşük gecikmeli ve güvenli bir MVP botu kurmak.
- **Kritik Başarı Göstergeleri (MVP)**:
  - **Canlı hit-rate**: %55–65 (rejime göre)
  - **Sharpe (aylık, yıllıklandırılmış)**: ≥ 1.5
  - **Maks. günlük drawdown**: ≤ -3% (devre kesiciyle)
  - **Latency p95** (ingestion→order): ≤ 150 ms
  - **Slipaj/ücret payı**: Brüt PnL’nin ≤ %25’i

### 2) Kapsam
- **Borsalar**: Binance Futures (öncelik), Gate.io; orta vadede Bybit/OKX.
- **Veriler**: OHLCV (1m–1d), order book (L1–L10), trades, funding, open interest, long/short ratio, likidasyon akışı, sosyal duyarlılık (Twitter/Telegram/Reddit), haber şok göstergeleri.
- **İndikatör/Osilatör**: 100+ (RSI, MACD, BB, ATR, SuperTrend, Ichimoku, Stoch RSI, ADX, MFI, OBV, vb.).
- **Sinyal**: Long/Short + güven skoru + önerilen pozisyon büyüklüğü.
- **Yürütme**: Hedge mode, market/limit, post-only maker, reduce-only, risk yönetimi (SL/TP), kaldıraç 1–5x.

### 3) Üst Düzey Mimari
- **Event-driven mimari**: WebSocket akışları tek bir **event bus** (Kafka/Redis Streams) üzerinde; ingestion → feature compute → model → order servisleri ayrık consumer grupları.
- **Feature Store (point-in-time)**: Tüm öznitelikler zaman damgalı ve ileriye sızmasız tutulur (asof join + snapshot). Backtest ile canlı birebir uyuşur.
- **Model Sunumu**: TorchScript/ONNX ile hızlandırılmış inference; REST/gRPC servis.
- **Önbellek**: Redis (sıcak veri: son N bar, son N trade, hesaplanmış indikatörler, son order book özetleri).
- **Depolama**: Ham akışlar için Parquet (S3/MinIO); analitik için DuckDB/Polars; düşük gecikme için ClickHouse (opsiyonel).
- **Gözlemlenebilirlik**: Prometheus + Grafana; p95/p99 latency, throughput, hatalar, fill ratio.
- **Güvenlik**: API key KMS/Vault, IP whitelist, RBAC, audit trail, kill-switch.

### 4) Veri Katmanı
#### 4.1 Entegrasyonlar
- Binance Futures, Gate.io (REST + WebSocket). Kimlik bilgileri KMS/Vault, sadece okuma ve trade yetkileri ayrıştırılmış.

#### 4.2 Toplanan Veri Türleri
- **OHLCV**: Tüm zaman dilimleri; her dilimden min. 500 bar tutma hedefi.
- **Order Book**: L2 derinlik (top-k) snapshot + delta; dengesizlik ve spoofing analizleri için gereken alanlar.
- **Trades**: Taker/maker ayrımı; büyük hacim (whale) bayrakları.
- **Türev Metrikler**: Funding rate, open interest, long/short ratio, likidasyon akışı, perp-spot baz farkı.
- **Sosyal/Haber**: Tweet/mesaj hacmi, duygu skorları, kaynak ağırlığı, ">3σ" şok bayrakları.

#### 4.3 Veri Kalitesi ve Tutarlılık
- **Saat dilimi standardı**: UTC.
- **Schema enforcement**: Event versiyonlama, null/aykırı değer kuralları.
- **Gecikme yönetimi**: Kaynağa göre watermark; out-of-order toleransı.

### 5) Feature Engineering
- **Teknik İndikatörler**: RSI, StochRSI, MACD, BB, Keltner, ATR, ADX, OBV, MFI, Ichimoku, SuperTrend, CCI, Williams %R, vb.
- **Order Book Özellikleri**: Top-k kademelerde hacim dengesizliği, spread, mid-price momentum, kısa ömürlü büyük emir (spoofing) oranı.
- **Hacim/Anomali**: Z-skorlu hacim sapmaları, likidite kuruş basamakları, gap tespitleri.
- **Türev/Piyasa Mikro Yapısı**: Funding, ΔOI, L/S ratio, likidasyon yoğunluğu, perp-spot baz farkı.
- **Çapraz Varlık**: BTC.D, DXY, Nasdaq vadeli, alt/defi endeksleri.
- **Sentiment/NLP**: Kaynak ağırlıklı duyarlılık, spam/bot ayıklama, haber şokları.

### 6) Modelleme (AI/ML)
- **Rejim Tespiti**: Volatilite, ADX, likidite metrikleri ile 3–5 rejim (trend/yatay/çalkantı/illikit). Rejime göre model/parametre seçimi.
- **Etiketleme**: \(\tau_u\) (üst), \(\tau_l\) (alt) ve \(T\) (zaman) olmak üzere triple-barrier; hedef: "TP mi SL mi önce?" + k-bar getirisi.
- **Meta-Labeling**: Ana sinyalin üstüne ikinci katman onay modeli (XGBoost/LightGBM) ile yanlış sinyal azaltma.
- **Modeller**: LSTM/GRU (sekans), XGBoost/LightGBM (tabular), logistic/Platt ile kalibrasyon. Ensemble komitesi → güven skoru.
- **CV/Backtest**: Purged K-Fold + walk-forward; White’s Reality Check/SPA.

### 7) Backtest ve Değerlendirme
- **Gerçekçilik**: Komisyon, slipaj, funding; order book tabanlı fill olasılığı; latency senaryoları.
- **Stres Dönemleri**: 2020-03, 2021-05, 2022-11 (FTX), 2024 spot ETF vb.
- **Metrikler**: Hit-rate, Sharpe, Sortino, Max DD, Avg R-multiple, Tail risk, Kalibrasyon (Brier/ACE), Feature drift.

### 8) Trade Engine ve Risk
- **Emir Tipleri**: Market/Limit, Post-only (maker), Reduce-only, IOC/FOK (opsiyonel), kademeli giriş/çıkış (TWAP/VWAP).
- **Hedge Mode**: Long/short eşleme, net-exposure limitleri, flip kuralı.
- **Risk**: Pozisyon başına %1–2 VaR, günlük DD valfi (-%3), dinamik kaldıraç (rejim/vola ile 1–5x), SL %1–3, TP %5–15.
- **Slipaj Koruması**: Slipaj eşiği aşılırsa iptal/yeniden fiyatlama.

### 9) Operasyon, İzleme ve Uyarılar
- **Dashboard**: PnL, Winrate, Max DD, slipaj/ücret payı, canlı latency; rejim ve model durumları.
- **Uyarılar**: Telegram/e-posta: pozisyon aç/kapat, VaR aşıldı, veri/latency bozulması, model drift.
- **Model Sürümleme**: MLflow/W&B; canary dağıtım (%5 sermaye), KPI tutarsa %100.
- **Kill-switch**: Veri kopması, API hatası, DD eşiği → otomatik flat.

### 10) Güvenlik
- **Kimlik Bilgileri**: KMS/Vault, servis hesapları, minimal yetki ilkesi.
- **Ağ**: IP whitelist, VPC izolasyonu, WAF (opsiyonel).
- **Uyum ve İz**: Emir/karar audit logları, konfig değişim geçmişi.

### 11) MVP Aşamaları ve Teslimatlar
1. **Aşama 1 – Veri Toplama**
   - OHLCV, order book, trades (WS) → event bus
   - S3/Parquet ham veri, Redis sıcak cache
   - Teslim: Çalışan collector + temel dashboard metrikleri
2. **Aşama 2 – Feature Mühendisliği**
   - 100+ indikatör, order book ve türev metrikleri
   - Feature Store (point-in-time) iskeleti
   - Teslim: Feature view’lar ve doğrulama raporu
3. **Aşama 3 – ML/AI**
   - Triple-barrier etiketleme + meta-labeling
   - Rejim tespiti + model/parametre seçici
   - Teslim: Ensemble inference servisi + kalibrasyon raporu
4. **Aşama 4 – Trade Engine**
   - Hedge mode emirleri, risk kuralları, slipaj koruma
   - Teslim: Dry-run → küçük sermaye canary
5. **Aşama 5 – İzleme & Raporlama**
   - PnL/risk dashboard, uyarılar, model sürümleme akışı
6. **Aşama 6 – Güvenlik & Dayanıklılık**
   - API key güvenliği, kill-switch, failover (opsiyonel)

### 12) Riskler ve Varsayımlar
- Borsa API değişiklikleri, rate-limit; veri eksiklikleri.
- Slipaj ve likidite etkisi; canlı ile backtest farkları.
- Sentiment gürültüsü ve kaynak güvenilirliği.
- Operasyonel riskler: ağ kesintisi, hata modları.

### 13) Ekler
- **Sözlük**: Rejim, meta-label, triple-barrier, VaR/ES, canary deployment.
- **Kaynaklar**: De Prado (Advances in Financial ML), Lopez de Prado triple-barrier, MLflow/W&B dokümantasyonu.

