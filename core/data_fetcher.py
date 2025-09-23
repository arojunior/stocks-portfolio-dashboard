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
from io import StringIO
from contextlib import redirect_stderr
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

from app.config import (
    BRAZILIAN_SECTORS, 
    BRAZILIAN_DIVIDEND_YIELDS, 
    API_KEYS,
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
    """Get sector information for a stock, with Brazilian stock mapping"""
    # First try to get from Yahoo Finance info
    sector = info.get("sector", "")
    if sector and sector != "Unknown":
        return sector

    # For Brazilian stocks, use our mapping
    if market == "Brazilian":
        ticker_clean = ticker.replace(".SA", "").upper()
        return BRAZILIAN_SECTORS.get(ticker_clean, "Unknown")

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
                        return value * 100 if value < 1 else value

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

    # Fallback to static data for Brazilian stocks only
    if market == "Brazilian":
        return BRAZILIAN_DIVIDEND_YIELDS.get(ticker_clean, 0.0)

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
            except:
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


def fetch_stock_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch stock data with fallback to multiple APIs"""
    # Try different APIs in order of preference
    apis = [
        ("Twelve Data", lambda: fetch_from_twelve_data(ticker, market)),
        ("Alpha Vantage", lambda: fetch_from_alpha_vantage(ticker, market)),
        ("BRAPI", lambda: fetch_from_brapi(ticker, market)),
        ("Yahoo Finance", lambda: fetch_from_yahoo_finance(ticker, market))
    ]

    for api_name, fetch_func in apis:
        try:
            # Add rate limiting
            time.sleep(RATE_LIMITS.get(api_name.lower().replace(" ", "_"), 0.5))
            
            data = fetch_func()
            if data:
                return data
        except Exception as e:
            print(f"Error with {api_name} for {ticker}: {e}")
            continue

    return None


def fetch_from_yahoo_finance(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch stock data from Yahoo Finance"""
    try:
        if market == "Brazilian" and not ticker.endswith(".SA"):
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = ticker

        with SuppressYFinanceOutput():
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period="1d")
            
            if hist.empty:
                return None

            info = stock.info
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Open'].iloc[-1]
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close > 0 else 0

            return {
                "ticker": ticker,
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "volume": hist['Volume'].iloc[-1],
                "market_cap": info.get("marketCap", 0),
                "sector": get_sector_info(ticker, market, info),
                "dividend_yield": get_dividend_yield(ticker, market, info),
                "info": info
            }
    except Exception as e:
        print(f"Error fetching from Yahoo Finance for {ticker}: {e}")
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

        if "price" in data:
            current_price = float(data["price"])
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


def fetch_from_brapi(ticker: str, market: str = "Brazilian") -> Optional[Dict]:
    """Fetch Brazilian stock data from BRAPI"""
    if market != "Brazilian":
        return None

    try:
        # Remove .SA suffix for BRAPI
        clean_ticker = ticker.replace(".SA", "")
        
        url = f"https://brapi.dev/api/quote/{clean_ticker}"
        params = {
            "range": "1d",
            "interval": "1d"
        }

        response = requests.get(url, params=params, timeout=10)
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
                "market_cap": float(result.get("marketCap", 0)),
                "sector": get_sector_info(ticker, market, result),
                "dividend_yield": get_dividend_yield(ticker, market, result),
                "info": result
            }
    except Exception as e:
        print(f"Error fetching from BRAPI for {ticker}: {e}")
        return None
