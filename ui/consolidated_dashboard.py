"""
Consolidated Portfolio Dashboard
Streamlit interface for viewing all portfolios together
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.consolidated_analyzer import ConsolidatedAnalyzer


def display_consolidated_dashboard():
    """Main consolidated dashboard interface"""
    st.title("🌍 Consolidated Portfolio Dashboard")
    st.markdown("Complete overview of all your portfolios across all markets")

    # Initialize analyzer
    analyzer = ConsolidatedAnalyzer()

    # Get consolidated data
    with st.spinner("🔄 Loading consolidated portfolio data..."):
        consolidated_data = analyzer.get_consolidated_data()
        consolidated_df = analyzer.get_consolidated_stock_data()
        metrics = analyzer.get_consolidated_metrics()
        fii_analysis = analyzer.get_fii_consolidated_analysis()

    if consolidated_data["total_stocks"] == 0:
        st.error("❌ No portfolio data found")
        return

    # Display consolidated summary
    display_consolidated_summary(consolidated_data, metrics, fii_analysis)

    # Display consolidated table
    display_consolidated_table(consolidated_df)

    # Display charts
    display_consolidated_charts(analyzer, metrics, consolidated_df)

    # Display detailed analysis
    display_detailed_analysis(consolidated_df, metrics)


def display_consolidated_summary(consolidated_data, metrics, fii_analysis):
    """Display consolidated portfolio summary"""
    st.subheader("📊 Portfolio Summary")

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Portfolios",
            consolidated_data["total_portfolios"],
            help="Number of portfolio categories"
        )

    with col2:
        st.metric(
            "Total Stocks",
            consolidated_data["total_stocks"],
            help="Total number of stocks across all portfolios"
        )

    with col3:
        st.metric(
            "Total Investment",
            f"R$ {consolidated_data['total_investment']:,.2f}",
            help="Total amount invested across all portfolios"
        )

    with col4:
        if metrics:
            st.metric(
                "Total Gain/Loss",
                f"R$ {metrics['total_gain_loss']:,.2f}",
                delta=f"{metrics['total_gain_loss_percent']:.2f}%",
                help="Total gain/loss across all portfolios"
            )

    # Portfolio breakdown
    st.subheader("🏢 Portfolio Breakdown")
    portfolio_cols = st.columns(len(consolidated_data["portfolios"]))

    for i, (portfolio_name, portfolio_data) in enumerate(consolidated_data["portfolios"].items()):
        with portfolio_cols[i]:
            st.metric(
                portfolio_name,
                f"R$ {portfolio_data['total_investment']:,.2f}",
                f"{portfolio_data['stock_count']} stocks"
            )

    # FII dividend summary (if applicable)
    if fii_analysis["fii_count"] > 0:
        st.subheader("🏢 FII Dividend Summary")
        fii_col1, fii_col2, fii_col3, fii_col4 = st.columns(4)

        with fii_col1:
            st.metric("FIIs", fii_analysis["fii_count"])
        with fii_col2:
            st.metric("Monthly Income", f"R$ {fii_analysis['monthly_income']:.2f}")
        with fii_col3:
            st.metric("Annual Income", f"R$ {fii_analysis['annual_income']:,.2f}")
        with fii_col4:
            st.metric("Average Yield", f"{fii_analysis['average_yield']:.2f}%")


def display_consolidated_table(consolidated_df):
    """Display consolidated stock table"""
    st.subheader("📋 All Stocks Overview")

    if not consolidated_df.empty:
        # Format the dataframe for display
        display_df = consolidated_df.copy()
        display_df["Avg Price"] = display_df["Avg Price"].apply(lambda x: f"R$ {x:.2f}")
        display_df["Current Price"] = display_df["Current Price"].apply(lambda x: f"R$ {x:.2f}")
        display_df["Total Investment"] = display_df["Total Investment"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["Current Value"] = display_df["Current Value"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["Gain/Loss"] = display_df["Gain/Loss"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["Gain/Loss %"] = display_df["Gain/Loss %"].apply(lambda x: f"{x:.2f}%")
        display_df["Change %"] = display_df["Change %"].apply(lambda x: f"{x:.2f}%")
        display_df["Dividend Yield"] = display_df["Dividend Yield"].apply(lambda x: f"{x:.2f}%")

        st.dataframe(display_df, width='stretch')
    else:
        st.info("No stock data available")


def display_consolidated_charts(analyzer, metrics, consolidated_df):
    """Display consolidated charts"""
    st.subheader("📈 Portfolio Analysis Charts")

    # Create tabs for different chart types
    tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Distribution", "Currency Distribution", "Sector Analysis", "Performance"])

    with tab1:
        st.subheader("🥧 Portfolio Distribution")
        portfolio_chart = analyzer.create_portfolio_distribution_chart(metrics)
        st.plotly_chart(portfolio_chart, use_container_width=True)

    with tab2:
        st.subheader("💱 Currency Distribution")
        currency_chart = analyzer.create_currency_distribution_chart(metrics)
        st.plotly_chart(currency_chart, use_container_width=True)

    with tab3:
        st.subheader("🏢 Sector Analysis")
        sector_chart = analyzer.create_sector_distribution_chart(metrics)
        st.plotly_chart(sector_chart, use_container_width=True)

    with tab4:
        st.subheader("📊 Performance Comparison")
        performance_chart = analyzer.create_performance_chart(consolidated_df)
        st.plotly_chart(performance_chart, use_container_width=True)


def display_detailed_analysis(consolidated_df, metrics):
    """Display detailed analysis sections"""
    st.subheader("🔍 Detailed Analysis")

    # Top and worst performers
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top Performers")
        top_performers = metrics.get("top_performers", pd.DataFrame())
        if not top_performers.empty:
            for _, stock in top_performers.iterrows():
                with st.expander(f"{stock['Ticker']} - {stock['Gain/Loss %']:.2f}% gain"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Investment", f"R$ {stock['Total Investment']:,.2f}")
                    with col_b:
                        st.metric("Current Value", f"R$ {stock['Current Value']:,.2f}")
                    with col_c:
                        st.metric("Gain/Loss", f"R$ {stock['Gain/Loss']:,.2f}")
        else:
            st.info("No performance data available")

    with col2:
        st.subheader("📉 Underperformers")
        worst_performers = metrics.get("worst_performers", pd.DataFrame())
        if not worst_performers.empty:
            for _, stock in worst_performers.iterrows():
                with st.expander(f"{stock['Ticker']} - {stock['Gain/Loss %']:.2f}% loss"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Investment", f"R$ {stock['Total Investment']:,.2f}")
                    with col_b:
                        st.metric("Current Value", f"R$ {stock['Current Value']:,.2f}")
                    with col_c:
                        st.metric("Gain/Loss", f"R$ {stock['Gain/Loss']:,.2f}")
        else:
            st.info("No performance data available")

    # Portfolio comparison
    st.subheader("📊 Portfolio Comparison")
    portfolio_comparison = consolidated_df.groupby("Portfolio").agg({
        "Total Investment": "sum",
        "Current Value": "sum",
        "Gain/Loss": "sum",
        "Gain/Loss %": "mean"
    }).round(2)

    st.dataframe(portfolio_comparison, width='stretch')

    # Market analysis
    st.subheader("🌍 Market Analysis")
    market_analysis = consolidated_df.groupby("Market").agg({
        "Total Investment": "sum",
        "Current Value": "sum",
        "Gain/Loss": "sum",
        "Gain/Loss %": "mean"
    }).round(2)

    st.dataframe(market_analysis, width='stretch')


if __name__ == "__main__":
    display_consolidated_dashboard()
