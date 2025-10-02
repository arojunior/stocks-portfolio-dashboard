"""
Main Streamlit Application
Portfolio Dashboard with real-time stock data
"""

import streamlit as st
import os
from core.portfolio_manager import PortfolioManager
from core.data_fetcher import fetch_stock_data
from core.analytics import (
    calculate_portfolio_metrics,
    create_portfolio_dataframe,
    calculate_risk_metrics,
    calculate_sector_diversification,
    generate_portfolio_summary
)
from ui.components import (
    create_portfolio_sidebar,
    create_portfolio_metrics,
    create_portfolio_table,
    create_portfolio_charts
)

# Page configuration
st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    st.title("📊 Portfolio Dashboard")
    st.markdown("Real-time stock portfolio analysis and tracking")

    # Initialize portfolio manager
    portfolio_manager = PortfolioManager()

    # Create sidebar
    selected_portfolio = create_portfolio_sidebar(portfolio_manager)

    # Cache control section
    st.sidebar.header("Cache Control")
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("ℹ️ Cache Info"):
        st.sidebar.info("Cache TTL: 30 minutes\nData sources: Multiple APIs with fallbacks")

    # Refresh settings
    st.sidebar.header("Refresh Settings")
    auto_refresh = st.sidebar.checkbox("Auto-refresh data", value=False)
    if auto_refresh:
        refresh_interval = st.sidebar.selectbox(
            "Refresh interval",
            ["5 minutes", "15 minutes", "30 minutes", "1 hour"],
            index=2
        )
        st.sidebar.info(f"Auto-refresh every {refresh_interval}")

    # API usage warning
    st.sidebar.warning("⚠️ Free API limits apply. Use refresh wisely.")

    # Manual refresh button
    if st.sidebar.button("🔄 Manual Refresh"):
        st.cache_data.clear()
        st.rerun()

    # Main dashboard area
    if selected_portfolio:
        portfolio_stocks = portfolio_manager.get_portfolio_stocks(selected_portfolio)

        if portfolio_stocks:
            # Determine market for data fetching
            market_type = portfolio_manager.get_market_from_portfolio_name(selected_portfolio)

            # Fetch stock data with caching
            stock_data = {}

            # Show loading message
            with st.spinner("🔄 Loading portfolio data..."):
                for ticker in portfolio_stocks.keys():
                    data = fetch_stock_data(ticker, market_type, force_refresh=False)
                    if data:
                        stock_data[ticker] = data

            # Create portfolio dataframe
            df = create_portfolio_dataframe(portfolio_stocks, stock_data)

            # Display portfolio content
            if not df.empty:
                # Calculate portfolio metrics
                portfolio_data = df.to_dict('records')
                metrics = calculate_portfolio_metrics(portfolio_data)

                # Display portfolio metrics
                create_portfolio_metrics(metrics)

                # Display portfolio table
                create_portfolio_table(df)

                # Display charts
                create_portfolio_charts(portfolio_data, metrics)

                # Display portfolio summary
                st.subheader("📋 Portfolio Summary")
                summary = generate_portfolio_summary(portfolio_data, metrics)
                st.markdown(summary)

                # Risk analysis
                risk_metrics = calculate_risk_metrics(portfolio_data)
                if risk_metrics:
                    st.subheader("⚠️ Risk Analysis")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Risk Level", risk_metrics.get("risk_level", "Unknown"))
                    with col2:
                        st.metric("Volatility", f"{risk_metrics.get('volatility', 0):.2f}%")
                    with col3:
                        st.metric("Mean Return", f"{risk_metrics.get('mean_return', 0):.2f}%")

                # Sector diversification
                sectors = metrics.get("sectors", {})
                if sectors:
                    diversification = calculate_sector_diversification(sectors)
                    st.subheader("🏢 Sector Diversification")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Diversification Score", f"{diversification.get('diversification_score', 0):.0f}/100")
                    with col2:
                        st.metric("Concentration Risk", diversification.get("concentration_risk", "Unknown"))

                # News Section
                st.subheader("📰 Latest News")
                try:
                    from core.data_fetcher import fetch_portfolio_news
                    news_data = fetch_portfolio_news(list(portfolio_stocks.keys()))
                    if news_data:
                        for article in news_data[:5]:  # Show top 5 articles
                            # Add sentiment indicator
                            sentiment = article.get('sentiment', 0)
                            sentiment_emoji = "😊" if sentiment > 0.1 else "😐" if sentiment > -0.1 else "😞"

                            with st.expander(f"{sentiment_emoji} {article.get('title', 'No title')}"):
                                st.write(f"**Source:** {article.get('source', 'Unknown')}")
                                st.write(f"**Published:** {article.get('publishedAt', 'Unknown')}")
                                st.write(f"**Description:** {article.get('description', 'No description')}")
                                if sentiment != 0:
                                    st.write(f"**Sentiment:** {sentiment:.2f}")
                                if article.get('url'):
                                    st.write(f"**Link:** {article['url']}")
                    else:
                        st.info("No news available at the moment")
                except Exception as e:
                    st.warning(f"News fetching error: {e}")

                # AI Analysis Section
                st.subheader("🤖 AI Portfolio Analysis")
                try:
                    from ai.ollama_client import OllamaClient
                    from ai.gemini_client import GeminiClient

                    # Try Ollama first (local)
                    ollama_client = OllamaClient()
                    if ollama_client.available:
                        with st.spinner("🤖 Analyzing portfolio with Ollama..."):
                            analysis = ollama_client.analyze_portfolio(portfolio_data, metrics)
                            if analysis:
                                st.success("✅ AI Analysis Complete")
                                st.markdown(analysis)
                            else:
                                st.warning("Ollama analysis failed")
                    else:
                        # Fallback to Gemini
                        gemini_client = GeminiClient()
                        if gemini_client.available:
                            with st.spinner("🤖 Analyzing portfolio with Gemini..."):
                                analysis = gemini_client.analyze_portfolio(portfolio_data, metrics)
                                if analysis:
                                    st.success("✅ AI Analysis Complete")
                                    st.markdown(analysis)
                                else:
                                    st.warning("Gemini analysis failed")
                        else:
                            st.info("💡 No AI services available. Install Ollama or configure Gemini API key for AI analysis.")
                except Exception as e:
                    st.warning(f"AI analysis error: {e}")
            else:
                st.error("No data available for portfolio stocks")
        else:
            st.info("No stocks in this portfolio. Add stocks using the sidebar.")
    else:
        st.info("Please select a portfolio from the sidebar.")

if __name__ == "__main__":
    main()
