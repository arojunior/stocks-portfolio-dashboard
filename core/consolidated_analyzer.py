"""
Consolidated Portfolio Analyzer
Analyzes all portfolios together for a complete view
"""

import json
import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.portfolio_manager import PortfolioManager
from core.data_fetcher import fetch_stock_data
from core.analytics import calculate_portfolio_metrics
from core.fii_dividend_analyzer import FIIDividendAnalyzer


class ConsolidatedAnalyzer:
    """Analyzes all portfolios together for consolidated view"""
    
    def __init__(self):
        self.portfolio_manager = PortfolioManager()
        self.fii_analyzer = FIIDividendAnalyzer()
    
    def load_all_portfolios(self) -> Dict:
        """Load all portfolio data"""
        try:
            with open("portfolios.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            st.error(f"Error loading portfolios: {e}")
            return {}
    
    def get_consolidated_data(self) -> Dict:
        """Get consolidated data from all portfolios"""
        all_portfolios = self.load_all_portfolios()
        consolidated = {
            "total_portfolios": len(all_portfolios),
            "portfolios": {},
            "total_stocks": 0,
            "total_investment": 0,
            "currencies": {},
            "markets": {}
        }
        
        for portfolio_name, stocks in all_portfolios.items():
            if not stocks:
                continue
                
            # Determine market type
            market_type = self.portfolio_manager.get_market_from_portfolio_name(portfolio_name)
            currency = "BRL" if market_type == "Brazilian" else "USD"
            
            # Calculate portfolio totals
            portfolio_investment = 0
            stock_count = len(stocks)
            
            for ticker, position in stocks.items():
                quantity = position.get("quantity", 0)
                avg_price = position.get("avg_price", 0)
                investment = quantity * avg_price
                portfolio_investment += investment
            
            consolidated["portfolios"][portfolio_name] = {
                "market_type": market_type,
                "currency": currency,
                "stock_count": stock_count,
                "total_investment": portfolio_investment,
                "stocks": stocks
            }
            
            consolidated["total_stocks"] += stock_count
            consolidated["total_investment"] += portfolio_investment
            
            # Track currencies
            if currency not in consolidated["currencies"]:
                consolidated["currencies"][currency] = 0
            consolidated["currencies"][currency] += portfolio_investment
            
            # Track markets
            if market_type not in consolidated["markets"]:
                consolidated["markets"][market_type] = 0
            consolidated["markets"][market_type] += portfolio_investment
        
        return consolidated
    
    def get_consolidated_stock_data(self) -> pd.DataFrame:
        """Get consolidated stock data with current prices"""
        consolidated = self.get_consolidated_data()
        all_stocks = []
        
        for portfolio_name, portfolio_data in consolidated["portfolios"].items():
            market_type = portfolio_data["market_type"]
            currency = portfolio_data["currency"]
            
            for ticker, position in portfolio_data["stocks"].items():
                # Get current stock data
                stock_data = fetch_stock_data(ticker, market_type)
                
                quantity = position.get("quantity", 0)
                avg_price = position.get("avg_price", 0)
                current_price = stock_data.get("current_price", avg_price) if stock_data else avg_price
                change_percent = stock_data.get("change_percent", 0) if stock_data else 0
                sector = stock_data.get("sector", "Unknown") if stock_data else "Unknown"
                dividend_yield = stock_data.get("dividend_yield", 0) if stock_data else 0
                
                # Calculate values
                total_investment = quantity * avg_price
                current_value = quantity * current_price
                gain_loss = current_value - total_investment
                gain_loss_percent = (gain_loss / total_investment * 100) if total_investment > 0 else 0
                
                all_stocks.append({
                    "Portfolio": portfolio_name,
                    "Ticker": ticker,
                    "Quantity": quantity,
                    "Avg Price": avg_price,
                    "Current Price": current_price,
                    "Change %": change_percent,
                    "Total Investment": total_investment,
                    "Current Value": current_value,
                    "Gain/Loss": gain_loss,
                    "Gain/Loss %": gain_loss_percent,
                    "Sector": sector,
                    "Dividend Yield": dividend_yield,
                    "Currency": currency,
                    "Market": market_type
                })
        
        return pd.DataFrame(all_stocks)
    
    def get_consolidated_metrics(self) -> Dict:
        """Calculate consolidated portfolio metrics"""
        df = self.get_consolidated_stock_data()
        if df.empty:
            return {}
        
        total_investment = df["Total Investment"].sum()
        total_current_value = df["Current Value"].sum()
        total_gain_loss = total_current_value - total_investment
        total_gain_loss_percent = (total_gain_loss / total_investment * 100) if total_investment > 0 else 0
        
        # Portfolio distribution
        portfolio_distribution = df.groupby("Portfolio").agg({
            "Total Investment": "sum",
            "Current Value": "sum",
            "Gain/Loss": "sum"
        }).to_dict("index")
        
        # Currency distribution
        currency_distribution = df.groupby("Currency")["Total Investment"].sum().to_dict()
        
        # Market distribution
        market_distribution = df.groupby("Market")["Total Investment"].sum().to_dict()
        
        # Sector distribution
        sector_distribution = df.groupby("Sector")["Total Investment"].sum().to_dict()
        
        # Top performers
        top_performers = df.nlargest(5, "Gain/Loss %")
        worst_performers = df.nsmallest(5, "Gain/Loss %")
        
        return {
            "total_investment": total_investment,
            "total_current_value": total_current_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": total_gain_loss_percent,
            "portfolio_distribution": portfolio_distribution,
            "currency_distribution": currency_distribution,
            "market_distribution": market_distribution,
            "sector_distribution": sector_distribution,
            "top_performers": top_performers,
            "worst_performers": worst_performers,
            "total_stocks": len(df)
        }
    
    def get_fii_consolidated_analysis(self) -> Dict:
        """Get FII analysis for consolidated view"""
        try:
            fii_analysis = self.fii_analyzer.analyze_portfolio_dividends()
            if "error" not in fii_analysis:
                return {
                    "monthly_income": fii_analysis.get("total_monthly_income", 0),
                    "annual_income": fii_analysis.get("total_annual_income", 0),
                    "average_yield": fii_analysis.get("average_yield", 0),
                    "fii_count": fii_analysis.get("total_fiis", 0)
                }
        except Exception as e:
            print(f"FII analysis error: {e}")
        
        return {
            "monthly_income": 0,
            "annual_income": 0,
            "average_yield": 0,
            "fii_count": 0
        }
    
    def create_portfolio_distribution_chart(self, metrics: Dict) -> go.Figure:
        """Create portfolio distribution pie chart"""
        portfolio_data = metrics.get("portfolio_distribution", {})
        
        labels = list(portfolio_data.keys())
        values = [data["Total Investment"] for data in portfolio_data.values()]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig.update_layout(
            title="Portfolio Distribution by Investment",
            showlegend=True
        )
        return fig
    
    def create_currency_distribution_chart(self, metrics: Dict) -> go.Figure:
        """Create currency distribution chart"""
        currency_data = metrics.get("currency_distribution", {})
        
        fig = go.Figure(data=[go.Bar(
            x=list(currency_data.keys()),
            y=list(currency_data.values()),
            text=[f"R$ {v:,.0f}" if k == "BRL" else f"$ {v:,.0f}" for k, v in currency_data.items()],
            textposition='auto'
        )])
        fig.update_layout(
            title="Investment Distribution by Currency",
            xaxis_title="Currency",
            yaxis_title="Total Investment"
        )
        return fig
    
    def create_sector_distribution_chart(self, metrics: Dict) -> go.Figure:
        """Create sector distribution chart"""
        sector_data = metrics.get("sector_distribution", {})
        
        # Sort by value for better visualization
        sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1], reverse=True)
        
        fig = go.Figure(data=[go.Bar(
            x=[item[0] for item in sorted_sectors],
            y=[item[1] for item in sorted_sectors],
            text=[f"R$ {v:,.0f}" for v in [item[1] for item in sorted_sectors]],
            textposition='auto'
        )])
        fig.update_layout(
            title="Investment Distribution by Sector",
            xaxis_title="Sector",
            yaxis_title="Total Investment",
            xaxis_tickangle=-45
        )
        return fig
    
    def create_performance_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create performance comparison chart"""
        # Group by portfolio and calculate performance
        portfolio_performance = df.groupby("Portfolio").agg({
            "Total Investment": "sum",
            "Current Value": "sum",
            "Gain/Loss": "sum"
        }).reset_index()
        
        portfolio_performance["Gain/Loss %"] = (
            portfolio_performance["Gain/Loss"] / portfolio_performance["Total Investment"] * 100
        )
        
        fig = go.Figure(data=[
            go.Bar(
                name="Investment",
                x=portfolio_performance["Portfolio"],
                y=portfolio_performance["Total Investment"],
                text=[f"R$ {v:,.0f}" for v in portfolio_performance["Total Investment"]],
                textposition='auto'
            ),
            go.Bar(
                name="Current Value",
                x=portfolio_performance["Portfolio"],
                y=portfolio_performance["Current Value"],
                text=[f"R$ {v:,.0f}" for v in portfolio_performance["Current Value"]],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Portfolio Performance Comparison",
            xaxis_title="Portfolio",
            yaxis_title="Value",
            barmode='group'
        )
        return fig
