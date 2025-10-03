#!/usr/bin/env python3
"""
Test script for risk analysis functionality
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.analytics import calculate_risk_metrics


def test_risk_metrics():
    """Test risk metrics calculation with sample portfolio data"""
    print("Testing risk analysis functionality...")

    # Sample portfolio data with different return scenarios
    test_portfolio_data = [
        {
            "Ticker": "AAPL",
            "_gain_loss_percent": 5.2,
            "_total_value": 10000,
            "_total_cost": 9500
        },
        {
            "Ticker": "MSFT",
            "_gain_loss_percent": -2.1,
            "_total_value": 8000,
            "_total_cost": 8200
        },
        {
            "Ticker": "GOOGL",
            "_gain_loss_percent": 8.7,
            "_total_value": 12000,
            "_total_cost": 11000
        },
        {
            "Ticker": "TSLA",
            "_gain_loss_percent": -5.3,
            "_total_value": 15000,
            "_total_cost": 15800
        },
        {
            "Ticker": "AMZN",
            "_gain_loss_percent": 3.1,
            "_total_value": 9000,
            "_total_cost": 8700
        }
    ]

    print(f"\n1. Testing risk metrics with {len(test_portfolio_data)} stocks:")
    print("   Portfolio returns:", [stock["_gain_loss_percent"] for stock in test_portfolio_data])

    try:
        risk_metrics = calculate_risk_metrics(test_portfolio_data)
        print(f"   Risk Level: {risk_metrics.get('risk_level', 'Unknown')}")
        print(f"   Volatility: {risk_metrics.get('volatility', 0):.2f}%")
        print(f"   Mean Return: {risk_metrics.get('mean_return', 0):.2f}%")

        # Verify the calculations make sense
        expected_mean = sum(stock["_gain_loss_percent"] for stock in test_portfolio_data) / len(test_portfolio_data)
        print(f"   Expected Mean Return: {expected_mean:.2f}%")

        if abs(risk_metrics.get('mean_return', 0) - expected_mean) < 0.01:
            print("   ✅ Mean return calculation is correct")
        else:
            print("   ❌ Mean return calculation is incorrect")

    except Exception as e:
        print(f"   Error: {e}")

    # Test with empty portfolio
    print(f"\n2. Testing with empty portfolio:")
    try:
        empty_risk = calculate_risk_metrics([])
        print(f"   Result: {empty_risk}")
        if not empty_risk:
            print("   ✅ Empty portfolio handled correctly")
        else:
            print("   ❌ Empty portfolio should return empty dict")
    except Exception as e:
        print(f"   Error: {e}")

    # Test with single stock
    print(f"\n3. Testing with single stock:")
    try:
        single_stock = [test_portfolio_data[0]]
        single_risk = calculate_risk_metrics(single_stock)
        print(f"   Risk Level: {single_risk.get('risk_level', 'Unknown')}")
        print(f"   Volatility: {single_risk.get('volatility', 0):.2f}%")
        print(f"   Mean Return: {single_risk.get('mean_return', 0):.2f}%")

        if single_risk.get('risk_level') == 'Low':
            print("   ✅ Single stock correctly classified as Low risk")
        else:
            print("   ❌ Single stock should be Low risk")

    except Exception as e:
        print(f"   Error: {e}")


def test_risk_levels():
    """Test different risk level scenarios"""
    print(f"\n4. Testing different risk level scenarios:")

    # High volatility portfolio
    high_vol_portfolio = [
        {"Ticker": "STOCK1", "_gain_loss_percent": 20.0},
        {"Ticker": "STOCK2", "_gain_loss_percent": -15.0},
        {"Ticker": "STOCK3", "_gain_loss_percent": 25.0},
        {"Ticker": "STOCK4", "_gain_loss_percent": -10.0}
    ]

    try:
        high_risk = calculate_risk_metrics(high_vol_portfolio)
        print(f"   High volatility portfolio: {high_risk.get('risk_level', 'Unknown')} risk")
        print(f"   Volatility: {high_risk.get('volatility', 0):.2f}%")
    except Exception as e:
        print(f"   Error: {e}")

    # Low volatility portfolio
    low_vol_portfolio = [
        {"Ticker": "STOCK1", "_gain_loss_percent": 2.0},
        {"Ticker": "STOCK2", "_gain_loss_percent": 1.5},
        {"Ticker": "STOCK3", "_gain_loss_percent": 3.0},
        {"Ticker": "STOCK4", "_gain_loss_percent": 2.5}
    ]

    try:
        low_risk = calculate_risk_metrics(low_vol_portfolio)
        print(f"   Low volatility portfolio: {low_risk.get('risk_level', 'Unknown')} risk")
        print(f"   Volatility: {low_risk.get('volatility', 0):.2f}%")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("RISK ANALYSIS TESTS")
    print("=" * 60)

    test_risk_metrics()
    test_risk_levels()

    print("\n" + "=" * 60)
    print("RISK ANALYSIS TESTS COMPLETED")
    print("=" * 60)

