# 📱 Telegram Integration Setup Guide

This guide will help you set up Telegram channel monitoring for your portfolio stocks.

## 🎯 What This Does

The Telegram integration allows you to:
- **Monitor multiple Telegram channels** for mentions of your portfolio stocks
- **Filter messages** by ticker symbols automatically
- **Track engagement metrics** (views, forwards) for stock mentions
- **Analyze sentiment** and discussions around your holdings
- **Get real-time alerts** when your stocks are mentioned

## 🔧 Setup Steps

### 1. Get Telegram API Credentials

1. **Visit Telegram API page:**
   - Go to https://my.telegram.org/apps
   - Log in with your Telegram account

2. **Create a new application:**
   - Click "Create new application"
   - Fill in the form:
     - **App title:** Portfolio Monitor (or any name)
     - **Short name:** portfoliomonitor
     - **Platform:** Desktop
   - Click "Create application"

3. **Copy your credentials:**
   - **API ID:** Copy the numeric ID
   - **API Hash:** Copy the hash string

### 2. Configure Environment Variables

Add these to your `.env` file:

```bash
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890
```

**Important:** Use your phone number with country code (e.g., +1234567890)

### 3. Install Dependencies

The required dependency is already in `requirements.txt`:

```bash
pip install telethon
```

### 4. First-Time Authentication

When you first run the Telegram monitor, you'll need to authenticate:

1. **Run the dashboard** and go to Telegram Monitor
2. **Click "Load Available Channels"**
3. **Enter your phone number** when prompted
4. **Enter the verification code** sent to your phone
5. **Enter your 2FA password** if you have 2FA enabled

This creates a session file that will be reused for future runs.

## 📺 Using the Telegram Monitor

### Channel Selection

1. **Go to Telegram Monitor** in the main dashboard
2. **Click "Load Available Channels"** to see your joined channels
3. **Select channels** you want to monitor
4. **Configure monitoring settings:**
   - Hours to look back
   - Messages per channel
   - Minimum mentions threshold

### Monitoring Features

- **Real-time filtering** by your portfolio tickers
- **Message analytics** with views and forwards
- **Trending stocks** in your portfolio
- **Channel performance** metrics
- **Historical tracking** of mentions

### Filtering Options

- **Include hashtags** (#AAPL, #VALE3)
- **Include dollar signs** ($AAPL, $VALE3)
- **Case sensitivity** options
- **Whole words only** matching

## 🔍 Example Use Cases

### 1. News Monitoring
Monitor financial news channels for mentions of your stocks:
- `@stocknews` - General market news
- `@brstocks` - Brazilian stock discussions
- `@usstocks` - US stock discussions

### 2. FII Discussions
Track FII (Real Estate Investment Fund) discussions:
- `@fiidiscussion` - FII-specific channels
- `@rendafixa` - Fixed income discussions

### 3. Sector Analysis
Monitor sector-specific channels:
- `@energia` - Energy sector
- `@mineracao` - Mining sector
- `@tecnologia` - Technology sector

## 📊 Dashboard Features

### Message Statistics
- **Total messages** found
- **Unique tickers** mentioned
- **Channel breakdown** of mentions
- **Engagement metrics** (views, forwards)

### Recent Messages
- **Last 10 messages** mentioning your stocks
- **Message preview** with full text
- **Engagement data** for each message
- **Time stamps** for tracking

### Analytics Charts
- **Ticker mention frequency** bar chart
- **Channel performance** comparison
- **Time-based trends** of mentions
- **Engagement correlation** analysis

## ⚙️ Configuration Options

### Monitoring Schedule
- **Check frequency:** Every 5 minutes to 1 hour
- **Retention period:** 1 day to 1 month
- **Message limits:** 10-200 messages per channel

### Filter Settings
- **Minimum mentions:** Filter out low-activity mentions
- **Include views/forwards:** Show engagement metrics
- **Case sensitivity:** Match exact case or ignore
- **Whole words:** Match complete words only

### Channel Management
- **Add/remove channels** dynamically
- **Channel performance** tracking
- **Mention frequency** by channel
- **Engagement rates** comparison

## 🚨 Important Notes

### Privacy & Security
- **Session files** are stored locally and encrypted
- **No message content** is stored permanently
- **Only ticker mentions** are tracked
- **Full message text** is only shown in the dashboard

### Rate Limits
- **Telegram API limits** apply (30 requests per second)
- **Channel access** depends on your membership
- **Message history** limited by channel settings
- **Monitoring frequency** should respect API limits

### Legal Considerations
- **Respect channel rules** and terms of service
- **Don't spam** or abuse the monitoring
- **Use responsibly** for investment research
- **Follow Telegram's** terms of service

## 🔧 Troubleshooting

### Common Issues

1. **"No channels found"**
   - Make sure you're a member of the channels
   - Check if channels are public or private
   - Verify your Telegram account is active

2. **"Authentication failed"**
   - Check your API credentials
   - Verify your phone number format
   - Try deleting the session file and re-authenticating

3. **"Rate limit exceeded"**
   - Reduce monitoring frequency
   - Decrease message limits per channel
   - Wait before retrying

4. **"No messages found"**
   - Check if your tickers are mentioned
   - Verify channel activity
   - Adjust time range settings

### Getting Help

If you encounter issues:
1. **Check the logs** in the terminal
2. **Verify your configuration** in the .env file
3. **Test with a simple channel** first
4. **Check Telegram's status** for API issues

## 🎉 Success!

Once configured, you'll have:
- **Real-time monitoring** of your portfolio stocks
- **Engagement analytics** from Telegram discussions
- **Trending insights** from community discussions
- **Early warning system** for market movements
- **Research assistance** for investment decisions

Happy monitoring! 📱📊
