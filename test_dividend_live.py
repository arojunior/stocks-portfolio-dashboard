#!/usr/bin/env python3
"""
Test live dividend data with different approaches
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from portfolio_dashboard import get_dividend_yield, get_dividend_yield_from_yfinance
import time

def test_dividend_approaches():
    """Test different approaches to get dividend data"""
    print("=== Testing Dividend Data Approaches ===")
    
    # Test stocks
    test_stocks = [
        ("ITUB4", "Brazilian"),  # Itaú - should have static data
        ("SANB11", "Brazilian"), # Santander - should have live data
        ("AAPL", "US"),          # Apple - should have live data
    ]
    
    for ticker, market in test_stocks:
        print(f"\n--- Testing {ticker} ({market}) ---")
        
        # Test 1: With empty info (should use static for Brazilian)
        print("1. Empty info:")
        yield_empty = get_dividend_yield(ticker, market, {})
        print(f"   Yield: {yield_empty}%")
        
        # Test 2: Direct yfinance approach
        print("2. Direct yfinance:")
        try:
            yield_yfinance = get_dividend_yield_from_yfinance(ticker, market)
            print(f"   Yield: {yield_yfinance}%")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Mock live data
        print("3. Mock live data:")
        mock_info = {
            "dividendYield": 0.0605,  # 6.05% as decimal
            "trailingAnnualDividendYield": 0.0545,  # 5.45% as decimal
        }
        yield_mock = get_dividend_yield(ticker, market, mock_info)
        print(f"   Yield: {yield_mock}%")
        
        # Add delay to avoid rate limiting
        time.sleep(2)

if __name__ == "__main__":
    test_dividend_approaches()
