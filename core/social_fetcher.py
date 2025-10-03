"""
Social Media Data Fetcher
Handles fetching data from social platforms like X/Twitter, Reddit, etc.
"""

import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st


def fetch_x_twitter_mentions(ticker: str, limit: int = 10) -> List[Dict]:
    """Fetch X/Twitter mentions for a stock ticker"""
    try:
        # Note: This would require X API v2 access
        # For now, we'll create a mock implementation
        # In production, you'd use tweepy or requests with X API v2
        
        # Mock data for demonstration
        mock_tweets = [
            {
                "text": f"Just bought more {ticker} shares! 🚀",
                "author": "CryptoTrader",
                "created_at": datetime.now().isoformat(),
                "retweet_count": 15,
                "like_count": 42,
                "sentiment": 0.8,
                "url": f"https://x.com/status/1234567890",
                "source": "X (Twitter)"
            },
            {
                "text": f"{ticker} earnings report looks promising 📈",
                "author": "FinanceGuru",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "retweet_count": 8,
                "like_count": 23,
                "sentiment": 0.6,
                "url": f"https://x.com/status/1234567891",
                "source": "X (Twitter)"
            }
        ]
        
        return mock_tweets[:limit]
        
    except Exception as e:
        print(f"Error fetching X/Twitter data for {ticker}: {e}")
        return []


def fetch_reddit_discussions(ticker: str, limit: int = 5) -> List[Dict]:
    """Fetch Reddit discussions about a stock"""
    try:
        # Reddit API (free tier available)
        # This would use praw (Python Reddit API Wrapper)
        
        # Mock data for demonstration
        mock_reddit_posts = [
            {
                "title": f"DD: Why I'm bullish on {ticker}",
                "content": f"Detailed analysis of {ticker} fundamentals...",
                "subreddit": "investing",
                "author": "u/StockAnalyst",
                "score": 156,
                "comments": 23,
                "created_at": datetime.now().isoformat(),
                "sentiment": 0.7,
                "url": f"https://reddit.com/r/investing/comments/abc123",
                "source": "Reddit"
            },
            {
                "title": f"{ticker} earnings beat expectations",
                "content": f"Just saw the {ticker} earnings report...",
                "subreddit": "stocks",
                "author": "u/MarketWatcher",
                "score": 89,
                "comments": 12,
                "created_at": (datetime.now() - timedelta(hours=4)).isoformat(),
                "sentiment": 0.5,
                "url": f"https://reddit.com/r/stocks/comments/def456",
                "source": "Reddit"
            }
        ]
        
        return mock_reddit_posts[:limit]
        
    except Exception as e:
        print(f"Error fetching Reddit data for {ticker}: {e}")
        return []


def fetch_financial_blogs(ticker: str, limit: int = 5) -> List[Dict]:
    """Fetch financial blog posts and analysis"""
    try:
        # This could integrate with RSS feeds from financial blogs
        # or use web scraping for specific financial sites
        
        mock_blog_posts = [
            {
                "title": f"Technical Analysis: {ticker} Chart Patterns",
                "content": f"Deep dive into {ticker} technical indicators...",
                "author": "Technical Trader",
                "blog": "FinanceBlog.com",
                "published_at": datetime.now().isoformat(),
                "sentiment": 0.3,
                "url": f"https://financeblog.com/{ticker.lower()}-analysis",
                "source": "Financial Blog"
            },
            {
                "title": f"Fundamental Analysis: {ticker} Valuation",
                "content": f"Comprehensive analysis of {ticker} financials...",
                "author": "Value Investor",
                "blog": "InvestmentInsights.com",
                "published_at": (datetime.now() - timedelta(hours=6)).isoformat(),
                "sentiment": 0.6,
                "url": f"https://investmentinsights.com/{ticker.lower()}-valuation",
                "source": "Investment Blog"
            }
        ]
        
        return mock_blog_posts[:limit]
        
    except Exception as e:
        print(f"Error fetching blog data for {ticker}: {e}")
        return []


