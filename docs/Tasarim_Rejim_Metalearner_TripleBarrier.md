# AI Trading Bot - ML Tasarım Dokümanı
## Piyasa Rejimi Tespiti, Meta-Learning ve Triple Barrier Etiketleme

## 1. Genel Bakış

Bu doküman, AI trading bot projesi için makine öğrenmesi tasarımını detaylandırır. Özellikle piyasa rejimi tespiti, meta-learning stratejisi ve triple barrier etiketleme yöntemlerini kapsar.

## 2. Piyasa Rejimi Tespiti

### 2.1 Rejim Kategorileri

#### 2.1.1 Trend Rejimi
- **Yükselen Trend**: Güçlü alım baskısı, yüksek ADX (>25)
- **Düşen Trend**: Güçlü satış baskısı, düşük ADX (<25)
- **Yatay Trend**: Düşük volatilite, düşük ADX (<20)

#### 2.1.2 Volatilite Rejimi
- **Yüksek Volatilite**: ATR > %3, Bollinger Bands geniş
- **Düşük Volatilite**: ATR < %1, Bollinger Bands dar
- **Normal Volatilite**: ATR %1-%3 arası

#### 2.1.3 Likidite Rejimi
- **Yüksek Likidite**: Düşük spread, yüksek hacim
- **Düşük Likidite**: Yüksek spread, düşük hacim
- **Normal Likidite**: Orta seviye spread ve hacim

### 2.2 Rejim Tespit Algoritması

```python
class MarketRegimeDetector:
    def __init__(self):
        self.regime_classifier = None
        self.feature_scaler = None
        
    def extract_regime_features(self, data):
        """Piyasa rejimi için özellik çıkarımı"""
        features = {}
        
        # Trend gücü
        features['adx'] = self.calculate_adx(data, period=14)
        features['trend_strength'] = self.calculate_trend_strength(data)
        
        # Volatilite
        features['atr'] = self.calculate_atr(data, period=14)
        features['bb_width'] = self.calculate_bollinger_width(data)
        features['volatility_ratio'] = features['atr'] / data['close'].rolling(20).mean()
        
        # Likidite
        features['spread'] = self.calculate_spread(data)
        features['volume_ratio'] = data['volume'] / data['volume'].rolling(20).mean()
        features['bid_ask_imbalance'] = self.calculate_orderbook_imbalance(data)
        
        # Momentum
        features['rsi'] = self.calculate_rsi(data, period=14)
        features['macd'] = self.calculate_macd(data)
        features['momentum'] = self.calculate_momentum(data, period=10)
        
        return features
    
    def classify_regime(self, features):
        """Piyasa rejimini sınıflandır"""
        # Normalize features
        scaled_features = self.feature_scaler.transform([features])
        
        # Predict regime
        regime = self.regime_classifier.predict(scaled_features)[0]
        confidence = self.regime_classifier.predict_proba(scaled_features).max()
        
        return {
            'regime': regime,
            'confidence': confidence,
            'regime_name': self.get_regime_name(regime)
        }
    
    def get_regime_name(self, regime_id):
        """Rejim ID'sini isme çevir"""
        regime_names = {
            0: 'trending_bullish',
            1: 'trending_bearish', 
            2: 'ranging_high_vol',
            3: 'ranging_low_vol',
            4: 'volatile_breakout',
            5: 'low_liquidity'
        }
        return regime_names.get(regime_id, 'unknown')
```

### 2.3 Rejim-Spesifik Stratejiler

