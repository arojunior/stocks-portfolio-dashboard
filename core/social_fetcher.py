"""
Social Media Data Fetcher
Handles fetching data from free sources only - no paid APIs or mock data
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st


def fetch_threads_mentions(ticker: str, limit: int = 10) -> List[Dict]:
    """Fetch Meta Threads mentions for a stock ticker"""
    try:
        access_token = os.getenv("META_ACCESS_TOKEN")
        app_id = os.getenv("META_APP_ID")
        
        if not access_token or not app_id:
            print(f"Meta credentials not found for {ticker}")
            return []
        
        # Meta Threads API requires OAuth flow and specific permissions
        # For now, we'll implement a basic test to check if the token works
        # The actual implementation would need proper OAuth setup
        
        # Test basic API connection first
        test_url = "https://graph.threads.net/v1.0/me"
        test_params = {"access_token": access_token}
        
        test_response = requests.get(test_url, params=test_params, timeout=10)
        
        if test_response.status_code == 401:
            print(f"Meta Threads: Invalid access token for {ticker}")
            print("   Note: Threads API requires OAuth flow and specific permissions")
            return []
        elif test_response.status_code == 500:
            print(f"Meta Threads: API error for {ticker}")
            print("   Note: This might be due to missing permissions or OAuth setup")
            return []
        elif test_response.status_code != 200:
            print(f"Meta Threads: Unexpected response {test_response.status_code} for {ticker}")
            return []
        
        # If we get here, the token works but we need proper OAuth setup for full functionality
        print(f"Meta Threads: Token valid but full integration requires OAuth setup")
        print("   For now, returning empty results until OAuth is properly configured")
        
        # TODO: Implement proper OAuth flow for Threads API
        # This would involve:
        # 1. Setting up OAuth redirect URI
        # 2. Getting authorization code from user
        # 3. Exchanging code for access token
        # 4. Using token to access Threads data
        
        return []
        
    except Exception as e:
        print(f"Error fetching Threads data for {ticker}: {e}")
        return []


def fetch_enhanced_portfolio_news(tickers: List[str]) -> Dict[str, List[Dict]]:
    """
    Fetch enhanced news from free sources only
    Uses existing free APIs: NewsAPI, Alpha Vantage
    """
    enhanced_news = {
        "traditional_news": [],
        "market_analysis": [],
        "earnings_news": [],
        "analyst_ratings": [],
        "social_media": []
    }

    # Limit to avoid rate limiting
    max_tickers = min(len(tickers), 3)
    selected_tickers = tickers[:max_tickers]

    for ticker in selected_tickers:
        try:
            # Use existing free news sources
            from core.data_fetcher import fetch_stock_news_newsapi, fetch_stock_news_alpha_vantage

            # Get traditional news from NewsAPI (free)
            newsapi_news = fetch_stock_news_newsapi(ticker)
            enhanced_news["traditional_news"].extend(newsapi_news)

            # Get additional news from Alpha Vantage (free tier)
            alpha_news = fetch_stock_news_alpha_vantage(ticker)
            enhanced_news["traditional_news"].extend(alpha_news)

            # Get social media mentions from Threads (free)
            threads_mentions = fetch_threads_mentions(ticker, 3)
            enhanced_news["social_media"].extend(threads_mentions)

            # Categorize news by type
            categorized = categorize_news_by_type(newsapi_news + alpha_news)
            enhanced_news["earnings_news"].extend(categorized.get("earnings", []))
            enhanced_news["analyst_ratings"].extend(categorized.get("analyst_ratings", []))
            enhanced_news["market_analysis"].extend(categorized.get("market_news", []))

        except Exception as e:
            print(f"Error fetching enhanced news for {ticker}: {e}")
            continue

    return enhanced_news


def categorize_news_by_type(news_items: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize news items by type using free text analysis"""
    categories = {
        "earnings": [],
        "analyst_ratings": [],
        "market_news": [],
        "technical_analysis": [],
        "fundamental_analysis": []
    }

    for item in news_items:
        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        source = item.get("source", "").lower()

        # Categorize based on keywords (free text analysis)
        if any(keyword in title or keyword in description for keyword in
               ["earnings", "revenue", "profit", "quarterly", "q1", "q2", "q3", "q4"]):
            categories["earnings"].append(item)
        elif any(keyword in title or keyword in description for keyword in
                 ["upgrade", "downgrade", "rating", "target", "analyst", "buy", "sell", "hold"]):
            categories["analyst_ratings"].append(item)
        elif any(keyword in title or keyword in description for keyword in
                 ["chart", "technical", "pattern", "indicator", "resistance", "support"]):
            categories["technical_analysis"].append(item)
        elif any(keyword in title or keyword in description for keyword in
                 ["fundamental", "valuation", "financial", "balance sheet", "cash flow"]):
            categories["fundamental_analysis"].append(item)
        else:
            categories["market_news"].append(item)

    return categories


def get_news_sentiment_summary(news_items: List[Dict]) -> Dict[str, float]:
    """Calculate basic sentiment metrics from news (free analysis)"""
    if not news_items:
        return {"positive": 0, "neutral": 0, "negative": 0, "overall": 0}

    positive_keywords = ["up", "rise", "gain", "profit", "beat", "exceed", "strong", "bullish"]
    negative_keywords = ["down", "fall", "loss", "miss", "weak", "bearish", "decline", "drop"]

    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for item in news_items:
        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        text = f"{title} {description}"

        positive_score = sum(1 for keyword in positive_keywords if keyword in text)
        negative_score = sum(1 for keyword in negative_keywords if keyword in text)

        if positive_score > negative_score:
            positive_count += 1
        elif negative_score > positive_score:
            negative_count += 1
        else:
            neutral_count += 1

    total = len(news_items)
    return {
        "positive": positive_count / total if total > 0 else 0,
        "neutral": neutral_count / total if total > 0 else 0,
        "negative": negative_count / total if total > 0 else 0,
        "overall": (positive_count - negative_count) / total if total > 0 else 0
    }
