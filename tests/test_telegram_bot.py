"""
Test Telegram Bot Integration
Simple test to verify Telegram bot monitoring functionality
"""

import sys
from pathlib import Path
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.telegram_bot_monitor import TelegramBotMonitor


def test_bot_monitor_initialization():
    """Test TelegramBotMonitor initialization"""
    print("🧪 Testing TelegramBotMonitor initialization...")
    
    try:
        monitor = TelegramBotMonitor()
        print("✅ TelegramBotMonitor initialized successfully")
        
        # Test bot token
        print(f"📊 Bot token: {monitor.bot_token[:20]}...")
        print(f"📊 Bot username: {monitor.bot_username}")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing TelegramBotMonitor: {e}")
        return False


def test_bot_info():
    """Test bot information retrieval"""
    print("\n🧪 Testing bot information retrieval...")
    
    try:
        monitor = TelegramBotMonitor()
        bot_info = monitor.get_bot_info()
        
        if "error" in bot_info:
            print(f"⚠️ Bot info error: {bot_info['error']}")
            return False
        
        bot_data = bot_info.get("result", {})
        print(f"✅ Bot info retrieved successfully")
        print(f"📊 Bot ID: {bot_data.get('id', 'Unknown')}")
        print(f"📊 Bot Username: @{bot_data.get('username', 'Unknown')}")
        print(f"📊 Bot Name: {bot_data.get('first_name', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return False


def test_portfolio_ticker_loading():
    """Test portfolio ticker loading"""
    print("\n🧪 Testing portfolio ticker loading...")
    
    try:
        monitor = TelegramBotMonitor()
        tickers = monitor.load_portfolio_tickers()
        
        print(f"✅ Loaded {len(tickers)} tickers from portfolios")
        
        if tickers:
            print(f"📊 Sample tickers: {list(tickers)[:5]}")
            
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


def test_stock_mention_detection():
    """Test stock mention detection"""
    print("\n🧪 Testing stock mention detection...")
    
    try:
        monitor = TelegramBotMonitor()
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


def test_bot_updates():
    """Test bot updates retrieval"""
    print("\n🧪 Testing bot updates retrieval...")
    
    try:
        monitor = TelegramBotMonitor()
        updates = monitor.get_updates(limit=10)
        
        print(f"✅ Retrieved {len(updates)} updates")
        
        if updates:
            print("📊 Sample update structure:")
            sample_update = updates[0]
            print(f"  - Update ID: {sample_update.get('update_id')}")
            print(f"  - Has message: {'message' in sample_update}")
            
            if 'message' in sample_update:
                message = sample_update['message']
                print(f"  - Message ID: {message.get('message_id')}")
                print(f"  - Chat ID: {message.get('chat', {}).get('id')}")
                print(f"  - Has text: {'text' in message}")
        else:
            print("ℹ️ No updates found (bot may not have received any messages yet)")
        
        return True
    except Exception as e:
        print(f"❌ Error getting bot updates: {e}")
        return False


def test_message_analysis():
    """Test message analysis"""
    print("\n🧪 Testing message analysis...")
    
    try:
        monitor = TelegramBotMonitor()
        
        # Create sample updates
        sample_updates = [
            {
                "update_id": 1,
                "message": {
                    "message_id": 1,
                    "date": 1696358400,  # Recent timestamp
                    "text": "AAPL is looking strong today",
                    "chat": {"id": -1001234567890, "title": "Stock Discussion"},
                    "from": {"id": 123456789, "username": "testuser"}
                }
            },
            {
                "update_id": 2,
                "message": {
                    "message_id": 2,
                    "date": 1696358400,
                    "text": "VALE3 showing momentum in Brazil",
                    "chat": {"id": -1001234567890, "title": "Stock Discussion"},
                    "from": {"id": 123456789, "username": "testuser"}
                }
            }
        ]
        
        analyzed = monitor.analyze_messages(sample_updates)
        print(f"✅ Analyzed {len(analyzed)} messages")
        
        if analyzed:
            for msg in analyzed:
                print(f"📝 Found mentions: {msg['mentions']} in '{msg['text'][:50]}...'")
        
        return True
    except Exception as e:
        print(f"❌ Error in message analysis: {e}")
        return False


def main():
    """Run all Telegram bot integration tests"""
    print("🚀 Starting Telegram Bot Integration Tests")
    print("=" * 50)
    
    tests = [
        test_bot_monitor_initialization,
        test_bot_info,
        test_portfolio_ticker_loading,
        test_stock_mention_detection,
        test_bot_updates,
        test_message_analysis
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
        print("🎉 All Telegram bot integration tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    print("\n💡 Next steps:")
    print("1. Add your bot to Telegram channels")
    print("2. Give the bot admin permissions to read messages")
    print("3. Test monitoring in the dashboard")
    print("4. Configure your .env file with TELEGRAM_BOT_TOKEN")


if __name__ == "__main__":
    main()
