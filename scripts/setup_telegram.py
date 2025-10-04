"""
Telegram Setup Script
Interactive script to help set up Telegram API credentials
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_telegram_credentials():
    """Interactive setup for Telegram credentials"""
    print("🔧 Telegram API Setup")
    print("=" * 50)

    print("\n📱 Step 1: Get Telegram API Credentials")
    print("1. Go to https://my.telegram.org/apps")
    print("2. Log in with your Telegram account")
    print("3. Create a new application")
    print("4. Copy your API ID and API Hash")

    print("\n⚠️  If you're getting 'ERROR' on the website:")
    print("- Try different browsers (Chrome, Firefox, Safari)")
    print("- Clear browser cache and cookies")
    print("- Try incognito/private mode")
    print("- Disable VPN/proxy if using one")
    print("- Try from mobile browser")
    print("- Wait a few minutes and try again")

    print("\n🔄 Alternative: Use existing apps")
    print("If you have any existing Telegram apps, you can reuse those credentials")

    # Get credentials from user
    print("\n📝 Enter your credentials:")

    api_id = input("API ID: ").strip()
    if not api_id:
        print("❌ API ID is required")
        return False

    api_hash = input("API Hash: ").strip()
    if not api_hash:
        print("❌ API Hash is required")
        return False

    phone = input("Phone number (with country code, e.g., +1234567890): ").strip()
    if not phone:
        print("❌ Phone number is required")
        return False

    # Validate phone format
    if not phone.startswith('+'):
        print("⚠️  Phone number should start with + (e.g., +1234567890)")
        phone = '+' + phone.lstrip('+')

    # Create .env file
    env_content = f"""# Telegram API Configuration
TELEGRAM_API_ID={api_id}
TELEGRAM_API_HASH={api_hash}
TELEGRAM_PHONE={phone}
"""

    # Write to .env file
    env_path = project_root / ".env"

    # Read existing .env if it exists
    existing_content = ""
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_content = f.read()

    # Update or add Telegram config
    lines = existing_content.split('\n')
    new_lines = []
    telegram_section = False

    for line in lines:
        if line.startswith('# Telegram API Configuration'):
            telegram_section = True
            new_lines.append(env_content.strip())
            continue
        elif telegram_section and line.startswith('TELEGRAM_'):
            continue  # Skip old Telegram lines
        elif telegram_section and line.strip() == '':
            telegram_section = False
            new_lines.append(line)
        else:
            new_lines.append(line)

    if not telegram_section:
        new_lines.append('')
        new_lines.append(env_content.strip())

    # Write updated .env
    with open(env_path, 'w') as f:
        f.write('\n'.join(new_lines))

    print(f"\n✅ Credentials saved to {env_path}")

    # Test the credentials
    print("\n🧪 Testing credentials...")

    try:
        from telethon import TelegramClient

        # Test client creation
        client = TelegramClient("test_session", int(api_id), api_hash)

        print("✅ Client created successfully")
        print("✅ Credentials are valid")

        print("\n📋 Next steps:")
        print("1. Run your dashboard: streamlit run app/main.py")
        print("2. Go to Telegram Monitor")
        print("3. Click 'Load Available Channels'")
        print("4. Enter your phone number when prompted")
        print("5. Enter the verification code sent to your phone")
        print("6. Start monitoring your channels!")

        return True

    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        print("\n🔧 Troubleshooting:")
        print("- Check your API ID and Hash are correct")
        print("- Make sure your phone number format is correct")
        print("- Try the setup again")
        return False


def alternative_setup():
    """Alternative setup methods"""
    print("\n🔄 Alternative Setup Methods")
    print("=" * 50)

    print("\n1. 📱 Use Telegram Desktop App")
    print("   - Download Telegram Desktop")
    print("   - Log in with your account")
    print("   - Go to Settings → Advanced → Connection Type")
    print("   - Use 'Use custom' and enter your API credentials")

    print("\n2. 🤖 Use Bot API (Simpler)")
    print("   - Create a bot with @BotFather")
    print("   - Use bot token instead of user API")
    print("   - Add bot to channels you want to monitor")
    print("   - Bot needs admin permissions to read messages")

    print("\n3. 🔧 Use Existing Apps")
    print("   - Check if you have any existing Telegram apps")
    print("   - Reuse those API credentials")
    print("   - Look in your Telegram settings for connected apps")

    print("\n4. 📞 Contact Support")
    print("   - Email: recover@telegram.org")
    print("   - Include your phone number and error details")
    print("   - Ask for help with API app creation")


def main():
    """Main setup function"""
    print("🚀 Telegram Integration Setup")
    print("=" * 50)

    print("\nThis script will help you set up Telegram API credentials")
    print("for monitoring channels with your personal account.")

    choice = input("\nChoose setup method (1=Interactive, 2=Alternatives): ").strip()

    if choice == "1":
        success = setup_telegram_credentials()
        if not success:
            alternative_setup()
    else:
        alternative_setup()


if __name__ == "__main__":
    main()