```python
class RegimeSpecificStrategy:
    def __init__(self):
        self.strategies = {
            'trending_bullish': self.trending_bullish_strategy,
            'trending_bearish': self.trending_bearish_strategy,
            'ranging_high_vol': self.ranging_high_vol_strategy,
            'ranging_low_vol': self.ranging_low_vol_strategy,
            'volatile_breakout': self.volatile_breakout_strategy,
            'low_liquidity': self.low_liquidity_strategy
        }
    
    def get_strategy(self, regime):
        """Rejime uygun stratejiyi döndür"""
        return self.strategies.get(regime, self.default_strategy)
    
    def trending_bullish_strategy(self, features):
        """Yükselen trend stratejisi"""
        return {
            'signal': 'long',
            'confidence': min(features['adx'] / 50, 0.95),
            'stop_loss': features['atr'] * 2,
            'take_profit': features['atr'] * 4,
            'position_size': 0.1  # %10 pozisyon
        }
    
    def trending_bearish_strategy(self, features):
        """Düşen trend stratejisi"""
        return {
            'signal': 'short',
            'confidence': min(features['adx'] / 50, 0.95),
            'stop_loss': features['atr'] * 2,
            'take_profit': features['atr'] * 4,
            'position_size': 0.1
        }
    
    def ranging_high_vol_strategy(self, features):
        """Yüksek volatilite yatay stratejisi"""
        return {
            'signal': 'mean_reversion',
            'confidence': 0.7,
            'stop_loss': features['atr'] * 1.5,
            'take_profit': features['atr'] * 2,
            'position_size': 0.05  # Daha küçük pozisyon
        }
```

## 3. Meta-Learning Sistemi

### 3.1 Meta-Learner Mimarisi

```python
class MetaLearner:
    def __init__(self):
        self.base_models = {
            'lstm': LSTMModel(),
            'xgboost': XGBoostModel(),
            'random_forest': RandomForestModel(),
            'svm': SVMModel()
        }
        self.meta_model = None
        self.regime_detector = MarketRegimeDetector()
        
    def train_meta_model(self, training_data):
        """Meta-model eğitimi"""
        meta_features = []
        meta_labels = []
        
        for regime in self.get_regimes(training_data):
            regime_data = self.filter_by_regime(training_data, regime)
            
            # Her base model için performans hesapla
            for model_name, model in self.base_models.items():
                performance = self.evaluate_model(model, regime_data)
                meta_features.append({
                    'regime': regime,
                    'model': model_name,
                    'performance': performance,
                    'market_conditions': self.extract_market_conditions(regime_data)
                })
                meta_labels.append(performance['sharpe_ratio'])
        
        # Meta-model eğitimi
        self.meta_model = XGBoostRegressor()
        self.meta_model.fit(meta_features, meta_labels)
    
    def select_best_model(self, current_features):
        """Mevcut koşullar için en iyi modeli seç"""
        regime = self.regime_detector.classify_regime(current_features)
        
        # Her model için performans tahmini
        model_scores = {}
        for model_name in self.base_models.keys():
            meta_features = {
                'regime': regime['regime'],
                'model': model_name,
                'market_conditions': current_features
            }
            score = self.meta_model.predict([meta_features])[0]
            model_scores[model_name] = score
        
        # En yüksek skorlu modeli döndür
        best_model = max(model_scores, key=model_scores.get)
        return {
            'model': best_model,
            'confidence': model_scores[best_model],
            'all_scores': model_scores
        }
```

### 3.2 Ensemble Stratejisi

```python
class EnsembleStrategy:
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.meta_learner = MetaLearner()
        
    def predict_ensemble(self, features):
        """Ensemble tahmin"""
        predictions = {}
        weights = {}
        
        # Her model için tahmin al
        for model_name, model in self.models.items():
            pred = model.predict(features)
            predictions[model_name] = pred
            
            # Model ağırlığını hesapla
            weight = self.calculate_model_weight(model_name, features)
            weights[model_name] = weight
        
        # Ağırlıklı ensemble
        ensemble_pred = 0
        total_weight = sum(weights.values())
        
        for model_name in predictions:
            ensemble_pred += predictions[model_name] * weights[model_name] / total_weight
        
        return {
            'prediction': ensemble_pred,
            'confidence': self.calculate_ensemble_confidence(predictions, weights),
            'model_contributions': {k: v * weights[k] / total_weight 
                                  for k, v in predictions.items()}
        }
    
    def calculate_model_weight(self, model_name, features):
        """Model ağırlığını hesapla"""
        # Rejim bazlı ağırlık
        regime_weight = self.get_regime_weight(model_name, features)
        
        # Performans bazlı ağırlık
        performance_weight = self.get_performance_weight(model_name)
        
        # Güncellik ağırlığı
        recency_weight = self.get_recency_weight(model_name)
        
        return regime_weight * performance_weight * recency_weight
```

## 4. Triple Barrier Etiketleme

### 4.1 Triple Barrier Algoritması

