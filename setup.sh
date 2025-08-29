#!/bin/bash

# AI Trading Bot - Setup Script
# This script sets up the development environment for the AI trading bot

set -e

echo "🚀 Setting up AI Trading Bot Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is installed
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    print_success "Python $python_version is installed (>= 3.9.0)"
else
    print_error "Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

# Check if pip is installed
print_status "Checking pip installation..."
if command -v pip3 &> /dev/null; then
    print_success "pip3 is installed"
else
    print_error "pip3 is not installed"
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
print_status "Creating project directories..."
mkdir -p logs data config models backup

# Copy example configuration
print_status "Setting up configuration..."
if [ ! -f "config/config.yaml" ]; then
    cp config/config.example.yaml config/config.yaml
    print_success "Configuration file created (config/config.yaml)"
    print_warning "Please update config/config.yaml with your API keys and settings"
else
    print_warning "Configuration file already exists"
fi

# Create .env file
print_status "Creating environment file..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# AI Trading Bot Environment Variables
ENVIRONMENT=development
CONFIG_FILE=config/config.yaml

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=trading_bot
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=trading_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Exchange API Keys (Update these with your actual keys)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_secret_key_here
BINANCE_TESTNET=true

GATE_IO_API_KEY=your_gate_io_api_key_here
GATE_IO_API_SECRET=your_gate_io_secret_key_here
GATE_IO_TESTNET=true

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Logging
LOG_LEVEL=INFO
EOF
    print_success "Environment file created (.env)"
    print_warning "Please update .env with your actual API keys and settings"
else
    print_warning "Environment file already exists"
fi

# Check if Docker is installed
print_status "Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_success "Docker is installed"
    
    # Check if Docker Compose is available
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is available"
    else
        print_warning "Docker Compose not found, but Docker is installed"
    fi
else
    print_warning "Docker is not installed. You can install it manually for containerized deployment"
fi

# Check if TA-Lib is available
print_status "Checking TA-Lib installation..."
python3 -c "import talib" 2>/dev/null && print_success "TA-Lib is installed" || {
    print_warning "TA-Lib is not installed. Installing..."
    if command -v brew &> /dev/null; then
        # macOS
        brew install ta-lib
        pip install TA-Lib
    elif command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y build-essential wget
        wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
        tar -xzf ta-lib-0.4.0-src.tar.gz
        cd ta-lib/
        ./configure --prefix=/usr
        make
        sudo make install
        cd ..
        rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/
        pip install TA-Lib
    else
        print_error "Could not install TA-Lib automatically. Please install it manually."
        print_status "Visit: https://github.com/mrjbq7/ta-lib#installation"
    fi
}

# Set up pre-commit hooks
print_status "Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "pre-commit not installed. Install it with: pip install pre-commit"
fi

# Create a simple test script
print_status "Creating test script..."
cat > test_setup.py << EOF
#!/usr/bin/env python3
"""
Simple test script to verify the setup
"""

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import pandas as pd
        import numpy as np
        import ccxt
        import talib
        import tensorflow as tf
        import torch
        import xgboost as xgb
        import sklearn
        import fastapi
        import streamlit
        import plotly
        import redis
        import psycopg2
        print("✅ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    try:
        import sys
        sys.path.append('src')
        from utils.config import Config
        config = Config()
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Trading Bot setup...")
    
    success = True
    success &= test_imports()
    success &= test_config()
    
    if success:
        print("🎉 Setup test completed successfully!")
    else:
        print("⚠️  Setup test completed with warnings")
EOF

print_success "Test script created (test_setup.py)"

# Make scripts executable
chmod +x start.py
chmod +x setup.sh

print_success "Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update config/config.yaml with your API keys"
echo "2. Update .env with your environment variables"
echo "3. Run: python test_setup.py to verify the setup"
echo "4. Run: python start.py --mode development to start the bot"
echo ""
echo "🐳 For Docker deployment:"
echo "1. Run: docker-compose up -d to start all services"
echo "2. Access dashboard at: http://localhost:8501"
echo "3. Access Grafana at: http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "- MVP Project Document: docs/MVP_Proje_Dokumani_TR.md"
echo "- Feature Store Schema: docs/Feature_Store_Sema_TR.md"
echo "- ML Design Document: docs/Tasarim_Rejim_Metalearner_TripleBarrier.md"
echo "- Quick Start Plan: docs/Quick_Wins_Week1_Plan_TR.md"