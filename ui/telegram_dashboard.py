"""
Telegram Dashboard UI
Streamlit interface for Telegram channel monitoring
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import json
from core.telegram_monitor import TelegramMonitor, TelegramDashboard


def display_telegram_dashboard():
    """Main Telegram dashboard interface"""
    st.title("📱 Telegram Stock Monitor")
    st.markdown("Monitor Telegram channels for mentions of your portfolio stocks")
    
    # Initialize dashboard
    dashboard = TelegramDashboard()
    
    # Display setup instructions
    dashboard.display_telegram_setup()
    
    st.divider()
    
    # Channel monitoring section
    display_channel_monitoring()
    
    st.divider()
    
    # Message analysis section
    display_message_analysis()
    
    st.divider()
    
    # Configuration section
    display_telegram_configuration()


def display_channel_monitoring():
    """Display channel monitoring interface"""
    st.subheader("📺 Channel Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Monitor Settings**")
        hours = st.slider("Monitor last N hours", 1, 168, 24, help="How far back to look for messages")
        limit = st.slider("Messages per channel", 10, 200, 50, help="Maximum messages to check per channel")
    
    with col2:
        st.markdown("**Filter Settings**")
        min_mentions = st.slider("Minimum mentions", 1, 10, 1, help="Minimum number of stock mentions to show")
        show_views = st.checkbox("Show message views", value=True)
        show_forwards = st.checkbox("Show message forwards", value=True)
    
    # Channel selection
    st.markdown("**Select Channels to Monitor**")
    
    # This would be populated with actual channels when Telegram is configured
    sample_channels = [
        {"id": 1, "title": "Stock Market News", "username": "stocknews", "participants_count": 50000},
        {"id": 2, "title": "Brazilian Stocks", "username": "brstocks", "participants_count": 25000},
        {"id": 3, "title": "FII Discussion", "username": "fiidiscussion", "participants_count": 15000},
        {"id": 4, "title": "US Stocks", "username": "usstocks", "participants_count": 30000},
    ]
    
    selected_channels = []
    for channel in sample_channels:
        if st.checkbox(f"📺 {channel['title']} ({channel['participants_count']:,} members)", key=f"channel_{channel['id']}"):
            selected_channels.append(channel['id'])
    
    if st.button("🔍 Start Monitoring", type="primary"):
        if selected_channels:
            with st.spinner("Monitoring channels for stock mentions..."):
                # This would call the actual monitoring function
                st.success(f"Monitoring {len(selected_channels)} channels...")
                st.info("Telegram monitoring requires proper API configuration to work.")
        else:
            st.warning("Please select at least one channel to monitor.")


def display_message_analysis():
    """Display message analysis interface"""
    st.subheader("📊 Message Analysis")
    
    # Sample data for demonstration
    sample_messages = [
        {
            "date": datetime.now() - timedelta(hours=2),
            "ticker": "VALE3",
            "text": "VALE3 showing strong momentum today with positive earnings outlook",
            "channel": "Brazilian Stocks",
            "views": 1250,
            "forwards": 15
        },
        {
            "date": datetime.now() - timedelta(hours=4),
            "ticker": "AAPL",
            "text": "AAPL earnings beat expectations, stock up 3% in pre-market",
            "channel": "US Stocks",
            "views": 2100,
            "forwards": 45
        },
        {
            "date": datetime.now() - timedelta(hours=6),
            "ticker": "HGLG11",
            "text": "HGLG11 dividend yield looking attractive for income investors",
            "channel": "FII Discussion",
            "views": 890,
            "forwards": 8
        },
        {
            "date": datetime.now() - timedelta(hours=8),
            "ticker": "PETR4",
            "text": "PETR4 benefiting from oil price recovery, strong technical setup",
            "channel": "Brazilian Stocks",
            "views": 1560,
            "forwards": 22
        }
    ]
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Messages", len(sample_messages))
    
    with col2:
        unique_tickers = len(set(msg['ticker'] for msg in sample_messages))
        st.metric("Unique Tickers", unique_tickers)
    
    with col3:
        total_views = sum(msg['views'] for msg in sample_messages)
        st.metric("Total Views", f"{total_views:,}")
    
    with col4:
        total_forwards = sum(msg['forwards'] for msg in sample_messages)
        st.metric("Total Forwards", f"{total_forwards:,}")
    
    # Ticker mention chart
    st.subheader("📈 Ticker Mentions")
    
    ticker_counts = {}
    for msg in sample_messages:
        ticker = msg['ticker']
        ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
    
    if ticker_counts:
        ticker_df = pd.DataFrame([
            {"Ticker": ticker, "Mentions": count}
            for ticker, count in ticker_counts.items()
        ])
        
        fig = px.bar(ticker_df, x="Ticker", y="Mentions", 
                    title="Stock Mentions in Telegram Channels",
                    color="Mentions", color_continuous_scale="viridis")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent messages table
    st.subheader("💬 Recent Messages")
    
    if sample_messages:
        messages_df = pd.DataFrame(sample_messages)
        messages_df['date'] = messages_df['date'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Format the dataframe for display
        display_df = messages_df[['date', 'ticker', 'text', 'channel', 'views', 'forwards']].copy()
        display_df.columns = ['Date', 'Ticker', 'Message', 'Channel', 'Views', 'Forwards']
        
        # Truncate long messages
        display_df['Message'] = display_df['Message'].apply(lambda x: x[:100] + "..." if len(x) > 100 else x)
        
        st.dataframe(display_df, width='stretch')
    else:
        st.info("No messages found")


def display_telegram_configuration():
    """Display Telegram configuration interface"""
    st.subheader("⚙️ Configuration")
    
    # API Configuration
    st.markdown("**API Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("API ID", value="", help="Your Telegram API ID", disabled=True)
        st.text_input("API Hash", value="", help="Your Telegram API Hash", disabled=True)
    
    with col2:
        st.text_input("Phone Number", value="", help="Your phone number with country code", disabled=True)
        st.text_input("Session Name", value="telegram_session", help="Session file name", disabled=True)
    
    st.info("""
    **Configuration Steps:**
    
    1. **Get API Credentials:**
       - Visit https://my.telegram.org/apps
       - Create a new application
       - Copy your API ID and API Hash
    
    2. **Set Environment Variables:**
       ```bash
       export TELEGRAM_API_ID=your_api_id
       export TELEGRAM_API_HASH=your_api_hash
       export TELEGRAM_PHONE=+1234567890
       ```
    
    3. **Add to .env file:**
       ```
       TELEGRAM_API_ID=your_api_id
       TELEGRAM_API_HASH=your_api_hash
       TELEGRAM_PHONE=+1234567890
       ```
    """)
    
    # Channel Configuration
    st.markdown("**Channel Configuration**")
    
    st.text_area("Monitored Channels", 
                value="""# Add channel usernames or IDs here
