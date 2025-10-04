"""
Telegram Channel Monitor
Monitors Telegram channels for mentions of portfolio stocks
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import streamlit as st
from telethon import TelegramClient
from telethon.tl.types import Message
from telethon.errors import SessionPasswordNeededError
import asyncio
import pandas as pd


class TelegramMonitor:
    """Monitors Telegram channels for stock mentions"""

    def __init__(self):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        self.session_name = "telegram_session"
        self.client = None
        self.portfolio_tickers = set()
        self.monitored_channels = []
        self.message_cache = {}

    def load_portfolio_tickers(self) -> Set[str]:
        """Load all tickers from portfolios"""
        try:
            with open("portfolios.json", 'r', encoding='utf-8') as f:
                portfolios = json.load(f)

            tickers = set()
            for portfolio_name, stocks in portfolios.items():
                for ticker in stocks.keys():
                    # Clean ticker names (remove .SA suffix for Brazilian stocks)
                    clean_ticker = ticker.replace(".SA", "")
                    tickers.add(clean_ticker)
                    tickers.add(ticker)  # Also keep original

            return tickers
        except Exception as e:
            print(f"Error loading portfolio tickers: {e}")
            return set()

    async def initialize_client(self) -> bool:
        """Initialize Telegram client"""
        try:
            if not all([self.api_id, self.api_hash, self.phone]):
                return False

            self.client = TelegramClient(
                self.session_name,
                int(self.api_id),
                self.api_hash
            )

            await self.client.start(phone=self.phone)
            return True
        except Exception as e:
            print(f"Error initializing Telegram client: {e}")
            return False

    async def get_available_channels(self) -> List[Dict]:
        """Get list of available channels"""
        if not self.client:
            return []

        try:
            channels = []
            async for dialog in self.client.iter_dialogs():
                if dialog.is_channel and dialog.entity.broadcast:
                    channels.append({
                        "id": dialog.id,
                        "title": dialog.title,
                        "username": dialog.entity.username,
                        "participants_count": getattr(dialog.entity, 'participants_count', 0)
                    })
            return channels
        except Exception as e:
            print(f"Error getting channels: {e}")
            return []

    def create_ticker_patterns(self, tickers: Set[str]) -> List[str]:
        """Create regex patterns for ticker matching"""
        patterns = []

        for ticker in tickers:
            # Create various patterns for each ticker
            patterns.extend([
                f"\\b{ticker}\\b",  # Word boundary
                f"#{ticker}\\b",    # Hashtag
                f"\\${ticker}\\b",  # Dollar sign (for US stocks)
                f"\\b{ticker}\\s",  # Ticker followed by space
            ])

        return patterns

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

    async def monitor_channel(self, channel_id: int, limit: int = 100) -> List[Dict]:
        """Monitor a specific channel for stock mentions"""
        if not self.client:
            return []

        try:
            messages = []
            tickers = self.load_portfolio_tickers()

            async for message in self.client.iter_messages(channel_id, limit=limit):
                if message.text:
                    mentions = self.find_stock_mentions(message.text, tickers)
                    if mentions:
                        messages.append({
                            "id": message.id,
                            "date": message.date,
                            "text": message.text,
                            "mentions": mentions,
                            "channel_id": channel_id,
                            "views": getattr(message, 'views', 0),
                            "forwards": getattr(message, 'forwards', 0)
                        })

            return messages
        except Exception as e:
            print(f"Error monitoring channel {channel_id}: {e}")
            return []

    async def monitor_multiple_channels(self, channel_ids: List[int], limit: int = 50) -> List[Dict]:
        """Monitor multiple channels for stock mentions"""
        all_messages = []

        for channel_id in channel_ids:
            messages = await self.monitor_channel(channel_id, limit)
            all_messages.extend(messages)

        # Sort by date (newest first)
        all_messages.sort(key=lambda x: x['date'], reverse=True)
        return all_messages

    def filter_messages_by_ticker(self, messages: List[Dict], ticker: str) -> List[Dict]:
        """Filter messages by specific ticker"""
        return [msg for msg in messages if ticker in msg['mentions']]

    def get_recent_messages(self, hours: int = 24) -> List[Dict]:
        """Get recent messages from cache"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_messages = []
        for channel_id, channel_messages in self.message_cache.items():
            for message in channel_messages:
                if message['date'] > cutoff_time:
                    recent_messages.append(message)

        return sorted(recent_messages, key=lambda x: x['date'], reverse=True)

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

    async def close_client(self):
        """Close Telegram client"""
        if self.client:
            await self.client.disconnect()


