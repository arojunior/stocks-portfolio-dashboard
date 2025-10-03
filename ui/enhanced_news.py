"""
Enhanced News UI Components
Uses only free data sources - no paid APIs or mock data
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
from datetime import datetime


def create_enhanced_news_feed(enhanced_news: Dict[str, List[Dict]]):
    """Create enhanced news feed using only free data sources"""

    if not any(enhanced_news.values()):
        st.info("No enhanced news available at the moment")
        return

    # Create tabs for different news categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📰 All News", "📊 Market Analysis", "💰 Earnings", "⭐ Analyst Ratings", "🧵 Social Media"])
    
    with tab1:
        display_all_news(enhanced_news)
    
    with tab2:
        display_market_analysis(enhanced_news.get("market_analysis", []))
    
    with tab3:
        display_earnings_news(enhanced_news.get("earnings_news", []))
    
    with tab4:
        display_analyst_ratings(enhanced_news.get("analyst_ratings", []))
    
    with tab5:
        display_social_media(enhanced_news.get("social_media", []))


def display_all_news(enhanced_news: Dict[str, List[Dict]]):
    """Display all news in a unified feed"""
    all_news = []
    for category, items in enhanced_news.items():
        all_news.extend(items)

    if not all_news:
        st.info("No news available")
        return

    # Sort by date (newest first)
    all_news.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)

    st.subheader(f"📰 Latest News ({len(all_news)} articles)")

    for i, article in enumerate(all_news[:10]):  # Show top 10
        with st.expander(f"📄 {article.get('title', 'No title')}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Source:** {article.get('source', 'Unknown')}")
                st.write(f"**Published:** {format_date(article.get('publishedAt', ''))}")
                if article.get('description'):
                    st.write(f"**Description:** {article['description']}")

            with col2:
                if article.get('url'):
                    st.link_button("Read More", article['url'])

            # Add sentiment indicator if available
            sentiment = article.get('sentiment', 0)
            if sentiment != 0:
                sentiment_emoji = "😊" if sentiment > 0.1 else "😐" if sentiment > -0.1 else "😞"
                st.write(f"**Sentiment:** {sentiment_emoji} {sentiment:.2f}")


def display_market_analysis(market_news: List[Dict]):
    """Display market analysis news"""
    if not market_news:
        st.info("No market analysis available")
        return

    st.subheader(f"📊 Market Analysis ({len(market_news)} articles)")

    for article in market_news[:5]:
        with st.expander(f"📈 {article.get('title', 'No title')}"):
            st.write(f"**Source:** {article.get('source', 'Unknown')}")
            st.write(f"**Published:** {format_date(article.get('publishedAt', ''))}")
            if article.get('description'):
                st.write(f"**Analysis:** {article['description']}")
            if article.get('url'):
                st.link_button("Read Full Analysis", article['url'])


def display_earnings_news(earnings_news: List[Dict]):
    """Display earnings-related news"""
    if not earnings_news:
        st.info("No earnings news available")
        return

    st.subheader(f"💰 Earnings News ({len(earnings_news)} articles)")

    for article in earnings_news[:5]:
        with st.expander(f"💼 {article.get('title', 'No title')}"):
            st.write(f"**Source:** {article.get('source', 'Unknown')}")
            st.write(f"**Published:** {format_date(article.get('publishedAt', ''))}")
            if article.get('description'):
                st.write(f"**Details:** {article['description']}")
            if article.get('url'):
                st.link_button("Read Full Report", article['url'])


def display_analyst_ratings(analyst_news: List[Dict]):
    """Display analyst ratings and reports"""
    if not analyst_news:
        st.info("No analyst ratings available")
        return
    
    st.subheader(f"⭐ Analyst Ratings ({len(analyst_news)} reports)")
    
    for article in analyst_news[:5]:
        with st.expander(f"📋 {article.get('title', 'No title')}"):
            st.write(f"**Source:** {article.get('source', 'Unknown')}")
            st.write(f"**Published:** {format_date(article.get('publishedAt', ''))}")
            if article.get('description'):
                st.write(f"**Rating:** {article['description']}")
            if article.get('url'):
                st.link_button("Read Full Report", article['url'])


def display_social_media(social_news: List[Dict]):
    """Display social media mentions from Threads"""
    if not social_news:
        st.info("No social media mentions available")
        st.info("💡 **Meta Threads Integration**: To enable Threads data, you'll need to:")
        st.markdown("""
        1. **Create a Meta Developer Account**: Visit [developers.facebook.com](https://developers.facebook.com/)
        2. **Set up a Threads App**: Create a new app with 'Access the Threads API' use case
        3. **Configure OAuth**: Set up authentication to get access tokens
        4. **Add API Key**: Add your Meta app credentials to your `.env` file
        """)
        return
    
    st.subheader(f"🧵 Social Media Mentions ({len(social_news)} posts)")
    
    for post in social_news[:5]:
        with st.expander(f"🧵 {post.get('text', 'No content')[:50]}..."):
            st.write(f"**Author:** {post.get('author', 'Unknown')}")
            st.write(f"**Platform:** {post.get('source', 'Threads')}")
            st.write(f"**Posted:** {format_date(post.get('created_at', ''))}")
            if post.get('text'):
                st.write(f"**Content:** {post['text']}")
            if post.get('url'):
                st.link_button("View on Threads", post['url'])
            
            # Show engagement metrics if available
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Likes", post.get('like_count', 0))
            with col2:
                st.metric("Replies", post.get('reply_count', 0))
            with col3:
                st.metric("Reposts", post.get('repost_count', 0))


def create_sentiment_chart(news_items: List[Dict]):
    """Create sentiment analysis chart using free text analysis"""
    if not news_items:
        return None

    # Simple sentiment analysis using keyword matching
    positive_keywords = ["up", "rise", "gain", "profit", "beat", "exceed", "strong", "bullish"]
    negative_keywords = ["down", "fall", "loss", "miss", "weak", "bearish", "decline", "drop"]

    sentiment_data = {"Positive": 0, "Neutral": 0, "Negative": 0}

    for item in news_items:
        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        text = f"{title} {description}"

        positive_score = sum(1 for keyword in positive_keywords if keyword in text)
        negative_score = sum(1 for keyword in negative_keywords if keyword in text)

        if positive_score > negative_score:
            sentiment_data["Positive"] += 1
        elif negative_score > positive_score:
            sentiment_data["Negative"] += 1
        else:
            sentiment_data["Neutral"] += 1

    # Create pie chart
    fig = px.pie(
        values=list(sentiment_data.values()),
        names=list(sentiment_data.keys()),
        title="News Sentiment Distribution",
        color_discrete_map={
            "Positive": "#28a745",
            "Neutral": "#ffc107",
            "Negative": "#dc3545"
        }
    )

    return fig


def format_date(date_str: str) -> str:
    """Format date string for display"""
    if not date_str:
        return "Unknown"

    try:
        # Handle different date formats
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, '%Y-%m-%d')

        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str
