"""
Test Telegram Authentication
Simple script to test Telegram API authentication
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.telegram_monitor import TelegramMonitor


async def test_telegram_auth():
    """Test Telegram authentication"""
    print("🧪 Testing Telegram Authentication")
    print("=" * 50)

    monitor = TelegramMonitor()

    # Check credentials
    print(f"📊 API ID: {monitor.api_id}")
    print(f"📊 API Hash: {monitor.api_hash[:10]}..." if monitor.api_hash else "None")
    print(f"📊 Phone: {monitor.phone}")

    if not all([monitor.api_id, monitor.api_hash, monitor.phone]):
        print("\n❌ Missing credentials!")
        print("Please run: python scripts/setup_telegram.py")
        return False

    print("\n🔄 Attempting to connect to Telegram...")

    try:
        # Initialize client
        success = await monitor.initialize_client()

        if success:
            print("✅ Successfully connected to Telegram!")

            # Test getting channels
            print("\n📺 Getting available channels...")
            channels = await monitor.get_available_channels()

            print(f"✅ Found {len(channels)} channels")

            if channels:
                print("\n📋 Available channels:")
                for i, channel in enumerate(channels[:5]):  # Show first 5
                    print(f"  {i+1}. {channel['title']} ({channel['participants_count']:,} members)")

                if len(channels) > 5:
                    print(f"  ... and {len(channels) - 5} more channels")

            # Test monitoring a channel
            if channels:
                test_channel = channels[0]
                print(f"\n🔍 Testing monitoring on: {test_channel['title']}")

                messages = await monitor.monitor_channel(test_channel['id'], limit=10)
                print(f"✅ Found {len(messages)} messages with stock mentions")

                if messages:
                    print("\n📝 Sample messages:")
                    for msg in messages[:3]:
                        print(f"  - {msg['date'].strftime('%Y-%m-%d %H:%M')}: {', '.join(msg['mentions'])}")

            # Close client
            await monitor.close_client()
            print("\n🎉 Telegram authentication test successful!")
            return True

        else:
            print("❌ Failed to connect to Telegram")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your API credentials")
        print("2. Verify your phone number format (+1234567890)")
        print("3. Make sure you have internet connection")
        print("4. Try running setup_telegram.py again")
        return False


def main():
    """Main test function"""
    print("🚀 Telegram Authentication Test")
    print("=" * 50)

    print("This script will test your Telegram API credentials")
    print("and verify that you can connect to Telegram.")

    # Run async test
    try:
        result = asyncio.run(test_telegram_auth())

        if result:
            print("\n✅ All tests passed!")
            print("You can now use Telegram monitoring in your dashboard.")
        else:
            print("\n❌ Tests failed.")
            print("Please check your credentials and try again.")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
