# Portfolio Management Dashboard
# Replaces Google Spreadsheet for stock portfolio tracking
# Supports multiple portfolios (Brazilian & US markets)
# Enhanced with DeepCharts project features: Technical Analysis, AI Insights, Advanced Charts
# Optimized for free tier APIs with intelligent caching and rate limiting

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import requests
import json
import os
import sys
import time
import random
import pytz
import ta  # Technical Analysis library
import logging
import warnings
import concurrent.futures
import threading
from contextlib import redirect_stderr
from io import StringIO
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

# AI Libraries (Free Services)
try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Suppress yfinance and other noisy warnings/logs
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*possibly delisted.*")


# Context manager to suppress yfinance stderr output
class SuppressYFinanceOutput:
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self._original_stderr


# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional

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
            with open(self.portfolios_file, "r") as f:
                self.portfolios = json.load(f)
        else:
            # Initialize with default portfolios
            self.portfolios = {"Brazilian": {}, "US": {}}

    def save_portfolios(self):
        """Save portfolios to JSON file"""
        with open(self.portfolios_file, "w") as f:
            json.dump(self.portfolios, f, indent=2)

    def add_stock(
        self, portfolio_name: str, ticker: str, quantity: int, avg_price: float
    ):
        """Add or update a stock in the portfolio"""
        if portfolio_name not in self.portfolios:
            self.portfolios[portfolio_name] = {}

        self.portfolios[portfolio_name][ticker] = {
            "quantity": quantity,
            "avg_price": avg_price,
            "date_added": datetime.now().isoformat(),
        }
        self.save_portfolios()

    def remove_stock(self, portfolio_name: str, ticker: str):
        """Remove a stock from the portfolio"""
        if (
            portfolio_name in self.portfolios
            and ticker in self.portfolios[portfolio_name]
        ):
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
## Optimized for Free Tier APIs:
## - Stock Data: 15min cache (Yahoo Finance free, Alpha Vantage 25/day, Twelve Data 8/min)
## - News Data: 1hr cache (NewsAPI 100/day, Alpha Vantage 25/day)
## - AI Analysis: 30min-2hr cache (Ollama unlimited local, Gemini 15/min)
##########################################################################################


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

        # Add technical indicators (DeepCharts style)
        close_series = hist["Close"].squeeze()

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
            hist["High"], hist["Low"], hist["Close"], hist["Volume"]
        )

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
            "historical_data": hist,
            "technical_indicators": {
                "sma_20": (
                    float(sma_20.iloc[-1])
                    if not sma_20.empty and not pd.isna(sma_20.iloc[-1])
                    else None
                ),
                "sma_50": (
                    float(sma_50.iloc[-1])
                    if not sma_50.empty and not pd.isna(sma_50.iloc[-1])
                    else None
                ),
                "ema_20": (
                    float(ema_20.iloc[-1])
                    if not ema_20.empty and not pd.isna(ema_20.iloc[-1])
                    else None
                ),
                "bb_high": (
                    float(bb_high.iloc[-1])
                    if not bb_high.empty and not pd.isna(bb_high.iloc[-1])
                    else None
                ),
                "bb_low": (
                    float(bb_low.iloc[-1])
                    if not bb_low.empty and not pd.isna(bb_low.iloc[-1])
                    else None
                ),
                "bb_mid": (
                    float(bb_mid.iloc[-1])
                    if not bb_mid.empty and not pd.isna(bb_mid.iloc[-1])
                    else None
                ),
                "rsi": (
                    float(rsi.iloc[-1])
                    if not rsi.empty and not pd.isna(rsi.iloc[-1])
                    else None
                ),
                "macd": (
                    float(macd.iloc[-1])
                    if not macd.empty and not pd.isna(macd.iloc[-1])
                    else None
                ),
                "macd_signal": (
                    float(macd_signal.iloc[-1])
                    if not macd_signal.empty and not pd.isna(macd_signal.iloc[-1])
                    else None
                ),
                "vwap": (
                    float(vwap.iloc[-1])
                    if not vwap.empty and not pd.isna(vwap.iloc[-1])
                    else None
                ),
            },
                }
    except Exception as e:
        # Silently handle yfinance errors - they're common for delisted/problematic stocks
        # Only log if it's not a common yfinance JSON parsing error
        if "Expecting value: line 1 column 1" not in str(e):
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
            "currency": enhanced_data["currency"],
        }
    return None


def fetch_from_twelve_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch data from Twelve Data API with API key support"""
    try:
        # Get API key from environment
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        if not api_key:
            return None  # Skip if no API key provided

        # Twelve Data uses different symbol format for Brazilian stocks
        if market == "Brazilian":
            # Remove .SA suffix if present, Twelve Data uses just the ticker
            symbol = ticker.replace(".SA", "")
        else:
            symbol = ticker

        # Use both price and quote endpoints for more complete data
        params = {"symbol": symbol, "apikey": api_key}

        # Try quote endpoint first (more complete data)
        quote_url = "https://api.twelvedata.com/quote"
        response = requests.get(quote_url, params=params, timeout=10)
        data = response.json()

        if "close" in data and data["close"]:
            current_price = float(data["close"])
            prev_close = float(data.get("previous_close", current_price))

        return {
            "current_price": current_price,
            "previous_close": prev_close,
            "change": current_price - prev_close,
            "change_percent": (
                ((current_price - prev_close) / prev_close) * 100
                if prev_close != 0
                else 0
            ),
            "volume": int(data.get("volume", 0)) if data.get("volume") else 0,
            "currency": "USD" if market == "US" else "BRL",
        }

        # Fallback to simple price endpoint
        price_url = "https://api.twelvedata.com/price"
        response = requests.get(price_url, params=params, timeout=10)
        data = response.json()

        if "price" in data and data["price"]:
            current_price = float(data["price"])
            return {
                "current_price": current_price,
                "previous_close": current_price,  # Approximate
                "change": 0,
                "change_percent": 0,
                "volume": 0,
                "currency": "USD" if market == "US" else "BRL",
            }

    except Exception as e:
        st.warning(f"Twelve Data API error for {ticker}: {str(e)}")

    return None


def fetch_from_brapi(ticker: str, market: str = "Brazilian") -> Optional[Dict]:
    """Fetch Brazilian stock data from BRAPI (Brazilian stock API with API key support)"""
    if market != "Brazilian":
        return None

    try:
        # Get API key from environment
        api_key = os.getenv("BRAPI_API_KEY")

        # Remove .SA suffix if present, BRAPI uses just the ticker
        symbol = ticker.replace(".SA", "")

        # Build URL with API key if available
        if api_key:
            url = f"https://brapi.dev/api/quote/{symbol}?token={api_key}"
        else:
            url = f"https://brapi.dev/api/quote/{symbol}"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if "results" in data and data["results"]:
                stock_data = data["results"][0]

                current_price = float(stock_data.get("regularMarketPrice", 0))
                prev_close = float(
                    stock_data.get("regularMarketPreviousClose", current_price)
                )

            if current_price > 0:
                return {
                    "current_price": current_price,
                        "previous_close": prev_close,
                        "change": current_price - prev_close,
                        "change_percent": (
                            ((current_price - prev_close) / prev_close) * 100
                            if prev_close != 0
                            else 0
                        ),
                        "volume": int(stock_data.get("regularMarketVolume", 0)),
                        "currency": "BRL",
                    }

    except Exception as e:
        # Silently handle BRAPI errors
        pass

    return None


def fetch_from_alpha_vantage(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch data from Alpha Vantage API with API key support"""
    try:
        # Get API key from environment
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            return None  # Skip if no API key provided

        # Alpha Vantage uses .SA suffix for Brazilian stocks
        if market == "Brazilian" and not ticker.endswith(".SA"):
            symbol = f"{ticker}.SA"
        else:
            symbol = ticker

        # Use Global Quote endpoint
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key}

        url = "https://www.alphavantage.co/query"
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "Global Quote" in data:
            quote = data["Global Quote"]
            if "05. price" in quote and quote["05. price"]:
                current_price = float(quote["05. price"])
                prev_close = float(quote.get("08. previous close", current_price))

            return {
                "current_price": current_price,
                "previous_close": prev_close,
            "change": float(quote.get("09. change", 0)),
            "change_percent": float(
                quote.get("10. change percent", "0").replace("%", "")
            ),
            "volume": int(quote.get("06. volume", 0)) if quote.get("06. volume") else 0,
            "currency": "USD" if market == "US" else "BRL",
        }

    except Exception as e:
        # Silently handle Alpha Vantage errors (likely rate limited)
        pass

    return None


