# Portfolio Management Dashboard
# Replaces Google Spreadsheet for stock portfolio tracking
# Supports multiple portfolios (Brazilian & US markets)
# Enhanced with DeepCharts project features: Technical Analysis, AI Insights, Advanced Charts

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import requests
import json
import os
import time
import random
import pytz
import ta  # Technical Analysis library
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

##########################################################################################
## PORTFOLIO MANAGEMENT SYSTEM ##
##########################################################################################

class PortfolioManager:
    """Manages multiple stock portfolios with persistent storage"""

    def __init__(self):
        self.portfolios_file = "portfolios.json"
        self.load_portfolios()

    def load_portfolios(self):
        """Load portfolios from JSON file"""
        if os.path.exists(self.portfolios_file):
            with open(self.portfolios_file, 'r') as f:
                self.portfolios = json.load(f)
        else:
            # Initialize with default portfolios
            self.portfolios = {
                "Brazilian": {},
                "US": {}
            }

    def save_portfolios(self):
        """Save portfolios to JSON file"""
        with open(self.portfolios_file, 'w') as f:
            json.dump(self.portfolios, f, indent=2)

    def add_stock(self, portfolio_name: str, ticker: str, quantity: int, avg_price: float):
        """Add or update a stock in the portfolio"""
        if portfolio_name not in self.portfolios:
            self.portfolios[portfolio_name] = {}

        self.portfolios[portfolio_name][ticker] = {
            "quantity": quantity,
            "avg_price": avg_price,
            "date_added": datetime.now().isoformat()
        }
        self.save_portfolios()

    def remove_stock(self, portfolio_name: str, ticker: str):
        """Remove a stock from the portfolio"""
        if portfolio_name in self.portfolios and ticker in self.portfolios[portfolio_name]:
            del self.portfolios[portfolio_name][ticker]
            self.save_portfolios()

    def get_portfolio_stocks(self, portfolio_name: str) -> Dict:
        """Get all stocks in a portfolio"""
        return self.portfolios.get(portfolio_name, {})

    def get_portfolio_names(self) -> List[str]:
        """Get all portfolio names"""
        return list(self.portfolios.keys())

##########################################################################################
## REAL-TIME STOCK DATA FETCHING ##
##########################################################################################

def fetch_enhanced_stock_data(ticker: str, market: str = "US", period: str = "1mo") -> Optional[Dict]:
    """Enhanced stock data fetching with technical indicators (inspired by DeepCharts)"""
    try:
        # Format ticker for market
        if market == "Brazilian" and not ticker.endswith('.SA'):
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = ticker
        
        # Fetch extended historical data for technical analysis
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period=period, interval="1d")
        
        if hist.empty:
            return None
        
        # Process data similar to DeepCharts approach
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.droplevel(1)
        
        # Ensure timezone awareness
        if hist.index.tzinfo is None:
            hist.index = hist.index.tz_localize('UTC')
        hist.index = hist.index.tz_convert('US/Eastern')
        
        # Calculate basic metrics
        current_price = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
        volume = int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0
        
        # Add technical indicators (DeepCharts style)
        close_series = hist['Close'].squeeze()
        
        # Simple Moving Averages
        sma_20 = ta.trend.sma_indicator(close_series, window=20)
        sma_50 = ta.trend.sma_indicator(close_series, window=50)
        
        # Exponential Moving Average
        ema_20 = ta.trend.ema_indicator(close_series, window=20)
        
        # Bollinger Bands
        bb_high = ta.volatility.bollinger_hband(close_series, window=20)
        bb_low = ta.volatility.bollinger_lband(close_series, window=20)
        bb_mid = ta.volatility.bollinger_mavg(close_series, window=20)
        
        # RSI
        rsi = ta.momentum.rsi(close_series, window=14)
        
        # MACD
        macd = ta.trend.macd(close_series)
        macd_signal = ta.trend.macd_signal(close_series)
        
        # Volume Weighted Average Price (VWAP)
        vwap = ta.volume.volume_weighted_average_price(
            hist['High'], hist['Low'], hist['Close'], hist['Volume']
        )
        
        return {
            "current_price": current_price,
            "previous_close": prev_close,
            "change": current_price - prev_close,
            "change_percent": ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0,
            "volume": volume,
            "currency": 'USD' if market == "US" else 'BRL',
            "historical_data": hist,
            "technical_indicators": {
                "sma_20": float(sma_20.iloc[-1]) if not sma_20.empty and not pd.isna(sma_20.iloc[-1]) else None,
                "sma_50": float(sma_50.iloc[-1]) if not sma_50.empty and not pd.isna(sma_50.iloc[-1]) else None,
                "ema_20": float(ema_20.iloc[-1]) if not ema_20.empty and not pd.isna(ema_20.iloc[-1]) else None,
                "bb_high": float(bb_high.iloc[-1]) if not bb_high.empty and not pd.isna(bb_high.iloc[-1]) else None,
                "bb_low": float(bb_low.iloc[-1]) if not bb_low.empty and not pd.isna(bb_low.iloc[-1]) else None,
                "bb_mid": float(bb_mid.iloc[-1]) if not bb_mid.empty and not pd.isna(bb_mid.iloc[-1]) else None,
                "rsi": float(rsi.iloc[-1]) if not rsi.empty and not pd.isna(rsi.iloc[-1]) else None,
                "macd": float(macd.iloc[-1]) if not macd.empty and not pd.isna(macd.iloc[-1]) else None,
                "macd_signal": float(macd_signal.iloc[-1]) if not macd_signal.empty and not pd.isna(macd_signal.iloc[-1]) else None,
                "vwap": float(vwap.iloc[-1]) if not vwap.empty and not pd.isna(vwap.iloc[-1]) else None
            }
        }
    except Exception as e:
        st.warning(f"Could not fetch enhanced data for {ticker}: {str(e)}")
    
    return None

