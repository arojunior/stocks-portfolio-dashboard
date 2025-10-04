# 📱 Telegram User API Setup Guide

This guide will help you set up Telegram monitoring using your personal account (not a bot).

## 🎯 **Why Use User API Instead of Bot?**

- **Monitor any channel** you're a member of
- **No need to add bots** to channels
- **Access to all your channels** automatically
- **More flexible** for personal use
- **Better for monitoring** public channels

## 🔧 **Step-by-Step Setup**

### **Step 1: Get API Credentials (Alternative Methods)**

Since the web interface at https://my.telegram.org/apps is giving you "ERROR", try these alternatives:

#### **Method 1: Use Telegram Desktop App**

1. **Download Telegram Desktop** from https://desktop.telegram.org
2. **Log in** with your account
3. **Go to Settings** → Advanced → Connection Type
4. **Use "Use custom"** and enter your API credentials
5. **This bypasses** the web interface entirely

#### **Method 2: Try Different Browsers/Devices**

1. **Try Chrome** (most compatible)
2. **Try Firefox** or Safari
3. **Try mobile browser** on your phone
4. **Try incognito/private mode**
5. **Clear browser cache** and cookies
6. **Disable VPN/proxy** if using one

#### **Method 3: Use Existing Apps**

1. **Check your Telegram settings** for connected apps
2. **Look for any existing apps** you've created
3. **Reuse those credentials** if available
4. **Check your email** for any Telegram app confirmations

#### **Method 4: Contact Telegram Support**

1. **Email:** recover@telegram.org
2. **Include:** Your phone number and the exact error
3. **Ask for help** with API app creation
4. **They can help** you get credentials

### **Step 2: Manual Credential Entry**

If you manage to get credentials, add them to your `.env` file:

```bash
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890
```

**Important:** Use your phone number with country code (e.g., +1234567890)

### **Step 3: Test Authentication**

Run the test script to verify your credentials:

```bash
python scripts/test_telegram_auth.py
```

This will:

- Test your API credentials
- Connect to Telegram
- Show available channels
- Test message monitoring

## 🚨 **Common Issues & Solutions**

### **"ERROR" on Website**

- **Try different browsers** (Chrome, Firefox, Safari)
- **Clear browser cache** and cookies
- **Try incognito/private mode**
- **Disable VPN/proxy**
- **Try mobile browser**
- **Wait a few minutes** and try again

### **"Missing Credentials" Error**

- **Check your .env file** has the correct format
- **Verify API ID** is numeric (e.g., 12345678)
- **Verify API Hash** is a string (e.g., abc123def456)
- **Check phone number** format (+1234567890)

### **"Authentication Failed" Error**

- **Check phone number** format (+1234567890)
- **Verify API credentials** are correct
- **Try running setup again**
- **Check internet connection**

### **"2FA Required" Error**

- **Enter your 2FA password** when prompted
- **Make sure 2FA is enabled** in your Telegram account
- **Use the correct password**

## 🔄 **Alternative: Use Bot API Instead**

If you continue having issues with the user API, you can use the bot approach:

1. **Create a bot** with @BotFather (already done)
2. **Add bot to channels** you want to monitor
3. **Give bot admin permissions** to read messages
4. **Use bot token** instead of user API

The bot approach is simpler but requires adding the bot to each channel.

## 📱 **Using the Dashboard**

Once configured:

1. **Run your dashboard:** `streamlit run app/main.py`
2. **Go to Telegram Monitor** (sidebar or radio option)
3. **Click "Load Available Channels"**
4. **Select channels** to monitor
5. **Start monitoring** for stock mentions

## 🎯 **What You Can Monitor**

- **Any channel** you're a member of
- **Public channels** and groups
- **Private channels** (if you're a member)
- **Your portfolio stocks** (42 tickers)
- **Real-time mentions** and discussions

## 🔒 **Security & Privacy**

- **Session files** are stored locally and encrypted
- **No message content** is stored permanently
- **Only ticker mentions** are tracked
- **Full message text** is only shown in dashboard
- **Your account** remains secure

## 📞 **Getting Help**

If you're still having issues:

1. **Try the alternative methods** above
2. **Check Telegram's status** for service issues
3. **Contact Telegram support** for API issues
4. **Use the bot approach** as a fallback
5. **Ask for help** in the project repository

## 🎉 **Success!**

Once working, you'll have:

- **Real-time monitoring** of your portfolio stocks
- **Channel analytics** and engagement metrics
- **Trending insights** from community discussions
- **Early warning system** for market movements
- **Research assistance** for investment decisions

The user API approach gives you the most flexibility for monitoring any channels you're part of! 🚀📱
