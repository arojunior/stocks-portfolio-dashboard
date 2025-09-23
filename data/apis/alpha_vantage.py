"""
Alpha Vantage API Module
Handles all Alpha Vantage API operations
"""

import requests
import os
from typing import Dict, Optional
from app.config import API_KEYS


def fetch_stock_quote(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch stock quote from Alpha Vantage API"""
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
                "info": quote
            }
    except Exception as e:
        print(f"Error fetching from Alpha Vantage for {ticker}: {e}")
        return None


def fetch_historical_data(ticker: str, market: str = "US", period: str = "1mo") -> Optional[Dict]:
    """Fetch historical data from Alpha Vantage API"""
    api_key = API_KEYS.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return None

    try:
        # Map period to Alpha Vantage function
        if period in ["1d", "5d"]:
            function = "TIME_SERIES_INTRADAY"
            interval = "5min"
        else:
            function = "TIME_SERIES_DAILY"
            interval = None

        url = f"https://www.alphavantage.co/query"
        params = {
            "function": function,
            "symbol": ticker,
            "apikey": api_key
        }

        if interval:
            params["interval"] = interval

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract time series data
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break

        if time_series_key and data[time_series_key]:
            return {
                "ticker": ticker,
                "historical_data": data[time_series_key],
                "info": data
            }
    except Exception as e:
        print(f"Error fetching historical data from Alpha Vantage for {ticker}: {e}")
        return None


def fetch_dividend_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch dividend data from Alpha Vantage API"""
    api_key = API_KEYS.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return None

    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "DIVIDEND",
            "symbol": ticker,
            "apikey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "dividend" in data:
            return {
                "ticker": ticker,
                "dividend_history": data["dividend"],
                "info": data
            }
    except Exception as e:
        print(f"Error fetching dividend data from Alpha Vantage for {ticker}: {e}")
        return None


def fetch_company_info(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch company information from Alpha Vantage API"""
    api_key = API_KEYS.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return None

    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "Name" in data:
            return {
                "ticker": ticker,
                "company_info": data,
                "info": data
            }
    except Exception as e:
        print(f"Error fetching company info from Alpha Vantage for {ticker}: {e}")
        return None


def fetch_news(ticker: str, limit: int = 10) -> Optional[Dict]:
    """Fetch news from Alpha Vantage API"""
    api_key = API_KEYS.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return None

    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "apikey": api_key,
            "limit": limit
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "feed" in data:
            return {
                "ticker": ticker,
                "news": data["feed"],
                "info": data
            }
    except Exception as e:
        print(f"Error fetching news from Alpha Vantage for {ticker}: {e}")
        return None
