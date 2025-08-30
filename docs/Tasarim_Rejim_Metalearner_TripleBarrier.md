# Tasarım: Piyasa Rejimi Tespiti, Meta-Learning ve Triple-Barrier Sistem

## 1. Piyasa Rejimi Tespiti (Market Regime Detection)

### 1.1 Rejim Kategorileri

```python
class MarketRegime(Enum):
    TRENDING_UP = "trending_up"      # Güçlü yükseliş trendi
    TRENDING_DOWN = "trending_down"  # Güçlü düşüş trendi  
    SIDEWAYS = "sideways"           # Yatay hareket
    HIGH_VOLATILITY = "high_vol"    # Yüksek volatilite
    LOW_LIQUIDITY = "low_liquidity" # Düşük likidite
```

### 1.2 Rejim Tespiti İndikatörleri

#### 1.2.1 Trend Gücü Metrikleri
```python
def calculate_trend_strength(data):
    """Trend gücü hesaplama"""
    adx = ta.ADX(data.high, data.low, data.close, timeperiod=14)
    
    # Trend direction
    plus_di = ta.PLUS_DI(data.high, data.low, data.close, timeperiod=14)
    minus_di = ta.MINUS_DI(data.high, data.low, data.close, timeperiod=14)
    
    # Price momentum
    roc = ta.ROC(data.close, timeperiod=20)
    
    return {
        'adx': adx,
        'trend_direction': plus_di - minus_di,
        'momentum': roc
    }
```

#### 1.2.2 Volatilite Ölçümleri
```python
def calculate_volatility_metrics(data):
    """Volatilite rejimi tespiti"""
    
    # Realized volatility (20-period)
    returns = data.close.pct_change()
    realized_vol = returns.rolling(20).std() * np.sqrt(24*365)  # Annualized
    
    # ATR normalized
    atr = ta.ATR(data.high, data.low, data.close, timeperiod=14)
    atr_normalized = atr / data.close
    
    # Bollinger Band width
    bb_upper, bb_middle, bb_lower = ta.BBANDS(data.close, timeperiod=20)
    bb_width = (bb_upper - bb_lower) / bb_middle
    
    return {
        'realized_vol': realized_vol,
        'atr_normalized': atr_normalized, 
        'bb_width': bb_width
    }
```

#### 1.2.3 Likidite Metrikleri
```python
def calculate_liquidity_metrics(data, orderbook_data):
    """Likidite rejimi analizi"""
    
    # Volume-based metrics
    volume_ma = data.volume.rolling(20).mean()
    volume_ratio = data.volume / volume_ma
    
    # Order book depth
    bid_depth = orderbook_data.bids.sum()
    ask_depth = orderbook_data.asks.sum()
    total_depth = bid_depth + ask_depth
    
    # Spread metrics
    spread = (orderbook_data.best_ask - orderbook_data.best_bid)
    spread_bps = (spread / orderbook_data.mid_price) * 10000
    
    return {
        'volume_ratio': volume_ratio,
        'order_depth': total_depth,
        'spread_bps': spread_bps
    }
```

### 1.3 Rejim Sınıflandırıcı Model

```python
class RegimeClassifier:
    def __init__(self):
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def prepare_features(self, data):
        """Rejim tespiti için feature hazırlama"""
        features = pd.DataFrame()
        
        # Trend features
        trend_metrics = calculate_trend_strength(data)
        features['adx'] = trend_metrics['adx']
        features['trend_direction'] = trend_metrics['trend_direction']
        features['momentum'] = trend_metrics['momentum']
        
        # Volatility features  
        vol_metrics = calculate_volatility_metrics(data)
        features['realized_vol'] = vol_metrics['realized_vol']
        features['atr_normalized'] = vol_metrics['atr_normalized']
        features['bb_width'] = vol_metrics['bb_width']
        
        # Additional features
        features['rsi'] = ta.RSI(data.close, timeperiod=14)
        features['macd_signal'] = ta.MACD(data.close)[2]  # MACD histogram
        
        return features.fillna(method='ffill').dropna()
        
    def create_labels(self, data):
        """Rejim etiketleri oluşturma"""
        labels = []
        
        for i in range(len(data)):
            # Trend strength
            adx_val = data.iloc[i]['adx']
            trend_dir = data.iloc[i]['trend_direction'] 
            vol = data.iloc[i]['realized_vol']
            
            if adx_val > 25:  # Strong trend
                if trend_dir > 0:
                    label = MarketRegime.TRENDING_UP.value
                else:
                    label = MarketRegime.TRENDING_DOWN.value
            elif vol > 0.8:  # High volatility threshold
                label = MarketRegime.HIGH_VOLATILITY.value
            else:
                label = MarketRegime.SIDEWAYS.value
                
            labels.append(label)
            
        return labels
        
    def train(self, data):
        """Model eğitimi"""
        features = self.prepare_features(data)
        labels = self.create_labels(features)
        
        X_scaled = self.scaler.fit_transform(features)
        self.model.fit(X_scaled, labels)
        
    def predict(self, data):
        """Rejim tahmini"""
        features = self.prepare_features(data)
        X_scaled = self.scaler.transform(features)
        
        prediction = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return prediction[-1], probabilities[-1]  # Latest prediction
```

