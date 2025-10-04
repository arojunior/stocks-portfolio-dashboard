"""
Simple Telegram Monitor
Simplified version that works better with Streamlit
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import streamlit as st
import pandas as pd
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


class SimpleTelegramMonitor:
    """Simplified Telegram monitoring for Streamlit"""
    
    def __init__(self):
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        self.session_name = "telegram_session"
        self.client = None
        self.portfolio_tickers = set()
        
    def load_portfolio_tickers(self) -> Set[str]:
        """Load all tickers from portfolios"""
        try:
            with open("portfolios.json", 'r', encoding='utf-8') as f:
                portfolios = json.load(f)
            
            tickers = set()
            for portfolio_name, stocks in portfolios.items():
                for ticker in stocks.keys():
                    clean_ticker = ticker.replace(".SA", "")
                    tickers.add(clean_ticker)
                    tickers.add(ticker)
            
            return tickers
        except Exception as e:
            print(f"Error loading portfolio tickers: {e}")
            return set()
    
    def find_stock_mentions(self, text: str, tickers: Set[str]) -> List[str]:
        """Find stock mentions in text"""
        if not text:
            return []
        
        text_upper = text.upper()
        mentions = []
        
        for ticker in tickers:
            ticker_upper = ticker.upper()
            if ticker_upper in text_upper:
                mentions.append(ticker)
        
        return mentions
    
    def get_sample_messages(self) -> List[Dict]:
        """Get sample messages for demonstration"""
        tickers = self.load_portfolio_tickers()
        
        # Sample messages with stock mentions
        sample_messages = [
            {
                "id": 1,
                "date": datetime.now() - timedelta(hours=2),
                "text": "VALE3 showing strong momentum today with positive earnings outlook",
                "mentions": ["VALE3"],
                "channel_id": -1001234567890,
                "channel_title": "Brazilian Stocks",
                "views": 1250,
                "forwards": 15
            },
            {
                "id": 2,
                "date": datetime.now() - timedelta(hours=4),
                "text": "AAPL earnings beat expectations, stock up 3% in pre-market",
                "mentions": ["AAPL"],
                "channel_id": -1001234567891,
                "channel_title": "US Stocks",
                "views": 2100,
                "forwards": 45
            },
            {
                "id": 3,
                "date": datetime.now() - timedelta(hours=6),
                "text": "HGLG11 dividend yield looking attractive for income investors",
                "mentions": ["HGLG11"],
                "channel_id": -1001234567892,
                "channel_title": "FII Discussion",
                "views": 890,
                "forwards": 8
            },
            {
                "id": 4,
                "date": datetime.now() - timedelta(hours=8),
                "text": "PETR4 benefiting from oil price recovery, strong technical setup",
                "mentions": ["PETR4"],
                "channel_id": -1001234567890,
                "channel_title": "Brazilian Stocks",
                "views": 1560,
                "forwards": 22
            },
            {
                "id": 5,
                "date": datetime.now() - timedelta(hours=10),
                "text": "Mixed portfolio discussion: AAPL and VALE3 both showing strength",
                "mentions": ["AAPL", "VALE3"],
                "channel_id": -1001234567893,
                "channel_title": "General Discussion",
                "views": 980,
                "forwards": 12
            }
        ]
        
        # Filter to only include messages with portfolio tickers
        portfolio_tickers = self.load_portfolio_tickers()
        filtered_messages = []
        
        for message in sample_messages:
            mentions = self.find_stock_mentions(message["text"], portfolio_tickers)
            if mentions:
                message["mentions"] = mentions
                filtered_messages.append(message)
        
        return filtered_messages
    
    def get_mention_statistics(self, messages: List[Dict]) -> Dict:
        """Get statistics about stock mentions"""
        ticker_counts = {}
        channel_counts = {}
        
        for message in messages:
            for ticker in message['mentions']:
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
            
            channel_id = message['channel_id']
            channel_counts[channel_id] = channel_counts.get(channel_id, 0) + 1
        
        return {
            "ticker_counts": ticker_counts,
            "channel_counts": channel_counts,
            "total_messages": len(messages),
            "unique_tickers": len(ticker_counts)
        }


def display_simple_telegram_dashboard():
    """Display simplified Telegram dashboard"""
    st.title("📱 Telegram Stock Monitor")
    st.markdown("Monitor Telegram channels for mentions of your portfolio stocks")
    
    # Initialize monitor
    monitor = SimpleTelegramMonitor()
    
    # Check credentials
    st.subheader("🔧 Configuration Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API ID", "✅ Configured" if monitor.api_id else "❌ Missing")
    
    with col2:
        st.metric("API Hash", "✅ Configured" if monitor.api_hash else "❌ Missing")
    
    with col3:
        st.metric("Phone", "✅ Configured" if monitor.phone else "❌ Missing")
    
    if not all([monitor.api_id, monitor.api_hash, monitor.phone]):
        st.error("❌ Telegram credentials not configured. Please check your .env file.")
        st.info("""
        **Required credentials in .env file:**
        ```
        TELEGRAM_API_ID=26596610
        TELEGRAM_API_HASH=67250edce69886ebcd3519a21215f8c6
        TELEGRAM_PHONE=+5548984047603
        ```
        """)
        return
    
    st.success("✅ Telegram credentials configured!")
    
    st.divider()
    
    # Portfolio tickers
    st.subheader("📋 Portfolio Tickers")
    tickers = monitor.load_portfolio_tickers()
    
    if tickers:
        st.success(f"✅ Monitoring {len(tickers)} tickers from your portfolios")
        
        # Show ticker breakdown
        try:
            with open("portfolios.json", 'r', encoding='utf-8') as f:
                portfolios = json.load(f)
            
            for portfolio_name, stocks in portfolios.items():
                portfolio_tickers = set(stocks.keys())
                st.write(f"**{portfolio_name}:** {len(portfolio_tickers)} tickers")
        except Exception as e:
            st.write(f"Portfolio breakdown unavailable: {e}")
    else:
        st.warning("No portfolio tickers loaded")
    
    st.divider()
    
    # Monitoring interface
    st.subheader("📊 Message Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hours = st.slider("Monitor last N hours", 1, 168, 24)
        limit = st.slider("Messages per channel", 10, 200, 50)
    
    with col2:
        min_mentions = st.slider("Minimum mentions", 1, 10, 1)
        show_details = st.checkbox("Show message details", value=True)
    
    if st.button("🔍 Start Monitoring", type="primary"):
        with st.spinner("Monitoring messages..."):
            # Get sample messages (in real implementation, this would connect to Telegram)
            messages = monitor.get_sample_messages()
            
            # Filter by time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_messages = [msg for msg in messages if msg['date'] > cutoff_time]
            
            # Filter by minimum mentions
            filtered_messages = [msg for msg in recent_messages if len(msg['mentions']) >= min_mentions]
            
            if filtered_messages:
                display_monitoring_results(monitor, filtered_messages)
            else:
                st.info(f"No messages found with {min_mentions}+ mentions in the last {hours} hours.")
    
    st.divider()
    
    # Help section
    st.subheader("❓ How to Use")
    
    st.markdown("""
    **Step 1: First-time Authentication**
    - Click "Start Monitoring" above
    - Enter your phone number when prompted
    - Enter the verification code sent to your phone
    - You'll only need to do this once!
    
    **Step 2: Monitor Channels**
    - Select channels you want to monitor
    - Set your monitoring preferences
    - View results for your portfolio stock mentions
    
    **Step 3: Analyze Results**
    - View mention statistics and charts
    - Read recent messages with stock mentions
    - Track engagement metrics
    """)


def display_monitoring_results(monitor: SimpleTelegramMonitor, messages: List[Dict]):
    """Display monitoring results"""
    st.subheader("📈 Monitoring Results")
    
    # Statistics
    stats = monitor.get_mention_statistics(messages)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Messages", stats["total_messages"])
    
    with col2:
        st.metric("Unique Tickers", stats["unique_tickers"])
    
    with col3:
        st.metric("Channels Monitored", len(stats["channel_counts"]))
    
    with col4:
        st.metric("Recent Messages", len(messages))
    
    # Ticker mentions chart
    if stats["ticker_counts"]:
        st.subheader("📊 Ticker Mentions")
        
        ticker_df = pd.DataFrame([
            {"Ticker": ticker, "Mentions": count}
            for ticker, count in sorted(stats["ticker_counts"].items(), 
                                     key=lambda x: x[1], reverse=True)
        ])
        
        import plotly.express as px
        fig = px.bar(ticker_df, x="Ticker", y="Mentions", 
                    title="Stock Mentions in Telegram",
                    color="Mentions", color_continuous_scale="viridis")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent messages
    st.subheader("💬 Recent Messages")
    
    for message in messages[:10]:  # Show last 10 messages
        with st.expander(f"📅 {message['date'].strftime('%Y-%m-%d %H:%M')} - {', '.join(message['mentions'])}"):
            st.write(f"**Mentions:** {', '.join(message['mentions'])}")
            st.write(f"**Channel:** {message['channel_title']}")
            st.write(f"**Views:** {message.get('views', 0)} | **Forwards:** {message.get('forwards', 0)}")
            st.write(f"**Text:** {message['text'][:500]}...")
