"""
UI Components Module
Reusable Streamlit components for the portfolio dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
from datetime import datetime
from app.config import MARKET_CONFIGS


def create_portfolio_sidebar(portfolio_manager):
    """Create the portfolio management sidebar"""
    st.sidebar.header("Portfolio Management")

    portfolio_names = portfolio_manager.get_portfolio_names()

    # Portfolio selection
    st.sidebar.subheader("Select Portfolio")
    selected_portfolio = st.sidebar.selectbox(
        "Choose Portfolio",
        options=portfolio_names,
        index=0 if portfolio_names else None
    )

    # Add new portfolio
    st.sidebar.subheader("Create New Portfolio")

    # Portfolio creation with market selection
    col1, col2 = st.sidebar.columns(2)
    with col1:
        market_selection = st.selectbox("Market", ["Brazilian", "US"], key="market_select")
    with col2:
        exchange_selection = st.selectbox(
            "Exchange",
            MARKET_CONFIGS[market_selection]["exchanges"],
            key="exchange_select"
        )

    new_portfolio_name = st.sidebar.text_input("Portfolio Name (optional)")
    if st.sidebar.button("Create Portfolio"):
        if new_portfolio_name:
            portfolio_key = new_portfolio_name
        else:
            portfolio_key = f"{market_selection}_{exchange_selection}"

        if portfolio_manager.create_portfolio(portfolio_key, market_selection, exchange_selection):
            st.sidebar.success(f"✅ Created portfolio: {portfolio_key}")
            st.rerun()
        else:
            st.sidebar.error("Portfolio already exists!")

    # Add stock to portfolio
    if selected_portfolio:
        st.sidebar.subheader("Add Stock")

        col1, col2 = st.sidebar.columns(2)
        with col1:
            ticker = st.sidebar.text_input("Ticker", key="ticker_input")
        with col2:
            quantity = st.sidebar.number_input("Quantity", min_value=1, value=1, key="quantity_input")

        avg_price = st.sidebar.number_input("Average Price", min_value=0.01, value=0.01, step=0.01, key="price_input")

        if st.sidebar.button("Add Stock"):
            if ticker and quantity and avg_price:
                portfolio_manager.add_stock(selected_portfolio, ticker, quantity, avg_price)
                st.sidebar.success(f"✅ Added {quantity} shares of {ticker}")
                st.rerun()
            else:
                st.sidebar.error("Please fill in all fields")

    return selected_portfolio


def create_portfolio_table(df: pd.DataFrame):
    """Create the portfolio table display"""
    st.subheader("📊 Portfolio Holdings")

    # Filter out internal calculation columns (those starting with _)
    display_columns = [col for col in df.columns if not col.startswith('_')]
    display_df = df[display_columns]

    # Style the dataframe - disable formatting to avoid errors
    styled_df = display_df

    st.dataframe(styled_df, width='stretch', height=400)

    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Portfolio Data",
        data=csv,
        file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


def create_portfolio_metrics(metrics: Dict):
    """Create portfolio metrics display"""
    st.subheader("📈 Portfolio Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Value",
            f"${metrics.get('total_value', 0):,.2f}",
            f"{metrics.get('total_gain_loss', 0):,.2f}"
        )

    with col2:
        st.metric(
            "Total Return",
            f"{metrics.get('total_gain_loss_percent', 0):.2f}%",
            f"${metrics.get('total_gain_loss', 0):,.2f}"
        )

    with col3:
        st.metric(
            "Annual Dividends",
            f"${metrics.get('total_annual_dividends', 0):,.2f}",
            f"{metrics.get('portfolio_dividend_yield', 0):.2f}% yield"
        )

    with col4:
        st.metric(
            "Number of Stocks",
            f"{metrics.get('num_stocks', 0)}",
            f"Best: {metrics.get('best_performer', {}).get('ticker', 'N/A')}"
        )


def create_portfolio_charts(portfolio_data: List[Dict], metrics: Dict):
    """Create portfolio visualization charts"""
    st.subheader("📊 Portfolio Visualizations")

    # Portfolio composition pie chart
    if portfolio_data:
        df = pd.DataFrame(portfolio_data)

        # Sector composition
        if 'sector' in df.columns:
            sector_counts = df['sector'].value_counts()

            col1, col2 = st.columns(2)

            with col1:
                # Sector pie chart
                fig_sector = px.pie(
                    values=sector_counts.values,
                    names=sector_counts.index,
                    title="Portfolio by Sector"
                )
                st.plotly_chart(fig_sector, width='stretch')

            with col2:
                # Value by sector
                sector_values = df.groupby('sector')['total_value'].sum().sort_values(ascending=True)
                fig_value = px.bar(
                    x=sector_values.values,
                    y=sector_values.index,
                    orientation='h',
                    title="Portfolio Value by Sector"
                )
                st.plotly_chart(fig_value, width='stretch')

        # Performance chart
        if len(portfolio_data) > 1:
            st.subheader("📈 Stock Performance")

            # Sort by gain/loss percentage
            df_sorted = df.sort_values('gain_loss_percent', ascending=True)

            fig_performance = px.bar(
                df_sorted,
                x='Ticker',
                y='gain_loss_percent',
                title="Stock Performance (Gain/Loss %)",
                color='gain_loss_percent',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            fig_performance.update_layout(
                xaxis_tickangle=-45,
                showlegend=False
            )
            st.plotly_chart(fig_performance, width='stretch')

        # Dividend analysis
        dividend_stocks = df[df['dividend_yield'] > 0]
        if not dividend_stocks.empty:
            st.subheader("💰 Dividend Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # Dividend yield by stock
                fig_dividend = px.bar(
                    dividend_stocks,
                    x='Ticker',
                    y='dividend_yield',
                    title="Dividend Yield by Stock"
                )
                st.plotly_chart(fig_dividend, width='stretch')

            with col2:
                # Annual dividend income by stock
                fig_income = px.bar(
                    dividend_stocks,
                    x='Ticker',
                    y='annual_dividend',
                    title="Annual Dividend Income by Stock"
                )
                st.plotly_chart(fig_income, width='stretch')


def create_risk_analysis(risk_metrics: Dict):
    """Create risk analysis display"""
    if not risk_metrics:
        return

    st.subheader("⚠️ Risk Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        risk_level = risk_metrics.get("risk_level", "Unknown")
        color = "red" if risk_level == "High" else "orange" if risk_level == "Medium" else "green"
        st.metric("Risk Level", risk_level)

    with col2:
        volatility = risk_metrics.get("volatility", 0)
        st.metric("Volatility", f"{volatility:.2f}%")

    with col3:
        mean_return = risk_metrics.get("mean_return", 0)
        st.metric("Mean Return", f"{mean_return:.2f}%")


def create_sector_analysis(sectors: Dict):
    """Create sector analysis display"""
    if not sectors:
        return

    st.subheader("🏢 Sector Analysis")

    # Sector diversification metrics
    diversification = calculate_sector_diversification(sectors)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Diversification Score", f"{diversification.get('diversification_score', 0):.0f}/100")

    with col2:
        st.metric("Concentration Risk", diversification.get("concentration_risk", "Unknown"))

    # Sector breakdown table
    sector_df = pd.DataFrame([
        {
            "Sector": sector,
            "Count": data.get("count", 0),
            "Value": f"${data.get('value', 0):,.2f}",
            "Percentage": f"{data.get('percentage', 0):.1f}%"
        }
        for sector, data in sectors.items()
    ])

    st.dataframe(sector_df, width='stretch')