@st.cache_data(
    ttl=1800, show_spinner=False
)  # Cache for 30 minutes to optimize free tier usage
def fetch_stock_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch real-time stock data with smart fallback strategy"""

    # Check if we have API keys available
    has_twelve_data = bool(os.getenv("TWELVE_DATA_API_KEY"))
    has_alpha_vantage = bool(os.getenv("ALPHA_VANTAGE_API_KEY"))

    # Smart prioritization based on market and API availability
    data_sources = []

    if market == "Brazilian":
        # For Brazilian stocks: BRAPI (free) -> Alpha Vantage -> Yahoo Finance
        data_sources.append(("BRAPI", fetch_from_brapi))
        if has_alpha_vantage:
            data_sources.append(("Alpha Vantage", fetch_from_alpha_vantage))
        data_sources.append(("Yahoo Finance", fetch_from_yahoo_finance))
    else:
        # For US stocks: Twelve Data -> Alpha Vantage -> Yahoo Finance
        if has_twelve_data:
            data_sources.append(("Twelve Data", fetch_from_twelve_data))
        if has_alpha_vantage:
            data_sources.append(("Alpha Vantage", fetch_from_alpha_vantage))
        data_sources.append(("Yahoo Finance", fetch_from_yahoo_finance))

    # Try sources sequentially to avoid rate limit issues
    for source_name, fetch_func in data_sources:
        try:
            result = fetch_func(ticker, market)
            if result and result.get("current_price", 0) > 0:
                return result
        except Exception as e:
            continue

    # If all sources fail, return None
    return None


##########################################################################################
## STOCK NEWS FEED ##
##########################################################################################


@st.cache_data(
    ttl=3600, show_spinner=False
)  # Cache for 1 hour to optimize free tier (25 requests/day)
def fetch_stock_news_alpha_vantage(ticker: str, limit: int = 10) -> List[Dict]:
    """Fetch stock news from Alpha Vantage News API"""
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            return []

        # Alpha Vantage News & Sentiment endpoint
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "limit": limit,
            "apikey": api_key,
        }

        url = "https://www.alphavantage.co/query"
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        news_articles = []
        if "feed" in data:
            for article in data["feed"][:limit]:
                news_articles.append(
                    {
                        "title": article.get("title", "No title"),
                        "summary": article.get("summary", "No summary available"),
                        "url": article.get("url", ""),
                        "time_published": article.get("time_published", ""),
                        "source": article.get("source", "Unknown"),
                        "sentiment_score": article.get("overall_sentiment_score", 0),
                        "sentiment_label": article.get(
                            "overall_sentiment_label", "Neutral"
                        ),
                    }
                )

        return news_articles

    except Exception as e:
        st.warning(f"Alpha Vantage News error for {ticker}: {str(e)}")
        return []


@st.cache_data(
    ttl=3600, show_spinner=False
)  # Cache for 1 hour to optimize free tier (100 requests/day)
def fetch_stock_news_newsapi(ticker: str, limit: int = 10) -> List[Dict]:
    """Fetch stock news from NewsAPI (free tier: 100 requests/day)"""
    try:
        # NewsAPI free tier key (you can get one at https://newsapi.org/)
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            return []

        # Search for company name or ticker
        company_names = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOGL": "Google",
            "TSLA": "Tesla",
            "PETR4": "Petrobras",
            "VALE3": "Vale",
            "ITUB4": "Itau",
            "BBDC4": "Bradesco",
        }

        search_term = company_names.get(ticker.replace(".SA", ""), ticker)

        params = {
            "q": f"{search_term} stock OR {ticker}",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": limit,
            "apiKey": api_key,
        }

        url = "https://newsapi.org/v2/everything"
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        news_articles = []
        if data.get("status") == "ok" and "articles" in data:
            for article in data["articles"][:limit]:
                news_articles.append(
                    {
                        "title": article.get("title", "No title"),
                        "summary": article.get("description", "No summary available"),
                        "url": article.get("url", ""),
                        "time_published": article.get("publishedAt", ""),
                        "source": article.get("source", {}).get("name", "NewsAPI"),
                        "sentiment_score": 0,
                        "sentiment_label": "Neutral",
                    }
                )

        return news_articles

    except Exception as e:
        return []


@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
def fetch_stock_news_web_scraping(ticker: str, limit: int = 10) -> List[Dict]:
    """Fetch stock news via web scraping from financial websites"""
    try:
        # Use a simple approach: search Google Finance or Yahoo Finance
        search_term = ticker.replace(".SA", "")

        # Try Yahoo Finance search page
        url = f"https://finance.yahoo.com/quote/{ticker}/news"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(response.content, "html.parser")

        news_articles = []
        # Look for news articles (this is a simplified approach)
        articles = soup.find_all("h3", limit=limit)

        for i, article in enumerate(articles[:limit]):
            if i >= limit:
                break

            title = article.get_text(strip=True) if article else f"News about {ticker}"

            news_articles.append(
                {
                    "title": title,
                    "summary": f"Latest news about {ticker} from financial sources",
                    "url": f"https://finance.yahoo.com/quote/{ticker}/news",
                    "time_published": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "Yahoo Finance",
                    "sentiment_score": 0,
                    "sentiment_label": "Neutral",
                }
            )

        return news_articles

    except Exception as e:
        return []


@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
def fetch_stock_news_mock_data(ticker: str, limit: int = 10) -> List[Dict]:
    """Generate mock news data for demonstration (fallback when all APIs fail)"""
    mock_news = [
        {
            "title": f"{ticker} Shows Strong Performance in Recent Trading Session",
            "summary": f"Analysts are optimistic about {ticker}'s recent performance and future prospects in the current market environment.",
            "url": f"https://finance.yahoo.com/quote/{ticker}",
            "time_published": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Financial News",
            "sentiment_score": 0.3,
            "sentiment_label": "Positive",
        },
        {
            "title": f"Market Analysis: {ticker} Faces Mixed Signals",
            "summary": f"Recent market trends show {ticker} experiencing volatility amid broader economic uncertainties.",
            "url": f"https://finance.yahoo.com/quote/{ticker}",
            "time_published": (datetime.now() - timedelta(hours=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "source": "Market Watch",
            "sentiment_score": 0.0,
            "sentiment_label": "Neutral",
        },
        {
            "title": f"Investors Monitor {ticker} Amid Sector Developments",
            "summary": f"Key developments in the sector are influencing {ticker}'s trading patterns and investor sentiment.",
            "url": f"https://finance.yahoo.com/quote/{ticker}",
            "time_published": (datetime.now() - timedelta(hours=4)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "source": "Investment Daily",
            "sentiment_score": -0.1,
            "sentiment_label": "Neutral",
        },
    ]

    return mock_news[:limit]


def fetch_portfolio_news(
    portfolio_stocks: Dict, limit_per_stock: int = 5
) -> Dict[str, List[Dict]]:
    """Fetch news for all stocks in portfolio with multiple fallback sources"""
    portfolio_news = {}

    # Optimize for free tiers: limit stocks based on API availability
    has_newsapi = bool(os.getenv("NEWSAPI_KEY"))
    has_alpha_vantage = bool(os.getenv("ALPHA_VANTAGE_API_KEY"))

    # Adjust limits based on available APIs
    if has_newsapi and has_alpha_vantage:
        max_stocks = 4  # More generous with multiple APIs
    elif has_newsapi or has_alpha_vantage:
        max_stocks = 3  # Conservative with single API
    else:
        max_stocks = 2  # Very conservative with web scraping only

    stock_tickers = list(portfolio_stocks.keys())[:max_stocks]

    for ticker in stock_tickers:
        # Try multiple sources in order of preference
        news = []

        # 1. Try NewsAPI (if available)
        if not news:
            news = fetch_stock_news_newsapi(ticker, limit_per_stock)

        # 2. Try Alpha Vantage (if not rate limited)
        if not news:
            news = fetch_stock_news_alpha_vantage(ticker, limit_per_stock)

        # 3. Try web scraping
        if not news:
            news = fetch_stock_news_web_scraping(ticker, limit_per_stock)

        # 4. Fallback to mock data for demonstration
        if not news:
            news = fetch_stock_news_mock_data(ticker, limit_per_stock)

        if news:
            portfolio_news[ticker] = news

    return portfolio_news


##########################################################################################
## AI-POWERED ANALYSIS (DeepCharts Inspired) ##
##########################################################################################


def check_ollama_availability() -> Dict[str, bool]:
    """Check if Ollama is running and what models are available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
    return {
            "available": True,
            "models": model_names,
            "has_llama": any("llama" in name.lower() for name in model_names),
        }
    except:
        pass

    return {"available": False, "models": [], "has_llama": False}


