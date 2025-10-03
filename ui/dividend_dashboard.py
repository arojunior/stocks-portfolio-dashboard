"""
Comprehensive Dividend Dashboard
Streamlit interface for analyzing dividend income across all stocks
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.dividend_analyzer import DividendAnalyzer


def display_dividend_dashboard():
    """Main dividend dashboard interface"""
    st.title("💰 Comprehensive Dividend Analysis")
    st.markdown("Complete dividend income analysis across all your stocks and portfolios")
    
    # Initialize analyzer
    analyzer = DividendAnalyzer()
    
    # Get dividend data
    with st.spinner("🔄 Analyzing dividend income across all stocks..."):
        dividend_data = analyzer.get_all_dividend_data()
        sector_data = analyzer.get_dividend_by_sector()
        forecast = analyzer.get_dividend_forecast(12)
    
    if dividend_data["total_stocks"] == 0:
        st.error("❌ No stock data found")
        return
    
    # Display dividend summary
    display_dividend_summary(dividend_data, forecast)
    
    # Display dividend table
    display_dividend_table(dividend_data)
    
    # Display charts
    display_dividend_charts(analyzer, dividend_data, sector_data)
    
    # Display detailed analysis
    display_detailed_dividend_analysis(dividend_data, sector_data)


def display_dividend_summary(dividend_data, forecast):
    """Display dividend income summary"""
    st.subheader("📊 Dividend Income Summary")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Stocks",
            dividend_data["total_stocks"],
            help="Number of stocks with dividend potential"
        )
    
    with col2:
        st.metric(
            "Monthly Income",
            f"R$ {dividend_data['total_monthly_income']:,.2f}",
            help="Total monthly dividend income"
        )
    
    with col3:
        st.metric(
            "Annual Income",
            f"R$ {dividend_data['total_annual_income']:,.2f}",
            help="Total annual dividend income"
        )
    
    with col4:
        st.metric(
            "Average Yield",
            f"{dividend_data['average_yield']:.2f}%",
            help="Average dividend yield across all stocks"
        )
    
    # Portfolio breakdown
    st.subheader("🏢 Portfolio Dividend Breakdown")
    portfolio_cols = st.columns(len(dividend_data["portfolios"]))
    
    for i, (portfolio_name, portfolio_data) in enumerate(dividend_data["portfolios"].items()):
        with portfolio_cols[i]:
            st.metric(
                portfolio_name,
                f"R$ {portfolio_data['annual_income']:,.2f}",
                f"{portfolio_data['stock_count']} stocks • {portfolio_data['average_yield']:.2f}% yield"
            )
    
    # Income forecast
    st.subheader("📈 12-Month Income Forecast")
    forecast_col1, forecast_col2, forecast_col3 = st.columns(3)
    
    with forecast_col1:
        st.metric("Monthly Income", f"R$ {forecast['monthly_income']:.2f}")
    with forecast_col2:
        st.metric("12-Month Forecast", f"R$ {forecast['total_forecast']:,.2f}")
    with forecast_col3:
        st.metric("Daily Average", f"R$ {forecast['monthly_income'] / 30:.2f}")


def display_dividend_table(dividend_data):
    """Display comprehensive dividend table"""
    st.subheader("📋 All Stocks Dividend Analysis")
    
    if dividend_data["stocks"]:
        # Create dataframe
        df = pd.DataFrame(dividend_data["stocks"])
        
        # Format for display
        display_df = df.copy()
        display_df["Avg Price"] = display_df["Avg Price"].apply(lambda x: f"R$ {x:.2f}")
        display_df["Current Price"] = display_df["Current Price"].apply(lambda x: f"R$ {x:.2f}")
        display_df["Total Investment"] = display_df["Total Investment"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["Current Value"] = display_df["Current Value"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["Monthly Income"] = display_df["Monthly Income"].apply(lambda x: f"R$ {x:.2f}")
        display_df["Annual Income"] = display_df["Annual Income"].apply(lambda x: f"R$ {x:,.2f}")
        display_df["Dividend Yield"] = display_df["Dividend Yield"].apply(lambda x: f"{x:.2f}%")
        display_df["Income Yield"] = display_df["Income Yield"].apply(lambda x: f"{x:.2f}%")
        display_df["Change %"] = display_df["Change %"].apply(lambda x: f"{x:.2f}%")
        
        # Sort by annual income
        display_df = display_df.sort_values("Annual Income", ascending=False)
        
        st.dataframe(display_df, width='stretch')
    else:
        st.info("No dividend data available")


def display_dividend_charts(analyzer, dividend_data, sector_data):
    """Display dividend analysis charts"""
    st.subheader("📈 Dividend Analysis Charts")
    
    # Create tabs for different chart types
    tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Distribution", "Sector Analysis", "Dividend Yields", "Income Forecast"])
    
    with tab1:
        st.subheader("🥧 Dividend Income by Portfolio")
        portfolio_chart = analyzer.create_dividend_income_chart(dividend_data)
        st.plotly_chart(portfolio_chart, use_container_width=True)
    
    with tab2:
        st.subheader("🏢 Dividend Income by Sector")
        sector_chart = analyzer.create_sector_dividend_chart(sector_data)
        st.plotly_chart(sector_chart, use_container_width=True)
    
    with tab3:
        st.subheader("📊 Dividend Yield Comparison")
        top_stocks = analyzer.get_top_dividend_stocks(15)
        yield_chart = analyzer.create_dividend_yield_chart(top_stocks)
        st.plotly_chart(yield_chart, use_container_width=True)
    
    with tab4:
        st.subheader("💰 Income Forecast")
        forecast = analyzer.get_dividend_forecast(12)
        
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


def display_detailed_dividend_analysis(dividend_data, sector_data):
    """Display detailed dividend analysis"""
    st.subheader("🔍 Detailed Dividend Analysis")
    
    # Top dividend stocks
    st.subheader("🏆 Top Dividend Stocks")
    top_stocks = sorted(dividend_data["stocks"], key=lambda x: x["annual_income"], reverse=True)[:10]
    
    if top_stocks:
        for i, stock in enumerate(top_stocks, 1):
            with st.expander(f"{i}. {stock['ticker']} - R$ {stock['annual_income']:,.2f}/year"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Dividend Yield", f"{stock['dividend_yield']:.2f}%")
                with col2:
                    st.metric("Monthly Income", f"R$ {stock['monthly_income']:.2f}")
                with col3:
                    st.metric("Annual Income", f"R$ {stock['annual_income']:,.2f}")
                with col4:
                    st.metric("Total Investment", f"R$ {stock['total_investment']:,.2f}")
    
    # Sector analysis
    st.subheader("🏢 Sector Dividend Analysis")
    sector_df = pd.DataFrame([
        {
            "Sector": sector,
            "Stocks": data["stocks"],
            "Total Investment": f"R$ {data['total_investment']:,.2f}",
            "Annual Income": f"R$ {data['annual_income']:,.2f}",
            "Average Yield": f"{data['average_yield']:.2f}%"
        }
        for sector, data in sector_data.items()
    ])
    
    if not sector_df.empty:
        st.dataframe(sector_df, width='stretch')
    
    # Currency breakdown
    st.subheader("💱 Currency Breakdown")
    currency_data = dividend_data.get("currencies", {})
    if currency_data:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("BRL Income", f"R$ {currency_data.get('BRL', 0):,.2f}")
        with col2:
            st.metric("USD Income", f"$ {currency_data.get('USD', 0):,.2f}")
    
    # Market breakdown
    st.subheader("🌍 Market Breakdown")
    market_data = dividend_data.get("markets", {})
    if market_data:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Brazilian Market", f"R$ {market_data.get('Brazilian', 0):,.2f}")
        with col2:
            st.metric("US Market", f"$ {market_data.get('US', 0):,.2f}")


if __name__ == "__main__":
    display_dividend_dashboard()
