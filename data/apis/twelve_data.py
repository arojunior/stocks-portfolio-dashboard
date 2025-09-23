"""
Twelve Data API Module
Handles all Twelve Data API operations
"""

import requests
import os
from typing import Dict, Optional
from app.config import API_KEYS


def fetch_stock_quote(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch stock quote from Twelve Data API"""
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
                "info": data
            }
    except Exception as e:
        print(f"Error fetching from Twelve Data for {ticker}: {e}")
        return None


def fetch_historical_data(ticker: str, market: str = "US", period: str = "1mo") -> Optional[Dict]:
    """Fetch historical data from Twelve Data API"""
    api_key = API_KEYS.get("TWELVE_DATA_API_KEY")
    if not api_key:
        return None

    try:
        # Format ticker for API
        if market == "Brazilian" and not ticker.endswith(".SA"):
            symbol = f"{ticker}.SA"
        else:
            symbol = ticker

        # Map period to Twelve Data format
        period_map = {
            "1d": "1day",
            "5d": "5day", 
            "1mo": "1month",
            "3mo": "3month",
            "6mo": "6month",
            "1y": "1year",
            "2y": "2year",
            "5y": "5year"
        }
        
        interval = period_map.get(period, "1day")

        url = f"https://api.twelvedata.com/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "apikey": api_key,
            "outputsize": 100
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "values" in data:
            return {
                "ticker": ticker,
                "historical_data": data["values"],
                "info": data
            }
    except Exception as e:
        print(f"Error fetching historical data from Twelve Data for {ticker}: {e}")
        return None


def fetch_dividend_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch dividend data from Twelve Data API"""
    api_key = API_KEYS.get("TWELVE_DATA_API_KEY")
    if not api_key:
        return None

    try:
        # Format ticker for API
        if market == "Brazilian" and not ticker.endswith(".SA"):
            symbol = f"{ticker}.SA"
        else:
            symbol = ticker

        url = f"https://api.twelvedata.com/dividends"
        params = {
            "symbol": symbol,
            "apikey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "dividends" in data:
            return {
                "ticker": ticker,
                "dividend_history": data["dividends"],
                "info": data
            }
    except Exception as e:
        print(f"Error fetching dividend data from Twelve Data for {ticker}: {e}")
        return None


def fetch_company_info(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch company information from Twelve Data API"""
    api_key = API_KEYS.get("TWELVE_DATA_API_KEY")
    if not api_key:
        return None

    try:
        # Format ticker for API
        if market == "Brazilian" and not ticker.endswith(".SA"):
            symbol = f"{ticker}.SA"
        else:
            symbol = ticker

        url = f"https://api.twelvedata.com/profile"
        params = {
            "symbol": symbol,
            "apikey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "name" in data:
            return {
                "ticker": ticker,
                "company_info": data,
                "info": data
            }
    except Exception as e:
        print(f"Error fetching company info from Twelve Data for {ticker}: {e}")
        return None
