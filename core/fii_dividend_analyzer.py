"""
FII Dividend Analyzer Module
Handles comprehensive dividend analysis for Brazilian Real Estate Investment Funds (FIIs)
"""

import json
import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from data.apis.brapi import fetch_fii_dividend_analysis, fetch_dividend_data
from core.data_fetcher import fetch_stock_data


class FIIDividendAnalyzer:
    """Comprehensive FII dividend analysis and portfolio management"""

    def __init__(self):
        self.portfolio_file = "portfolios.json"

    def load_portfolio(self) -> Dict:
        """Load portfolio data from JSON file"""
        try:
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            st.error(f"Error loading portfolio: {e}")
            return {}

    def get_fii_portfolio(self) -> Dict:
        """Get FII portfolio from the loaded data"""
        portfolio = self.load_portfolio()
        return portfolio.get("FII_B3", {})

    def analyze_fii_dividends(self, ticker: str) -> Optional[Dict]:
        """Analyze dividends for a specific FII with fallback to static data"""
        try:
            # Try to get comprehensive dividend analysis from API
            dividend_data = fetch_fii_dividend_analysis(ticker)

            # If API fails, use fallback static data
            if not dividend_data:
                return self._get_fallback_fii_data(ticker)

            # Get current stock data for additional metrics
            stock_data = fetch_stock_data(ticker, "Brazilian")

            return {
                "ticker": ticker,
                "current_price": dividend_data.get("current_price", 0),
                "dividend_history": dividend_data.get("dividend_history", []),
                "total_dividends_2y": dividend_data.get("total_dividends_2y", 0),
                "dividend_count_2y": dividend_data.get("dividend_count_2y", 0),
                "avg_monthly_dividend": dividend_data.get("avg_monthly_dividend", 0),
                "annual_dividend_yield": dividend_data.get("annual_dividend_yield", 0),
                "monthly_dividend_yield": dividend_data.get("monthly_dividend_yield", 0),
                "projected_annual_income": dividend_data.get("projected_annual_income", 0),
                "change_percent": stock_data.get("change_percent", 0) if stock_data else 0,
                "volume": stock_data.get("volume", 0) if stock_data else 0
            }
        except Exception as e:
            # Fallback to static data on any error
            return self._get_fallback_fii_data(ticker)

    def _get_fallback_fii_data(self, ticker: str) -> Dict:
        """Get fallback FII data using static configurations"""
        from app.config import BRAZILIAN_DIVIDEND_YIELDS

        # Get static dividend yield
        annual_yield = BRAZILIAN_DIVIDEND_YIELDS.get(ticker, 7.0)  # Default 7% for FIIs

        # Get portfolio position for current price estimation
        fii_portfolio = self.get_fii_portfolio()
        position = fii_portfolio.get(ticker, {})
        current_price = position.get("avg_price", 100.0)  # Use avg price as fallback

        # Calculate monthly dividend based on yield
        monthly_dividend = (annual_yield / 100) * current_price / 12

        return {
            "ticker": ticker,
            "current_price": current_price,
            "dividend_history": [],
            "total_dividends_2y": monthly_dividend * 24,  # 2 years
            "dividend_count_2y": 24,  # Monthly dividends
            "avg_monthly_dividend": monthly_dividend,
            "annual_dividend_yield": annual_yield,
            "monthly_dividend_yield": annual_yield / 12,
            "projected_annual_income": monthly_dividend * 12,
            "change_percent": 0,
            "volume": 0
        }

    def calculate_portfolio_dividend_income(self, quantity: int, ticker: str) -> Dict:
        """Calculate dividend income for a specific position"""
        dividend_analysis = self.analyze_fii_dividends(ticker)
        if not dividend_analysis:
            return {
                "ticker": ticker,
                "quantity": quantity,
                "monthly_income": 0,
                "annual_income": 0,
                "dividend_yield": 0,
                "total_investment": 0,
                "income_yield": 0
            }

        current_price = dividend_analysis.get("current_price", 0)
        avg_monthly_dividend = dividend_analysis.get("avg_monthly_dividend", 0)
        annual_dividend_yield = dividend_analysis.get("annual_dividend_yield", 0)

        # Calculate income projections
        monthly_income = avg_monthly_dividend * quantity
        annual_income = monthly_income * 12
        total_investment = current_price * quantity
        income_yield = (annual_income / total_investment * 100) if total_investment > 0 else 0

        return {
            "ticker": ticker,
            "quantity": quantity,
            "current_price": current_price,
            "total_investment": total_investment,
            "monthly_income": monthly_income,
            "annual_income": annual_income,
            "dividend_yield": annual_dividend_yield,
            "income_yield": income_yield,
            "avg_monthly_dividend": avg_monthly_dividend
        }

    def analyze_portfolio_dividends(self) -> Dict:
        """Analyze dividends for the entire FII portfolio"""
        fii_portfolio = self.get_fii_portfolio()
        if not fii_portfolio:
            return {"error": "No FII portfolio found"}

        portfolio_analysis = {
            "total_fiis": len(fii_portfolio),
            "fiis": [],
            "total_monthly_income": 0,
            "total_annual_income": 0,
            "total_investment": 0,
            "average_yield": 0
        }

        total_monthly = 0
        total_annual = 0
        total_investment = 0
        yields = []

        for ticker, position in fii_portfolio.items():
            quantity = position.get("quantity", 0)
            try:
                income_data = self.calculate_portfolio_dividend_income(quantity, ticker)

                portfolio_analysis["fiis"].append(income_data)

                total_monthly += income_data.get("monthly_income", 0)
                total_annual += income_data.get("annual_income", 0)
                total_investment += income_data.get("total_investment", 0)

                if income_data.get("dividend_yield", 0) > 0:
                    yields.append(income_data["dividend_yield"])
            except Exception as e:
                # Skip problematic FIIs but continue with others
                print(f"Warning: Could not analyze {ticker}: {e}")
                continue

        portfolio_analysis["total_monthly_income"] = total_monthly
        portfolio_analysis["total_annual_income"] = total_annual
        portfolio_analysis["total_investment"] = total_investment
        portfolio_analysis["average_yield"] = sum(yields) / len(yields) if yields else 0

        return portfolio_analysis

    def get_dividend_history_summary(self, ticker: str, months: int = 12) -> Dict:
        """Get dividend history summary for the last N months"""
        dividend_analysis = self.analyze_fii_dividends(ticker)
        if not dividend_analysis:
            return {"error": f"No dividend data found for {ticker}"}

        dividend_history = dividend_analysis.get("dividend_history", [])

        # Filter last N months
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        recent_dividends = []

        for dividend in dividend_history:
            try:
                dividend_date = datetime.strptime(dividend["date"], "%Y-%m-%d")
                if dividend_date >= cutoff_date:
                    recent_dividends.append(dividend)
            except:
                continue

        # Calculate summary metrics
        total_recent = sum(dividend["value"] for dividend in recent_dividends)
        avg_monthly = total_recent / months if months > 0 else 0

        return {
            "ticker": ticker,
            "period_months": months,
            "total_dividends": total_recent,
            "dividend_count": len(recent_dividends),
            "avg_monthly": avg_monthly,
            "recent_dividends": recent_dividends[:6]  # Last 6 dividends
        }

    def compare_fii_performance(self) -> pd.DataFrame:
        """Compare FII performance metrics"""
        portfolio_analysis = self.analyze_portfolio_dividends()
        if "error" in portfolio_analysis:
            return pd.DataFrame()

        fiis_data = []
        for fii in portfolio_analysis["fiis"]:
            # Handle missing fields gracefully
            current_price = fii.get("current_price", 0)
            total_investment = fii.get("total_investment", 0)
            monthly_income = fii.get("monthly_income", 0)
            annual_income = fii.get("annual_income", 0)
            dividend_yield = fii.get("dividend_yield", 0)
            income_yield = fii.get("income_yield", 0)

            fiis_data.append({
                "Ticker": fii.get("ticker", "N/A"),
                "Quantity": fii.get("quantity", 0),
                "Current Price": f"R$ {current_price:.2f}" if current_price > 0 else "N/A",
                "Total Investment": f"R$ {total_investment:,.2f}",
                "Monthly Income": f"R$ {monthly_income:.2f}",
                "Annual Income": f"R$ {annual_income:,.2f}",
                "Dividend Yield": f"{dividend_yield:.2f}%" if dividend_yield > 0 else "N/A",
                "Income Yield": f"{income_yield:.2f}%"
            })

        return pd.DataFrame(fiis_data)

    def get_top_dividend_yielders(self, limit: int = 5) -> List[Dict]:
        """Get top dividend yielding FIIs in the portfolio"""
        portfolio_analysis = self.analyze_portfolio_dividends()
        if "error" in portfolio_analysis:
            return []

        # Sort by dividend yield
        sorted_fiis = sorted(
            portfolio_analysis["fiis"],
            key=lambda x: x["dividend_yield"],
            reverse=True
        )

        return sorted_fiis[:limit]

    def get_dividend_income_forecast(self, months: int = 12) -> Dict:
        """Get dividend income forecast for the next N months"""
        portfolio_analysis = self.analyze_portfolio_dividends()
        if "error" in portfolio_analysis:
            return {"error": "No portfolio data available"}

        monthly_income = portfolio_analysis["total_monthly_income"]

        forecast = {
            "period_months": months,
            "monthly_income": monthly_income,
            "total_forecast": monthly_income * months,
            "monthly_breakdown": []
        }

        # Generate monthly breakdown
        for month in range(1, months + 1):
            forecast["monthly_breakdown"].append({
                "month": month,
                "income": monthly_income,
                "cumulative": monthly_income * month
            })

        return forecast
