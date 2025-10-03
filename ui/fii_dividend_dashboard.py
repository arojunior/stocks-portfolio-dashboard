"""
FII Dividend Dashboard
Streamlit interface for FII dividend analysis and portfolio management
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from core.fii_dividend_analyzer import FIIDividendAnalyzer


def display_fii_dividend_dashboard():
    """Main FII dividend dashboard interface"""
    st.title("🏢 FII Dividend Analysis Dashboard")
    st.markdown("Comprehensive analysis of your Real Estate Investment Fund (FII) portfolio dividends")

    # Initialize analyzer
    analyzer = FIIDividendAnalyzer()

    # Sidebar controls
    st.sidebar.header("📊 Analysis Options")
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type",
        ["Portfolio Overview", "Individual FII Analysis", "Dividend History", "Performance Comparison"]
    )

    # Get portfolio analysis
    with st.spinner("Analyzing FII portfolio dividends..."):
        try:
            portfolio_analysis = analyzer.analyze_portfolio_dividends()
        except Exception as e:
            st.error(f"❌ Error analyzing portfolio: {e}")
            return

    if "error" in portfolio_analysis:
        st.error(f"❌ {portfolio_analysis['error']}")
        return

    # Display portfolio summary
    display_portfolio_summary(portfolio_analysis)

    # Show data source status
    st.info("ℹ️ **Data Source**: Using fallback data due to API limitations. For real-time data, check your API keys and rate limits.")

    if analysis_type == "Portfolio Overview":
        display_portfolio_overview(analyzer, portfolio_analysis)
    elif analysis_type == "Individual FII Analysis":
        display_individual_analysis(analyzer)
    elif analysis_type == "Dividend History":
        display_dividend_history(analyzer)
    elif analysis_type == "Performance Comparison":
        display_performance_comparison(analyzer)


def display_portfolio_summary(portfolio_analysis):
    """Display portfolio summary metrics"""
    st.subheader("📈 Portfolio Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total FIIs",
            portfolio_analysis["total_fiis"],
            help="Number of FIIs in your portfolio"
        )

    with col2:
        st.metric(
            "Monthly Income",
            f"R$ {portfolio_analysis['total_monthly_income']:,.2f}",
            help="Projected monthly dividend income"
        )

    with col3:
        st.metric(
            "Annual Income",
            f"R$ {portfolio_analysis['total_annual_income']:,.2f}",
            help="Projected annual dividend income"
        )

    with col4:
        st.metric(
            "Average Yield",
            f"{portfolio_analysis['average_yield']:.2f}%",
            help="Average dividend yield across all FIIs"
        )


def display_portfolio_overview(analyzer, portfolio_analysis):
    """Display comprehensive portfolio overview"""
    st.subheader("🏢 Portfolio Overview")

    # Create comparison table
    try:
        comparison_df = analyzer.compare_fii_performance()
        if not comparison_df.empty:
            st.dataframe(comparison_df, width='stretch')
        else:
            st.info("No comparison data available (API may be unavailable)")
    except Exception as e:
        st.warning(f"Could not generate comparison table: {e}")
        st.info("This may be due to API limitations. The system is using fallback data.")

    # Top performers
    st.subheader("🏆 Top Dividend Yielders")
    top_performers = analyzer.get_top_dividend_yielders(5)

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
    forecast = analyzer.get_dividend_income_forecast(12)

    if "error" not in forecast:
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Monthly Income", f"R$ {forecast['monthly_income']:.2f}")
            st.metric("12-Month Forecast", f"R$ {forecast['total_forecast']:,.2f}")

        with col2:
            # Create forecast chart
            forecast_df = pd.DataFrame(forecast["monthly_breakdown"])
            fig = px.line(
                forecast_df,
                x="month",
                y="cumulative",
                title="Cumulative Dividend Income Forecast",
                labels={"month": "Month", "cumulative": "Cumulative Income (R$)"}
            )
            st.plotly_chart(fig, use_container_width=True)


def display_individual_analysis(analyzer):
    """Display individual FII analysis"""
    st.subheader("🔍 Individual FII Analysis")

    # Get FII portfolio
    fii_portfolio = analyzer.get_fii_portfolio()
    if not fii_portfolio:
        st.error("No FII portfolio found")
        return

    # FII selector
    selected_fii = st.selectbox("Select FII to analyze", list(fii_portfolio.keys()))

    if selected_fii:
        with st.spinner(f"Analyzing {selected_fii}..."):
            dividend_analysis = analyzer.analyze_fii_dividends(selected_fii)

        if dividend_analysis:
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Current Price", f"R$ {dividend_analysis['current_price']:.2f}")
            with col2:
                st.metric("Annual Yield", f"{dividend_analysis['annual_dividend_yield']:.2f}%")
            with col3:
                st.metric("Monthly Dividend", f"R$ {dividend_analysis['avg_monthly_dividend']:.2f}")
            with col4:
                st.metric("Projected Annual Income", f"R$ {dividend_analysis['projected_annual_income']:.2f}")

            # Position analysis
            position = fii_portfolio[selected_fii]
            quantity = position.get("quantity", 0)
            income_data = analyzer.calculate_portfolio_dividend_income(quantity, selected_fii)

            st.subheader("💼 Position Analysis")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Your Position", f"{quantity} shares")
                st.metric("Monthly Income", f"R$ {income_data['monthly_income']:.2f}")
            with col2:
                st.metric("Total Investment", f"R$ {income_data['total_investment']:,.2f}")
                st.metric("Annual Income", f"R$ {income_data['annual_income']:,.2f}")
            with col3:
                st.metric("Income Yield", f"{income_data['income_yield']:.2f}%")
                st.metric("Dividend Yield", f"{income_data['dividend_yield']:.2f}%")


def display_dividend_history(analyzer):
    """Display dividend history analysis"""
    st.subheader("📅 Dividend History Analysis")

    # Get FII portfolio
    fii_portfolio = analyzer.get_fii_portfolio()
    if not fii_portfolio:
        st.error("No FII portfolio found")
        return

    # FII selector
    selected_fii = st.selectbox("Select FII for history", list(fii_portfolio.keys()))
    months = st.slider("Analysis Period (months)", 6, 24, 12)

    if selected_fii:
        with st.spinner(f"Loading dividend history for {selected_fii}..."):
            history_summary = analyzer.get_dividend_history_summary(selected_fii, months)

        if "error" not in history_summary:
            # Display summary
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Dividends", f"R$ {history_summary['total_dividends']:.2f}")
            with col2:
                st.metric("Dividend Count", history_summary['dividend_count'])
            with col3:
                st.metric("Avg Monthly", f"R$ {history_summary['avg_monthly']:.2f}")
            with col4:
                st.metric("Period", f"{months} months")

            # Recent dividends table
            if history_summary['recent_dividends']:
                st.subheader("📊 Recent Dividends")
                recent_df = pd.DataFrame(history_summary['recent_dividends'])
                recent_df['value'] = recent_df['value'].apply(lambda x: f"R$ {x:.2f}")
                st.dataframe(recent_df, use_container_width=True)

            # Dividend trend chart
            if len(history_summary['recent_dividends']) > 1:
                st.subheader("📈 Dividend Trend")
                trend_df = pd.DataFrame(history_summary['recent_dividends'])
                trend_df['date'] = pd.to_datetime(trend_df['date'])

                fig = px.line(
                    trend_df,
                    x="date",
                    y="value",
                    title=f"Dividend History - {selected_fii}",
                    labels={"date": "Date", "value": "Dividend Amount (R$)"}
                )
                st.plotly_chart(fig, use_container_width=True)


def display_performance_comparison(analyzer):
    """Display performance comparison charts"""
    st.subheader("📊 Performance Comparison")

    # Get portfolio analysis
    portfolio_analysis = analyzer.analyze_portfolio_dividends()
    if "error" in portfolio_analysis:
        st.error("No portfolio data available")
        return

    # Create performance charts
    fiis_data = portfolio_analysis["fiis"]

    # Dividend yield comparison
    st.subheader("🎯 Dividend Yield Comparison")
    yield_data = []
    for fii in fiis_data:
        yield_data.append({
            "FII": fii["ticker"],
            "Dividend Yield": fii["dividend_yield"],
            "Monthly Income": fii["monthly_income"]
        })

    yield_df = pd.DataFrame(yield_data)

    fig = px.bar(
        yield_df,
        x="FII",
        y="Dividend Yield",
        title="Dividend Yield by FII",
        labels={"FII": "FII Ticker", "Dividend Yield": "Dividend Yield (%)"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Monthly income comparison
    st.subheader("💰 Monthly Income by FII")
    fig2 = px.bar(
        yield_df,
        x="FII",
        y="Monthly Income",
        title="Monthly Dividend Income by FII",
        labels={"FII": "FII Ticker", "Monthly Income": "Monthly Income (R$)"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Portfolio distribution
    st.subheader("🥧 Portfolio Distribution")
    total_investment = sum(fii["total_investment"] for fii in fiis_data)

    distribution_data = []
    for fii in fiis_data:
        percentage = (fii["total_investment"] / total_investment * 100) if total_investment > 0 else 0
        distribution_data.append({
            "FII": fii["ticker"],
            "Percentage": percentage,
            "Investment": fii["total_investment"]
        })

    dist_df = pd.DataFrame(distribution_data)

    fig3 = px.pie(
        dist_df,
        values="Percentage",
        names="FII",
        title="Portfolio Investment Distribution"
    )
    st.plotly_chart(fig3, use_container_width=True)


if __name__ == "__main__":
    display_fii_dividend_dashboard()