def fetch_analyst_reports(ticker: str, limit: int = 3) -> List[Dict]:
    """Fetch analyst reports and ratings"""
    try:
        # This could integrate with financial data providers
        # or scrape analyst report sites
        
        mock_analyst_reports = [
            {
                "title": f"Analyst Upgrade: {ticker} Target Price Raised",
                "content": f"Analyst firm upgrades {ticker} from Hold to Buy...",
                "analyst": "Goldman Sachs",
                "rating": "Buy",
                "target_price": "$150.00",
                "published_at": datetime.now().isoformat(),
                "sentiment": 0.8,
                "url": f"https://analystreports.com/{ticker.lower()}-upgrade",
                "source": "Analyst Report"
            },
            {
                "title": f"Earnings Preview: {ticker} Q4 Expectations",
                "content": f"Analysts expect {ticker} to report strong Q4...",
                "analyst": "Morgan Stanley",
                "rating": "Overweight",
                "target_price": "$145.00",
                "published_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "sentiment": 0.6,
                "url": f"https://analystreports.com/{ticker.lower()}-earnings",
                "source": "Analyst Report"
            }
        ]
        
        return mock_analyst_reports[:limit]
        
    except Exception as e:
        print(f"Error fetching analyst data for {ticker}: {e}")
        return []


@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
def fetch_enhanced_portfolio_news(tickers: List[str]) -> Dict[str, List[Dict]]:
    """Fetch enhanced news from multiple social and financial sources"""
    enhanced_news = {
        "traditional_news": [],
        "social_media": [],
        "reddit_discussions": [],
        "financial_blogs": [],
        "analyst_reports": []
    }
    
    # Limit to avoid rate limiting
    max_tickers = min(len(tickers), 3)
    selected_tickers = tickers[:max_tickers]
    
    for ticker in selected_tickers:
        try:
            # Fetch from different sources
            social_media = fetch_x_twitter_mentions(ticker, 3)
            reddit_posts = fetch_reddit_discussions(ticker, 2)
            blog_posts = fetch_financial_blogs(ticker, 2)
            analyst_reports = fetch_analyst_reports(ticker, 1)
            
            # Add to enhanced news
            enhanced_news["social_media"].extend(social_media)
            enhanced_news["reddit_discussions"].extend(reddit_posts)
            enhanced_news["financial_blogs"].extend(blog_posts)
            enhanced_news["analyst_reports"].extend(analyst_reports)
            
        except Exception as e:
            print(f"Error fetching enhanced news for {ticker}: {e}")
            continue
    
    return enhanced_news


def categorize_news_by_type(news_items: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize news items by type"""
    categories = {
        "earnings": [],
        "analyst_ratings": [],
        "market_news": [],
        "social_sentiment": [],
        "technical_analysis": [],
        "fundamental_analysis": []
    }
    
    for item in news_items:
        title = item.get("title", "").lower()
        content = item.get("content", "").lower()
        source = item.get("source", "").lower()
        
        # Categorize based on keywords
        if any(keyword in title or keyword in content for keyword in ["earnings", "revenue", "profit", "quarterly"]):
            categories["earnings"].append(item)
        elif any(keyword in title or keyword in content for keyword in ["upgrade", "downgrade", "rating", "target", "analyst"]):
            categories["analyst_ratings"].append(item)
        elif any(keyword in title or keyword in content for keyword in ["market", "trading", "price", "volatility"]):
            categories["market_news"].append(item)
        elif source in ["x (twitter)", "reddit"]:
            categories["social_sentiment"].append(item)
        elif any(keyword in title or keyword in content for keyword in ["chart", "technical", "pattern", "indicator"]):
            categories["technical_analysis"].append(item)
        elif any(keyword in title or keyword in content for keyword in ["fundamental", "valuation", "financial", "balance sheet"]):
            categories["fundamental_analysis"].append(item)
        else:
            categories["market_news"].append(item)
    
    return categories
