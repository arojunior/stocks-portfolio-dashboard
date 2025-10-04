"""
Simple Telegram Test
Test Telegram connection without interactive prompts
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.telegram_monitor import TelegramMonitor


async def simple_test():
    """Simple test without interactive prompts"""
    print("🧪 Simple Telegram Test")
    print("=" * 50)

    monitor = TelegramMonitor()

    # Check credentials
    print(f"📊 API ID: {monitor.api_id}")
    print(f"📊 API Hash: {monitor.api_hash[:10]}..." if monitor.api_hash else "None")
    print(f"📊 Phone: {monitor.phone}")

    if not all([monitor.api_id, monitor.api_hash, monitor.phone]):
        print("\n❌ Missing credentials!")
        return False

    print("\n✅ Credentials loaded successfully!")
    print("\n📋 Next steps:")
    print("1. Run your dashboard: streamlit run app/main.py")
    print("2. Go to Telegram Monitor")
    print("3. Click 'Load Available Channels'")
    print("4. Enter your phone number when prompted")
    print("5. Enter the verification code sent to your phone")
    print("6. Start monitoring your channels!")

    return True


def main():
    """Main test function"""
    print("🚀 Simple Telegram Test")
    print("=" * 50)

    try:
        result = asyncio.run(simple_test())

        if result:
            print("\n✅ Credentials are configured correctly!")
            print("You can now use Telegram monitoring in your dashboard.")
        else:
            print("\n❌ Credentials not found.")
            print("Please check your .env file.")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
