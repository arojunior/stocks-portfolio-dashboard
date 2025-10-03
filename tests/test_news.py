#!/usr/bin/env python3
"""
Test script for news fetching functionality
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data_fetcher import (
    fetch_stock_news_alpha_vantage,
    fetch_stock_news_newsapi,
    fetch_portfolio_news
)


def test_news_apis():
    """Test the news APIs with a sample ticker"""
    print("Testing news APIs...")

    # Test ticker
    test_ticker = "AAPL"

    print(f"\n1. Testing Alpha Vantage for {test_ticker}:")
    try:
        alpha_news = fetch_stock_news_alpha_vantage(test_ticker)
        print(f"   Found {len(alpha_news)} articles")
        if alpha_news:
            print(f"   First article: {alpha_news[0].get('title', 'No title')}")
        else:
            print("   No articles found")
    except Exception as e:
        print(f"   Error: {e}")

    print(f"\n2. Testing NewsAPI for {test_ticker}:")
    try:
        newsapi_news = fetch_stock_news_newsapi(test_ticker)
        print(f"   Found {len(newsapi_news)} articles")
        if newsapi_news:
            print(f"   First article: {newsapi_news[0].get('title', 'No title')}")
        else:
            print("   No articles found")
    except Exception as e:
        print(f"   Error: {e}")

    print(f"\n3. Testing portfolio news for [{test_ticker}]:")
    try:
        portfolio_news = fetch_portfolio_news([test_ticker])
        print(f"   Found {len(portfolio_news)} articles")
        if portfolio_news:
            print(f"   First article: {portfolio_news[0].get('title', 'No title')}")
        else:
            print("   No articles found")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n4. Environment variables:")
    print(f"   ALPHA_VANTAGE_API_KEY: {'Set' if os.getenv('ALPHA_VANTAGE_API_KEY') else 'Not set'}")
    print(f"   NEWSAPI_KEY: {'Set' if os.getenv('NEWSAPI_KEY') else 'Not set'}")


def test_brazilian_news():
    """Test news fetching for Brazilian stocks"""
    print("\nTesting news for Brazilian stocks...")

    # Test with Brazilian stocks from your portfolio
    brazilian_tickers = ["ITSA4", "FESA4", "VIVT3", "UNIP6", "CPLE6"]

    print(f"\nTesting portfolio news for {brazilian_tickers}:")
    try:
        portfolio_news = fetch_portfolio_news(brazilian_tickers)
        print(f"   Found {len(portfolio_news)} total articles")

        if portfolio_news:
            print("\n   Sample articles:")
            for i, article in enumerate(portfolio_news[:3]):  # Show first 3
                print(f"   {i+1}. {article.get('title', 'No title')}")
                print(f"      Source: {article.get('source', 'Unknown')}")
                print(f"      Sentiment: {article.get('sentiment', 0)}")
                print()
        else:
            print("   No articles found")
    except Exception as e:
        print(f"   Error: {e}")


def test_real_news():
    """Test real news fetching with renewed API key"""
    print("\nTesting real news with renewed NewsAPI key...")

    # Test with a popular US stock
    test_ticker = "AAPL"

    print(f"\n1. Testing NewsAPI for {test_ticker}:")
    try:
        news = fetch_stock_news_newsapi(test_ticker)
        print(f"   Found {len(news)} articles")
        if news:
            print(f"   First article: {news[0].get('title', 'No title')}")
            print(f"   Source: {news[0].get('source', 'Unknown')}")
            print(f"   Published: {news[0].get('publishedAt', 'Unknown')}")
        else:
            print("   No articles found")
    except Exception as e:
        print(f"   Error: {e}")

    print(f"\n2. Testing portfolio news for [{test_ticker}]:")
    try:
        portfolio_news = fetch_portfolio_news([test_ticker])
        print(f"   Found {len(portfolio_news)} total articles")
        if portfolio_news:
            print(f"   First article: {portfolio_news[0].get('title', 'No title')}")
            print(f"   Source: {portfolio_news[0].get('source', 'Unknown')}")
        else:
            print("   No articles found")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("NEWS FUNCTIONALITY TESTS")
    print("=" * 60)

    test_news_apis()
    test_brazilian_news()
    test_real_news()

    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)