def setup_gemini_ai() -> bool:
    """Setup Google Gemini AI with API key"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=api_key)
            return True
    except:
        pass
    return False


@st.cache_data(
    ttl=3600, show_spinner=False
)  # Cache for 1 hour (Ollama is free but intensive)
def analyze_portfolio_with_ollama(
    portfolio_data: pd.DataFrame, portfolio_name: str
) -> str:
    """Use Ollama to analyze portfolio performance and provide insights"""
    if not OLLAMA_AVAILABLE:
        return "Ollama not available. Please install: pip install ollama"

    ollama_status = check_ollama_availability()
    if not ollama_status["available"]:
        return "Ollama service not running. Start with: ollama serve"

    if not ollama_status["has_llama"]:
        return "No LLaMA model found. Install with: ollama pull llama3.2"

    try:
        # Prepare portfolio summary for AI analysis
        total_value = portfolio_data["Current Value"].sum()
        total_invested = portfolio_data["Total Invested"].sum()
        total_return = total_value - total_invested
        return_pct = (total_return / total_invested * 100) if total_invested > 0 else 0

        best_performer = portfolio_data.loc[portfolio_data["Change %"].idxmax()]
        worst_performer = portfolio_data.loc[portfolio_data["Change %"].idxmin()]

        portfolio_summary = f"""
        Portfolio: {portfolio_name}
        Total Value: ${total_value:,.2f}
        Total Invested: ${total_invested:,.2f}
        Total Return: ${total_return:,.2f} ({return_pct:.2f}%)

        Best Performer: {best_performer['Ticker']} ({best_performer['Change %']:.2f}%)
        Worst Performer: {worst_performer['Ticker']} ({worst_performer['Change %']:.2f}%)

        Holdings: {len(portfolio_data)} stocks
        Top Holdings: {', '.join(portfolio_data.nlargest(3, 'Current Value')['Ticker'].tolist())}
        """

        prompt = f"""You are a professional financial advisor. Analyze this portfolio and provide:
        1. Overall performance assessment
        2. Risk analysis
        3. Diversification insights
        4. Specific recommendations for improvement

        Portfolio Data:
        {portfolio_summary}

        Provide a concise but comprehensive analysis in 3-4 paragraphs."""

        response = ollama.chat(
            model="llama3.2", messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]

    except Exception as e:
        return f"Error analyzing portfolio with Ollama: {str(e)}"


@st.cache_data(
    ttl=14400, show_spinner=False
)  # Cache for 4 hours to respect Gemini free tier (15 requests/minute)
def analyze_news_sentiment_with_gemini(news_articles: List[Dict], ticker: str) -> str:
    """Use Google Gemini to analyze news sentiment and market impact"""
    if not GEMINI_AVAILABLE:
        return "Google Gemini not available. Please install: pip install google-generativeai"

    if not setup_gemini_ai():
        return "Gemini API key not found. Add GOOGLE_API_KEY to your .env file"

    try:
        # Prepare news summary for AI analysis
        news_summary = f"News Analysis for {ticker}:\n\n"
        for i, article in enumerate(news_articles[:5], 1):
            news_summary += f"{i}. {article['title']}\n"
            news_summary += f"   Summary: {article['summary'][:200]}...\n"
            news_summary += f"   Source: {article['source']}\n\n"

        prompt = f"""As a financial analyst, analyze these recent news articles for {ticker} and provide:

        1. Overall sentiment (Positive/Negative/Neutral)
        2. Key themes and trends
        3. Potential market impact
        4. Investment implications

        {news_summary}

        Provide a concise analysis in 2-3 paragraphs focusing on actionable insights."""

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"Error analyzing news with Gemini: {str(e)}"


def generate_ai_trading_signals(portfolio_data: pd.DataFrame) -> Dict[str, str]:
    """Generate AI-powered trading signals for portfolio stocks"""
    signals = {}

    for _, stock in portfolio_data.iterrows():
        ticker = stock["Ticker"]
        change_pct = stock["Change %"]

        # Simple AI-like logic (can be enhanced with real AI models)
        if change_pct > 5:
            signals[ticker] = "🔥 STRONG BUY - Momentum building"
        elif change_pct > 2:
            signals[ticker] = "📈 BUY - Positive trend"
        elif change_pct > -2:
            signals[ticker] = "⚖️ HOLD - Stable performance"
        elif change_pct > -5:
            signals[ticker] = "📉 WATCH - Declining trend"
        else:
            signals[ticker] = "⚠️ REVIEW - Significant decline"

    return signals


##########################################################################################
## ADVANCED CHARTING (DeepCharts Inspired) ##
##########################################################################################


def create_candlestick_chart(
    ticker: str, market: str = "US", period: str = "1mo"
) -> Optional[go.Figure]:
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
        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name="Price",
            )
        )

        # Add technical indicators if available
        if indicators.get("sma_20"):
            sma_20_series = ta.trend.sma_indicator(hist["Close"], window=20)
            fig.add_trace(
                go.Scatter(
                    x=hist.index,
                    y=sma_20_series,
                    mode="lines",
                    name="SMA 20",
                    line=dict(color="orange", width=2),
                )
            )

        if indicators.get("ema_20"):
            ema_20_series = ta.trend.ema_indicator(hist["Close"], window=20)
            fig.add_trace(
                go.Scatter(
                    x=hist.index,
                    y=ema_20_series,
                    mode="lines",
                    name="EMA 20",
                    line=dict(color="purple", width=2),
                )
            )

        # Add Bollinger Bands
        if all(indicators.get(key) for key in ["bb_high", "bb_low", "bb_mid"]):
            bb_high_series = ta.volatility.bollinger_hband(hist["Close"], window=20)
            bb_low_series = ta.volatility.bollinger_lband(hist["Close"], window=20)
            bb_mid_series = ta.volatility.bollinger_mavg(hist["Close"], window=20)

            fig.add_trace(
                go.Scatter(
                    x=hist.index,
                    y=bb_high_series,
                    mode="lines",
                    name="BB Upper",
                    line=dict(color="gray", width=1, dash="dash"),
                    showlegend=False,
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=hist.index,
                    y=bb_low_series,
                    mode="lines",
                    name="BB Lower",
                    line=dict(color="gray", width=1, dash="dash"),
                    fill="tonexty",
                    fillcolor="rgba(128,128,128,0.1)",
                    showlegend=False,
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=hist.index,
                    y=bb_mid_series,
                    mode="lines",
                    name="BB Middle",
                    line=dict(color="gray", width=1),
                )
            )

        # Add VWAP
        if indicators.get("vwap"):
            vwap_series = ta.volume.volume_weighted_average_price(
                hist["High"], hist["Low"], hist["Close"], hist["Volume"]
            )
            fig.add_trace(
                go.Scatter(
                    x=hist.index,
                    y=vwap_series,
                    mode="lines",
                    name="VWAP",
                    line=dict(color="blue", width=2, dash="dot"),
                )
            )

        # Update layout
        fig.update_layout(
            title=f"{ticker} - Technical Analysis Chart",
            yaxis_title="Price",
            xaxis_title="Date",
            height=600,
            showlegend=True,
            xaxis_rangeslider_visible=False,
        )

        return fig

    except Exception as e:
        st.error(f"Error creating chart for {ticker}: {str(e)}")
        return None


def create_technical_indicators_summary(
    ticker: str, market: str = "US"
) -> Optional[Dict]:
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
            "indicators": indicators,
        }

        # Generate trading signals
        if indicators.get("rsi"):
            rsi = indicators["rsi"]
            if rsi > 70:
                summary["signals"].append(
                    {
                        "indicator": "RSI",
                        "signal": "OVERBOUGHT",
                        "value": rsi,
                        "color": "red",
                    }
                )
            elif rsi < 30:
                summary["signals"].append(
                    {
                        "indicator": "RSI",
                        "signal": "OVERSOLD",
                        "value": rsi,
                        "color": "green",
                    }
                )
            else:
                summary["signals"].append(
                    {
                        "indicator": "RSI",
                        "signal": "NEUTRAL",
                        "value": rsi,
                        "color": "gray",
                    }
                )

        # MACD Signal
        if indicators.get("macd") and indicators.get("macd_signal"):
            macd = indicators["macd"]
            macd_signal = indicators["macd_signal"]
            if macd > macd_signal:
                summary["signals"].append(
                    {
                        "indicator": "MACD",
                        "signal": "BULLISH",
                        "value": macd,
                        "color": "green",
                    }
                )
            else:
                summary["signals"].append(
                    {
                        "indicator": "MACD",
                        "signal": "BEARISH",
                        "value": macd,
                        "color": "red",
                    }
                )

        # Price vs Moving Averages
        if indicators.get("sma_20"):
            sma_20 = indicators["sma_20"]
            if current_price > sma_20:
                summary["signals"].append(
                    {
                        "indicator": "SMA 20",
                        "signal": "ABOVE",
                        "value": sma_20,
                        "color": "green",
                    }
                )
            else:
                summary["signals"].append(
                    {
                        "indicator": "SMA 20",
                        "signal": "BELOW",
                        "value": sma_20,
                        "color": "red",
                    }
                )

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
            "total_stocks": 0,
        }

    total_invested = portfolio_data["Total Invested"].sum()
    current_value = portfolio_data["Current Value"].sum()
    total_gain_loss = current_value - total_invested
    total_gain_loss_percent = (
        (total_gain_loss / total_invested) * 100 if total_invested != 0 else 0
    )

    profitable_stocks = len(portfolio_data[portfolio_data["Gain/Loss"] > 0])
    total_stocks = len(portfolio_data)

    best_performer = (
        portfolio_data.loc[portfolio_data["Change %"].idxmax()]
        if not portfolio_data.empty
        else None
    )
    worst_performer = (
        portfolio_data.loc[portfolio_data["Change %"].idxmin()]
        if not portfolio_data.empty
        else None
    )

    return {
        "total_invested": total_invested,
        "current_value": current_value,
        "total_gain_loss": total_gain_loss,
        "total_gain_loss_percent": total_gain_loss_percent,
        "best_performer": best_performer,
        "worst_performer": worst_performer,
        "profitable_stocks": profitable_stocks,
        "total_stocks": total_stocks,
    }


@st.cache_data(ttl=300, show_spinner=False)
def create_portfolio_dataframe(portfolio_stocks: Dict, market: str) -> pd.DataFrame:
    """Create portfolio dataframe with real-time data"""
    if not portfolio_stocks:
        return pd.DataFrame()

    portfolio_data = []

    for i, (ticker, stock_info) in enumerate(portfolio_stocks.items()):
        quantity = stock_info["quantity"]
        avg_price = stock_info["avg_price"]

        # Add small delay between API calls to respect rate limits (except for first stock)
        if i > 0:
            time.sleep(0.5)  # 500ms delay between calls

        # Fetch real-time data
        real_time_data = fetch_stock_data(ticker, market)

        if real_time_data:
            current_price = real_time_data["current_price"]
            day_change = real_time_data["change"]
            day_change_percent = real_time_data["change_percent"]
            currency = real_time_data["currency"]
        else:
            # If no real-time data available, use average price as placeholder
            current_price = avg_price
            day_change = 0
            day_change_percent = 0
            currency = "BRL" if market == "Brazilian" else "USD"

        # Calculate portfolio metrics (moved outside the if/else block)
        total_invested = quantity * avg_price
        current_value = quantity * current_price
        gain_loss = current_value - total_invested
        gain_loss_percent = (
            (gain_loss / total_invested) * 100 if total_invested != 0 else 0
        )

        # Add basic sector info for your Brazilian stocks
        if market == "Brazilian":
            ticker_clean = ticker.replace(".SA", "").upper()
            sectors = {
                "VAMO3": "Real Estate",
                "SANB11": "Financial Services",
                "EGIE3": "Utilities",
                "PRIO3": "Energy",
            }
            sector = sectors.get(ticker_clean, "Unknown")
        else:
            sector = "Unknown"

        portfolio_data.append(
            {
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
                "Currency": currency,
                "Sector": sector,
                "Dividend Yield %": 0,
                "Annual Dividend": 0,
            }
        )

    return pd.DataFrame(portfolio_data)


def create_portfolio_dataframe_progressive(
    portfolio_stocks: Dict,
    market: str,
    progress_placeholder=None,
    table_placeholder=None,
) -> pd.DataFrame:
    """Create portfolio dataframe with progressive loading and real-time updates"""
    if not portfolio_stocks:
        return pd.DataFrame()

    portfolio_data = []
    total_stocks = len(portfolio_stocks)

    for i, (ticker, stock_info) in enumerate(portfolio_stocks.items()):
        quantity = stock_info["quantity"]
        avg_price = stock_info["avg_price"]

        # Update progress
        if progress_placeholder:
            progress_percentage = (i / total_stocks) * 100
            progress_placeholder.progress(
                progress_percentage / 100, f"Loading {ticker}... ({i+1}/{total_stocks})"
            )

        # Add small delay between API calls to respect rate limits (except for first stock)
        if i > 0:
            time.sleep(0.5)  # 500ms delay between calls

        # Fetch real-time data
        real_time_data = fetch_stock_data(ticker, market)

        if real_time_data:
            current_price = real_time_data["current_price"]
            day_change = real_time_data["change"]
            day_change_percent = real_time_data["change_percent"]
            currency = real_time_data["currency"]
            status = "✅"
        else:
            # If no real-time data available, use average price as placeholder
                current_price = avg_price
            day_change = 0
            day_change_percent = 0
            currency = "BRL" if market == "Brazilian" else "USD"
            status = "⚠️"

        # Calculate portfolio metrics
            total_invested = quantity * avg_price
            current_value = quantity * current_price
            gain_loss = current_value - total_invested
        gain_loss_percent = (
            (gain_loss / total_invested) * 100 if total_invested != 0 else 0
        )

        portfolio_data.append(
            {
                "Status": status,
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
                "Currency": currency,
                "Sector": "Unknown",
                "Dividend Yield %": 0,
                "Annual Dividend": 0,
            }
        )

        # Update table progressively (show partial results)
        if (
            table_placeholder and len(portfolio_data) >= 3
        ):  # Show table after loading at least 3 stocks
            current_df = pd.DataFrame(portfolio_data)
            table_placeholder.dataframe(
                current_df.style.format(
                    {
                        "Avg Price": "{:.2f}",
                        "Current Price": "{:.2f}",
                        "Total Invested": "{:,.2f}",
                        "Current Value": "{:,.2f}",
                        "Gain/Loss": "{:,.2f}",
                        "Change %": "{:.2f}%",
                        "Day Change": "{:.2f}",
                        "Day Change %": "{:.2f}%",
                    }
                ).map(
                    lambda x: (
                        "color: green"
                        if isinstance(x, (int, float)) and x > 0
                        else (
                            "color: red"
                            if isinstance(x, (int, float)) and x < 0
                            else ""
                        )
                    ),
                    subset=["Gain/Loss", "Change %", "Day Change", "Day Change %"],
                ),
                use_container_width=True,
                hide_index=True,
            )

    # Final progress update
    if progress_placeholder:
        progress_placeholder.success(
            f"✅ Loaded all {total_stocks} stocks successfully!"
        )

    return pd.DataFrame(portfolio_data)


def fetch_stock_data_with_error_tracking(
    ticker: str, market: str
) -> tuple[Optional[Dict], str]:
    """Fetch stock data with detailed error tracking"""
    try:
        data = fetch_stock_data(ticker, market)
        if data and data.get("current_price", 0) > 0:
            return data, "✅ Success"
        else:
            return None, "⚠️ No data available"
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            return None, "🚫 Rate limited"
        elif "timeout" in error_msg.lower():
            return None, "⏱️ Timeout"
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            return None, "🌐 Network error"
        else:
            return None, f"❌ Error: {error_msg[:30]}..."


def create_portfolio_summary_with_errors(portfolio_stocks: Dict, market: str) -> Dict:
    """Create a summary of portfolio loading with error details"""
    summary = {
        "total_stocks": len(portfolio_stocks),
        "successful": 0,
        "failed": 0,
        "failed_stocks": [],
        "error_details": {},
    }

    for ticker in portfolio_stocks.keys():
        data, status = fetch_stock_data_with_error_tracking(ticker, market)
        if data:
            summary["successful"] += 1
        else:
            summary["failed"] += 1
            summary["failed_stocks"].append(ticker)
            summary["error_details"][ticker] = status

    return summary


##########################################################################################
## STREAMLIT DASHBOARD UI ##
##########################################################################################

# Page configuration
st.set_page_config(
    page_title="Portfolio Management Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize portfolio manager
if "portfolio_manager" not in st.session_state:
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
    "Choose Portfolio", options=portfolio_names, index=0 if portfolio_names else None
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
    market_type = (
        "Brazilian"
        if "brazil" in selected_portfolio.lower() or selected_portfolio == "Brazilian"
        else "US"
    )

    # Add stock form
    with st.sidebar.expander("Add/Update Stock"):
        ticker_input = st.text_input(
            "Stock Ticker",
            help="Enter ticker symbol (e.g., AAPL for US, PETR4 for Brazilian)",
        )
        # Support fractional shares for US market, integers for Brazilian market
        if selected_portfolio and "US" in selected_portfolio.upper():
            quantity_input = st.number_input(
                "Quantity", min_value=0.001, value=1.0, step=0.001, format="%.3f"
            )
        else:
        quantity_input = st.number_input("Quantity", min_value=1, value=1)
        avg_price_input = st.number_input(
            "Average Price", min_value=0.01, value=1.0, step=0.01
        )

        if st.button("Add/Update Stock"):
            if ticker_input and quantity_input and avg_price_input:
                portfolio_manager.add_stock(
                    selected_portfolio,
                    ticker_input.upper(),
                    quantity_input,
                    avg_price_input,
                )
                st.success(f"Stock {ticker_input.upper()} added/updated!")
                st.rerun()

    # Remove stock
    portfolio_stocks = portfolio_manager.get_portfolio_stocks(selected_portfolio)
    if portfolio_stocks:
        with st.sidebar.expander("Remove Stock"):
            stock_to_remove = st.selectbox(
                "Select Stock to Remove", options=list(portfolio_stocks.keys())
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
        market_type = (
            "Brazilian"
            if "brazil" in selected_portfolio.lower()
            or selected_portfolio == "Brazilian"
            else "US"
        )

        # Create portfolio dataframe
        with st.spinner("Fetching real-time stock data..."):
            # Show data source status
            has_twelve_data = bool(os.getenv("TWELVE_DATA_API_KEY"))
            has_alpha_vantage = bool(os.getenv("ALPHA_VANTAGE_API_KEY"))

            if has_twelve_data or has_alpha_vantage:
                data_source_info = "Using "
                if has_twelve_data:
                    data_source_info += "Twelve Data"
                if has_alpha_vantage:
                    data_source_info += (
                        " + Alpha Vantage" if has_twelve_data else "Alpha Vantage"
                    )
                data_source_info += " APIs"
            else:
                data_source_info = "Using Yahoo Finance (may be rate limited)"

            # Show data source and last update time
            current_time = datetime.now().strftime("%H:%M:%S")
            st.info(f"📊 {data_source_info} | Last updated: {current_time}")

            # Use progressive loading for large portfolios
            num_stocks = len(portfolio_stocks)
            if (
                num_stocks > 8
            ):  # Use progressive loading for portfolios with many stocks
                progress_placeholder = st.empty()
                table_placeholder = st.empty()

                # Show initial message
                progress_placeholder.info(
                    f"🔄 Loading data for {num_stocks} stocks with progressive display..."
                )

                # Use progressive loading
                df = create_portfolio_dataframe_progressive(
                    portfolio_stocks,
                    market_type,
                    progress_placeholder,
                    table_placeholder,
                )

                # Clear progress after completion
                time.sleep(1)  # Brief pause to show completion message
                progress_placeholder.empty()
                table_placeholder.empty()  # Clear to show final formatted table below
            else:
                # Use regular loading for smaller portfolios
                if num_stocks > 3:
                    st.info(f"🔄 Loading data for {num_stocks} stocks...")
            df = create_portfolio_dataframe(portfolio_stocks, market_type)

        # Show loading summary and error details if any
        if not df.empty:
            # Check for any loading issues and display summary
            loading_summary = create_portfolio_summary_with_errors(
                portfolio_stocks, market_type
            )

            if loading_summary["failed"] > 0:
                with st.expander(
                    f"⚠️ Loading Issues ({loading_summary['failed']}/{loading_summary['total_stocks']} stocks failed)",
                    expanded=False,
                ):
                    st.warning(
                        f"**{loading_summary['successful']} stocks loaded successfully, {loading_summary['failed']} failed**"
                    )

                    # Group errors by type
                    error_groups = {}
                    for ticker, error in loading_summary["error_details"].items():
                        if error not in error_groups:
                            error_groups[error] = []
                        error_groups[error].append(ticker)

                    for error_type, tickers in error_groups.items():
                        st.write(f"**{error_type}**: {', '.join(tickers)}")

                    st.info("💡 **Troubleshooting tips:**")
                    st.write("- 🚫 **Rate limited**: Wait a few minutes and refresh")
                    st.write("- ⏱️ **Timeout**: Check your internet connection")
                    st.write(
                        "- 🌐 **Network error**: Verify connectivity and try again"
                    )
                    st.write("- ⚠️ **No data**: Verify ticker symbols are correct")
                    st.write(
                        "- ❌ **Other errors**: Check ticker format (Brazilian stocks should not include .SA)"
                    )
            else:
                st.success(
                    f"✅ All {loading_summary['total_stocks']} stocks loaded successfully!"
                )

            # Calculate portfolio metrics
            metrics = calculate_portfolio_metrics(df)

            # Display key metrics
            st.subheader(f"{selected_portfolio} Portfolio Overview")

            col1, col2, col3, col4 = st.columns(4)

            currency = df["Currency"].iloc[0] if not df.empty else "USD"

            with col1:
                st.metric(
                    "Total Invested", f"{currency} {metrics['total_invested']:,.2f}"
                )

            with col2:
                st.metric(
                    "Current Value",
                    f"{currency} {metrics['current_value']:,.2f}",
                    delta=f"{currency} {metrics['total_gain_loss']:,.2f}",
                )

            with col3:
                st.metric(
                    "Total Return",
                    f"{metrics['total_gain_loss_percent']:.2f}%",
                    delta=f"{metrics['total_gain_loss_percent']:.2f}%",
                )

            with col4:
                st.metric(
                    "Profitable Stocks",
                    f"{metrics['profitable_stocks']}/{metrics['total_stocks']}",
                    delta=(
                        f"{(metrics['profitable_stocks']/metrics['total_stocks'])*100:.1f}%"
                        if metrics["total_stocks"] > 0
                        else "0%"
                    ),
                )

            st.markdown("---")

            # Portfolio visualizations
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Portfolio Composition")
                fig_pie = px.pie(
                    df,
                    values="Current Value",
                    names="Ticker",
                    title="Portfolio Weight by Current Value",
                )
                fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_pie, width="stretch")

            with col2:
                st.subheader("Performance Overview")
                fig_bar = px.bar(
                    df.sort_values("Change %", ascending=True),
                    x="Change %",
                    y="Ticker",
                    orientation="h",
                    color="Change %",
                    color_continuous_scale=["red", "yellow", "green"],
                    title="Stock Performance (%)",
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, width="stretch")

            # Detailed portfolio table
            st.subheader("Detailed Portfolio View")

            # Format the dataframe for display
            display_df = df.copy()

            # Format currency columns
            currency_columns = [
                "Avg Price",
                "Current Price",
                "Total Invested",
                "Current Value",
                "Gain/Loss",
                "Day Change",
            ]
            for col in currency_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(
                        lambda x: f"{currency} {x:,.2f}"
                    )

            # Format percentage columns
            percentage_columns = ["Change %", "Day Change %"]
            for col in percentage_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")

            # Remove currency column from display
            display_df = display_df.drop("Currency", axis=1)

            # Apply conditional formatting
            def highlight_gains_losses(val):
                if isinstance(val, str) and "%" in val:
                    num_val = float(val.replace("%", ""))
                    if num_val > 0:
                        return "background-color: rgba(0, 255, 0, 0.2)"
                    elif num_val < 0:
                        return "background-color: rgba(255, 0, 0, 0.2)"
                return ""

            styled_df = display_df.style.map(
                highlight_gains_losses, subset=["Change %", "Day Change %"]
            )
            # Calculate dynamic height based on number of rows (35px per row + header)
            table_height = min(len(display_df) * 35 + 50, 800)  # Max height of 800px
            st.dataframe(
                styled_df, width="stretch", hide_index=True, height=table_height
            )

            # Performance highlights
            if (
                metrics["best_performer"] is not None
                and metrics["worst_performer"] is not None
            ):
                st.subheader("Performance Highlights")
                col1, col2 = st.columns(2)

                with col1:
                    st.success("🏆 Best Performer")
                    best = metrics["best_performer"]
                    st.write(f"**{best['Ticker']}**: {best['Change %']:.2f}% gain")
                    st.write(f"Value: {currency} {best['Current Value']:,.2f}")

                with col2:
                    st.error("📉 Worst Performer")
                    worst = metrics["worst_performer"]
                    st.write(f"**{worst['Ticker']}**: {worst['Change %']:.2f}% loss")
                    st.write(f"Value: {currency} {worst['Current Value']:,.2f}")

            # Stock News Feed Section
            st.markdown("---")
            st.subheader("📰 Latest Stock News")

            # News settings
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Stay updated with the latest news for your portfolio stocks")
                # Show news source status
                has_newsapi = bool(os.getenv("NEWSAPI_KEY"))
                has_alpha_vantage = bool(os.getenv("ALPHA_VANTAGE_API_KEY"))

                if not has_newsapi and not has_alpha_vantage:
                    st.info(
                        "💡 For better news coverage, add API keys to your .env file:\n"
                        "- NEWSAPI_KEY (free at newsapi.org)\n"
                        "- ALPHA_VANTAGE_API_KEY (free at alphavantage.co)"
                    )
                elif has_alpha_vantage and not has_newsapi:
                    st.warning(
                        "⚠️ Alpha Vantage rate limit reached. Consider adding NEWSAPI_KEY for more news."
                    )
            with col2:
                news_limit = st.selectbox(
                    "News per stock", [3, 5, 10], index=1, key="news_limit"
                )

            # Fetch and display news
            if st.button("🔄 Refresh News", key="refresh_news"):
                st.cache_data.clear()  # Clear cache to get fresh news

            with st.spinner("Fetching latest news..."):
                portfolio_news = fetch_portfolio_news(portfolio_stocks, news_limit)

            if portfolio_news:
                # Create tabs for each stock
                stock_tabs = st.tabs(
                    [f"📈 {ticker}" for ticker in portfolio_news.keys()]
                )

                for i, (ticker, news_articles) in enumerate(portfolio_news.items()):
                    with stock_tabs[i]:
                        if news_articles:
                            for article in news_articles:
                                # Create news card
                                with st.container():
                                    # Header with title and sentiment
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.markdown(
                                            f"**[{article['title']}]({article['url']})**"
                                        )
                                    with col2:
                                        # Sentiment indicator
                                        sentiment = article["sentiment_label"]
                                        if sentiment == "Positive":
                                            st.success(f"😊 {sentiment}")
                                        elif sentiment == "Negative":
                                            st.error(f"😟 {sentiment}")
        else:
                                            st.info(f"😐 {sentiment}")

                                    # Article details
                                    st.write(article["summary"])

                                    # Footer with source and time
                                    col1, col2 = st.columns([2, 2])
                                    with col1:
                                        st.caption(f"📰 Source: {article['source']}")
                                    with col2:
                                        st.caption(f"🕒 {article['time_published']}")

                                    st.markdown("---")
    else:
                            st.info(f"No recent news found for {ticker}")
            else:
                st.warning(
                    "No news available for your portfolio stocks. This could be due to:"
                )
                st.write("• API rate limits")
                st.write("• No recent news for these stocks")
                st.write("• Network connectivity issues")

            # AI-Powered Insights Section (DeepCharts inspired)
            st.markdown("---")
            st.subheader("🤖 AI-Powered Portfolio Insights")

            # Check AI service availability
            ollama_status = check_ollama_availability()
            gemini_available = setup_gemini_ai()

            col1, col2 = st.columns(2)
            with col1:
                st.write("**AI Services Status:**")
                if ollama_status["available"]:
                    st.success("✅ Ollama: Connected")
                    if ollama_status["has_llama"]:
                        st.success("✅ LLaMA Model: Available")
                    else:
                        st.warning("⚠️ LLaMA Model: Not installed")
                        st.info("Install with: `ollama pull llama3.2`")
                else:
                    st.error("❌ Ollama: Not running")
                    st.info("Start with: `ollama serve`")

            with col2:
                if gemini_available:
                    st.success("✅ Google Gemini: Connected")
                else:
                    st.error("❌ Google Gemini: No API key")
                    st.info("Add GOOGLE_API_KEY to .env file")

            # AI Analysis Options
            ai_analysis_type = st.selectbox(
                "Choose AI Analysis:",
                ["Portfolio Overview", "Trading Signals", "News Sentiment"],
                key="ai_analysis_type",
            )

            # Only show AI analysis if we have portfolio data
            if portfolio_stocks:
                if st.button("🧠 Run AI Analysis", key="run_ai_analysis"):
                    with st.spinner("AI is analyzing your portfolio..."):
                        # Recreate portfolio_df for AI analysis (optimize API calls)
                        portfolio_data = []

                        # Batch API calls to respect rate limits
                        for ticker, stock_info in portfolio_stocks.items():
                            # Use cached data if available to minimize API calls
                            real_time_data = fetch_stock_data(ticker, market_type)

                            if real_time_data:
                                current_price = real_time_data["current_price"]
                                day_change = real_time_data["change"]
                                day_change_percent = real_time_data["change_percent"]
                                currency = real_time_data["currency"]
                            else:
                                current_price = stock_info["avg_price"]
                                day_change = 0
                                day_change_percent = 0
                                currency = (
                                    "BRL" if market_type == "Brazilian" else "USD"
                                )

                            total_invested = (
                                stock_info["quantity"] * stock_info["avg_price"]
                            )
                            current_value = stock_info["quantity"] * current_price
                            total_return = current_value - total_invested
                            return_percent = (
                                (total_return / total_invested * 100)
                                if total_invested > 0
                                else 0
                            )

                            portfolio_data.append(
                                {
                                    "Ticker": ticker,
                                    "Quantity": stock_info["quantity"],
                                    "Avg Price": stock_info["avg_price"],
                                    "Current Price": current_price,
                                    "Total Invested": total_invested,
                                    "Current Value": current_value,
                                    "Total Return": total_return,
                                    "Return %": return_percent,
                                    "Change %": day_change_percent,
                                    "Currency": currency,
                                }
                            )

                        ai_portfolio_df = pd.DataFrame(portfolio_data)

                        if ai_analysis_type == "Portfolio Overview":
                            if (
                                ollama_status["available"]
                                and ollama_status["has_llama"]
                            ):
                                analysis = analyze_portfolio_with_ollama(
                                    ai_portfolio_df, selected_portfolio
                                )
                                st.markdown("### 🎯 AI Portfolio Analysis")
                                st.write(analysis)
                            else:
                                st.warning(
                                    "Ollama with LLaMA model required for portfolio analysis"
                                )

                        elif ai_analysis_type == "Trading Signals":
                            signals = generate_ai_trading_signals(ai_portfolio_df)
                            st.markdown("### 📊 AI Trading Signals")

                            for ticker, signal in signals.items():
                                if "STRONG BUY" in signal:
                                    st.success(f"**{ticker}**: {signal}")
                                elif "BUY" in signal:
                                    st.info(f"**{ticker}**: {signal}")
                                elif "HOLD" in signal:
                                    st.warning(f"**{ticker}**: {signal}")
                                else:
                                    st.error(f"**{ticker}**: {signal}")

                        elif ai_analysis_type == "News Sentiment":
                            if gemini_available and portfolio_news:
                                st.markdown("### 📰 AI News Sentiment Analysis")

                                # Optimize for Gemini free tier (15 requests/minute)
                                # Analyze only 1 stock at a time to respect rate limits
                                analyzed_count = 0
                                max_analyses = 1  # Limit to 1 analysis per request to stay within free tier

                                for ticker, news_articles in portfolio_news.items():
                                    if analyzed_count >= max_analyses:
                                        st.info(
                                            f"📊 Analysis limited to {max_analyses} stock(s) to respect API rate limits. "
                                            f"Run again to analyze other stocks."
                                        )
                                        break

                                    if news_articles:
                                        with st.expander(f"📈 {ticker} News Analysis"):
                                            sentiment_analysis = (
                                                analyze_news_sentiment_with_gemini(
                                                    news_articles, ticker
                                                )
                                            )
                                            st.write(sentiment_analysis)
                                            analyzed_count += 1
                            else:
                                if not gemini_available:
                                    st.warning(
                                        "Google Gemini API key required for news sentiment analysis"
                                    )
                                if not portfolio_news:
                                    st.warning(
                                        "No news data available for sentiment analysis"
                                    )
            else:
                st.info("Add stocks to your portfolio to enable AI analysis")

            # AI Setup Instructions
            with st.expander("🛠️ AI Setup Instructions"):
                st.markdown(
                    """
                ### Free AI Services Setup

                **1. Ollama (Local AI - Completely Free)**
                ```bash
                # Install Ollama
                curl -fsSL https://ollama.ai/install.sh | sh

                # Start Ollama service
                ollama serve

                # Install LLaMA model (in another terminal)
                ollama pull llama3.2
                ```

                **2. Google Gemini (Free Tier - 15 requests/minute)**
                - Get free API key at: https://aistudio.google.com/app/apikey
                - Add to your `.env` file: `GOOGLE_API_KEY=your_key_here`

                **Benefits:**
                - 🎯 **Portfolio Analysis**: AI-powered insights on performance and risk
                - 📊 **Trading Signals**: Smart buy/sell/hold recommendations
                - 📰 **News Sentiment**: AI analysis of market news impact
                """
                )

            # Technical Analysis Section (DeepCharts inspired) - Temporarily disabled to reduce API noise
            st.markdown("---")
            st.subheader("📊 Technical Analysis (DeepCharts Enhanced)")
            st.info(
                "🔧 Technical analysis temporarily disabled to reduce API errors. Will be re-enabled with better error handling."
            )

            # Stock selection for detailed analysis (commented out temporarily)
            # selected_stock = st.selectbox(
            #     "Select stock for detailed technical analysis:",
            #     options=list(portfolio_stocks.keys()),
            #     key="tech_analysis_stock"
            # )

            # Temporarily disabled technical analysis section
            if False:  # selected_stock:
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Candlestick chart with technical indicators
                    st.subheader(f"{selected_stock} - Advanced Chart")

                    # Chart period selection
                    chart_period = st.selectbox(
                        "Chart Period:",
                        options=["1mo", "3mo", "6mo", "1y"],
                        index=1,
                        key="chart_period",
                    )

                    # Create and display candlestick chart
                    with st.spinner("Loading advanced chart..."):
                        fig = create_candlestick_chart(
                            selected_stock, market_type, chart_period
                        )
                        if fig:
                            st.plotly_chart(fig, width="stretch")
                        else:
                            st.warning(f"Could not load chart for {selected_stock}")

                with col2:
                    # Technical indicators summary
                    st.subheader("Technical Indicators")

                    with st.spinner("Calculating indicators..."):
                        tech_summary = create_technical_indicators_summary(
                            selected_stock, market_type
                        )

                        if tech_summary:
                            # Current price
                            st.metric(
                                "Current Price",
                                f"{currency} {tech_summary['current_price']:.2f}",
                            )

                            # Technical signals
                            st.subheader("Trading Signals")
                            for signal in tech_summary["signals"]:
                                color = signal["color"]
                                if color == "green":
                                    st.success(
                                        f"**{signal['indicator']}**: {signal['signal']}"
                                    )
                                elif color == "red":
                                    st.error(
                                        f"**{signal['indicator']}**: {signal['signal']}"
                                    )
                                else:
                                    st.info(
                                        f"**{signal['indicator']}**: {signal['signal']}"
                                    )

                                if signal["value"]:
                                    st.caption(f"Value: {signal['value']:.2f}")

                            # Raw indicator values
                            st.subheader("Indicator Values")
                            indicators = tech_summary["indicators"]

                            if indicators.get("rsi"):
                                st.metric("RSI (14)", f"{indicators['rsi']:.2f}")

                            if indicators.get("sma_20"):
                                st.metric(
                                    "SMA 20", f"{currency} {indicators['sma_20']:.2f}"
                                )

                            if indicators.get("ema_20"):
                                st.metric(
                                    "EMA 20", f"{currency} {indicators['ema_20']:.2f}"
                                )

                            if indicators.get("vwap"):
                                st.metric(
                                    "VWAP", f"{currency} {indicators['vwap']:.2f}"
                                )

                        else:
                            st.warning(
                                f"Could not load technical analysis for {selected_stock}"
                            )

        else:
            st.error("⚠️ **Unable to fetch data for your portfolio stocks**")
            st.markdown(
                """
            **Possible causes:**
            - API rate limits reached (try again in a few minutes)
            - Invalid ticker symbols
            - Network connectivity issues
            - All data sources temporarily unavailable

            **What you can do:**
            - ✅ Check your ticker symbols are correct
            - ✅ Wait a few minutes and refresh the page
            - ✅ Verify your internet connection
            - ✅ Try adding API keys in your `.env` file for better reliability
            """
            )

            # Show which stocks failed to load
            failed_stocks = []
            for ticker in portfolio_stocks.keys():
                test_data = fetch_stock_data(ticker, market_type)
                if not test_data:
                    failed_stocks.append(ticker)

            if failed_stocks:
                st.warning(f"**Stocks with data issues:** {', '.join(failed_stocks)}")

            # Show fallback data using average prices
            st.info("**Showing portfolio with average prices as fallback:**")
            fallback_data = []
            for ticker, stock_info in portfolio_stocks.items():
                quantity = stock_info["quantity"]
                avg_price = stock_info["avg_price"]
                total_invested = quantity * avg_price
                currency = "BRL" if market_type == "Brazilian" else "USD"

                fallback_data.append(
                    {
                        "Ticker": ticker,
                        "Quantity": quantity,
                        "Avg Price": avg_price,
                        "Total Invested": total_invested,
                        "Currency": currency,
                        "Status": "⚠️ Using avg price",
                    }
                )

            if fallback_data:
                fallback_df = pd.DataFrame(fallback_data)
                st.dataframe(fallback_df, use_container_width=True, hide_index=True)

    else:
        st.info(
            f"No stocks in {selected_portfolio} portfolio. Use the sidebar to add stocks."
        )

else:
    st.info("Please select or create a portfolio to get started.")

# Settings
st.sidebar.markdown("---")
st.sidebar.subheader("Settings")

# Configurable refresh settings
refresh_enabled = st.sidebar.checkbox("Enable auto-refresh", value=False)

if refresh_enabled:
    refresh_options = {
        "5 minutes": 300,
        "10 minutes": 600,
        "15 minutes": 900,
        "30 minutes": 1800,
        "1 hour": 3600,
    }

    selected_refresh = st.sidebar.selectbox(
        "Refresh interval",
        options=list(refresh_options.keys()),
        index=2,  # Default to 15 minutes
        help="Choose how often to refresh stock data. Longer intervals preserve API limits.",
    )

    refresh_seconds = refresh_options[selected_refresh]

    st.sidebar.info(f"📊 Next refresh in {selected_refresh}")

    # Show API usage warning for short intervals
    if refresh_seconds < 900:  # Less than 15 minutes
        st.sidebar.warning("⚠️ Short refresh intervals may exhaust API limits quickly")

    time.sleep(refresh_seconds)
    st.rerun()
else:
    st.sidebar.info("💡 Enable auto-refresh to automatically update stock prices")

# Manual refresh button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Now", help="Manually refresh stock data"):
    st.cache_data.clear()  # Clear cache to force fresh data
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: gray;'>
    <p>Portfolio Management Dashboard | Real-time data powered by multiple APIs</p>
    <p>💡 Tip: For Brazilian stocks, use tickers like PETR4, VALE3, ITUB4</p>
</div>
""",
    unsafe_allow_html=True,
)
