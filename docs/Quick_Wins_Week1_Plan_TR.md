# Quick Wins - 1. Hafta Uygulama Planı

## Genel Bakış
İlk 7 günde temel altyapıyı kurup çalışan bir prototip oluşturmak. Bu plan, hızlı sonuç alınabilecek adımları önceliklendirip momentum kazandırmayı hedefler.

## Günlük Plan

### 🚀 Gün 1: Temel Altyapı & Veri Toplama
**Hedef**: Binance'den real-time veri akışı kurulumu

#### Sabah (4 saat)
```bash
# Proje kurulumu
mkdir ai-trading-bot
cd ai-trading-bot
python -m venv venv
source venv/bin/activate

# Temel dependencies
pip install python-binance pandas numpy redis asyncio websockets
```

**Yapılacaklar**:
- [ ] Binance WebSocket bağlantısı
- [ ] BTCUSDT 1m mum verisi toplama
- [ ] Redis'e real-time veri yazma
- [ ] Basic logging sistemi

```python
# data_collector.py - Temel veri toplayıcı
import asyncio
import json
import redis
from binance import AsyncClient, BinanceSocketManager

class DataCollector:
    def __init__(self):
        self.client = None
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
    async def start_kline_socket(self, symbol='BTCUSDT'):
        """1 dakikalık mum verisi toplama"""
        self.client = await AsyncClient.create()
        bsm = BinanceSocketManager(self.client)
        
        socket = bsm.kline_socket(symbol, '1m')
        
        async with socket as stream:
            while True:
                msg = await stream.recv()
                await self.process_kline(msg)
                
    async def process_kline(self, msg):
        """Mum verisini işle ve Redis'e kaydet"""
        kline = msg['k']
        
        data = {
            'symbol': kline['s'],
            'timestamp': kline['t'],
            'open': float(kline['o']),
            'high': float(kline['h']),
            'low': float(kline['l']),
            'close': float(kline['c']),
            'volume': float(kline['v'])
        }
        
        # Redis'e kaydet
        key = f"kline:{data['symbol']}:{data['timestamp']}"
        self.redis_client.setex(key, 3600, json.dumps(data))
        
        print(f"Saved: {data['symbol']} - {data['close']}")

if __name__ == "__main__":
    collector = DataCollector()
    asyncio.run(collector.start_kline_socket())
```

#### Öğleden Sonra (4 saat)
- [ ] Order book veri toplama
- [ ] Trade data entegrasyonu
- [ ] Veri kalitesi kontrolü
- [ ] Docker container hazırlama

**Çıktı**: Çalışan veri toplama sistemi

---

### 📊 Gün 2: Feature Engineering Temelleri
**Hedef**: Temel teknik indikatörleri hesaplama

#### Sabah (4 saat)
```python
# indicators.py - Temel indikatörler
import pandas as pd
import numpy as np
from typing import Dict

class TechnicalIndicators:
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
        
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period).mean()
        
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
        
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD Indicator"""
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
```

**Yapılacaklar**:
- [ ] 20 temel indikatör implementasyonu
- [ ] Feature hesaplama pipeline'ı
- [ ] Redis'den veri okuma ve işleme
- [ ] Hesaplanan feature'ları kaydetme

#### Öğleden Sonra (4 saat)
- [ ] Feature validation
- [ ] Performance optimization (Numba)
- [ ] Batch processing capability
- [ ] Unit testler

**Çıktı**: Çalışan feature engineering sistemi

---

### 🤖 Gün 3: Basit ML Model & Rejim Tespiti
**Hedef**: İlk sinyal üretici model

