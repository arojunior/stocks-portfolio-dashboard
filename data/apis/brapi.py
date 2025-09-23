"""
BRAPI API Module
Handles all BRAPI operations for Brazilian stocks
"""

import requests
import os
from typing import Dict, Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def fetch_stock_quote(ticker: str, market: str = "Brazilian") -> Optional[Dict]:
    """Fetch Brazilian stock data from BRAPI (Brazilian stock API with API key support)"""
    if market != "Brazilian":
        return None

    try:
        import os
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
                        "info": stock_data
                    }

    except Exception as e:
        # Silently handle BRAPI errors
        print(f"Error fetching from BRAPI for {ticker}: {e}")
        return None


def fetch_historical_data(ticker: str, market: str = "Brazilian", period: str = "1mo") -> Optional[Dict]:
    """Fetch historical data from BRAPI"""
    if market != "Brazilian":
        return None

    try:
        # Remove .SA suffix for BRAPI
        clean_ticker = ticker.replace(".SA", "")

        # Map period to BRAPI format
        period_map = {
            "1d": "1d",
            "5d": "5d",
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "2y": "2y",
            "5y": "5y"
        }

        range_param = period_map.get(period, "1mo")

        url = f"https://brapi.dev/api/quote/{clean_ticker}"
        params = {
            "range": range_param,
            "interval": "1d"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "results" in data and data["results"]:
            result = data["results"][0]
            historical_data = result.get("historicalDataPrice", [])

            return {
                "ticker": ticker,
                "historical_data": historical_data,
                "info": result
            }
    except Exception as e:
        print(f"Error fetching historical data from BRAPI for {ticker}: {e}")
        return None


def fetch_dividend_data(ticker: str, market: str = "Brazilian") -> Optional[Dict]:
    """Fetch dividend data from BRAPI"""
    if market != "Brazilian":
        return None

    try:
        # Remove .SA suffix for BRAPI
        clean_ticker = ticker.replace(".SA", "")

        url = f"https://brapi.dev/api/quote/{clean_ticker}"
        params = {
            "range": "1y",
            "interval": "1d"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "results" in data and data["results"]:
            result = data["results"][0]
            dividends = result.get("dividends", [])

            return {
                "ticker": ticker,
                "dividend_history": dividends,
                "info": result
            }
    except Exception as e:
        print(f"Error fetching dividend data from BRAPI for {ticker}: {e}")
        return None


def fetch_company_info(ticker: str, market: str = "Brazilian") -> Optional[Dict]:
    """Fetch company information from BRAPI"""
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

            return {
                "ticker": ticker,
                "company_info": result,
                "info": result
            }
    except Exception as e:
        print(f"Error fetching company info from BRAPI for {ticker}: {e}")
        return None


def fetch_market_data() -> Optional[Dict]:
    """Fetch general market data from BRAPI"""
    try:
        url = "https://brapi.dev/api/quote/list"
        params = {
            "limit": 100,
            "sortBy": "market_cap",
            "sortOrder": "desc"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "stocks" in data:
            return {
                "market_data": data["stocks"],
                "info": data
            }
    except Exception as e:
        print(f"Error fetching market data from BRAPI: {e}")
        return None