## 2. Meta-Learning Sistemi

### 2.1 Strateji Havuzu

```python
class TradingStrategy:
    def __init__(self, name, regime_affinity):
        self.name = name
        self.regime_affinity = regime_affinity  # Hangi rejimlerde iyi çalışır
        self.performance_history = []
        self.current_weight = 1.0
        
class StrategyPool:
    def __init__(self):
        self.strategies = {
            'trend_following': TradingStrategy(
                'trend_following', 
                [MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN]
            ),
            'mean_reversion': TradingStrategy(
                'mean_reversion',
                [MarketRegime.SIDEWAYS]
            ),
            'breakout': TradingStrategy(
                'breakout',
                [MarketRegime.HIGH_VOLATILITY]
            ),
            'scalping': TradingStrategy(
                'scalping',
                [MarketRegime.SIDEWAYS, MarketRegime.LOW_LIQUIDITY]
            )
        }
```

### 2.2 Meta-Learner Implementation

```python
class MetaLearner:
    def __init__(self, strategy_pool):
        self.strategy_pool = strategy_pool
        self.regime_classifier = RegimeClassifier()
        self.performance_tracker = PerformanceTracker()
        
    def select_strategy(self, current_data, regime_prediction):
        """Mevcut rejim için en uygun stratejiyi seç"""
        
        # Rejim uyumlu stratejileri filtrele
        compatible_strategies = []
        for strategy_name, strategy in self.strategy_pool.strategies.items():
            if regime_prediction in strategy.regime_affinity:
                compatible_strategies.append((strategy_name, strategy))
        
        if not compatible_strategies:
            # Fallback to best performing strategy
            return self._get_best_performing_strategy()
            
        # Son performansa göre ağırlıklandır
        strategy_scores = {}
        for strategy_name, strategy in compatible_strategies:
            recent_performance = self._calculate_recent_performance(strategy)
            regime_fit_score = self._calculate_regime_fit(strategy, regime_prediction)
            
            final_score = 0.7 * recent_performance + 0.3 * regime_fit_score
            strategy_scores[strategy_name] = final_score
            
        # En yüksek skora sahip stratejiyi seç
        best_strategy = max(strategy_scores, key=strategy_scores.get)
        return best_strategy
        
    def _calculate_recent_performance(self, strategy, lookback_days=30):
        """Son N günlük performans"""
        recent_trades = strategy.performance_history[-lookback_days:]
        if not recent_trades:
            return 0.5  # Neutral score
            
        win_rate = sum(1 for trade in recent_trades if trade > 0) / len(recent_trades)
        avg_return = np.mean(recent_trades)
        
        # Normalize to 0-1 scale
        performance_score = min(max(win_rate * 0.6 + avg_return * 0.4, 0), 1)
        return performance_score
        
    def _calculate_regime_fit(self, strategy, current_regime):
        """Strateji-rejim uyum skoru"""
        if current_regime in strategy.regime_affinity:
            return 1.0
        else:
            return 0.2  # Düşük ama sıfır olmayan skor
            
    def update_performance(self, strategy_name, trade_result):
        """Strateji performansını güncelle"""
        strategy = self.strategy_pool.strategies[strategy_name]
        strategy.performance_history.append(trade_result)
        
        # Sliding window (son 100 trade)
        if len(strategy.performance_history) > 100:
            strategy.performance_history.pop(0)
            
        # Ağırlık güncelleme (adaptive)
        recent_performance = self._calculate_recent_performance(strategy)
        strategy.current_weight = recent_performance
```

## 3. Triple-Barrier Labeling Sistemi

### 3.1 Triple-Barrier Konsepti