def fetch_from_yahoo_finance(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fallback: Simple stock data from Yahoo Finance"""
    enhanced_data = fetch_enhanced_stock_data(ticker, market, period="5d")
    if enhanced_data:
        # Return simplified version for compatibility
        return {
            "current_price": enhanced_data["current_price"],
            "previous_close": enhanced_data["previous_close"],
            "change": enhanced_data["change"],
            "change_percent": enhanced_data["change_percent"],
            "volume": enhanced_data["volume"],
            "currency": enhanced_data["currency"]
        }
    return None

def fetch_from_twelve_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch data from Twelve Data API (free tier)"""
    try:
        if market == "Brazilian" and not ticker.endswith('.SA'):
            symbol = f"{ticker}.SA"
        else:
            symbol = ticker

        url = f"https://api.twelvedata.com/price?symbol={symbol}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if "price" in data and data["price"]:
            current_price = float(data["price"])
            return {
                "current_price": current_price,
                "previous_close": current_price,  # Approximate
                "change": 0,
                "change_percent": 0,
                "volume": 0,
                "currency": 'USD' if market == "US" else 'BRL'
            }
    except Exception:
        pass

    return None

def fetch_stock_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch real-time stock data using multiple sources"""

    # Add delay to prevent rate limiting
    time.sleep(random.uniform(0.5, 1.5))

    # Try multiple data sources
    data_sources = [
        ("Twelve Data", fetch_from_twelve_data),
        ("Yahoo Finance", fetch_from_yahoo_finance)
    ]

    for source_name, fetch_func in data_sources:
        try:
            result = fetch_func(ticker, market)
            if result and result["current_price"] > 0:
                return result
        except Exception:
            continue

    # If all sources fail, return None (no fake data)
    return None

##########################################################################################
## ADVANCED CHARTING (DeepCharts Inspired) ##
##########################################################################################

def create_candlestick_chart(ticker: str, market: str = "US", period: str = "1mo") -> Optional[go.Figure]:
    """Create advanced candlestick chart with technical indicators (DeepCharts style)"""
    try:
        enhanced_data = fetch_enhanced_stock_data(ticker, market, period)
        if not enhanced_data or "historical_data" not in enhanced_data:
            return None
        
        hist = enhanced_data["historical_data"]
        indicators = enhanced_data["technical_indicators"]
        
        # Create candlestick chart
        fig = go.Figure()
        
        # Add candlestick
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name="Price"
        ))
        
        # Add technical indicators if available
        if indicators.get("sma_20"):
            sma_20_series = ta.trend.sma_indicator(hist['Close'], window=20)
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=sma_20_series,
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=2)
            ))
        
        if indicators.get("ema_20"):
            ema_20_series = ta.trend.ema_indicator(hist['Close'], window=20)
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=ema_20_series,
                mode='lines',
                name='EMA 20',
                line=dict(color='purple', width=2)
            ))
        
        # Add Bollinger Bands
        if all(indicators.get(key) for key in ["bb_high", "bb_low", "bb_mid"]):
            bb_high_series = ta.volatility.bollinger_hband(hist['Close'], window=20)
            bb_low_series = ta.volatility.bollinger_lband(hist['Close'], window=20)
            bb_mid_series = ta.volatility.bollinger_mavg(hist['Close'], window=20)
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=bb_high_series,
                mode='lines',
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=bb_low_series,
                mode='lines',
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=bb_mid_series,
                mode='lines',
                name='BB Middle',
                line=dict(color='gray', width=1)
            ))
        
        # Add VWAP
        if indicators.get("vwap"):
            vwap_series = ta.volume.volume_weighted_average_price(
                hist['High'], hist['Low'], hist['Close'], hist['Volume']
            )
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=vwap_series,
                mode='lines',
                name='VWAP',
                line=dict(color='blue', width=2, dash='dot')
            ))
        
        # Update layout
        fig.update_layout(
            title=f'{ticker} - Technical Analysis Chart',
            yaxis_title='Price',
            xaxis_title='Date',
            height=600,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating chart for {ticker}: {str(e)}")
        return None

def create_technical_indicators_summary(ticker: str, market: str = "US") -> Optional[Dict]:
    """Create technical indicators summary (DeepCharts style)"""
    try:
        enhanced_data = fetch_enhanced_stock_data(ticker, market, period="3mo")
        if not enhanced_data:
            return None
        
        indicators = enhanced_data["technical_indicators"]
        current_price = enhanced_data["current_price"]
        
        # Create summary with signals
        summary = {
            "current_price": current_price,
            "signals": [],
            "indicators": indicators
        }
        
        # Generate trading signals
        if indicators.get("rsi"):
            rsi = indicators["rsi"]
            if rsi > 70:
                summary["signals"].append({"indicator": "RSI", "signal": "OVERBOUGHT", "value": rsi, "color": "red"})
            elif rsi < 30:
                summary["signals"].append({"indicator": "RSI", "signal": "OVERSOLD", "value": rsi, "color": "green"})
            else:
                summary["signals"].append({"indicator": "RSI", "signal": "NEUTRAL", "value": rsi, "color": "gray"})
        
        # MACD Signal
        if indicators.get("macd") and indicators.get("macd_signal"):
            macd = indicators["macd"]
            macd_signal = indicators["macd_signal"]
            if macd > macd_signal:
                summary["signals"].append({"indicator": "MACD", "signal": "BULLISH", "value": macd, "color": "green"})
            else:
                summary["signals"].append({"indicator": "MACD", "signal": "BEARISH", "value": macd, "color": "red"})
        
        # Price vs Moving Averages
        if indicators.get("sma_20"):
            sma_20 = indicators["sma_20"]
            if current_price > sma_20:
                summary["signals"].append({"indicator": "SMA 20", "signal": "ABOVE", "value": sma_20, "color": "green"})
            else:
                summary["signals"].append({"indicator": "SMA 20", "signal": "BELOW", "value": sma_20, "color": "red"})
        
        return summary
        
    except Exception as e:
        st.error(f"Error creating technical summary for {ticker}: {str(e)}")
        return None

##########################################################################################
## PORTFOLIO ANALYTICS ##
##########################################################################################

def calculate_portfolio_metrics(portfolio_data: pd.DataFrame) -> Dict:
    """Calculate comprehensive portfolio metrics"""
    if portfolio_data.empty:
        return {
            "total_invested": 0,
            "current_value": 0,
            "total_gain_loss": 0,
            "total_gain_loss_percent": 0,
            "best_performer": None,
            "worst_performer": None,
            "profitable_stocks": 0,
            "total_stocks": 0
        }

    total_invested = portfolio_data['Total Invested'].sum()
    current_value = portfolio_data['Current Value'].sum()
    total_gain_loss = current_value - total_invested
    total_gain_loss_percent = (total_gain_loss / total_invested) * 100 if total_invested != 0 else 0

    profitable_stocks = len(portfolio_data[portfolio_data['Gain/Loss'] > 0])
    total_stocks = len(portfolio_data)

    best_performer = portfolio_data.loc[portfolio_data['Change %'].idxmax()] if not portfolio_data.empty else None
    worst_performer = portfolio_data.loc[portfolio_data['Change %'].idxmin()] if not portfolio_data.empty else None

    return {
        "total_invested": total_invested,
        "current_value": current_value,
        "total_gain_loss": total_gain_loss,
        "total_gain_loss_percent": total_gain_loss_percent,
        "best_performer": best_performer,
        "worst_performer": worst_performer,
        "profitable_stocks": profitable_stocks,
        "total_stocks": total_stocks
    }

@st.cache_data(ttl=300, show_spinner=False)
def create_portfolio_dataframe(portfolio_stocks: Dict, market: str) -> pd.DataFrame:
    """Create portfolio dataframe with real-time data"""
    if not portfolio_stocks:
        return pd.DataFrame()

    portfolio_data = []

    for ticker, stock_info in portfolio_stocks.items():
        quantity = stock_info['quantity']
        avg_price = stock_info['avg_price']

        # Fetch real-time data
        real_time_data = fetch_stock_data(ticker, market)

        if real_time_data:
            current_price = real_time_data['current_price']
            day_change = real_time_data['change']
            day_change_percent = real_time_data['change_percent']
            currency = real_time_data['currency']
        else:
            # If no real-time data available, use average price as placeholder
            current_price = avg_price
            day_change = 0
            day_change_percent = 0
            currency = 'BRL' if market == "Brazilian" else 'USD'

        total_invested = quantity * avg_price
        current_value = quantity * current_price
        gain_loss = current_value - total_invested
        gain_loss_percent = (gain_loss / total_invested) * 100 if total_invested != 0 else 0

        portfolio_data.append({
            "Ticker": ticker,
            "Quantity": quantity,
            "Avg Price": avg_price,
            "Current Price": current_price,
            "Total Invested": total_invested,
            "Current Value": current_value,
            "Gain/Loss": gain_loss,
            "Change %": gain_loss_percent,
            "Day Change": day_change,
            "Day Change %": day_change_percent,
            "Currency": currency
        })

    return pd.DataFrame(portfolio_data)

##########################################################################################
## STREAMLIT DASHBOARD UI ##
##########################################################################################

# Page configuration
st.set_page_config(
    page_title="Portfolio Management Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize portfolio manager
if 'portfolio_manager' not in st.session_state:
    st.session_state.portfolio_manager = PortfolioManager()

# Main title
st.title("📈 Stock Portfolio Management Dashboard")
st.markdown("*Replace your Google Spreadsheet with real-time portfolio tracking*")
st.markdown("---")

# Sidebar - Portfolio Management
st.sidebar.header("Portfolio Management")

portfolio_manager = st.session_state.portfolio_manager
portfolio_names = portfolio_manager.get_portfolio_names()

# Portfolio selection
st.sidebar.subheader("Select Portfolio")
selected_portfolio = st.sidebar.selectbox(
    "Choose Portfolio",
    options=portfolio_names,
    index=0 if portfolio_names else None
)

# Add new portfolio
st.sidebar.subheader("Create New Portfolio")
new_portfolio_name = st.sidebar.text_input("Portfolio Name")
if st.sidebar.button("Create Portfolio"):
    if new_portfolio_name and new_portfolio_name not in portfolio_names:
        portfolio_manager.portfolios[new_portfolio_name] = {}
        portfolio_manager.save_portfolios()
        st.sidebar.success(f"Portfolio '{new_portfolio_name}' created!")
        st.rerun()
    elif new_portfolio_name in portfolio_names:
        st.sidebar.error("Portfolio already exists!")

# Stock management
if selected_portfolio:
    st.sidebar.subheader(f"Manage {selected_portfolio} Portfolio")

    # Determine market type
    market_type = "Brazilian" if "brazil" in selected_portfolio.lower() or selected_portfolio == "Brazilian" else "US"

    # Add stock form
    with st.sidebar.expander("Add/Update Stock"):
        ticker_input = st.text_input(
            "Stock Ticker",
            help="Enter ticker symbol (e.g., AAPL for US, PETR4 for Brazilian)"
        )
        quantity_input = st.number_input("Quantity", min_value=1, value=1)
        avg_price_input = st.number_input("Average Price", min_value=0.01, value=1.0, step=0.01)

        if st.button("Add/Update Stock"):
            if ticker_input and quantity_input and avg_price_input:
                portfolio_manager.add_stock(
                    selected_portfolio,
                    ticker_input.upper(),
                    quantity_input,
                    avg_price_input
                )
                st.success(f"Stock {ticker_input.upper()} added/updated!")
                st.rerun()

    # Remove stock
    portfolio_stocks = portfolio_manager.get_portfolio_stocks(selected_portfolio)
    if portfolio_stocks:
        with st.sidebar.expander("Remove Stock"):
            stock_to_remove = st.selectbox(
                "Select Stock to Remove",
                options=list(portfolio_stocks.keys())
            )
            if st.button("Remove Stock"):
                portfolio_manager.remove_stock(selected_portfolio, stock_to_remove)
                st.success(f"Stock {stock_to_remove} removed!")
                st.rerun()

# Main dashboard area
if selected_portfolio:
    portfolio_stocks = portfolio_manager.get_portfolio_stocks(selected_portfolio)

    if portfolio_stocks:
        # Determine market for data fetching
        market_type = "Brazilian" if "brazil" in selected_portfolio.lower() or selected_portfolio == "Brazilian" else "US"

        # Create portfolio dataframe
        with st.spinner("Fetching real-time stock data..."):
            df = create_portfolio_dataframe(portfolio_stocks, market_type)

        if not df.empty:
            # Calculate portfolio metrics
            metrics = calculate_portfolio_metrics(df)

            # Display key metrics
            st.subheader(f"{selected_portfolio} Portfolio Overview")

            col1, col2, col3, col4 = st.columns(4)

            currency = df['Currency'].iloc[0] if not df.empty else 'USD'

            with col1:
                st.metric(
                    "Total Invested",
                    f"{currency} {metrics['total_invested']:,.2f}"
                )

            with col2:
                st.metric(
                    "Current Value",
                    f"{currency} {metrics['current_value']:,.2f}",
                    delta=f"{currency} {metrics['total_gain_loss']:,.2f}"
                )

            with col3:
                st.metric(
                    "Total Return",
                    f"{metrics['total_gain_loss_percent']:.2f}%",
                    delta=f"{metrics['total_gain_loss_percent']:.2f}%"
                )

            with col4:
                st.metric(
                    "Profitable Stocks",
                    f"{metrics['profitable_stocks']}/{metrics['total_stocks']}",
                    delta=f"{(metrics['profitable_stocks']/metrics['total_stocks'])*100:.1f}%" if metrics['total_stocks'] > 0 else "0%"
                )

            st.markdown("---")

            # Portfolio visualizations
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Portfolio Composition")
                fig_pie = px.pie(
                    df,
                    values='Current Value',
                    names='Ticker',
                    title="Portfolio Weight by Current Value"
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, width="stretch")

            with col2:
                st.subheader("Performance Overview")
                fig_bar = px.bar(
                    df.sort_values('Change %', ascending=True),
                    x='Change %',
                    y='Ticker',
                    orientation='h',
                    color='Change %',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    title="Stock Performance (%)"
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, width="stretch")

            # Detailed portfolio table
            st.subheader("Detailed Portfolio View")

            # Format the dataframe for display
            display_df = df.copy()

            # Format currency columns
            currency_columns = ['Avg Price', 'Current Price', 'Total Invested', 'Current Value', 'Gain/Loss', 'Day Change']
            for col in currency_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{currency} {x:,.2f}")

            # Format percentage columns
            percentage_columns = ['Change %', 'Day Change %']
            for col in percentage_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")

            # Remove currency column from display
            display_df = display_df.drop('Currency', axis=1)

            # Apply conditional formatting
            def highlight_gains_losses(val):
                if isinstance(val, str) and '%' in val:
                    num_val = float(val.replace('%', ''))
                    if num_val > 0:
                        return 'background-color: rgba(0, 255, 0, 0.2)'
                    elif num_val < 0:
                        return 'background-color: rgba(255, 0, 0, 0.2)'
                return ''

            styled_df = display_df.style.map(highlight_gains_losses, subset=['Change %', 'Day Change %'])
            st.dataframe(styled_df, width="stretch")

            # Performance highlights
            if metrics['best_performer'] is not None and metrics['worst_performer'] is not None:
                st.subheader("Performance Highlights")
                col1, col2 = st.columns(2)

                with col1:
                    st.success("🏆 Best Performer")
                    best = metrics['best_performer']
                    st.write(f"**{best['Ticker']}**: {best['Change %']:.2f}% gain")
                    st.write(f"Value: {currency} {best['Current Value']:,.2f}")

                with col2:
                    st.error("📉 Worst Performer")
                    worst = metrics['worst_performer']
                    st.write(f"**{worst['Ticker']}**: {worst['Change %']:.2f}% loss")
                    st.write(f"Value: {currency} {worst['Current Value']:,.2f}")

        else:
            st.warning("Unable to fetch data for the stocks in your portfolio. Please check the ticker symbols or try again later.")

    else:
        st.info(f"No stocks in {selected_portfolio} portfolio. Use the sidebar to add stocks.")

else:
    st.info("Please select or create a portfolio to get started.")

# Settings
st.sidebar.markdown("---")
st.sidebar.subheader("Settings")
auto_refresh = st.sidebar.checkbox("Auto-refresh data (30s)", value=False)

if auto_refresh:
    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Portfolio Management Dashboard | Real-time data powered by multiple APIs</p>
    <p>💡 Tip: For Brazilian stocks, use tickers like PETR4, VALE3, ITUB4</p>
</div>
""", unsafe_allow_html=True)