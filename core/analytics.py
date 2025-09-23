"""
Portfolio Analytics Module
Handles portfolio calculations, metrics, and analysis
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def calculate_portfolio_metrics(portfolio_data: List[Dict]) -> Dict:
    """Calculate comprehensive portfolio metrics"""
    if not portfolio_data:
        return {}

    total_value = sum(stock.get("total_value", 0) for stock in portfolio_data)
    total_cost = sum(stock.get("total_cost", 0) for stock in portfolio_data)
    total_gain_loss = total_value - total_cost
    total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

    # Best and worst performers
    performers = [(stock.get("ticker", ""), stock.get("gain_loss_percent", 0))
                 for stock in portfolio_data if stock.get("gain_loss_percent") is not None]

    best_performer = max(performers, key=lambda x: x[1]) if performers else ("", 0)
    worst_performer = min(performers, key=lambda x: x[1]) if performers else ("", 0)

    # Sector analysis
    sectors = {}
    for stock in portfolio_data:
        sector = stock.get("sector", "Unknown")
        if sector not in sectors:
            sectors[sector] = {"count": 0, "value": 0, "percentage": 0}
        sectors[sector]["count"] += 1
        sectors[sector]["value"] += stock.get("total_value", 0)

    # Calculate sector percentages
    for sector in sectors:
        sectors[sector]["percentage"] = (sectors[sector]["value"] / total_value * 100) if total_value > 0 else 0

    # Dividend analysis
    total_annual_dividends = sum(stock.get("annual_dividend", 0) for stock in portfolio_data)
    portfolio_dividend_yield = (total_annual_dividends / total_value * 100) if total_value > 0 else 0

    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain_loss": total_gain_loss,
        "total_gain_loss_percent": total_gain_loss_percent,
        "best_performer": {"ticker": best_performer[0], "return": best_performer[1]},
        "worst_performer": {"ticker": worst_performer[0], "return": worst_performer[1]},
        "sectors": sectors,
        "total_annual_dividends": total_annual_dividends,
        "portfolio_dividend_yield": portfolio_dividend_yield,
        "num_stocks": len(portfolio_data)
    }


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def create_portfolio_dataframe(portfolio_stocks: Dict, stock_data: Dict) -> pd.DataFrame:
    """Create a comprehensive portfolio DataFrame"""
    portfolio_data = []

    for ticker, position in portfolio_stocks.items():
        quantity = position.get("quantity", 0)
        avg_price = position.get("avg_price", 0)

        if ticker in stock_data and stock_data[ticker]:
            data = stock_data[ticker]
            current_price = data.get("current_price", 0)
            change_percent = data.get("change_percent", 0)
            sector = data.get("sector", "Unknown")
            dividend_yield = data.get("dividend_yield", 0)

            # Calculate position metrics
            total_cost = quantity * avg_price
            total_value = quantity * current_price
            gain_loss = total_value - total_cost
            gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0

            # Calculate annual dividend income
            annual_dividend = (dividend_yield / 100) * total_value if dividend_yield > 0 else 0

            portfolio_data.append({
                "Ticker": ticker,
                "Quantity": quantity,
                "Avg Price": f"R$ {avg_price:.2f}" if "R$" in str(avg_price) else f"$ {avg_price:.2f}",
                "Current Price": f"R$ {current_price:.2f}" if "R$" in str(current_price) else f"$ {current_price:.2f}",
                "Total Cost": f"R$ {total_cost:.2f}" if "R$" in str(total_cost) else f"$ {total_cost:.2f}",
                "Total Value": f"R$ {total_value:.2f}" if "R$" in str(total_value) else f"$ {total_value:.2f}",
                "Gain/Loss": f"R$ {gain_loss:.2f}" if "R$" in str(gain_loss) else f"$ {gain_loss:.2f}",
                "Gain/Loss %": f"{gain_loss_percent:.2f}%",
                "Daily Change": f"{change_percent:.2f}%",
                "Sector": sector,
                "Dividend Yield": f"{dividend_yield:.2f}%",
                "Annual Dividend": f"R$ {annual_dividend:.2f}" if "R$" in str(annual_dividend) else f"$ {annual_dividend:.2f}",
                "total_value": total_value,
                "total_cost": total_cost,
                "gain_loss_percent": gain_loss_percent,
                "annual_dividend": annual_dividend,
                "sector": sector,
                "dividend_yield": dividend_yield
            })

    return pd.DataFrame(portfolio_data)


def calculate_sector_diversification(sectors: Dict) -> Dict:
    """Calculate sector diversification metrics"""
    if not sectors:
        return {"concentration_risk": "High", "diversification_score": 0}

    # Calculate Herfindahl-Hirschman Index (HHI) for concentration
    hhi = sum(percentage ** 2 for percentage in sectors.values() if isinstance(percentage, (int, float)))

    # Determine concentration risk
    if hhi > 2500:  # > 50% in one sector
        concentration_risk = "Very High"
    elif hhi > 1800:  # > 42% in one sector
        concentration_risk = "High"
    elif hhi > 1000:  # > 32% in one sector
        concentration_risk = "Medium"
    else:
        concentration_risk = "Low"

    # Calculate diversification score (0-100)
    max_sector_percentage = max(sectors.values()) if sectors else 0
    diversification_score = max(0, 100 - (max_sector_percentage * 2))

    return {
        "concentration_risk": concentration_risk,
        "diversification_score": diversification_score,
        "hhi": hhi,
        "max_sector_percentage": max_sector_percentage
    }


def generate_portfolio_summary(portfolio_data: List[Dict], metrics: Dict) -> str:
    """Generate a text summary of portfolio performance"""
    if not portfolio_data:
        return "No stocks in portfolio"

    summary = f"""
📊 **Portfolio Summary**
- **Total Value**: ${metrics.get('total_value', 0):,.2f}
- **Total Cost**: ${metrics.get('total_cost', 0):,.2f}
- **Total Gain/Loss**: ${metrics.get('total_gain_loss', 0):,.2f} ({metrics.get('total_gain_loss_percent', 0):.2f}%)
- **Number of Stocks**: {metrics.get('num_stocks', 0)}
- **Annual Dividends**: ${metrics.get('total_annual_dividends', 0):,.2f}
- **Portfolio Dividend Yield**: {metrics.get('portfolio_dividend_yield', 0):.2f}%

🏆 **Top Performers**
- **Best**: {metrics.get('best_performer', {}).get('ticker', 'N/A')} ({metrics.get('best_performer', {}).get('return', 0):.2f}%)
- **Worst**: {metrics.get('worst_performer', {}).get('ticker', 'N/A')} ({metrics.get('worst_performer', {}).get('return', 0):.2f}%)
"""

    return summary


def calculate_risk_metrics(portfolio_data: List[Dict]) -> Dict:
    """Calculate portfolio risk metrics"""
    if not portfolio_data:
        return {}

    # Calculate portfolio volatility (simplified)
    returns = [stock.get("gain_loss_percent", 0) for stock in portfolio_data if stock.get("gain_loss_percent") is not None]

    if len(returns) < 2:
        return {"volatility": 0, "risk_level": "Low"}

    # Simple volatility calculation
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    volatility = variance ** 0.5

    # Determine risk level
    if volatility > 20:
        risk_level = "High"
    elif volatility > 10:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "volatility": volatility,
        "risk_level": risk_level,
        "mean_return": mean_return
    }
