"""
Data Fetching Module
Handles all stock data fetching from various APIs
"""

import yfinance as yf
import requests
import os
import time
import random
import sys
import streamlit as st
import pandas as pd
from io import StringIO
from contextlib import redirect_stderr
from datetime import datetime, timedelta

# Simple in-memory cache
_cache = {}
_cache_timestamps = {}
CACHE_TTL = 1800  # 30 minutes
from typing import Dict, List, Optional


class SuppressYFinanceOutput:
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self._original_stderr
from bs4 import BeautifulSoup

from app.config import (
    API_KEYS,
    BRAZILIAN_SECTORS,
    US_SECTORS,
    RATE_LIMITS
)


class SuppressYFinanceOutput:
    """Context manager to suppress yfinance stderr output"""
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self._original_stderr


def get_sector_info(ticker: str, market: str, info: Dict) -> str:
    """Get sector information for a stock, with Brazilian and US stock mapping"""
    # First try to get from Yahoo Finance info
    sector = info.get("sector", "")
    if sector and sector != "Unknown":
        return sector

    # Try to get sector from API data first, then fallback to basic categorization
    if market == "Brazilian":
        ticker_clean = ticker.replace(".SA", "").upper()

        # Special handling for FIIs (Fundos Imobiliários) - these are always Real Estate
        if ticker_clean.endswith("11") and len(ticker_clean) >= 5:
            return "Real Estate FII"

        # Use static mapping as fallback
        return BRAZILIAN_SECTORS.get(ticker_clean, "Unknown")

    # For US stocks, use static mapping as fallback
    if market == "US":
        ticker_clean = ticker.replace(".SA", "").upper()
        return US_SECTORS.get(ticker_clean, "Unknown")

    return "Unknown"


def get_dividend_yield_from_yfinance(ticker: str, market: str) -> float:
    """Try to get dividend yield directly from yfinance with multiple approaches"""
    try:
        # Format ticker for market
        if market == "Brazilian" and not ticker.endswith(".SA"):
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = ticker

        with SuppressYFinanceOutput():
            stock = yf.Ticker(ticker_symbol)

            # Try different methods to get dividend data
            try:
                # Method 1: Try to get from stock.info
                info = stock.info
                dividend_fields = ["dividendYield", "trailingAnnualDividendYield", "forwardDividendYield"]

                for field in dividend_fields:
                    value = info.get(field, 0)
                    if value and value > 0:
                        result = value * 100 if value < 1 else value
                        # print(f"DEBUG: Live dividend yield for {ticker} from {field}: {result}%")
                        return result

                # Method 2: Try to calculate from dividend history
                try:
                    dividends = stock.dividends
                    if not dividends.empty:
                        # Get the last 4 quarters of dividends
                        recent_dividends = dividends.tail(4)
                        if len(recent_dividends) >= 4:
                            annual_dividend = recent_dividends.sum()
                            current_price = info.get("currentPrice", 0)
                            if current_price and current_price > 0:
                                dividend_yield = (annual_dividend / current_price) * 100
                                # print(f"DEBUG: Calculated dividend yield for {ticker}: {dividend_yield:.2f}%")
                                return dividend_yield
                except:
                    pass

            except Exception as e:
                print(f"Error getting dividend data from yfinance for {ticker}: {e}")
                return 0.0

    except Exception as e:
        print(f"Error accessing yfinance for {ticker}: {e}")
        return 0.0

    return 0.0


def get_dividend_yield(ticker: str, market: str, info: Dict) -> float:
    """Get dividend yield for a stock - prioritize live data over static data"""
    ticker_clean = ticker.replace(".SA", "").upper()

    # First, try to get live dividend data from API response
    dividend_fields = [
        "dividendYield",
        "trailingAnnualDividendYield",
        "forwardDividendYield",
        "dividendRate",
        "yield",
        "dividend_yield",
        "yieldPercent",
        "dividend_yield_percent",
        "dividend_yield_percentage",
        "yield_percent",
        "yield_percentage",
        "dividend_yield_annual",
        "annual_dividend_yield",
        "dividend_yield_rate",
        "yield_rate",
        "dividend_percent",
        "dividend_percentage",
        "dividend_yield_pct",
        "yield_pct",
        "dividend_yield_ratio",
        "yield_ratio"
    ]

    for field in dividend_fields:
        value = info.get(field, 0)
        if value and value > 0:
            # Convert to percentage if it's a decimal (0.05 -> 5.0)
            return value * 100 if value < 1 else value

    # If no live data found, try yfinance direct approach
    if market == "Brazilian" or market == "US":
        yfinance_yield = get_dividend_yield_from_yfinance(ticker, market)
        if yfinance_yield > 0:
            return yfinance_yield

    # No static fallback - we want live data only
    return 0.0