@stocknews
@brstocks
@fiidiscussion
@usstocks""", 
                help="One channel per line, use @username or channel ID")
    
    # Filter Configuration
    st.markdown("**Filter Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Include hashtags", value=True, help="Include messages with #ticker")
        st.checkbox("Include dollar signs", value=True, help="Include messages with $ticker")
    
    with col2:
        st.checkbox("Case sensitive", value=False, help="Match exact case")
        st.checkbox("Whole words only", value=True, help="Match whole words only")
    
    # Monitoring Schedule
    st.markdown("**Monitoring Schedule**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Check Frequency", ["Every 5 minutes", "Every 15 minutes", "Every hour", "Every 6 hours"], index=1)
    
    with col2:
        st.selectbox("Retention Period", ["1 day", "3 days", "1 week", "1 month"], index=2)


def display_telegram_integration_help():
    """Display help for Telegram integration"""
    st.subheader("❓ How to Use Telegram Integration")
    
    st.markdown("""
    **Telegram Stock Monitoring** allows you to:
    
    ### 📱 **Features:**
    - **Monitor multiple channels** for mentions of your portfolio stocks
    - **Real-time filtering** by ticker symbols
    - **Message analytics** with views and forwards
    - **Historical tracking** of stock mentions
    - **Customizable filters** for relevant content
    
    ### 🔧 **Setup Process:**
    1. **Get Telegram API credentials** from https://my.telegram.org/apps
    2. **Configure environment variables** with your credentials
    3. **Select channels to monitor** from your joined channels
    4. **Set up filters** for relevant stock mentions
    5. **Start monitoring** and analyze results
    
    ### 📊 **What You'll See:**
    - **Stock mention statistics** across channels
    - **Recent messages** mentioning your stocks
    - **Engagement metrics** (views, forwards)
    - **Trending stocks** in your portfolio
    - **Channel performance** for stock discussions
    
    ### 🎯 **Use Cases:**
    - **News monitoring** for your holdings
    - **Sentiment analysis** of stock discussions
    - **Early warning system** for market movements
    - **Community insights** from fellow investors
    - **Research assistance** for investment decisions
    """)


if __name__ == "__main__":
    display_telegram_dashboard()