```python
class TripleBarrierLabeler:
    def __init__(self, profit_target=0.02, stop_loss=0.01, max_holding_period=24):
        """
        profit_target: Take profit seviyesi (% olarak)
        stop_loss: Stop loss seviyesi (% olarak)  
        max_holding_period: Maksimum tutma süresi (bar sayısı)
        """
        self.profit_target = profit_target
        self.stop_loss = stop_loss
        self.max_holding_period = max_holding_period
        
    def apply_triple_barrier(self, prices, entry_times, side=1):
        """
        Triple barrier labeling uygula
        
        Args:
            prices: Fiyat serisi
            entry_times: Giriş zamanları
            side: 1 for long, -1 for short
            
        Returns:
            labels: -1 (stop loss), 0 (time barrier), 1 (take profit)
            exit_times: Çıkış zamanları
        """
        labels = []
        exit_times = []
        
        for entry_time in entry_times:
            entry_idx = prices.index.get_loc(entry_time)
            entry_price = prices.iloc[entry_idx]
            
            # Barrier seviyelerini hesapla
            if side == 1:  # Long position
                take_profit_level = entry_price * (1 + self.profit_target)
                stop_loss_level = entry_price * (1 - self.stop_loss)
            else:  # Short position
                take_profit_level = entry_price * (1 - self.profit_target)
                stop_loss_level = entry_price * (1 + self.stop_loss)
            
            # İleri doğru tarama
            label = 0  # Default: time barrier
            exit_time = None
            
            max_idx = min(entry_idx + self.max_holding_period, len(prices) - 1)
            
            for i in range(entry_idx + 1, max_idx + 1):
                current_price = prices.iloc[i]
                current_time = prices.index[i]
                
                if side == 1:  # Long position
                    if current_price >= take_profit_level:
                        label = 1  # Take profit hit
                        exit_time = current_time
                        break
                    elif current_price <= stop_loss_level:
                        label = -1  # Stop loss hit
                        exit_time = current_time
                        break
                else:  # Short position
                    if current_price <= take_profit_level:
                        label = 1  # Take profit hit
                        exit_time = current_time
                        break
                    elif current_price >= stop_loss_level:
                        label = -1  # Stop loss hit
                        exit_time = current_time
                        break
            
            # Hiçbir barrier tetiklenmediyse time barrier
            if exit_time is None:
                exit_time = prices.index[max_idx]
                label = 0
                
            labels.append(label)
            exit_times.append(exit_time)
            
        return pd.Series(labels, index=entry_times), pd.Series(exit_times, index=entry_times)
```

### 3.2 Dinamik Barrier Hesaplama

```python
class DynamicBarrierCalculator:
    def __init__(self, volatility_window=20, volatility_multiplier=2.0):
        self.volatility_window = volatility_window
        self.volatility_multiplier = volatility_multiplier
        
    def calculate_dynamic_barriers(self, prices, regime):
        """Rejim ve volatiliteye göre dinamik barrier hesapla"""
        
        # Volatilite hesapla
        returns = prices.pct_change()
        rolling_vol = returns.rolling(self.volatility_window).std()
        
        # Rejim bazlı ayarlamalar
        regime_multipliers = {
            MarketRegime.TRENDING_UP: {'tp': 1.5, 'sl': 0.8},
            MarketRegime.TRENDING_DOWN: {'tp': 1.5, 'sl': 0.8},
            MarketRegime.SIDEWAYS: {'tp': 0.8, 'sl': 1.2},
            MarketRegime.HIGH_VOLATILITY: {'tp': 2.0, 'sl': 1.5},
            MarketRegime.LOW_LIQUIDITY: {'tp': 1.0, 'sl': 1.0}
        }
        
        multiplier = regime_multipliers.get(regime, {'tp': 1.0, 'sl': 1.0})
        
        # Dinamik barrier seviyeleri
        dynamic_tp = rolling_vol * self.volatility_multiplier * multiplier['tp']
        dynamic_sl = rolling_vol * self.volatility_multiplier * multiplier['sl']
        
        return dynamic_tp, dynamic_sl
```

### 3.3 Meta-Labeling

```python
class MetaLabeler:
    """İkinci kademe labeling - hangi sinyallerin işlem yapılacağını belirle"""
    
    def __init__(self):
        self.meta_model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def prepare_meta_features(self, primary_signals, market_data):
        """Meta-labeling için özellik hazırlama"""
        
        meta_features = pd.DataFrame(index=primary_signals.index)
        
        # Primary signal strength
        meta_features['signal_strength'] = abs(primary_signals)
        
        # Market conditions
        meta_features['volatility'] = market_data.close.pct_change().rolling(20).std()
        meta_features['volume_ratio'] = market_data.volume / market_data.volume.rolling(20).mean()
        meta_features['rsi'] = ta.RSI(market_data.close, timeperiod=14)
        
        # Time-based features
        meta_features['hour'] = meta_features.index.hour
        meta_features['day_of_week'] = meta_features.index.dayofweek
        
        # Recent performance
        meta_features['recent_hit_rate'] = self._calculate_recent_hit_rate()
        
        return meta_features.fillna(method='ffill').dropna()
        
    def create_meta_labels(self, primary_signals, actual_outcomes):
        """Meta-label oluştur: 1 if trade should be taken, 0 otherwise"""
        
        # Sadece karlı işlemleri işaretle
        meta_labels = (actual_outcomes > 0).astype(int)
        
        return meta_labels
        
    def train_meta_model(self, primary_signals, market_data, actual_outcomes):
        """Meta-model eğitimi"""
        
        meta_features = self.prepare_meta_features(primary_signals, market_data)
        meta_labels = self.create_meta_labels(primary_signals, actual_outcomes)
        
        # Align indices
        common_idx = meta_features.index.intersection(meta_labels.index)
        X = meta_features.loc[common_idx]
        y = meta_labels.loc[common_idx]
        
        self.meta_model.fit(X, y)
        
    def predict_meta_label(self, primary_signal, current_market_data):
        """Meta-prediction: Bu sinyal işlenmeli mi?"""
        
        meta_features = self.prepare_meta_features(
            pd.Series([primary_signal], index=[current_market_data.index[-1]]),
            current_market_data
        )
        
        meta_prediction = self.meta_model.predict_proba(meta_features)[:, 1]  # Probability of class 1
        
        return meta_prediction[0]
```

