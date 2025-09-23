#!/usr/bin/env python3
"""
Debug script to check what yfinance returns for SANB11
"""

import yfinance as yf
import pandas as pd

def debug_sanb11():
    """Debug SANB11 dividend data from yfinance"""
    print("=== Debugging SANB11 Dividend Data ===")
    
    try:
        # Test with .SA suffix
        ticker = "SANB11.SA"
        print(f"\nTesting {ticker}:")
        
        stock = yf.Ticker(ticker)
        
        # Get basic info
        try:
            info = stock.info
            print(f"Info keys: {list(info.keys())}")
            
            # Look for dividend-related fields
            dividend_fields = [key for key in info.keys() if 'dividend' in key.lower() or 'yield' in key.lower()]
            print(f"Dividend/Yield fields: {dividend_fields}")
            
            for field in dividend_fields:
                value = info.get(field)
                print(f"  {field}: {value}")
                
        except Exception as e:
            print(f"Error getting info: {e}")
        
        # Try to get dividend history
        try:
            dividends = stock.dividends
            print(f"\nDividend history (last 5):")
            print(dividends.tail())
            
            if not dividends.empty:
                recent_dividends = dividends.tail(4)
                annual_dividend = recent_dividends.sum()
                print(f"Annual dividend (last 4 quarters): {annual_dividend}")
                
                # Get current price
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_price = hist["Close"].iloc[-1]
                    print(f"Current price: {current_price}")
                    if current_price > 0:
                        dividend_yield = (annual_dividend / current_price) * 100
                        print(f"Calculated dividend yield: {dividend_yield:.2f}%")
                        
        except Exception as e:
            print(f"Error getting dividend history: {e}")
            
    except Exception as e:
        print(f"Error with {ticker}: {e}")
    
    # Also test without .SA suffix
    try:
        ticker = "SANB11"
        print(f"\nTesting {ticker} (without .SA):")
        
        stock = yf.Ticker(ticker)
        
        try:
            info = stock.info
            dividend_fields = [key for key in info.keys() if 'dividend' in key.lower() or 'yield' in key.lower()]
            print(f"Dividend/Yield fields: {dividend_fields}")
            
            for field in dividend_fields:
                value = info.get(field)
                print(f"  {field}: {value}")
                
        except Exception as e:
            print(f"Error getting info: {e}")
            
    except Exception as e:
        print(f"Error with {ticker}: {e}")

if __name__ == "__main__":
    debug_sanb11()
