"""
Main Streamlit Application
Portfolio Dashboard with real-time stock data
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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

    # Quick Analysis Options - Right after portfolio selection
    st.sidebar.subheader("📊 Quick Analysis")

    if st.sidebar.button("🌍 All Portfolios", use_container_width=True):
        from ui.consolidated_dashboard import display_consolidated_dashboard
        display_consolidated_dashboard()
        return

    if st.sidebar.button("💰 Dividends", use_container_width=True):
        from ui.dividend_dashboard import display_dividend_dashboard
        display_dividend_dashboard()
        return

    if st.sidebar.button("📱 Telegram", use_container_width=True):
        from ui.telegram_dashboard import display_telegram_dashboard
        display_telegram_dashboard()
        return

    # FII Dividend Analysis is automatically integrated
    st.sidebar.info("🏢 **FII Analysis**: Automatically shows when viewing FII portfolios or portfolios containing FIIs")

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

    # Portfolio Analysis Options
    st.subheader("📊 Portfolio Analysis")

    # Create a more compact layout with radio buttons
    analysis_option = st.radio(
        "Choose analysis type:",
        ["All Portfolios (Consolidated)", "Individual Portfolio", "Dividend Analysis (All Stocks)", "Telegram Monitor"],
        horizontal=True,
        index=0
    )

    if analysis_option == "All Portfolios (Consolidated)":
        from ui.consolidated_dashboard import display_consolidated_dashboard
        display_consolidated_dashboard()
        return
    elif analysis_option == "Dividend Analysis (All Stocks)":
        from ui.dividend_dashboard import display_dividend_dashboard
        display_dividend_dashboard()
        return
    elif analysis_option == "Telegram Monitor":
        from ui.telegram_dashboard import display_telegram_dashboard
        display_telegram_dashboard()
        return

    st.divider()

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

                # FII Dividend Analysis (if FII portfolio is selected or contains FIIs)
                has_fiis = any(ticker.endswith("11") for ticker in portfolio_stocks.keys())
                if selected_portfolio == "FII_B3" or has_fiis:
                    try:
                        from core.fii_dividend_analyzer import FIIDividendAnalyzer

                        st.subheader("🏢 FII Dividend Analysis")
                        st.info("ℹ️ **Data Source**: Using fallback data due to API limitations. For real-time data, check your API keys and rate limits.")

                        # Initialize FII analyzer
                        fii_analyzer = FIIDividendAnalyzer()

                        # Get FII portfolio analysis
                        with st.spinner("Analyzing FII dividends..."):
                            fii_analysis = fii_analyzer.analyze_portfolio_dividends()

                        if "error" not in fii_analysis:
                            # Display FII summary metrics
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric("Total FIIs", fii_analysis["total_fiis"])
                            with col2:
                                st.metric("Monthly Income", f"R$ {fii_analysis['total_monthly_income']:,.2f}")
                            with col3:
                                st.metric("Annual Income", f"R$ {fii_analysis['total_annual_income']:,.2f}")
                            with col4:
                                st.metric("Average Yield", f"{fii_analysis['average_yield']:.2f}%")

                            # Display FII comparison table
                            try:
                                comparison_df = fii_analyzer.compare_fii_performance()
                                if not comparison_df.empty:
                                    st.subheader("📊 FII Performance Comparison")
                                    st.dataframe(comparison_df, width='stretch')
                            except Exception as e:
                                st.warning(f"Could not generate FII comparison table: {e}")

                            # Top dividend yielders
                            st.subheader("🏆 Top Dividend Yielders")
                            top_performers = fii_analyzer.get_top_dividend_yielders(5)

                            if top_performers:
                                for i, fii in enumerate(top_performers, 1):
                                    with st.expander(f"{i}. {fii['ticker']} - {fii['dividend_yield']:.2f}% Yield"):
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Monthly Income", f"R$ {fii['monthly_income']:.2f}")
                                        with col2:
                                            st.metric("Annual Income", f"R$ {fii['annual_income']:,.2f}")
                                        with col3:
                                            st.metric("Total Investment", f"R$ {fii['total_investment']:,.2f}")

                            # Income forecast
                            st.subheader("💰 Income Forecast")
                            forecast = fii_analyzer.get_dividend_income_forecast(12)

                            if "error" not in forecast:
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.metric("Monthly Income", f"R$ {forecast['monthly_income']:.2f}")
                                    st.metric("12-Month Forecast", f"R$ {forecast['total_forecast']:,.2f}")

                                with col2:
                                    # Create forecast chart
                                    import pandas as pd
                                    import plotly.express as px

                                    forecast_df = pd.DataFrame(forecast["monthly_breakdown"])
                                    fig = px.line(
                                        forecast_df,
                                        x="month",
                                        y="cumulative",
                                        title="Cumulative Dividend Income Forecast",
                                        labels={"month": "Month", "cumulative": "Cumulative Income (R$)"}
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error(f"❌ FII Analysis Error: {fii_analysis['error']}")

                    except Exception as e:
                        st.warning(f"FII dividend analysis error: {e}")
                        st.info("FII analysis is available but may have limited functionality due to API limitations.")

                # Quick FII Summary (for any portfolio with FIIs)
                elif has_fiis:
                    try:
                        from core.fii_dividend_analyzer import FIIDividendAnalyzer

                        st.subheader("🏢 FII Quick Summary")
                        fii_analyzer = FIIDividendAnalyzer()

                        # Get only FIIs from current portfolio
                        fii_tickers = [ticker for ticker in portfolio_stocks.keys() if ticker.endswith("11")]

                        if fii_tickers:
                            st.info(f"Found {len(fii_tickers)} FIIs in this portfolio: {', '.join(fii_tickers)}")

                            # Quick analysis for FIIs in this portfolio
                            total_fii_investment = 0
                            total_fii_income = 0

                            for ticker in fii_tickers:
                                position = portfolio_stocks[ticker]
                                quantity = position.get("quantity", 0)
                                avg_price = position.get("avg_price", 0)
                                investment = quantity * avg_price
                                total_fii_investment += investment

                                # Estimate income using static yield
                                from app.config import BRAZILIAN_DIVIDEND_YIELDS
                                yield_pct = BRAZILIAN_DIVIDEND_YIELDS.get(ticker, 7.0)
                                monthly_income = (yield_pct / 100) * avg_price * quantity / 12
                                total_fii_income += monthly_income

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("FII Investment", f"R$ {total_fii_investment:,.2f}")
                            with col2:
                                st.metric("Monthly Income", f"R$ {total_fii_income:.2f}")
                            with col3:
                                st.metric("Annual Income", f"R$ {total_fii_income * 12:,.2f}")

                            st.info("💡 **Tip**: Select 'FII_B3' portfolio for detailed FII dividend analysis!")

                    except Exception as e:
                        st.warning(f"Quick FII analysis error: {e}")

    # Enhanced News Section (Free Sources Only)
    try:
        from core.social_fetcher import fetch_enhanced_portfolio_news
        from ui.enhanced_news import create_enhanced_news_feed

        # Fetch enhanced news from free sources only
        enhanced_news = fetch_enhanced_portfolio_news(list(portfolio_stocks.keys()))

        if any(enhanced_news.values()):
            create_enhanced_news_feed(enhanced_news)
        else:
            # Fallback to traditional news if enhanced news fails
            from core.data_fetcher import fetch_portfolio_news
            news_data = fetch_portfolio_news(list(portfolio_stocks.keys()))
            if news_data:
                st.subheader("📰 Latest News")
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
        st.warning(f"Enhanced news fetching error: {e}")
        # Fallback to basic news
        try:
            from core.data_fetcher import fetch_portfolio_news
            news_data = fetch_portfolio_news(list(portfolio_stocks.keys()))
            if news_data:
                st.subheader("📰 Latest News")
                for article in news_data[:5]:
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
        except Exception as fallback_error:
            st.warning(f"News fetching error: {fallback_error}")

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

if __name__ == "__main__":
    main()
