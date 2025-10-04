"""
Live Telegram Monitor
Real Telegram connection with proper authentication handling
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


class LiveTelegramMonitor:
    """Live Telegram monitoring with proper authentication"""

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

    async def initialize_client(self) -> bool:
        """Initialize Telegram client with proper error handling"""
        try:
            if not all([self.api_id, self.api_hash, self.phone]):
                return False

            self.client = TelegramClient(
                self.session_name,
                int(self.api_id),
                self.api_hash
            )

            # Start client
            await self.client.start(phone=self.phone)
            return True

        except SessionPasswordNeededError:
            # Handle 2FA
            st.error("🔐 2FA is enabled on your account. Please enter your 2FA password.")
            password = st.text_input("2FA Password:", type="password", key="telegram_2fa")

            if st.button("Submit 2FA Password"):
                try:
                    await self.client.sign_in(password=password)
                    st.success("✅ 2FA authentication successful!")
                    return True
                except Exception as e:
                    st.error(f"❌ 2FA authentication failed: {e}")
                    return False
            return False

        except Exception as e:
            st.error(f"❌ Error connecting to Telegram: {e}")
            return False

    async def get_available_channels(self) -> List[Dict]:
        """Get list of available channels and groups"""
        if not self.client:
            return []

        try:
            channels = []
            async for dialog in self.client.iter_dialogs():
                # Include both channels and groups
                if dialog.is_channel or dialog.is_group:
                    # Get entity info
                    entity = dialog.entity

                    # Determine type
                    if dialog.is_channel and entity.broadcast:
                        chat_type = "Channel"
                    elif dialog.is_group:
                        chat_type = "Group"
                    else:
                        chat_type = "Supergroup"

                    channels.append({
                        "id": dialog.id,
                        "title": dialog.title,
                        "username": getattr(entity, 'username', None),
                        "participants_count": getattr(entity, 'participants_count', 0),
                        "type": chat_type,
                        "is_broadcast": getattr(entity, 'broadcast', False),
                        "is_megagroup": getattr(entity, 'megagroup', False)
                    })
            return channels
        except Exception as e:
            st.error(f"Error getting channels and groups: {e}")
            return []

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
            st.error(f"Error monitoring channel {channel_id}: {e}")
            return []

    async def close_client(self):
        """Close Telegram client"""
        if self.client:
            await self.client.disconnect()


def display_live_telegram_dashboard():
    """Display live Telegram dashboard"""
    st.title("📱 Live Telegram Stock Monitor")
    st.markdown("Monitor Telegram channels for mentions of your portfolio stocks")

    # Initialize monitor
    monitor = LiveTelegramMonitor()

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

    # Channel selection
    st.subheader("📺 Channel Selection")

    if st.button("🔄 Load Available Channels"):
        with st.spinner("Connecting to Telegram and loading channels..."):
            try:
                # Run async function
                import asyncio

                async def load_channels():
                    # Initialize client
                    success = await monitor.initialize_client()

                    if success:
                        st.success("✅ Connected to Telegram!")

                        # Get channels
                        channels = await monitor.get_available_channels()

                        if channels:
                            st.success(f"✅ Found {len(channels)} channels and groups")

                            # Display channels and groups
                            st.write("**Available Channels & Groups:**")
                            for i, channel in enumerate(channels[:10]):  # Show first 10
                                type_emoji = "📺" if channel['type'] == "Channel" else "👥" if channel['type'] == "Group" else "🔗"
                                st.write(f"{i+1}. {type_emoji} {channel['title']} ({channel['type']}) - {channel['participants_count']:,} members")

                            if len(channels) > 10:
                                st.write(f"... and {len(channels) - 10} more channels and groups")

                            # Store channels in session state
                            st.session_state['telegram_channels'] = channels

                        else:
                            st.warning("No channels found. Make sure you're a member of some channels.")

                        # Close client
                        await monitor.close_client()

                    else:
                        st.error("❌ Failed to connect to Telegram. Please check your credentials.")

                # Run the async function
                asyncio.run(load_channels())

            except Exception as e:
                st.error(f"❌ Error: {e}")

    # Channel monitoring
    if 'telegram_channels' in st.session_state:
        st.subheader("📊 Channel Monitoring")

        channels = st.session_state['telegram_channels']

        # Channel selection
        selected_channels = []
        for channel in channels[:10]:  # Show first 10 channels
            type_emoji = "📺" if channel['type'] == "Channel" else "👥" if channel['type'] == "Group" else "🔗"
            if st.checkbox(f"{type_emoji} {channel['title']} ({channel['type']}) - {channel['participants_count']:,} members", key=f"channel_{channel['id']}"):
                selected_channels.append(channel['id'])

        if selected_channels:
            col1, col2 = st.columns(2)

            with col1:
                hours = st.slider("Monitor last N hours", 1, 168, 24)
                limit = st.slider("Messages per channel", 10, 200, 50)

            with col2:
                min_mentions = st.slider("Minimum mentions", 1, 10, 1)
                show_details = st.checkbox("Show message details", value=True)

            if st.button("🔍 Start Live Monitoring", type="primary"):
                with st.spinner("Monitoring channels for stock mentions..."):
                    try:
                        # Run async function
                        import asyncio

                        async def monitor_channels():
                            # Initialize client
                            success = await monitor.initialize_client()

                            if success:
                                st.success("✅ Connected to Telegram!")

                                # Monitor selected channels
                                all_messages = []
                                for channel_id in selected_channels:
                                    messages = await monitor.monitor_channel(channel_id, limit)
                                    all_messages.extend(messages)

                                # Filter by time (handle timezone-aware datetimes)
                                cutoff_time = datetime.now() - timedelta(hours=hours)
                                
                                recent_messages = []
                                for msg in all_messages:
                                    msg_date = msg['date']
                                    
                                    # Handle timezone comparison safely
                                    try:
                                        # Try direct comparison first
                                        if msg_date > cutoff_time:
                                            recent_messages.append(msg)
                                    except TypeError:
                                        # If timezone comparison fails, convert to naive datetimes
                                        if msg_date.tzinfo is not None:
                                            msg_date = msg_date.replace(tzinfo=None)
                                        if cutoff_time.tzinfo is not None:
                                            cutoff_time = cutoff_time.replace(tzinfo=None)
                                        
                                        if msg_date > cutoff_time:
                                            recent_messages.append(msg)

                                # Filter by minimum mentions
                                filtered_messages = [msg for msg in recent_messages if len(msg['mentions']) >= min_mentions]

                                if filtered_messages:
                                    display_live_monitoring_results(monitor, filtered_messages)
                                else:
                                    st.info(f"No messages found with {min_mentions}+ mentions in the last {hours} hours.")

                                # Close client
                                await monitor.close_client()

                            else:
                                st.error("❌ Failed to connect to Telegram.")

                        # Run the async function
                        asyncio.run(monitor_channels())

                    except Exception as e:
                        st.error(f"❌ Error during monitoring: {e}")

    st.divider()

    # Help section
    st.subheader("❓ How to Use")

    st.markdown("""
    **Step 1: Load Channels & Groups**
    - Click "Load Available Channels" above
    - Enter your phone number when prompted
    - Enter the verification code sent to your phone
    - You'll only need to do this once!

    **Step 2: Select Channels & Groups**
    - Choose channels and groups you want to monitor
    - Groups often have more active discussions
    - Set your monitoring preferences
    - Click "Start Live Monitoring"

    **Step 3: View Results**
    - See real-time stock mentions from all sources
    - View analytics and engagement metrics
    - Read full message content
    """)


def display_live_monitoring_results(monitor: LiveTelegramMonitor, messages: List[Dict]):
    """Display live monitoring results"""
    st.subheader("📈 Live Monitoring Results")

    # Statistics
    ticker_counts = {}
    channel_counts = {}

    for message in messages:
        for ticker in message['mentions']:
            ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

        channel_id = message['channel_id']
        channel_counts[channel_id] = channel_counts.get(channel_id, 0) + 1

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Messages", len(messages))

    with col2:
        st.metric("Unique Tickers", len(ticker_counts))

    with col3:
        st.metric("Channels Monitored", len(channel_counts))

    with col4:
        st.metric("Recent Messages", len(messages))

    # Ticker mentions chart
    if ticker_counts:
        st.subheader("📊 Ticker Mentions")

        ticker_df = pd.DataFrame([
            {"Ticker": ticker, "Mentions": count}
            for ticker, count in sorted(ticker_counts.items(),
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
            st.write(f"**Views:** {message.get('views', 0)} | **Forwards:** {message.get('forwards', 0)}")
            st.write(f"**Text:** {message['text'][:500]}...")
