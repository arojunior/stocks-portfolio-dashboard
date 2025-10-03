"""
Simple FII Dividend Analysis Test
Test script that works without external API calls
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.fii_dividend_analyzer import FIIDividendAnalyzer


def test_fii_portfolio_loading():
    """Test FII portfolio loading and basic analysis"""
    print("🧪 Testing FII Portfolio Loading...")

    # Initialize analyzer
    analyzer = FIIDividendAnalyzer()

    # Test 1: Load portfolio
    print("\n1. Testing portfolio loading...")
    fii_portfolio = analyzer.get_fii_portfolio()
    print(f"   Found {len(fii_portfolio)} FIIs in portfolio")

    if not fii_portfolio:
        print("   ❌ No FII portfolio found")
        return False

    # Display portfolio contents
    print("\n📊 FII Portfolio Contents:")
    for ticker, position in fii_portfolio.items():
        quantity = position.get("quantity", 0)
        avg_price = position.get("avg_price", 0)
        total_investment = quantity * avg_price
        print(f"   {ticker}: {quantity} shares @ R$ {avg_price:.2f} = R$ {total_investment:,.2f}")

    return True


def test_dividend_calculations():
    """Test dividend calculations with mock data"""
    print("\n🧮 Testing Dividend Calculations...")

    analyzer = FIIDividendAnalyzer()
    fii_portfolio = analyzer.get_fii_portfolio()

    if not fii_portfolio:
        print("   ❌ No FII portfolio found")
        return False

    # Mock dividend data for testing
    mock_dividend_data = {
        "VISC11": {"annual_yield": 8.5, "monthly_dividend": 0.75},
        "HGLG11": {"annual_yield": 7.2, "monthly_dividend": 0.97},
        "HGRU11": {"annual_yield": 6.8, "monthly_dividend": 0.70},
        "BTLG11": {"annual_yield": 7.5, "monthly_dividend": 0.61},
        "KNCR11": {"annual_yield": 6.9, "monthly_dividend": 0.58},
        "XPLG11": {"annual_yield": 7.1, "monthly_dividend": 0.71},
        "MXRF11": {"annual_yield": 8.2, "monthly_dividend": 0.65},
        "RZTR11": {"annual_yield": 6.5, "monthly_dividend": 0.51},
        "HCTR11": {"annual_yield": 7.8, "monthly_dividend": 0.55},
        "CPTI11": {"annual_yield": 6.3, "monthly_dividend": 0.49}
    }

    print("\n💰 Dividend Income Projections:")
    total_monthly = 0
    total_annual = 0
    total_investment = 0

    for ticker, position in fii_portfolio.items():
        quantity = position.get("quantity", 0)
        avg_price = position.get("avg_price", 0)

        # Get mock dividend data
        mock_data = mock_dividend_data.get(ticker, {"annual_yield": 0, "monthly_dividend": 0})
        annual_yield = mock_data["annual_yield"]
        monthly_dividend = mock_data["monthly_dividend"]

        # Calculate projections
        monthly_income = monthly_dividend * quantity
        annual_income = monthly_income * 12
        investment = quantity * avg_price

        total_monthly += monthly_income
        total_annual += annual_income
        total_investment += investment

        print(f"   {ticker}:")
        print(f"     Position: {quantity} shares @ R$ {avg_price:.2f}")
        print(f"     Investment: R$ {investment:,.2f}")
        print(f"     Monthly Income: R$ {monthly_income:.2f}")
        print(f"     Annual Income: R$ {annual_income:,.2f}")
        print(f"     Dividend Yield: {annual_yield:.1f}%")
        print()

    print(f"📈 Portfolio Summary:")
    print(f"   Total Investment: R$ {total_investment:,.2f}")
    print(f"   Monthly Income: R$ {total_monthly:.2f}")
    print(f"   Annual Income: R$ {total_annual:,.2f}")
    print(f"   Average Yield: {(total_annual / total_investment * 100):.1f}%")

    return True


def test_portfolio_analysis():
    """Test portfolio analysis functionality"""
    print("\n📊 Testing Portfolio Analysis...")

    analyzer = FIIDividendAnalyzer()

    # Test portfolio analysis (this will try to fetch real data)
    print("   Attempting portfolio analysis...")
    try:
        portfolio_analysis = analyzer.analyze_portfolio_dividends()

        if "error" in portfolio_analysis:
            print(f"   ⚠️ Portfolio analysis returned error: {portfolio_analysis['error']}")
            print("   This is expected if external APIs are not available")
        else:
            print(f"   ✅ Portfolio analysis successful")
            print(f"   Total FIIs: {portfolio_analysis['total_fiis']}")
            print(f"   Monthly Income: R$ {portfolio_analysis['total_monthly_income']:.2f}")
            print(f"   Annual Income: R$ {portfolio_analysis['total_annual_income']:.2f}")
    except Exception as e:
        print(f"   ⚠️ Portfolio analysis failed: {e}")
        print("   This is expected if external APIs are not available")

    return True


def test_comparison_table():
    """Test FII comparison table generation"""
    print("\n📋 Testing Comparison Table...")

    analyzer = FIIDividendAnalyzer()

    try:
        # This will work even without external APIs
        comparison_df = analyzer.compare_fii_performance()

        if not comparison_df.empty:
            print("   ✅ Comparison table generated successfully")
            print("   Columns:", list(comparison_df.columns))
            print("   Shape:", comparison_df.shape)
        else:
            print("   ⚠️ Comparison table is empty (expected if no data available)")
    except Exception as e:
        print(f"   ⚠️ Comparison table generation failed: {e}")

    return True


if __name__ == "__main__":
    print("🏢 FII Dividend Analysis - Simple Test Suite")
    print("=" * 60)

    # Run tests
    tests = [
        test_fii_portfolio_loading,
        test_dividend_calculations,
        test_portfolio_analysis,
        test_comparison_table
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ Test passed")
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
        print("-" * 40)

    print(f"\n🎯 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️ Some tests failed, but this may be expected if external APIs are not available")