def get_annual_dividend(ticker: str, market: str, info: Dict, current_price: float = 0, quantity: int = 0) -> float:
    """Calculate annual dividend income for a position"""
    dividend_yield = get_dividend_yield(ticker, market, info)
    if current_price > 0 and quantity > 0:
        return (dividend_yield / 100) * current_price * quantity
    return 0.0


def fetch_enhanced_stock_data(
    ticker: str, market: str = "US", period: str = "1mo"
) -> Optional[Dict]:
    """Enhanced stock data fetching with technical indicators"""
    try:
        # Format ticker for market
        if market == "Brazilian" and not ticker.endswith(".SA"):
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = ticker

        # Fetch extended historical data for technical analysis
        with SuppressYFinanceOutput():
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period=period, interval="1d")

            # Get additional stock info for sector and dividend data
            try:
                info = stock.info
                # print(f"DEBUG: Got live data for {ticker}: sector={info.get('sector', 'N/A')}, dividendYield={info.get('dividendYield', 'N/A')}")
            except Exception as e:
                # print(f"DEBUG: Failed to get live data for {ticker}: {e}")
                info = {}

            if hist.empty:
                return None

            # Calculate technical indicators
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['EMA_20'] = hist['Close'].ewm(span=20).mean()

            # RSI calculation
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))

            # Bollinger Bands
            hist['BB_Middle'] = hist['Close'].rolling(window=20).mean()
            bb_std = hist['Close'].rolling(window=20).std()
            hist['BB_Upper'] = hist['BB_Middle'] + (bb_std * 2)
            hist['BB_Lower'] = hist['BB_Middle'] - (bb_std * 2)

            # MACD
            exp1 = hist['Close'].ewm(span=12).mean()
            exp2 = hist['Close'].ewm(span=26).mean()
            hist['MACD'] = exp1 - exp2
            hist['MACD_Signal'] = hist['MACD'].ewm(span=9).mean()
            hist['MACD_Histogram'] = hist['MACD'] - hist['MACD_Signal']

            # Get current price and basic info
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close > 0 else 0

            # Get sector and dividend info
            sector = get_sector_info(ticker, market, info)
            dividend_yield = get_dividend_yield(ticker, market, info)

            return {
                "ticker": ticker,
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "volume": hist['Volume'].iloc[-1],
                "market_cap": info.get("marketCap", 0),
                "sector": sector,
                "dividend_yield": dividend_yield,
                "historical_data": hist,
                "info": info
            }

    except Exception as e:
        print(f"Error fetching enhanced data for {ticker}: {e}")
        return None


