"""
Social Media Data Fetcher
Handles fetching data from free sources only - no paid APIs or mock data
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st


def fetch_enhanced_portfolio_news(tickers: List[str]) -> Dict[str, List[Dict]]:
    """
    Fetch enhanced news from free sources only
    Uses existing free APIs: NewsAPI, Alpha Vantage
    """
    enhanced_news = {
        "traditional_news": [],
        "market_analysis": [],
        "earnings_news": [],
        "analyst_ratings": []
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