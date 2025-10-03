#!/usr/bin/env python3
"""
Test script for enhanced news functionality
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.social_fetcher import fetch_enhanced_portfolio_news, categorize_news_by_type


def test_enhanced_news():
    """Test enhanced news functionality"""
    print("Testing enhanced news functionality...")
    
    # Test with sample tickers
    test_tickers = ["AAPL", "TSLA", "MSFT"]
    
    print(f"\n1. Testing enhanced news for {test_tickers}:")
    try:
        enhanced_news = fetch_enhanced_portfolio_news(test_tickers)
        
        print(f"   Traditional News: {len(enhanced_news.get('traditional_news', []))}")
        print(f"   Social Media: {len(enhanced_news.get('social_media', []))}")
        print(f"   Reddit Discussions: {len(enhanced_news.get('reddit_discussions', []))}")
        print(f"   Financial Blogs: {len(enhanced_news.get('financial_blogs', []))}")
        print(f"   Analyst Reports: {len(enhanced_news.get('analyst_reports', []))}")
        
        # Test news categorization
        all_news = []
        for source, items in enhanced_news.items():
            all_news.extend(items)
        
        if all_news:
            print(f"\n2. Testing news categorization:")
            categories = categorize_news_by_type(all_news)
            
            for category, items in categories.items():
                print(f"   {category}: {len(items)} items")
                
                if items:
                    print(f"      Sample: {items[0].get('title', items[0].get('text', 'No title'))[:50]}...")
        
        print(f"\n✅ Enhanced news test completed successfully")
        
    except Exception as e:
        print(f"❌ Error testing enhanced news: {e}")
        import traceback
        traceback.print_exc()


def test_news_categorization():
    """Test news categorization functionality"""
    print(f"\n3. Testing news categorization:")
    
    # Sample news items
    sample_news = [
        {
            "title": "AAPL Reports Strong Q4 Earnings",
            "content": "Apple reported better than expected earnings...",
            "source": "Financial News",
            "sentiment": 0.8
        },
        {
            "title": "Analyst Upgrades TSLA to Buy Rating",
            "content": "Goldman Sachs upgrades Tesla...",
            "source": "Analyst Report",
            "sentiment": 0.6
        },
        {
            "text": "Just bought more MSFT shares! 🚀",
            "source": "X (Twitter)",
            "sentiment": 0.9
        }
    ]
    
    try:
        categories = categorize_news_by_type(sample_news)
        
        for category, items in categories.items():
            print(f"   {category}: {len(items)} items")
            
    except Exception as e:
        print(f"❌ Error testing categorization: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED NEWS TESTS")
    print("=" * 60)
    
    test_enhanced_news()
    test_news_categorization()
    
    print("\n" + "=" * 60)
    print("ENHANCED NEWS TESTS COMPLETED")
    print("=" * 60)
