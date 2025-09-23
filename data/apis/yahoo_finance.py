"""
Yahoo Finance API Module
Handles all Yahoo Finance data fetching operations
"""

import yfinance as yf
import sys
from io import StringIO
from contextlib import redirect_stderr
from typing import Dict, Optional
from core.data_fetcher import SuppressYFinanceOutput


def fetch_stock_quote(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch basic stock quote from Yahoo Finance"""
    try:
        # Format ticker for market
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
                "info": info
            }
    except Exception as e:
        print(f"Error fetching from Yahoo Finance for {ticker}: {e}")
        return None


def fetch_historical_data(ticker: str, market: str = "US", period: str = "1mo") -> Optional[Dict]:
    """Fetch historical data from Yahoo Finance"""
    try:
        # Format ticker for market
        if market == "Brazilian" and not ticker.endswith(".SA"):
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = ticker

        with SuppressYFinanceOutput():
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period=period, interval="1d")
            
            if hist.empty:
                return None

            return {
                "ticker": ticker,
                "historical_data": hist,
                "info": stock.info
            }
    except Exception as e:
        print(f"Error fetching historical data from Yahoo Finance for {ticker}: {e}")
        return None


def fetch_dividend_data(ticker: str, market: str = "US") -> Optional[Dict]:
    """Fetch dividend data from Yahoo Finance"""
    try:
        # Format ticker for market
        if market == "Brazilian" and not ticker.endswith(".SA"):
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = ticker

        with SuppressYFinanceOutput():
            stock = yf.Ticker(ticker_symbol)
            
            # Get dividend history
            dividends = stock.dividends
            info = stock.info
            
            # Get current dividend yield
            dividend_yield = info.get("dividendYield", 0)
            if dividend_yield and dividend_yield < 1:
                dividend_yield = dividend_yield * 100  # Convert to percentage
            
            return {
                "ticker": ticker,
                "dividend_yield": dividend_yield,
                "dividend_history": dividends,
                "info": info
            }
    except Exception as e:
        print(f"Error fetching dividend data from Yahoo Finance for {ticker}: {e}")
        return None


def fetch_enhanced_data(ticker: str, market: str = "US", period: str = "1mo") -> Optional[Dict]:
    """Fetch enhanced data with technical indicators from Yahoo Finance"""
    try:
        # Format ticker for market
        if market == "Brazilian" and not ticker.endswith(".SA"):
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = ticker

        with SuppressYFinanceOutput():
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period=period, interval="1d")
            
            if hist.empty:
                return None

            info = stock.info
            
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

            return {
                "ticker": ticker,
                "historical_data": hist,
                "info": info,
                "technical_indicators": {
                    "sma_20": hist['SMA_20'].iloc[-1] if not hist['SMA_20'].isna().iloc[-1] else None,
                    "sma_50": hist['SMA_50'].iloc[-1] if not hist['SMA_50'].isna().iloc[-1] else None,
                    "ema_20": hist['EMA_20'].iloc[-1] if not hist['EMA_20'].isna().iloc[-1] else None,
                    "rsi": hist['RSI'].iloc[-1] if not hist['RSI'].isna().iloc[-1] else None,
                    "bb_upper": hist['BB_Upper'].iloc[-1] if not hist['BB_Upper'].isna().iloc[-1] else None,
                    "bb_middle": hist['BB_Middle'].iloc[-1] if not hist['BB_Middle'].isna().iloc[-1] else None,
                    "bb_lower": hist['BB_Lower'].iloc[-1] if not hist['BB_Lower'].isna().iloc[-1] else None,
                    "macd": hist['MACD'].iloc[-1] if not hist['MACD'].isna().iloc[-1] else None,
                    "macd_signal": hist['MACD_Signal'].iloc[-1] if not hist['MACD_Signal'].isna().iloc[-1] else None,
                    "macd_histogram": hist['MACD_Histogram'].iloc[-1] if not hist['MACD_Histogram'].isna().iloc[-1] else None
                }
            }
    except Exception as e:
        print(f"Error fetching enhanced data from Yahoo Finance for {ticker}: {e}")
        return None
