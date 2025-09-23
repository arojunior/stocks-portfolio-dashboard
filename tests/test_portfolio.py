"""
Test Portfolio Manager
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.portfolio_manager import PortfolioManager


def test_portfolio_manager():
    """Test PortfolioManager functionality"""
    print("Testing PortfolioManager...")

    # Create portfolio manager
    pm = PortfolioManager()

    # Test portfolio creation
    result = pm.create_portfolio("Test_Portfolio", "US", "NYSE")
    print(f"Create portfolio result: {result}")
    print(f"Portfolio names: {pm.get_portfolio_names()}")
    # The create_portfolio method creates portfolios with format "Market_Exchange"
    assert "US_NYSE" in pm.get_portfolio_names()
    print("✅ Portfolio creation test passed")

    # Test adding stocks
    pm.add_stock("US_NYSE", "AAPL", 10, 150.0)
    stocks = pm.get_portfolio_stocks("US_NYSE")
    assert "AAPL" in stocks
    assert stocks["AAPL"]["quantity"] == 10
    assert stocks["AAPL"]["avg_price"] == 150.0
    print("✅ Add stock test passed")

    # Test market detection
    market = pm.get_market_from_portfolio_name("US_NYSE")
    assert market == "US"
    print("✅ Market detection test passed")

    # Test removing stocks
    pm.remove_stock("US_NYSE", "AAPL")
    stocks = pm.get_portfolio_stocks("US_NYSE")
    assert "AAPL" not in stocks
    print("✅ Remove stock test passed")

    # Clean up
    pm.delete_portfolio("US_NYSE")
    assert "US_NYSE" not in pm.get_portfolio_names()
    print("✅ Portfolio deletion test passed")

    print("All PortfolioManager tests passed! 🎉")


if __name__ == "__main__":
    test_portfolio_manager()