```python
class TripleBarrierLabeling:
    def __init__(self, upper_barrier=0.02, lower_barrier=0.02, time_barrier=24):
        self.upper_barrier = upper_barrier
        self.lower_barrier = lower_barrier
        self.time_barrier = time_barrier  # saat cinsinden
        
    def label_data(self, price_data, events):
        """Triple barrier etiketleme"""
        labels = []
        
        for event in events:
            event_time = event['timestamp']
            event_price = event['price']
            
            # Barrier'ları hesapla
            upper_price = event_price * (1 + self.upper_barrier)
            lower_price = event_price * (1 - self.lower_barrier)
            time_limit = event_time + pd.Timedelta(hours=self.time_barrier)
            
            # Gelecek fiyat hareketlerini izle
            future_data = price_data[
                (price_data['timestamp'] > event_time) & 
                (price_data['timestamp'] <= time_limit)
            ]
            
            # Barrier'ları kontrol et
            label = self.check_barriers(future_data, upper_price, lower_price, time_limit)
            
            labels.append({
                'event_time': event_time,
                'event_price': event_price,
                'label': label['label'],
                'label_time': label['label_time'],
                'return_value': label['return_value'],
                'barrier_hit': label['barrier_hit']
            })
        
        return labels
    
    def check_barriers(self, future_data, upper_price, lower_price, time_limit):
        """Barrier'ları kontrol et"""
        for _, row in future_data.iterrows():
            # Upper barrier kontrolü
            if row['high'] >= upper_price:
                return {
                    'label': 1,
                    'label_time': row['timestamp'],
                    'return_value': (upper_price - future_data.iloc[0]['close']) / future_data.iloc[0]['close'],
                    'barrier_hit': 'upper'
                }
            
            # Lower barrier kontrolü
            if row['low'] <= lower_price:
                return {
                    'label': -1,
                    'label_time': row['timestamp'],
                    'return_value': (lower_price - future_data.iloc[0]['close']) / future_data.iloc[0]['close'],
                    'barrier_hit': 'lower'
                }
        
        # Time barrier'a ulaşıldı
        return {
            'label': 0,
            'label_time': time_limit,
            'return_value': (future_data.iloc[-1]['close'] - future_data.iloc[0]['close']) / future_data.iloc[0]['close'],
            'barrier_hit': 'time'
        }
```

### 4.2 Dinamik Barrier Ayarlama

```python
class DynamicBarrierAdjustment:
    def __init__(self):
        self.atr_multiplier = 2.0
        self.volatility_lookback = 20
        
    def calculate_dynamic_barriers(self, price_data, event_time):
        """Dinamik barrier hesaplama"""
        # ATR hesapla
        atr = self.calculate_atr(price_data, event_time, period=14)
        
        # Volatilite bazlı barrier'lar
        volatility = self.calculate_volatility(price_data, event_time)
        
        # Dinamik barrier'lar
        upper_barrier = max(0.01, min(0.05, atr * self.atr_multiplier))
        lower_barrier = max(0.01, min(0.05, atr * self.atr_multiplier))
        
        # Volatiliteye göre zaman barrier'ı ayarla
        if volatility > 0.03:  # Yüksek volatilite
            time_barrier = 12  # 12 saat
        elif volatility < 0.01:  # Düşük volatilite
            time_barrier = 48  # 48 saat
        else:  # Normal volatilite
            time_barrier = 24  # 24 saat
        
        return {
            'upper_barrier': upper_barrier,
            'lower_barrier': lower_barrier,
            'time_barrier': time_barrier,
            'atr': atr,
            'volatility': volatility
        }
```

## 5. Model Performans Değerlendirme

### 5.1 Walk-Forward Analizi

