#!/usr/bin/env python3
"""
Test script to verify API integration is working
"""

import os
from dotenv import load_dotenv
import requests
import time

def test_twelve_data_api():
    """Test Twelve Data API with Brazilian stocks"""
    load_dotenv()
    api_key = os.getenv('TWELVE_DATA_API_KEY')

    if not api_key:
        print("❌ TWELVE_DATA_API_KEY not found in .env file")
        return

    print(f"🔑 API Key loaded: {api_key[:8]}...")

    # Test popular Brazilian stocks
    test_stocks = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3']

    print("\n📊 Testing Brazilian stocks with Twelve Data API:")
    print("-" * 60)

    for stock in test_stocks:
        try:
            params = {'symbol': stock, 'apikey': api_key}
            response = requests.get('https://api.twelvedata.com/quote', params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'close' in data:
                    price = float(data['close'])
                    prev_close = float(data.get('previous_close', price))
                    change = price - prev_close
                    change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

                    print(f"✅ {stock:<8} R$ {price:>8.2f} ({change_pct:+.2f}%)")
                else:
                    print(f"❌ {stock:<8} API Error: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ {stock:<8} HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ {stock:<8} Exception: {str(e)}")

        # Respect rate limit (8 calls/minute = 7.5 seconds between calls)
        time.sleep(8)

    print("\n🎉 API integration test completed!")
    print("If you see ✅ symbols above, your Twelve Data API is working correctly.")
    print("The dashboard will now fetch real-time prices for Brazilian stocks!")

if __name__ == "__main__":
    test_twelve_data_api()

