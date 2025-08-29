# AI Trading Bot - Kripto/Forex Algoritmik Trading Sistemi

## Proje Özeti / Project Overview

Bu proje, kripto para ve forex piyasalarında otomatik trading yapabilen yapay zeka tabanlı bir bot sistemidir. Sistem, çoklu veri kaynaklarından beslenerek %90+ doğrulukta sinyaller üretmeyi hedeflemektedir.

This project is an AI-powered trading bot system for cryptocurrency and forex markets. The system aims to generate signals with 90%+ accuracy by processing multiple data sources.

## Özellikler / Features

- **Çoklu Veri Kaynağı**: Mum verileri, order book, trade book, balina hareketleri
- **100+ Teknik İndikatör**: RSI, MACD, Bollinger Bands, vb.
- **Sosyal Medya Analizi**: Twitter, Telegram, haber akışları
- **Makine Öğrenmesi**: LSTM, XGBoost, Ensemble modeller
- **Risk Yönetimi**: Stop-loss, take-profit, pozisyon boyutlandırma
- **Gerçek Zamanlı İzleme**: Dashboard ve Telegram bildirimleri

## Proje Yapısı / Project Structure

```
├── docs/                          # Proje dokümantasyonu
│   ├── MVP_Proje_Dokumani_TR.md   # Ana proje dokümanı
│   ├── Feature_Store_Sema_TR.md   # Veri şeması
│   ├── Tasarim_Rejim_Metalearner_TripleBarrier.md # ML tasarımı
│   └── Quick_Wins_Week1_Plan_TR.md # Hızlı başlangıç planı
├── src/                           # Kaynak kodlar
├── tests/                         # Test dosyaları
├── config/                        # Konfigürasyon dosyaları
└── data/                          # Veri dosyaları
```

## Kurulum / Installation

```bash
# Gereksinimler / Requirements
pip install -r requirements.txt

# Konfigürasyon / Configuration
cp config/config.example.yaml config/config.yaml
# API anahtarlarınızı config.yaml dosyasına ekleyin
```

## Kullanım / Usage

```bash
# Veri toplama / Data collection
python src/data_collector.py

# Model eğitimi / Model training
python src/train_model.py

# Trading bot başlatma / Start trading bot
python src/trading_bot.py
```

## Katkıda Bulunma / Contributing

1. Fork yapın / Fork the project
2. Feature branch oluşturun / Create a feature branch
3. Değişikliklerinizi commit edin / Commit your changes
4. Pull request gönderin / Push to the branch and create a Pull Request

## Lisans / License

Bu proje MIT lisansı altında lisanslanmıştır.
This project is licensed under the MIT License.