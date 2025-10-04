# 🤖 Telegram Bot Setup Guide

This guide will help you set up your Telegram bot for portfolio stock monitoring.

## 🎯 **Your Bot Details**

- **Bot Username:** @your_bot_username_here
- **Bot Token:** `your_bot_token_here`
- **Bot Link:** [https://t.me/your_bot_username_here](https://t.me/your_bot_username_here)

## 🚀 **Quick Setup (3 Steps)**

### **Step 1: Add Bot to Your Channels**

1. **Open Telegram** and go to the channels you want to monitor
2. **Add the bot** to each channel:
   - Go to channel settings → Administrators
   - Click "Add Admin"
   - Search for `@your_bot_username_here`
   - Add the bot as an admin
3. **Give permissions** to read messages:
   - Make sure "Read Messages" is enabled
   - The bot needs this to monitor for stock mentions

### **Step 2: Configure Your Dashboard**

Add the bot token to your `.env` file:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### **Step 3: Start Monitoring**

1. **Run your dashboard:** `streamlit run app/main.py`
2. **Go to Telegram Monitor** (sidebar button or radio option)
3. **Click "Start Monitoring"**
4. **View results** for stock mentions

## 📊 **What the Bot Monitors**

Your bot will automatically track mentions of your **42 portfolio tickers**:

### **Brazilian Stocks (Acoes_B3)**
- VAMO3, SANB11, EGIE3, VBBR3, CSAN3, ISAE4, SAPR4, PRIO3, GOAU4, PSSA3, CPLE6, UNIP6, VIVT3, FESA4, ITSA4

### **US Stocks (US_NYSE)**
- WBD, LIT, TLT, QQQ, SOXX, VNQ, SGOV, BRK.B, XLE, XLV, HDV, LTC, CQQQ, APPS

### **FII Funds (FII_B3)**
- VISC11, HGLG11, HGRU11, BTLG11, KNCR11, XPLG11, MXRF11, RZTR11, HCTR11, CPTI11

## 🔍 **How It Works**

1. **Bot joins channels** you add it to
2. **Monitors messages** for your stock tickers
3. **Filters mentions** automatically
4. **Tracks engagement** (views, forwards)
5. **Shows analytics** in your dashboard

## 📱 **Channel Setup Examples**

### **Financial News Channels**
- Add bot to `@stocknews`, `@brstocks`, `@usstocks`
- Bot will track mentions of your stocks
- Get real-time alerts for your portfolio

### **FII Discussion Groups**
- Add bot to `@fiidiscussion`, `@rendafixa`
- Monitor FII-specific discussions
- Track FII fund mentions

### **Sector-Specific Channels**
- Add bot to energy, mining, tech channels
- Track sector-specific stock discussions
- Get insights on your holdings

## ⚙️ **Bot Permissions Required**

The bot needs these permissions in each channel:

- ✅ **Read Messages** - To monitor for stock mentions
- ✅ **Read Message History** - To access past messages
- ❌ **Send Messages** - Not needed (bot only reads)
- ❌ **Delete Messages** - Not needed
- ❌ **Ban Users** - Not needed

## 🔧 **Troubleshooting**

### **"No messages found"**
- **Check bot permissions** - Make sure it can read messages
- **Verify channel membership** - Bot must be added to channels
- **Check message activity** - Channels need recent messages
- **Adjust time range** - Try looking back further

### **"Bot not responding"**
- **Check bot token** - Verify it's correct in .env file
- **Restart dashboard** - Reload the Streamlit app
- **Check internet connection** - Bot needs API access

### **"No updates found"**
- **Add bot to channels** - Bot needs to be in channels to see messages
- **Give admin permissions** - Bot needs to read messages
- **Wait for messages** - Bot only sees messages after it's added

## 📊 **Dashboard Features**

### **Real-time Monitoring**
- **Live message tracking** from your channels
- **Automatic ticker detection** in messages
- **Engagement metrics** (views, forwards)
- **Time-based filtering** (last 24 hours, week, etc.)

### **Analytics**
- **Ticker mention frequency** charts
- **Channel performance** comparison
- **Trending stocks** in your portfolio
- **Message engagement** analysis

### **Filtering Options**
- **Minimum mentions** threshold
- **Time range** selection
- **Channel-specific** filtering
- **Ticker-specific** filtering

## 🎉 **Success!**

Once set up, you'll have:

- **Real-time monitoring** of your portfolio stocks
- **Engagement analytics** from Telegram discussions
- **Trending insights** from community discussions
- **Early warning system** for market movements
- **Research assistance** for investment decisions

## 🔒 **Security Notes**

- **Bot token is secure** - Only you can use it
- **No message storage** - Bot only reads, doesn't store
- **Privacy respected** - Only ticker mentions are tracked
- **Channel permissions** - Bot only reads what it's allowed to

## 📞 **Need Help?**

If you encounter issues:

1. **Check bot permissions** in channels
2. **Verify bot token** in .env file
3. **Restart the dashboard** application
4. **Check channel activity** - Make sure there are recent messages

Your bot is ready to monitor your portfolio stocks across Telegram channels! 🚀📱