class TelegramDashboard:
    """Streamlit dashboard for Telegram monitoring"""

    def __init__(self):
        self.monitor = TelegramMonitor()

    def display_telegram_setup(self):
        """Display Telegram setup instructions"""
        st.subheader("🔧 Telegram Setup")

        st.info("""
        **To use Telegram monitoring, you need to:**

        1. **Get Telegram API credentials:**
           - Go to https://my.telegram.org/apps
           - Create a new application
           - Get your API ID and API Hash

        2. **Set environment variables:**
           - `TELEGRAM_API_ID`: Your API ID
           - `TELEGRAM_API_HASH`: Your API Hash
           - `TELEGRAM_PHONE`: Your phone number (with country code)

        3. **Add to your .env file:**
           ```
           TELEGRAM_API_ID=your_api_id
           TELEGRAM_API_HASH=your_api_hash
           TELEGRAM_PHONE=+1234567890
           ```
        """)

        # Check if credentials are set
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        phone = os.getenv("TELEGRAM_PHONE")

        if all([api_id, api_hash, phone]):
            st.success("✅ Telegram credentials configured!")
        else:
            st.warning("⚠️ Telegram credentials not configured")

    def display_channel_selector(self):
        """Display channel selection interface"""
        st.subheader("📺 Channel Selection")

        if st.button("🔄 Load Available Channels"):
            with st.spinner("Loading channels..."):
                # This would need to be run in an async context
                st.info("Channel loading requires async execution")

    def display_message_monitor(self):
        """Display message monitoring interface"""
        st.subheader("📊 Message Monitor")

        col1, col2 = st.columns(2)

        with col1:
            hours = st.slider("Monitor last N hours", 1, 168, 24)

        with col2:
            limit = st.slider("Messages per channel", 10, 200, 50)

        if st.button("🔍 Start Monitoring"):
            with st.spinner("Monitoring channels..."):
                st.info("Message monitoring requires async execution")

    def display_mention_statistics(self, messages: List[Dict]):
        """Display mention statistics"""
        if not messages:
            st.info("No messages found")
            return

        stats = self.monitor.get_mention_statistics(messages)

        st.subheader("📈 Mention Statistics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Messages", stats["total_messages"])

        with col2:
            st.metric("Unique Tickers", stats["unique_tickers"])

        with col3:
            st.metric("Channels Monitored", len(stats["channel_counts"]))

        # Top mentioned tickers
        if stats["ticker_counts"]:
            st.subheader("🏆 Most Mentioned Stocks")
            ticker_df = pd.DataFrame([
                {"Ticker": ticker, "Mentions": count}
                for ticker, count in sorted(stats["ticker_counts"].items(),
                                         key=lambda x: x[1], reverse=True)
            ])
            st.dataframe(ticker_df, width='stretch')

    def display_recent_messages(self, messages: List[Dict]):
        """Display recent messages"""
        if not messages:
            st.info("No recent messages found")
            return

        st.subheader("💬 Recent Messages")

        for message in messages[:10]:  # Show last 10 messages
            with st.expander(f"📅 {message['date'].strftime('%Y-%m-%d %H:%M')} - {', '.join(message['mentions'])}"):
                st.write(f"**Mentions:** {', '.join(message['mentions'])}")
                st.write(f"**Text:** {message['text'][:500]}...")
                st.write(f"**Views:** {message.get('views', 0)} | **Forwards:** {message.get('forwards', 0)}")

    def display_telegram_dashboard(self):
        """Main Telegram dashboard"""
        st.title("📱 Telegram Stock Monitor")
        st.markdown("Monitor Telegram channels for mentions of your portfolio stocks")

        # Setup instructions
        self.display_telegram_setup()

        st.divider()

        # Channel selection
        self.display_channel_selector()

        st.divider()

        # Message monitoring
        self.display_message_monitor()

        st.divider()

        # Display sample data (when implemented)
        st.subheader("📊 Sample Data")
        st.info("Telegram monitoring features will be available once credentials are configured and channels are selected.")


# Async helper functions for Streamlit
async def get_telegram_channels():
    """Get available Telegram channels"""
    monitor = TelegramMonitor()
    if await monitor.initialize_client():
        channels = await monitor.get_available_channels()
        await monitor.close_client()
        return channels
    return []


async def monitor_telegram_channels(channel_ids: List[int], limit: int = 50):
    """Monitor Telegram channels for stock mentions"""
    monitor = TelegramMonitor()
    if await monitor.initialize_client():
        messages = await monitor.monitor_multiple_channels(channel_ids, limit)
        await monitor.close_client()
        return messages
    return []