```python
class WalkForwardAnalysis:
    def __init__(self, train_window=252, test_window=63, step_size=21):
        self.train_window = train_window  # 1 yıl
        self.test_window = test_window    # 3 ay
        self.step_size = step_size        # 1 ay
        
    def perform_walk_forward(self, data, model):
        """Walk-forward analizi"""
        results = []
        
        for start_idx in range(0, len(data) - self.train_window - self.test_window, self.step_size):
            # Eğitim verisi
            train_start = start_idx
            train_end = start_idx + self.train_window
            
            # Test verisi
            test_start = train_end
            test_end = test_start + self.test_window
            
            train_data = data[train_start:train_end]
            test_data = data[test_start:test_end]
            
            # Model eğitimi
            model.train(train_data)
            
            # Test performansı
            performance = self.evaluate_performance(model, test_data)
            
            results.append({
                'train_period': (train_data.index[0], train_data.index[-1]),
                'test_period': (test_data.index[0], test_data.index[-1]),
                'performance': performance
            })
        
        return results
    
    def evaluate_performance(self, model, test_data):
        """Model performansını değerlendir"""
        predictions = model.predict(test_data)
        actual_returns = test_data['returns']
        
        # Metrikler
        accuracy = accuracy_score(actual_returns, predictions)
        precision = precision_score(actual_returns, predictions, average='weighted')
        recall = recall_score(actual_returns, predictions, average='weighted')
        f1 = f1_score(actual_returns, predictions, average='weighted')
        
        # Trading metrikleri
        sharpe_ratio = self.calculate_sharpe_ratio(predictions, actual_returns)
        max_drawdown = self.calculate_max_drawdown(predictions, actual_returns)
        profit_factor = self.calculate_profit_factor(predictions, actual_returns)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor
        }
```

### 5.2 Stres Testleri

```python
class StressTesting:
    def __init__(self):
        self.stress_scenarios = {
            'high_volatility': self.high_volatility_scenario,
            'low_liquidity': self.low_liquidity_scenario,
            'market_crash': self.market_crash_scenario,
            'flash_crash': self.flash_crash_scenario
        }
    
    def run_stress_tests(self, model, data):
        """Stres testlerini çalıştır"""
        results = {}
        
        for scenario_name, scenario_func in self.stress_scenarios.items():
            # Stres senaryosu uygula
            stressed_data = scenario_func(data)
            
            # Model performansını test et
            performance = self.evaluate_stress_performance(model, stressed_data)
            
            results[scenario_name] = performance
        
        return results
    
    def high_volatility_scenario(self, data):
        """Yüksek volatilite senaryosu"""
        stressed_data = data.copy()
        stressed_data['volatility'] = stressed_data['volatility'] * 3
        stressed_data['atr'] = stressed_data['atr'] * 3
        return stressed_data
    
    def market_crash_scenario(self, data):
        """Piyasa çöküşü senaryosu"""
        stressed_data = data.copy()
        # Fiyatları %30 düşür
        stressed_data['close'] = stressed_data['close'] * 0.7
        stressed_data['high'] = stressed_data['high'] * 0.7
        stressed_data['low'] = stressed_data['low'] * 0.7
        stressed_data['open'] = stressed_data['open'] * 0.7
        return stressed_data
```

## 6. Model Güncelleme Stratejisi

### 6.1 Online Learning

```python
class OnlineLearning:
    def __init__(self, model, learning_rate=0.01):
        self.model = model
        self.learning_rate = learning_rate
        self.performance_history = []
        
    def update_model(self, new_data, prediction, actual):
        """Modeli online güncelle"""
        # Performans hesapla
        performance = self.calculate_performance(prediction, actual)
        self.performance_history.append(performance)
        
        # Model drift kontrolü
        if self.detect_model_drift():
            self.retrain_model(new_data)
        
        # Incremental learning
        self.incremental_update(new_data, prediction, actual)
    
    def detect_model_drift(self):
        """Model drift tespiti"""
        if len(self.performance_history) < 100:
            return False
        
        # Son 100 performansın ortalaması
        recent_performance = np.mean(self.performance_history[-100:])
        historical_performance = np.mean(self.performance_history[:-100])
        
        # %10'dan fazla düşüş varsa drift var
        return (historical_performance - recent_performance) / historical_performance > 0.1
    
    def incremental_update(self, new_data, prediction, actual):
        """Artırımlı güncelleme"""
        # Gradient hesapla
        gradient = self.calculate_gradient(prediction, actual)
        
        # Model parametrelerini güncelle
        self.model.update_parameters(gradient, self.learning_rate)
```

Bu tasarım dokümanı, AI trading bot projesi için gerekli tüm ML bileşenlerini detaylandırır ve %90+ doğruluk hedefini gerçekleştirmek için gerekli teknik altyapıyı sağlar.