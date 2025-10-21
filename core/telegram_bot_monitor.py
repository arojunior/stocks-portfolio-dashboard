"""
Simplified Telegram monitoring using bot API
"""

import os
import asyncio
import streamlit as st
from typing import Set, Dict, List, Optional
from datetime import datetime, timedelta
import json
import requests

class TelegramBotMonitor:
    """Simplified Telegram monitoring using bot API"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot_username = os.getenv("TELEGRAM_BOT_USERNAME", "your_bot_username")
        self.portfolio_tickers = set()
        self.message_cache = {}

    def load_portfolio_tickers(self) -> Set[str]:
        """Load all tickers from portfolios"""
        try:
            with open("portfolios.json", "r") as f:
                portfolios = json.load(f)
            
            tickers = set()
            for portfolio_name, stocks in portfolios.items():
                for ticker in stocks.keys():
                    # Clean ticker (remove .SA suffix for Brazilian stocks)
                    clean_ticker = ticker.replace(".SA", "")
                    tickers.add(clean_ticker)
            
            self.portfolio_tickers = tickers
            return tickers
        except Exception as e:
            st.error(f"Error loading portfolio tickers: {e}")
            return set()

    def get_bot_info(self) -> Optional[Dict]:
        """Get bot information"""
        if not self.bot_token:
            return None
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get("result")
        except Exception as e:
            st.error(f"Error getting bot info: {e}")
            return None

    def search_messages(self, query: str, limit: int = 100) -> List[Dict]:
        """Search for messages containing the query"""
        if not self.bot_token:
            return []
        
        # This is a simplified implementation
        # In a real scenario, you'd need to implement message search
        # which requires the bot to be added to channels/groups
        return []

    def display_bot_status(self):
        """Display bot status and information"""
        st.subheader("🤖 Bot Status")
        
        if not self.bot_token:
            st.error("❌ Bot token not configured")
            st.info("Please set TELEGRAM_BOT_TOKEN in your environment variables")
            return False
        
        bot_data = self.get_bot_info()
        if not bot_data:
            st.error("❌ Unable to connect to bot")
            return False
        
        # Display bot information
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Bot ID", bot_data.get("id", "Unknown"))
            st.metric("Username", f"@{bot_data.get('username', 'Unknown')}")
            st.metric("First Name", bot_data.get("first_name", "Unknown"))
        
        with col2:
            st.metric("Bot Name", bot_data.get("first_name", "Unknown"))
            st.metric("Can Join Groups", "✅" if bot_data.get("can_join_groups") else "❌")

        # Bot URL
        bot_url = f"https://t.me/{bot_data.get('username', 'your_bot_username')}"
        st.markdown(f"**Bot Link:** [{bot_url}]({bot_url})")

        # Instructions
        st.info("""
        **To use this bot for monitoring:**

        1. **Add bot to channels/groups:**
           - Go to your Telegram channels/groups
           - Add this bot as an admin
           - Give it permission to read messages

        2. **Start monitoring:**
           - Use the monitoring interface below
           - The bot will search for mentions of your portfolio stocks
        """)

        return True

    def display_portfolio_tickers(self):
        """Display loaded portfolio tickers"""
        st.subheader("📊 Portfolio Tickers")
        
        tickers = self.load_portfolio_tickers()
        
        if not tickers:
            st.warning("No portfolio tickers found")
            return
        
        # Display tickers in columns
        cols = st.columns(4)
        for i, ticker in enumerate(sorted(tickers)):
            with cols[i % 4]:
                st.code(ticker)
        
        st.info(f"**Total tickers loaded:** {len(tickers)}")

    def display_monitoring_interface(self):
        """Display the monitoring interface"""
        st.subheader("🔍 Monitoring Interface")
        
        # Search options
        col1, col2 = st.columns(2)
        
        with col1:
            search_query = st.text_input(
                "Search Query",
                placeholder="Enter stock ticker or keyword",
                help="Search for specific stock mentions"
            )
        
        with col2:
            message_limit = st.number_input(
                "Message Limit",
                min_value=10,
                max_value=1000,
                value=100,
                help="Maximum number of messages to retrieve"
            )
        
        # Time range
        time_range = st.selectbox(
            "Time Range",
            ["Last hour", "Last 6 hours", "Last 24 hours", "Last week"],
            index=2
        )
        
        # Search button
        if st.button("🔍 Search Messages", type="primary"):
            if search_query:
                self.search_and_display_messages(search_query, message_limit, time_range)
            else:
                st.warning("Please enter a search query")

    def search_and_display_messages(self, query: str, limit: int, time_range: str):
        """Search and display messages"""
        st.subheader(f"🔍 Search Results for: {query}")
        
        # This is a simplified implementation
        # In a real scenario, you'd implement actual message search
        st.info("""
        **Note:** This is a simplified demonstration.
        
        In a real implementation, the bot would:
        1. Search through channels/groups it's added to
        2. Filter messages by time range
        3. Look for mentions of your portfolio stocks
        4. Display relevant messages with context
        """)
        
        # Simulate search results
        st.success(f"Search completed for '{query}' with limit {limit} in {time_range}")

    def display_help(self):
        """Display help information"""
        st.subheader("❓ How to Use")

        st.markdown("""
        **Step 1: Add Bot to Channels**
        - Go to your Telegram channels
        - Add @your_bot_username as an admin
        - Give it permission to read messages

        **Step 2: Start Monitoring**
        - Use the monitoring interface above
        - Set your preferences (time range, message limits)
        - Search for specific stock mentions

        **Step 3: Review Results**
        - View filtered messages
        - Analyze stock mentions
        - Track market sentiment
        """)

def display_telegram_bot_dashboard():
    """Display the Telegram bot monitoring dashboard"""
    st.title("📱 Telegram Bot Monitor")
    st.markdown("Monitor Telegram channels for stock mentions using your bot")
    
    monitor = TelegramBotMonitor()
    
    # Display bot status
    if not monitor.display_bot_status():
        return
    
    # Display portfolio tickers
    monitor.display_portfolio_tickers()
    
    # Display monitoring interface
    monitor.display_monitoring_interface()
    
    # Display help
    monitor.display_help()
