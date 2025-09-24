"""
Main Streamlit Application
Portfolio Management Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import PAGE_CONFIG
from core.portfolio_manager import PortfolioManager
from core.data_fetcher import fetch_stock_data
from core.analytics import (
    calculate_portfolio_metrics,
    create_portfolio_dataframe,
    calculate_sector_diversification,
    generate_portfolio_summary,
    calculate_risk_metrics
)
from ui.components import (
    create_portfolio_sidebar,
    create_portfolio_table,
    create_portfolio_charts,
    create_portfolio_metrics
)


def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)

    # Initialize portfolio manager
    if "portfolio_manager" not in st.session_state:
        st.session_state.portfolio_manager = PortfolioManager()
        # Migrate old portfolio structure if needed
        st.session_state.portfolio_manager.migrate_old_portfolio_structure()

    portfolio_manager = st.session_state.portfolio_manager

    # Main title
    st.title("📈 Stock Portfolio Management Dashboard")
    st.markdown("*Replace your Google Spreadsheet with real-time portfolio tracking*")
    st.markdown("---")

    # Configurable refresh settings
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Data Refresh")

    refresh_enabled = st.sidebar.checkbox("Enable auto-refresh", value=False)

    if refresh_enabled:
        refresh_options = {
            "5 minutes": 300,
            "10 minutes": 600,
            "15 minutes": 900,
            "30 minutes": 1800,
            "1 hour": 3600,
        }

        selected_refresh = st.sidebar.selectbox(
            "Refresh interval",
            options=list(refresh_options.keys()),
            index=2,  # Default to 15 minutes
            help="Choose how often to refresh stock data. Longer intervals preserve API limits.",
        )

        refresh_seconds = refresh_options[selected_refresh]

        st.sidebar.info(f"📊 Next refresh in {selected_refresh}")

        # Show API usage warning for short intervals
        if refresh_seconds < 900:  # Less than 15 minutes
            st.sidebar.warning("⚠️ Short refresh intervals may exhaust API limits quickly")

        import time
        time.sleep(refresh_seconds)
        st.rerun()
    else:
        st.sidebar.info("💡 Enable auto-refresh to automatically update stock prices")

    # Manual refresh button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Now", help="Manually refresh stock data"):
        st.cache_data.clear()
        st.session_state['force_background_refresh'] = True
        st.sidebar.success("✅ Cache cleared! Data will be refreshed in background.")
        st.rerun()

    # Create sidebar
    selected_portfolio = create_portfolio_sidebar(portfolio_manager)

    # Main dashboard area
    if selected_portfolio:
        portfolio_stocks = portfolio_manager.get_portfolio_stocks(selected_portfolio)

        if portfolio_stocks:
            # Determine market for data fetching
            market_type = portfolio_manager.get_market_from_portfolio_name(selected_portfolio)

            # Create portfolio dataframe with smart caching
            # First, try to get cached data immediately
            cached_stock_data = {}
            fresh_data_needed = []

            # Show immediate status
            st.info("🔄 Loading portfolio data...")

            for ticker in portfolio_stocks.keys():
                # Try to get cached data first (no spinner, immediate)
                data = fetch_stock_data(ticker, market_type, force_refresh=False)
                if data:
                    cached_stock_data[ticker] = data
                else:
                    fresh_data_needed.append(ticker)

            if cached_stock_data:
                st.success("✅ Showing cached data")
                # Show background refresh indicator
                refresh_placeholder = st.empty()
                with refresh_placeholder.container():
                    st.info("🔄 Refreshing data in background...")

                # Use cached data for immediate display
                stock_data = cached_stock_data.copy()

                # Fetch fresh data in background for missing or all stocks
                if fresh_data_needed or st.session_state.get('force_background_refresh', False):
                    for ticker in (fresh_data_needed if fresh_data_needed else portfolio_stocks.keys()):
                        try:
                            fresh_data = fetch_stock_data(ticker, market_type, force_refresh=True)
                            if fresh_data:
                                stock_data[ticker] = fresh_data
                        except Exception as e:
                            st.warning(f"Background refresh failed for {ticker}: {e}")

                    # Clear the refresh indicator
                    refresh_placeholder.empty()
                    st.success("✅ Data refreshed in background!")
                    st.session_state['force_background_refresh'] = False

                # Create portfolio dataframe with cached data
                df = create_portfolio_dataframe(portfolio_stocks, stock_data)
                
                # Display portfolio content with cached data
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
                else:
                    st.error("No data available for portfolio stocks")
            else:
                # No cached data, show spinner for initial load
                with st.spinner("Fetching real-time stock data..."):
                    # Show data source status
                    has_twelve_data = bool(os.getenv("TWELVE_DATA_API_KEY"))
                    has_alpha_vantage = bool(os.getenv("ALPHA_VANTAGE_API_KEY"))

                    if has_twelve_data or has_alpha_vantage:
                        data_source_info = "Using "
                        if has_twelve_data:
                            data_source_info += "Twelve Data"
                        if has_alpha_vantage:
                            data_source_info += (
                                " + Alpha Vantage" if has_twelve_data else "Alpha Vantage"
                            )
                        data_source_info += " APIs"
                    else:
                        data_source_info = "Using Yahoo Finance (may be rate limited)"

                    # Show data source and last update time
                    current_time = datetime.now().strftime("%H:%M:%S")
                    st.info(f"📊 {data_source_info} | Last updated: {current_time}")

                    # Use progressive loading for large portfolios
                    num_stocks = len(portfolio_stocks)
                    if num_stocks > 8:
                        st.warning(f"⚠️ Large portfolio detected ({num_stocks} stocks). Using progressive loading...")

                    # Fetch stock data
                    stock_data = {}
                    progress_bar = st.progress(0)

                    for i, ticker in enumerate(portfolio_stocks.keys()):
                        try:
                            data = fetch_stock_data(ticker, market_type)
                            if data:
                                stock_data[ticker] = data
                        except Exception as e:
                            st.error(f"Error fetching data for {ticker}: {e}")

                        progress_bar.progress((i + 1) / len(portfolio_stocks))

                    progress_bar.empty()

                    # Create portfolio dataframe
                    df = create_portfolio_dataframe(portfolio_stocks, stock_data)

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
                    else:
                        st.error("No data available for portfolio stocks")
        else:
            st.info("No stocks in this portfolio. Add stocks using the sidebar.")
    else:
        st.info("Please select a portfolio from the sidebar.")


if __name__ == "__main__":
    main()
