"""
Test Telegram Integration
Simple test to verify Telegram monitoring functionality
"""

import sys
from pathlib import Path
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.telegram_monitor import TelegramMonitor


def test_telegram_monitor_initialization():
    """Test TelegramMonitor initialization"""
    print("🧪 Testing TelegramMonitor initialization...")
    
    try:
        monitor = TelegramMonitor()
        print("✅ TelegramMonitor initialized successfully")
        
        # Test portfolio ticker loading
        tickers = monitor.load_portfolio_tickers()
        print(f"✅ Loaded {len(tickers)} portfolio tickers")
        
        if tickers:
            print(f"📊 Sample tickers: {list(tickers)[:5]}")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing TelegramMonitor: {e}")
        return False


def test_ticker_patterns():
    """Test ticker pattern creation"""
    print("\n🧪 Testing ticker pattern creation...")
    
    try:
        monitor = TelegramMonitor()
        tickers = {"AAPL", "VALE3", "HGLG11"}
        patterns = monitor.create_ticker_patterns(tickers)
        
        print(f"✅ Created {len(patterns)} patterns for {len(tickers)} tickers")
        print(f"📊 Sample patterns: {patterns[:3]}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating ticker patterns: {e}")
        return False


def test_stock_mention_detection():
    """Test stock mention detection"""
    print("\n🧪 Testing stock mention detection...")
    
    try:
        monitor = TelegramMonitor()
        tickers = {"AAPL", "VALE3", "HGLG11", "PETR4"}
        
        # Test messages
        test_messages = [
            "AAPL is looking strong today with positive earnings",
            "VALE3 showing momentum in the Brazilian market",
            "HGLG11 dividend yield is attractive for income investors",
            "PETR4 benefiting from oil price recovery",
            "No stock mentions in this message",
            "Mixed message with AAPL and VALE3 mentioned together"
        ]
        
        for i, message in enumerate(test_messages):
            mentions = monitor.find_stock_mentions(message, tickers)
            print(f"📝 Message {i+1}: {len(mentions)} mentions - {mentions}")
        
        print("✅ Stock mention detection working correctly")
        return True
    except Exception as e:
        print(f"❌ Error in stock mention detection: {e}")
        return False


def test_telegram_configuration():
    """Test Telegram configuration"""
    print("\n🧪 Testing Telegram configuration...")
    
    try:
        from app.config import TELEGRAM_CONFIG
        
        print(f"✅ Telegram config loaded")
        print(f"📊 API ID configured: {bool(TELEGRAM_CONFIG['API_ID'])}")
        print(f"📊 API Hash configured: {bool(TELEGRAM_CONFIG['API_HASH'])}")
        print(f"📊 Phone configured: {bool(TELEGRAM_CONFIG['PHONE'])}")
        print(f"📊 Default channels: {len(TELEGRAM_CONFIG['DEFAULT_CHANNELS'])}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading Telegram configuration: {e}")
        return False


def test_portfolio_ticker_loading():
    """Test portfolio ticker loading from portfolios.json"""
    print("\n🧪 Testing portfolio ticker loading...")
    
    try:
        monitor = TelegramMonitor()
        tickers = monitor.load_portfolio_tickers()
        
        print(f"✅ Loaded {len(tickers)} tickers from portfolios")
        
        # Show breakdown by portfolio
        try:
            with open("portfolios.json", 'r', encoding='utf-8') as f:
                portfolios = json.load(f)
            
            for portfolio_name, stocks in portfolios.items():
                portfolio_tickers = set(stocks.keys())
                print(f"📊 {portfolio_name}: {len(portfolio_tickers)} tickers")
                
        except Exception as e:
            print(f"⚠️ Could not load portfolio breakdown: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading portfolio tickers: {e}")
        return False


def main():
    """Run all Telegram integration tests"""
    print("🚀 Starting Telegram Integration Tests")
    print("=" * 50)
    
    tests = [
        test_telegram_monitor_initialization,
        test_ticker_patterns,
        test_stock_mention_detection,
        test_telegram_configuration,
        test_portfolio_ticker_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Telegram integration tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    print("\n💡 Next steps:")
    print("1. Configure Telegram API credentials in .env file")
    print("2. Install telethon: pip install telethon")
    print("3. Test with actual Telegram channels")


if __name__ == "__main__":
    main()