@st.cache_data(
    ttl=1800, show_spinner=False, max_entries=1000
)  # Cache for 30 minutes to optimize free tier usage
def fetch_stock_data_cached(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch real-time stock data with smart fallback strategy"""
    import os

    # Check if we have API keys available
    has_twelve_data = bool(os.getenv("TWELVE_DATA_API_KEY"))
    has_alpha_vantage = bool(os.getenv("ALPHA_VANTAGE_API_KEY"))

    # Smart prioritization based on market and API availability
    data_sources = []

    if market == "Brazilian":
        # For Brazilian stocks: BRAPI (free) -> Alpha Vantage -> Yahoo Finance
        data_sources.append(("BRAPI", lambda: fetch_from_brapi(ticker, market)))
        if has_alpha_vantage:
            data_sources.append(("Alpha Vantage", lambda: fetch_from_alpha_vantage(ticker, market)))
        data_sources.append(("Yahoo Finance", lambda: fetch_from_yahoo_finance(ticker, market)))
    else:
        # For US stocks: Twelve Data -> Alpha Vantage -> Yahoo Finance
        if has_twelve_data:
            data_sources.append(("Twelve Data", lambda: fetch_from_twelve_data(ticker, market)))
        if has_alpha_vantage:
            data_sources.append(("Alpha Vantage", lambda: fetch_from_alpha_vantage(ticker, market)))
        data_sources.append(("Yahoo Finance", lambda: fetch_from_yahoo_finance(ticker, market)))

    # Try sources sequentially to avoid rate limit issues
    for source_name, fetch_func in data_sources:
        try:
            result = fetch_func()
            if result and result.get("current_price", 0) > 0:
                return result
        except Exception as e:
            continue

    # If all sources fail, return None
    return None


def _is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid"""
    if cache_key not in _cache or cache_key not in _cache_timestamps:
        return False

    age = time.time() - _cache_timestamps[cache_key]
    return age < CACHE_TTL

def _get_from_cache(cache_key: str) -> Optional[Dict]:
    """Get data from cache if valid"""
    if _is_cache_valid(cache_key):
        return _cache[cache_key]
    return None

def _set_cache(cache_key: str, data: Dict):
    """Set data in cache"""
    _cache[cache_key] = data
    _cache_timestamps[cache_key] = time.time()

def fetch_stock_data(ticker: str, market: str = "US", force_refresh: bool = False) -> Optional[Dict]:
    """Fetch stock data with smart caching - shows cached data immediately, refreshes in background"""
    cache_key = f"{ticker}_{market}"

    # If force refresh, clear this ticker's cache
    if force_refresh:
        if cache_key in _cache:
            del _cache[cache_key]
        if cache_key in _cache_timestamps:
            del _cache_timestamps[cache_key]

    # Try to get from simple cache first (instant if cached)
    cached_data = _get_from_cache(cache_key)
    if cached_data and not force_refresh:
        return cached_data

    # If no cached data or force refresh, fetch fresh data
    fresh_data = fetch_stock_data_cached(ticker, market)

    # Store in simple cache for instant access next time
    if fresh_data:
        _set_cache(cache_key, fresh_data)

    return fresh_data


@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
def fetch_enhanced_stock_data(
    ticker: str, market: str = "US", period: str = "1mo"
) -> Optional[Dict]:
    """Enhanced stock data fetching with technical indicators (inspired by DeepCharts)"""
    try:
        # Format ticker for market
        if market == "Brazilian" and not ticker.endswith(".SA"):
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = ticker

        # Fetch extended historical data for technical analysis (suppress yfinance errors)
        with SuppressYFinanceOutput():
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period=period, interval="1d")

            # Get additional stock info for sector and dividend data
            info = {}
            try:
                info = stock.info
            except Exception as e:
                # If rate limited or other error, try to get basic info
                try:
                    # Try to get just the basic info without the full details
                    info = {
                        "sector": "Unknown",
                        "dividendYield": None,
                        "trailingAnnualDividendYield": None,
                        "forwardDividendYield": None
                    }
                except:
                    info = {}

        if hist.empty:
            # If no historical data, return None silently (don't log error)
            return None

        # Process data similar to DeepCharts approach
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.droplevel(1)

        # Ensure timezone awareness
        if hist.index.tzinfo is None:
            hist.index = hist.index.tz_localize("UTC")
        hist.index = hist.index.tz_convert("US/Eastern")

        # Calculate basic metrics
        current_price = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price
        volume = int(hist["Volume"].iloc[-1]) if not hist["Volume"].empty else 0

        return {
            "current_price": current_price,
            "previous_close": prev_close,
            "change": current_price - prev_close,
            "change_percent": (
                ((current_price - prev_close) / prev_close) * 100
                if prev_close != 0
                else 0
            ),
            "volume": volume,
            "currency": "USD" if market == "US" else "BRL",
            "sector": info.get("sector", "Unknown"),
            "dividend_yield": get_dividend_yield_from_yfinance(ticker, market, info),
            "annual_dividend": get_annual_dividend(ticker, market, info),
            "info": info,
        }
    except Exception as e:
        print(f"Error fetching enhanced data for {ticker}: {e}")
        return None


@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
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
            "currency": enhanced_data["currency"],
            "sector": enhanced_data.get("sector", "Unknown"),
            "dividend_yield": enhanced_data.get("dividend_yield", 0),
            "annual_dividend": enhanced_data.get("annual_dividend", 0),
        }
    return None


def fetch_from_twelve_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch stock data from Twelve Data API"""
    api_key = API_KEYS.get("TWELVE_DATA_API_KEY")
    if not api_key:
        return None

    try:
        # Format ticker for API
        if market == "Brazilian" and not ticker.endswith(".SA"):
            symbol = f"{ticker}.SA"
        else:
            symbol = ticker

        url = f"https://api.twelvedata.com/quote"
        params = {
            "symbol": symbol,
            "apikey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "close" in data:
            current_price = float(data["close"])
            change = float(data.get("change", 0))
            change_percent = float(data.get("percent_change", 0))

            return {
                "ticker": ticker,
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "volume": int(data.get("volume", 0)),
                "market_cap": float(data.get("market_cap", 0)),
                "sector": get_sector_info(ticker, market, data),
                "dividend_yield": get_dividend_yield(ticker, market, data),
                "info": data
            }
    except Exception as e:
        print(f"Error fetching from Twelve Data for {ticker}: {e}")
        return None


def fetch_from_alpha_vantage(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch stock data from Alpha Vantage API"""
    api_key = API_KEYS.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return None

    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        quote = data.get("Global Quote", {})
        if quote:
            current_price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            change_percent = float(quote.get("10. change percent", "0%").replace("%", ""))

            return {
                "ticker": ticker,
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "volume": int(quote.get("06. volume", 0)),
                "market_cap": 0,  # Alpha Vantage doesn't provide market cap in quote
                "sector": get_sector_info(ticker, market, quote),
                "dividend_yield": get_dividend_yield(ticker, market, quote),
                "info": quote
            }
    except Exception as e:
        print(f"Error fetching from Alpha Vantage for {ticker}: {e}")
        return None