#### Sabah (4 saat)
```python
# regime_detector.py - Basit rejim tespiti
import numpy as np
from sklearn.cluster import KMeans
from enum import Enum

class MarketRegime(Enum):
    TRENDING = "trending"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

class SimpleRegimeDetector:
    def __init__(self):
        self.model = KMeans(n_clusters=3, random_state=42)
        
    def detect_regime(self, data: pd.DataFrame) -> str:
        """Basit rejim tespiti"""
        
        # Feature'lar: volatilite, trend gücü, hacim
        features = []
        
        # Volatilite (20-period std)
        volatility = data['close'].pct_change().rolling(20).std().iloc[-1]
        
        # Trend gücü (son 20 barın R²'si)
        y = data['close'].tail(20).values
        x = np.arange(len(y))
        trend_strength = np.corrcoef(x, y)[0, 1] ** 2
        
        # Hacim oranı
        volume_ratio = data['volume'].iloc[-1] / data['volume'].rolling(20).mean().iloc[-1]
        
        features = np.array([[volatility, trend_strength, volume_ratio]])
        
        # Basit kural tabanlı rejim
        if trend_strength > 0.7:
            return MarketRegime.TRENDING.value
        elif volatility > data['close'].pct_change().rolling(100).std().mean():
            return MarketRegime.VOLATILE.value
        else:
            return MarketRegime.SIDEWAYS.value
```

**Yapılacaklar**:
- [ ] Basit rejim sınıflandırıcı
- [ ] İlk ML model (XGBoost)
- [ ] Long/Short sinyal üretimi
- [ ] Model evaluation metrikleri

#### Öğleden Sonra (4 saat)
- [ ] Backtest framework temeli
- [ ] Sinyal doğruluk ölçümü
- [ ] Model parameter tuning
- [ ] Cross-validation

**Çıktı**: Sinyal üreten ML model

---

### 📈 Gün 4: Paper Trading & Risk Management
**Hedef**: Sanal trading sistemi

#### Sabah (4 saat)
```python
# paper_trader.py - Sanal trading
class PaperTrader:
    def __init__(self, initial_balance=10000):
        self.balance = initial_balance
        self.positions = {}
        self.trade_history = []
        
    def open_position(self, symbol, side, size, price):
        """Pozisyon aç"""
        position_value = size * price
        
        if position_value > self.balance * 0.02:  # Max %2 risk
            return False
            
        position = {
            'symbol': symbol,
            'side': side,  # 'long' or 'short'
            'size': size,
            'entry_price': price,
            'timestamp': datetime.now(),
            'pnl': 0
        }
        
        self.positions[f"{symbol}_{len(self.positions)}"] = position
        return True
        
    def close_position(self, position_id, price):
        """Pozisyon kapat"""
        if position_id not in self.positions:
            return False
            
        position = self.positions[position_id]
        
        if position['side'] == 'long':
            pnl = (price - position['entry_price']) * position['size']
        else:
            pnl = (position['entry_price'] - price) * position['size']
            
        position['exit_price'] = price
        position['pnl'] = pnl
        
        self.balance += pnl
        self.trade_history.append(position)
        del self.positions[position_id]
        
        return True
        
    def get_performance_metrics(self):
        """Performans metrikleri"""
        if not self.trade_history:
            return {}
            
        pnls = [trade['pnl'] for trade in self.trade_history]
        
        return {
            'total_trades': len(pnls),
            'win_rate': sum(1 for pnl in pnls if pnl > 0) / len(pnls),
            'total_pnl': sum(pnls),
            'avg_pnl': np.mean(pnls),
            'sharpe_ratio': np.mean(pnls) / (np.std(pnls) + 1e-8)
        }
```

**Yapılacaklar**:
- [ ] Paper trading engine
- [ ] Risk management kuralları
- [ ] Position sizing algoritması
- [ ] Stop-loss/Take-profit

#### Öğleden Sonra (4 saat)
- [ ] Performance tracking
- [ ] Trade logging
- [ ] Risk metrics hesaplama
- [ ] Alert sistemi (Telegram)

**Çıktı**: Çalışan paper trading sistemi

---

### 🔧 Gün 5: System Integration & Monitoring
**Hedef**: Tüm bileşenleri entegre etme

#### Sabah (4 saat)
```python
# main_system.py - Ana sistem
class TradingSystem:
    def __init__(self):
        self.data_collector = DataCollector()
        self.indicators = TechnicalIndicators()
        self.regime_detector = SimpleRegimeDetector()
        self.model = None  # ML model
        self.paper_trader = PaperTrader()
        
    async def run(self):
        """Ana sistem döngüsü"""
        while True:
            try:
                # 1. En son veriyi al
                latest_data = await self.get_latest_data()
                
                # 2. Feature'ları hesapla
                features = self.calculate_features(latest_data)
                
                # 3. Rejim tespit et
                regime = self.regime_detector.detect_regime(latest_data)
                
                # 4. Sinyal üret
                signal = self.generate_signal(features, regime)
                
                # 5. Trade kararı
                if signal:
                    await self.execute_trade(signal)
                    
                # 6. Mevcut pozisyonları kontrol et
                await self.manage_positions()
                
                await asyncio.sleep(60)  # 1 dakika bekle
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(5)
```

