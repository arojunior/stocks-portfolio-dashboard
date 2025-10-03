"""
Comprehensive Dividend Analyzer
Analyzes dividend income for all stocks in the portfolio
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.portfolio_manager import PortfolioManager
from core.data_fetcher import fetch_stock_data, get_dividend_yield
from core.fii_dividend_analyzer import FIIDividendAnalyzer
from app.config import BRAZILIAN_DIVIDEND_YIELDS, US_DIVIDEND_YIELDS


class DividendAnalyzer:
    """Analyzes dividend income for all stocks in the portfolio"""
    
    def __init__(self):
        self.portfolio_manager = PortfolioManager()
        self.fii_analyzer = FIIDividendAnalyzer()
    
    def get_all_dividend_data(self) -> Dict:
        """Get dividend data for all stocks across all portfolios"""
        all_portfolios = self.portfolio_manager.get_portfolio_names()
        dividend_data = {
            "total_stocks": 0,
            "total_monthly_income": 0,
            "total_annual_income": 0,
            "average_yield": 0,
            "stocks": [],
            "portfolios": {},
            "currencies": {"BRL": 0, "USD": 0},
            "markets": {"Brazilian": 0, "US": 0}
        }
        
        for portfolio_name in all_portfolios:
            portfolio_stocks = self.portfolio_manager.get_portfolio_stocks(portfolio_name)
            if not portfolio_stocks:
                continue
                
            market_type = self.portfolio_manager.get_market_from_portfolio_name(portfolio_name)
            currency = "BRL" if market_type == "Brazilian" else "USD"
            
            portfolio_dividend_data = {
                "portfolio_name": portfolio_name,
                "market_type": market_type,
                "currency": currency,
                "stock_count": 0,
                "monthly_income": 0,
                "annual_income": 0,
                "average_yield": 0,
                "stocks": []
            }
            
            for ticker, position in portfolio_stocks.items():
                stock_dividend = self.analyze_stock_dividend(ticker, position, market_type)
                if stock_dividend:
                    portfolio_dividend_data["stocks"].append(stock_dividend)
                    portfolio_dividend_data["stock_count"] += 1
                    portfolio_dividend_data["monthly_income"] += stock_dividend["monthly_income"]
                    portfolio_dividend_data["annual_income"] += stock_dividend["annual_income"]
                    
                    # Add to totals
                    dividend_data["total_stocks"] += 1
                    dividend_data["total_monthly_income"] += stock_dividend["monthly_income"]
                    dividend_data["total_annual_income"] += stock_dividend["annual_income"]
                    dividend_data["stocks"].append(stock_dividend)
                    dividend_data["currencies"][currency] += stock_dividend["annual_income"]
                    dividend_data["markets"][market_type] += stock_dividend["annual_income"]
            
            # Calculate portfolio average yield
            if portfolio_dividend_data["stock_count"] > 0:
                total_investment = sum(stock["total_investment"] for stock in portfolio_dividend_data["stocks"])
                if total_investment > 0:
                    portfolio_dividend_data["average_yield"] = (
                        portfolio_dividend_data["annual_income"] / total_investment * 100
                    )
            
            dividend_data["portfolios"][portfolio_name] = portfolio_dividend_data
        
        # Calculate overall average yield
        total_investment = sum(stock["total_investment"] for stock in dividend_data["stocks"])
        if total_investment > 0:
            dividend_data["average_yield"] = (
                dividend_data["total_annual_income"] / total_investment * 100
            )
        
        return dividend_data
    
    def analyze_stock_dividend(self, ticker: str, position: Dict, market_type: str) -> Optional[Dict]:
        """Analyze dividend for a specific stock"""
        try:
            quantity = position.get("quantity", 0)
            avg_price = position.get("avg_price", 0)
            total_investment = quantity * avg_price
            
            if total_investment <= 0:
                return None
            
            # Get current stock data
            stock_data = fetch_stock_data(ticker, market_type)
            current_price = stock_data.get("current_price", avg_price) if stock_data else avg_price
            
            # Get dividend yield
            dividend_yield = self.get_dividend_yield_for_stock(ticker, market_type, stock_data)
            
            # Calculate dividend income
            monthly_income = (dividend_yield / 100) * current_price * quantity / 12
            annual_income = monthly_income * 12
            
            # Get additional stock info
            sector = stock_data.get("sector", "Unknown") if stock_data else "Unknown"
            change_percent = stock_data.get("change_percent", 0) if stock_data else 0
            
            return {
                "ticker": ticker,
                "portfolio": self.get_portfolio_name_for_ticker(ticker),
                "market_type": market_type,
                "currency": "BRL" if market_type == "Brazilian" else "USD",
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "total_investment": total_investment,
                "current_value": quantity * current_price,
                "dividend_yield": dividend_yield,
                "monthly_income": monthly_income,
                "annual_income": annual_income,
                "sector": sector,
                "change_percent": change_percent,
                "income_yield": (annual_income / total_investment * 100) if total_investment > 0 else 0
            }
        except Exception as e:
            print(f"Error analyzing dividend for {ticker}: {e}")
            return None
    
    def get_dividend_yield_for_stock(self, ticker: str, market_type: str, stock_data: Optional[Dict]) -> float:
        """Get dividend yield for a stock with multiple fallback methods"""
        # Method 1: Try to get from stock data
        if stock_data and stock_data.get("dividend_yield", 0) > 0:
            return stock_data["dividend_yield"]
        
        # Method 2: Try to fetch from API
        try:
            api_yield = get_dividend_yield(ticker, market_type)
            if api_yield > 0:
                return api_yield
        except:
            pass
        
        # Method 3: Use static configuration
        if market_type == "Brazilian":
            return BRAZILIAN_DIVIDEND_YIELDS.get(ticker, 0)
        elif market_type == "US":
            return US_DIVIDEND_YIELDS.get(ticker, 0)
        
        # Method 4: Default based on market
        return 2.0 if market_type == "US" else 4.0  # Default yields
    
    def get_portfolio_name_for_ticker(self, ticker: str) -> str:
        """Get portfolio name for a ticker"""
        for portfolio_name in self.portfolio_manager.get_portfolio_names():
            portfolio_stocks = self.portfolio_manager.get_portfolio_stocks(portfolio_name)
            if ticker in portfolio_stocks:
                return portfolio_name
        return "Unknown"
    
    def get_top_dividend_stocks(self, limit: int = 10) -> List[Dict]:
        """Get top dividend yielding stocks"""
        dividend_data = self.get_all_dividend_data()
        stocks = dividend_data.get("stocks", [])
        
        # Sort by annual income
        return sorted(stocks, key=lambda x: x["annual_income"], reverse=True)[:limit]
    
    def get_dividend_by_sector(self) -> Dict:
        """Get dividend analysis by sector"""
        dividend_data = self.get_all_dividend_data()
        stocks = dividend_data.get("stocks", [])
        
        sector_analysis = {}
        for stock in stocks:
            sector = stock["sector"]
            if sector not in sector_analysis:
                sector_analysis[sector] = {
                    "stocks": 0,
                    "total_investment": 0,
                    "annual_income": 0,
                    "average_yield": 0
                }
            
            sector_analysis[sector]["stocks"] += 1
            sector_analysis[sector]["total_investment"] += stock["total_investment"]
            sector_analysis[sector]["annual_income"] += stock["annual_income"]
        
        # Calculate average yields
        for sector, data in sector_analysis.items():
            if data["total_investment"] > 0:
                data["average_yield"] = (data["annual_income"] / data["total_investment"] * 100)
        
        return sector_analysis
    
    def get_dividend_forecast(self, months: int = 12) -> Dict:
        """Get dividend income forecast"""
        dividend_data = self.get_all_dividend_data()
        monthly_income = dividend_data["total_monthly_income"]
        
        forecast = {
            "monthly_income": monthly_income,
            "total_forecast": monthly_income * months,
            "monthly_breakdown": []
        }
        
        cumulative = 0
        for month in range(1, months + 1):
            cumulative += monthly_income
            forecast["monthly_breakdown"].append({
                "month": f"Month {month}",
                "monthly": monthly_income,
                "cumulative": cumulative
            })
        
        return forecast
    
    def create_dividend_income_chart(self, dividend_data: Dict) -> go.Figure:
        """Create dividend income distribution chart"""
        portfolios = dividend_data.get("portfolios", {})
        
        labels = list(portfolios.keys())
        values = [portfolio["annual_income"] for portfolio in portfolios.values()]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig.update_layout(
            title="Dividend Income Distribution by Portfolio",
            showlegend=True
        )
        return fig
    
    def create_sector_dividend_chart(self, sector_data: Dict) -> go.Figure:
        """Create sector dividend analysis chart"""
        sectors = list(sector_data.keys())
        annual_incomes = [data["annual_income"] for data in sector_data.values()]
        yields = [data["average_yield"] for data in sector_data.values()]
        
        fig = go.Figure(data=[
            go.Bar(
                name="Annual Income",
                x=sectors,
                y=annual_incomes,
                text=[f"R$ {income:,.0f}" for income in annual_incomes],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Dividend Income by Sector",
            xaxis_title="Sector",
            yaxis_title="Annual Income (R$)",
            xaxis_tickangle=-45
        )
        return fig
    
    def create_dividend_yield_chart(self, stocks: List[Dict]) -> go.Figure:
        """Create dividend yield comparison chart"""
        tickers = [stock["ticker"] for stock in stocks[:15]]  # Top 15
        yields = [stock["dividend_yield"] for stock in stocks[:15]]
        
        fig = go.Figure(data=[go.Bar(
            x=tickers,
            y=yields,
            text=[f"{yield_val:.2f}%" for yield_val in yields],
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Dividend Yield by Stock (Top 15)",
            xaxis_title="Stock",
            yaxis_title="Dividend Yield (%)",
            xaxis_tickangle=-45
        )
        return fig
