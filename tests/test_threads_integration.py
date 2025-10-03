#!/usr/bin/env python3
"""
Test script for Meta Threads integration
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

from core.social_fetcher import fetch_threads_mentions, fetch_enhanced_portfolio_news


def test_threads_api_connection():
    """Test Meta Threads API connection"""
    print("Testing Meta Threads API connection...")

    # Check environment variables
    access_token = os.getenv("META_ACCESS_TOKEN")
    app_id = os.getenv("META_APP_ID")

    if not access_token:
        print("❌ META_ACCESS_TOKEN not found in environment")
        return False

    if not app_id:
        print("❌ META_APP_ID not found in environment")
        return False

    print(f"✅ Found Meta credentials:")
    print(f"   App ID: {app_id}")
    print(f"   Access Token: {access_token[:10]}...")

    return True


def test_threads_mentions():
    """Test fetching Threads mentions for a stock"""
    print("\nTesting Threads mentions for AAPL...")

    try:
        mentions = fetch_threads_mentions("AAPL", 5)

        print(f"✅ Threads API call successful")
        print(f"   Found {len(mentions)} mentions")

        if mentions:
            print("\n📱 Sample Threads mentions:")
            for i, mention in enumerate(mentions[:3], 1):
                print(f"   {i}. {mention.get('text', 'No text')[:50]}...")
                print(f"      Likes: {mention.get('like_count', 0)}")
                print(f"      Replies: {mention.get('reply_count', 0)}")
                print(f"      Reposts: {mention.get('repost_count', 0)}")
        else:
            print("   No mentions found (this is normal if no recent posts mention AAPL)")

        return True

    except Exception as e:
        print(f"❌ Error testing Threads mentions: {e}")
        return False


def test_enhanced_news_with_threads():
    """Test enhanced news with Threads integration"""
    print("\nTesting enhanced news with Threads integration...")

    try:
        enhanced_news = fetch_enhanced_portfolio_news(["AAPL", "TSLA"])

        print(f"✅ Enhanced news fetch successful")
        print(f"   Traditional News: {len(enhanced_news.get('traditional_news', []))}")
        print(f"   Social Media: {len(enhanced_news.get('social_media', []))}")
        print(f"   Market Analysis: {len(enhanced_news.get('market_analysis', []))}")
        print(f"   Earnings News: {len(enhanced_news.get('earnings_news', []))}")
        print(f"   Analyst Ratings: {len(enhanced_news.get('analyst_ratings', []))}")

        # Show social media data if available
        social_media = enhanced_news.get('social_media', [])
        if social_media:
            print(f"\n🧵 Threads mentions found:")
            for mention in social_media[:2]:
                print(f"   - {mention.get('text', 'No text')[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Error testing enhanced news: {e}")
        return False


def test_api_endpoints():
    """Test Meta Threads API endpoints"""
    print("\nTesting Meta Threads API endpoints...")

    try:
        import requests

        access_token = os.getenv("META_ACCESS_TOKEN")
        if not access_token:
            print("❌ No access token found")
            return False

        # Test basic API connection
        url = "https://graph.threads.net/v1.0/me"
        params = {"access_token": access_token}

        response = requests.get(url, params=params, timeout=10)

        print(f"   API Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API connection successful")
            print(f"   User ID: {data.get('id', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print(f"❌ Invalid access token")
            print(f"   Response: {response.text}")
            return False
        elif response.status_code == 500:
            print(f"❌ Server error (500)")
            print(f"   This usually means the API endpoint or permissions are incorrect")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("META THREADS INTEGRATION TEST")
    print("=" * 60)

    # Test 1: Check credentials
    creds_ok = test_threads_api_connection()

    if creds_ok:
        # Test 2: Test API endpoints
        api_ok = test_api_endpoints()

        if api_ok:
            # Test 3: Test Threads mentions
            mentions_ok = test_threads_mentions()

            # Test 4: Test enhanced news
            enhanced_ok = test_enhanced_news_with_threads()

            print(f"\n" + "=" * 60)
            print("TEST RESULTS SUMMARY")
            print("=" * 60)
            print(f"✅ Credentials: {'PASS' if creds_ok else 'FAIL'}")
            print(f"✅ API Connection: {'PASS' if api_ok else 'FAIL'}")
            print(f"✅ Threads Mentions: {'PASS' if mentions_ok else 'FAIL'}")
            print(f"✅ Enhanced News: {'PASS' if enhanced_ok else 'FAIL'}")

            if all([creds_ok, api_ok, mentions_ok, enhanced_ok]):
                print(f"\n🎉 ALL TESTS PASSED! Meta Threads integration is working!")
            else:
                print(f"\n⚠️  Some tests failed. Check the error messages above.")
        else:
            print(f"\n❌ API connection failed. Check your Meta credentials.")
    else:
        print(f"\n❌ Credentials not found. Please check your .env file.")

    print("=" * 60)