**Yapılacaklar**:
- [ ] Ana sistem döngüsü
- [ ] Error handling
- [ ] Logging sistemi
- [ ] Configuration management

#### Öğleden Sonra (4 saat)
- [ ] Monitoring dashboard (basit web interface)
- [ ] Performance metrikleri görselleştirme
- [ ] System health checks
- [ ] Telegram bot entegrasyonu

**Çıktı**: Entegre çalışan sistem

---

### 📊 Gün 6: Testing & Validation
**Hedef**: Sistem testleri ve doğrulama

#### Sabah (4 saat)
- [ ] Unit testler tamamlama
- [ ] Integration testler
- [ ] Backtest sonuçları analizi
- [ ] Model performance validation

#### Öğleden Sonra (4 saat)
- [ ] Stress testing
- [ ] Error scenario testing
- [ ] Performance benchmarking
- [ ] Documentation güncelleme

**Çıktı**: Test edilmiş ve doğrulanmış sistem

---

### 🚀 Gün 7: Deployment & Production Ready
**Hedef**: Production ortamına hazırlık

#### Sabah (4 saat)
```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
      
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: trading_bot
      POSTGRES_USER: trader
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
      
  trading-bot:
    build: .
    depends_on:
      - redis
      - postgres
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://trader:secure_password@postgres:5432/trading_bot
    volumes:
      - ./logs:/app/logs
```

**Yapılacaklar**:
- [ ] Docker containerization
- [ ] Environment configuration
- [ ] Production logging
- [ ] Monitoring setup

#### Öğleden Sonra (4 saat)
- [ ] Cloud deployment (AWS/GCP)
- [ ] CI/CD pipeline kurulumu
- [ ] Backup stratejisi
- [ ] Security hardening

**Çıktı**: Production-ready sistem

---

## Hafta Sonu Değerlendirmesi

### Beklenen Çıktılar
1. ✅ **Çalışan Veri Toplama**: Real-time Binance verisi
2. ✅ **Feature Engineering**: 20+ teknik indikatör
3. ✅ **ML Pipeline**: Basit sinyal üretici model
4. ✅ **Paper Trading**: Sanal trading sistemi
5. ✅ **Monitoring**: Temel performans takibi
6. ✅ **Production Setup**: Containerized deployment

### Key Performance Indicators (KPIs)
- **Veri Gecikme**: <5 saniye
- **Feature Hesaplama**: <1 saniye
- **Sinyal Doğruluğu**: >%60 (ilk hafta hedefi)
- **System Uptime**: >%95
- **Trade Execution**: <10 saniye

### Sonraki Adımlar (2. Hafta)
1. **Model Geliştirme**: LSTM/Transformer modelleri
2. **Çoklu Borsa**: Gate.io, Bybit entegrasyonu
3. **Sosyal Medya**: Sentiment analizi ekleme
4. **Risk Management**: Gelişmiş risk algoritmaları
5. **Backtesting**: Kapsamlı geçmiş veri testleri

---

## Günlük Checklist Template

### Her Gün Yapılması Gerekenler
- [ ] **Sabah**: Sistem durumu kontrolü
- [ ] **Gün İçi**: Kod geliştirme ve test
- [ ] **Akşam**: Commit & push
- [ ] **Gece**: System monitoring

### Kritik Başarı Faktörleri
1. **Hız**: Her gün çalışan bir şey üret
2. **Test**: Her feature'ı hemen test et
3. **Monitor**: Sistem performansını sürekli izle
4. **Document**: Yaptığın her şeyi dokümante et
5. **Iterate**: Hızlı feedback döngüsü kur

Bu plan, 7 günde çalışan bir prototip oluşturmayı hedefler. Her gün sonunda elle tutulur bir çıktı olması motivasyonu yüksek tutar ve momentum kazandırır.