@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
def fetch_from_brapi(ticker: str, market: str = "Brazilian") -> Optional[Dict]:
    """Fetch Brazilian stock data from BRAPI"""
    if market != "Brazilian":
        return None

    try:
        # Get API key from environment
        api_key = os.getenv("BRAPI_API_KEY")

        # Remove .SA suffix for BRAPI
        clean_ticker = ticker.replace(".SA", "")

        # Build URL with API key if available
        if api_key:
            url = f"https://brapi.dev/api/quote/{clean_ticker}?token={api_key}"
        else:
            url = f"https://brapi.dev/api/quote/{clean_ticker}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "results" in data and data["results"]:
            result = data["results"][0]
            current_price = float(result.get("regularMarketPrice", 0))
            change = float(result.get("regularMarketChange", 0))
            change_percent = float(result.get("regularMarketChangePercent", 0))

            return {
                "ticker": ticker,
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "volume": int(result.get("regularMarketVolume", 0)),
                "market_cap": float(result.get("marketCap", 0)) if result.get("marketCap") is not None else 0,
                "currency": "BRL",
                "sector": get_sector_info(ticker, market, result),
                "dividend_yield": get_dividend_yield(ticker, market, result),
                "info": result
            }
    except Exception as e:
        print(f"Error fetching from BRAPI for {ticker}: {e}")
        return None


def fetch_stock_news_alpha_vantage(ticker: str) -> List[Dict]:
    """Fetch news for a stock using Alpha Vantage API"""
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            return []

        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={api_key}&limit=5"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "feed" in data and data["feed"]:
            # Format the news data consistently
            formatted_news = []
            for article in data["feed"]:
                formatted_news.append({
                    "title": article.get("title", "No title"),
                    "description": article.get("summary", "No description"),
                    "url": article.get("url", ""),
                    "source": article.get("source", "Alpha Vantage"),
                    "publishedAt": article.get("time_published", ""),
                    "sentiment": article.get("overall_sentiment_score", 0)
                })
            return formatted_news
        return []
    except Exception as e:
        print(f"Error fetching news from Alpha Vantage for {ticker}: {e}")
        return []


def fetch_stock_news_newsapi(ticker: str) -> List[Dict]:
    """Fetch news for a stock using NewsAPI"""
    try:
        api_key = os.getenv("NEWSAPI_API_KEY")
        if not api_key:
            return []

        # Search for news about the company
        url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}&pageSize=5"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "articles" in data and data["articles"]:
            # Format the news data consistently
            formatted_news = []
            for article in data["articles"]:
                formatted_news.append({
                    "title": article.get("title", "No title"),
                    "description": article.get("description", "No description"),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "NewsAPI"),
                    "publishedAt": article.get("publishedAt", ""),
                    "sentiment": 0  # NewsAPI doesn't provide sentiment
                })
            return formatted_news
        return []
    except Exception as e:
        print(f"Error fetching news from NewsAPI for {ticker}: {e}")
        return []


def fetch_stock_news_web_scraping(ticker: str) -> List[Dict]:
    """Fetch news using web scraping (fallback method)"""
    try:
        # This is a simplified web scraping approach
        # In a real implementation, you'd use proper web scraping libraries
        return []
    except Exception as e:
        print(f"Error fetching news via web scraping for {ticker}: {e}")
        return []


def fetch_stock_news_mock_data(ticker: str) -> List[Dict]:
    """Return mock news data for testing"""
    return [
        {
            "title": f"Latest news about {ticker}",
            "description": f"Recent developments and analysis for {ticker} stock",
            "url": f"https://example.com/news/{ticker}",
            "publishedAt": datetime.now().isoformat(),
            "source": "Mock News"
        }
    ]


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def fetch_portfolio_news(tickers: List[str]) -> List[Dict]:
    """Fetch news for multiple stocks in a portfolio"""
    all_news = []

    for ticker in tickers:
        # Try different news sources
        news_sources = [
            fetch_stock_news_alpha_vantage,
            fetch_stock_news_newsapi,
            fetch_stock_news_web_scraping,
            fetch_stock_news_mock_data
        ]

        for fetch_func in news_sources:
            try:
                news = fetch_func(ticker)
                if news:
                    all_news.extend(news)
                    break  # Use first successful source
            except Exception as e:
                continue

    # Sort by date and return top 10
    all_news.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
    return all_news[:10]
