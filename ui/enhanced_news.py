"""
Enhanced News UI Components
Provides rich, interactive news display with social media integration
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


def create_enhanced_news_feed(enhanced_news: Dict[str, List[Dict]]):
    """Create an enhanced news feed with multiple sources and rich UI"""
    
    st.subheader("📰 Enhanced News Feed")
    
    # Create tabs for different news sources
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📰 All News", 
        "🐦 Social Media", 
        "💬 Reddit", 
        "📊 Analyst Reports", 
        "📈 Sentiment Analysis"
    ])
    
    with tab1:
        display_all_news(enhanced_news)
    
    with tab2:
        display_social_media_news(enhanced_news.get("social_media", []))
    
    with tab3:
        display_reddit_news(enhanced_news.get("reddit_discussions", []))
    
    with tab4:
        display_analyst_reports(enhanced_news.get("analyst_reports", []))
    
    with tab5:
        display_sentiment_analysis(enhanced_news)


def display_all_news(enhanced_news: Dict[str, List[Dict]]):
    """Display all news in a unified feed"""
    
    # Combine all news sources
    all_news = []
    for source, items in enhanced_news.items():
        for item in items:
            item["source_type"] = source
            all_news.append(item)
    
    # Sort by date
    all_news.sort(key=lambda x: x.get('created_at', x.get('published_at', '')), reverse=True)
    
    # Display news cards
    for i, item in enumerate(all_news[:10]):  # Show top 10
        create_news_card(item, i)


def display_social_media_news(social_news: List[Dict]):
    """Display social media news with engagement metrics"""
    
    if not social_news:
        st.info("No social media mentions found")
        return
    
    st.write(f"**Found {len(social_news)} social media mentions**")
    
    for item in social_news:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{item.get('text', item.get('title', 'No title'))}**")
                st.write(f"👤 {item.get('author', 'Unknown')}")
                st.write(f"🕒 {format_timestamp(item.get('created_at', ''))}")
            
            with col2:
                # Engagement metrics
                if 'retweet_count' in item:
                    st.metric("Retweets", item.get('retweet_count', 0))
                if 'like_count' in item:
                    st.metric("Likes", item.get('like_count', 0))
                if 'score' in item:
                    st.metric("Score", item.get('score', 0))
                
                # Sentiment indicator
                sentiment = item.get('sentiment', 0)
                sentiment_color = get_sentiment_color(sentiment)
                st.markdown(f"**Sentiment:** {sentiment:.2f}")
                st.markdown(f"<div style='background-color: {sentiment_color}; padding: 5px; border-radius: 5px; text-align: center; color: white;'>Sentiment: {sentiment:.2f}</div>", unsafe_allow_html=True)
            
            if item.get('url'):
                st.link_button("View Original", item['url'])
            
            st.divider()


def display_reddit_news(reddit_news: List[Dict]):
    """Display Reddit discussions with community metrics"""
    
    if not reddit_news:
        st.info("No Reddit discussions found")
        return
    
    st.write(f"**Found {len(reddit_news)} Reddit discussions**")
    
    for item in reddit_news:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{item.get('title', 'No title')}**")
                st.write(f"📝 {item.get('content', '')[:200]}...")
                st.write(f"👤 {item.get('author', 'Unknown')} • r/{item.get('subreddit', 'unknown')}")
                st.write(f"🕒 {format_timestamp(item.get('created_at', ''))}")
            
            with col2:
                st.metric("Score", item.get('score', 0))
                st.metric("Comments", item.get('comments', 0))
                
                # Sentiment indicator
                sentiment = item.get('sentiment', 0)
                sentiment_color = get_sentiment_color(sentiment)
                st.markdown(f"<div style='background-color: {sentiment_color}; padding: 5px; border-radius: 5px; text-align: center; color: white;'>Sentiment: {sentiment:.2f}</div>", unsafe_allow_html=True)
            
            if item.get('url'):
                st.link_button("View on Reddit", item['url'])
            
            st.divider()


def display_analyst_reports(analyst_news: List[Dict]):
    """Display analyst reports with ratings and target prices"""
    
    if not analyst_news:
        st.info("No analyst reports found")
        return
    
    st.write(f"**Found {len(analyst_news)} analyst reports**")
    
    for item in analyst_news:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{item.get('title', 'No title')}**")
                st.write(f"📝 {item.get('content', '')[:200]}...")
                st.write(f"🏢 {item.get('analyst', 'Unknown')}")
                st.write(f"🕒 {format_timestamp(item.get('published_at', ''))}")
            
            with col2:
                rating = item.get('rating', 'N/A')
                rating_color = get_rating_color(rating)
                st.markdown(f"**Rating:** {rating}")
                st.markdown(f"<div style='background-color: {rating_color}; padding: 5px; border-radius: 5px; text-align: center; color: white;'>{rating}</div>", unsafe_allow_html=True)
            
            with col3:
                target_price = item.get('target_price', 'N/A')
                st.metric("Target Price", target_price)
                
                # Sentiment indicator
                sentiment = item.get('sentiment', 0)
                sentiment_color = get_sentiment_color(sentiment)
                st.markdown(f"<div style='background-color: {sentiment_color}; padding: 5px; border-radius: 5px; text-align: center; color: white;'>Sentiment: {sentiment:.2f}</div>", unsafe_allow_html=True)
            
            if item.get('url'):
                st.link_button("Read Full Report", item['url'])
            
            st.divider()


def display_sentiment_analysis(enhanced_news: Dict[str, List[Dict]]):
    """Display sentiment analysis across all news sources"""
    
    # Collect all sentiment data
    sentiment_data = []
    for source, items in enhanced_news.items():
        for item in items:
            if 'sentiment' in item:
                sentiment_data.append({
                    'source': source,
                    'sentiment': item['sentiment'],
                    'title': item.get('title', item.get('text', 'No title'))[:50]
                })
    
    if not sentiment_data:
        st.info("No sentiment data available")
        return
    
    # Create sentiment visualization
    df = pd.DataFrame(sentiment_data)
    
    # Overall sentiment metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_sentiment = df['sentiment'].mean()
        st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
    
    with col2:
        positive_count = len(df[df['sentiment'] > 0.1])
        st.metric("Positive Items", positive_count)
    
    with col3:
        negative_count = len(df[df['sentiment'] < -0.1])
        st.metric("Negative Items", negative_count)
    
    with col4:
        neutral_count = len(df[(df['sentiment'] >= -0.1) & (df['sentiment'] <= 0.1)])
        st.metric("Neutral Items", neutral_count)
    
    # Sentiment distribution chart
    fig = px.histogram(df, x='sentiment', color='source', 
                      title="Sentiment Distribution by Source",
                      labels={'sentiment': 'Sentiment Score', 'count': 'Number of Items'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment by source
    source_sentiment = df.groupby('source')['sentiment'].mean().reset_index()
    fig2 = px.bar(source_sentiment, x='source', y='sentiment',
                  title="Average Sentiment by Source",
                  labels={'source': 'News Source', 'sentiment': 'Average Sentiment'})
    st.plotly_chart(fig2, use_container_width=True)


def create_news_card(item: Dict, index: int):
    """Create a rich news card with enhanced formatting"""
    
    with st.container():
        # Header with sentiment indicator
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            title = item.get('title', item.get('text', 'No title'))
            st.write(f"**{title}**")
        
        with col2:
            source = item.get('source', 'Unknown')
            st.write(f"📰 {source}")
        
        with col3:
            sentiment = item.get('sentiment', 0)
            sentiment_color = get_sentiment_color(sentiment)
            st.markdown(f"<div style='background-color: {sentiment_color}; padding: 5px; border-radius: 5px; text-align: center; color: white;'>Sentiment: {sentiment:.2f}</div>", unsafe_allow_html=True)
        
        # Content and metadata
        content = item.get('content', item.get('description', ''))
        if content:
            st.write(content[:300] + "..." if len(content) > 300 else content)
        
        # Metadata row
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            author = item.get('author', 'Unknown')
            timestamp = format_timestamp(item.get('created_at', item.get('published_at', '')))
            st.write(f"👤 {author} • 🕒 {timestamp}")
        
        with col2:
            if 'retweet_count' in item:
                st.write(f"🔄 {item['retweet_count']} retweets")
            elif 'score' in item:
                st.write(f"⬆️ {item['score']} score")
        
        with col3:
            if item.get('url'):
                st.link_button("Read More", item['url'])
        
        st.divider()


def get_sentiment_color(sentiment: float) -> str:
    """Get color based on sentiment score"""
    if sentiment > 0.3:
        return "#4CAF50"  # Green for positive
    elif sentiment < -0.3:
        return "#F44336"  # Red for negative
    else:
        return "#FF9800"  # Orange for neutral


def get_rating_color(rating: str) -> str:
    """Get color based on analyst rating"""
    rating_lower = rating.lower()
    if 'buy' in rating_lower or 'strong buy' in rating_lower:
        return "#4CAF50"  # Green
    elif 'sell' in rating_lower or 'strong sell' in rating_lower:
        return "#F44336"  # Red
    elif 'hold' in rating_lower:
        return "#FF9800"  # Orange
    else:
        return "#9E9E9E"  # Gray


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        if timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
    except:
        pass
    return "Unknown time"