## 4. Entegre Sistem Workflow

```python
class IntegratedTradingSystem:
    def __init__(self):
        self.regime_classifier = RegimeClassifier()
        self.meta_learner = MetaLearner(StrategyPool())
        self.barrier_labeler = TripleBarrierLabeler()
        self.meta_labeler = MetaLabeler()
        self.dynamic_barriers = DynamicBarrierCalculator()
        
    def generate_signal(self, market_data):
        """Entegre sinyal üretimi"""
        
        # 1. Piyasa rejimini tespit et
        current_regime, regime_confidence = self.regime_classifier.predict(market_data)
        
        # 2. Rejime uygun stratejiyi seç
        selected_strategy = self.meta_learner.select_strategy(market_data, current_regime)
        
        # 3. Primary signal üret (seçilen strateji ile)
        primary_signal = self._generate_primary_signal(selected_strategy, market_data)
        
        # 4. Meta-labeling ile sinyali filtrele
        meta_confidence = self.meta_labeler.predict_meta_label(primary_signal, market_data)
        
        # 5. Dinamik barrier seviyelerini hesapla
        tp_level, sl_level = self.dynamic_barriers.calculate_dynamic_barriers(
            market_data.close, current_regime
        )
        
        # 6. Final signal
        if meta_confidence > 0.6:  # Meta-model threshold
            final_signal = {
                'direction': np.sign(primary_signal),
                'strength': abs(primary_signal),
                'confidence': meta_confidence,
                'regime': current_regime,
                'strategy': selected_strategy,
                'take_profit': tp_level.iloc[-1],
                'stop_loss': sl_level.iloc[-1]
            }
        else:
            final_signal = None  # No trade
            
        return final_signal
        
    def update_system(self, trade_result, strategy_used):
        """Sistem performansını güncelle"""
        
        # Meta-learner güncelle
        self.meta_learner.update_performance(strategy_used, trade_result)
        
        # Model retraining trigger (haftada bir)
        if self._should_retrain():
            self._retrain_models()
```

## 5. Performans İzleme

```python
class SystemPerformanceTracker:
    def __init__(self):
        self.regime_accuracy = {}
        self.strategy_performance = {}
        self.barrier_hit_rates = {}
        
    def track_regime_accuracy(self, predicted_regime, actual_market_behavior):
        """Rejim tahmin doğruluğunu izle"""
        if predicted_regime not in self.regime_accuracy:
            self.regime_accuracy[predicted_regime] = []
            
        # Actual behavior classification (simplified)
        actual_regime = self._classify_actual_behavior(actual_market_behavior)
        accuracy = (predicted_regime == actual_regime)
        
        self.regime_accuracy[predicted_regime].append(accuracy)
        
    def track_strategy_performance(self, strategy_name, trade_pnl):
        """Strateji performansını izle"""
        if strategy_name not in self.strategy_performance:
            self.strategy_performance[strategy_name] = []
            
        self.strategy_performance[strategy_name].append(trade_pnl)
        
    def get_performance_report(self):
        """Performans raporu"""
        report = {
            'regime_accuracy': {
                regime: np.mean(accuracies) 
                for regime, accuracies in self.regime_accuracy.items()
            },
            'strategy_sharpe': {
                strategy: np.mean(pnls) / (np.std(pnls) + 1e-8)
                for strategy, pnls in self.strategy_performance.items()
            }
        }
        return report
```

Bu tasarım, piyasa rejimlerini otomatik olarak tespit eden, her rejim için en uygun stratejiyi seçen ve triple-barrier sistemiyle etiketleme yapan entegre bir yapı sağlar. Sistem sürekli öğrenir ve performansını optimize eder.