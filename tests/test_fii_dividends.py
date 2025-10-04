"""
Test FII Dividend Analysis
Test script for FII dividend functionality
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.fii_dividend_analyzer import FIIDividendAnalyzer
from data.apis.brapi import fetch_fii_dividend_analysis, fetch_dividend_data


def test_fii_dividend_analysis():
    """Test FII dividend analysis functionality"""
    print("🧪 Testing FII Dividend Analysis...")

    # Initialize analyzer
    analyzer = FIIDividendAnalyzer()

    # Test 1: Load portfolio
    print("\n1. Testing portfolio loading...")
    fii_portfolio = analyzer.get_fii_portfolio()
    print(f"   Found {len(fii_portfolio)} FIIs in portfolio")

    if not fii_portfolio:
        print("   ❌ No FII portfolio found")
        return False

    # Test 2: Analyze individual FII
    print("\n2. Testing individual FII analysis...")
    test_ticker = list(fii_portfolio.keys())[0]  # Get first FII
    print(f"   Analyzing {test_ticker}...")

    dividend_analysis = analyzer.analyze_fii_dividends(test_ticker)
    if dividend_analysis:
        print(f"   ✅ Analysis successful for {test_ticker}")
        print(f"   Current Price: R$ {dividend_analysis.get('current_price', 0):.2f}")
        print(f"   Annual Yield: {dividend_analysis.get('annual_dividend_yield', 0):.2f}%")
        print(f"   Monthly Dividend: R$ {dividend_analysis.get('avg_monthly_dividend', 0):.2f}")
    else:
        print(f"   ❌ Analysis failed for {test_ticker}")
        return False

    # Test 3: Portfolio analysis
    print("\n3. Testing portfolio analysis...")
    portfolio_analysis = analyzer.analyze_portfolio_dividends()

    if "error" not in portfolio_analysis:
        print(f"   ✅ Portfolio analysis successful")
        print(f"   Total FIIs: {portfolio_analysis['total_fiis']}")
        print(f"   Monthly Income: R$ {portfolio_analysis['total_monthly_income']:.2f}")
        print(f"   Annual Income: R$ {portfolio_analysis['total_annual_income']:.2f}")
        print(f"   Average Yield: {portfolio_analysis['average_yield']:.2f}%")
    else:
        print(f"   ❌ Portfolio analysis failed: {portfolio_analysis['error']}")
        return False

    # Test 4: BRAPI direct call
    print("\n4. Testing BRAPI direct call...")
    try:
        brapi_data = fetch_fii_dividend_analysis(test_ticker)
        if brapi_data:
            print(f"   ✅ BRAPI call successful for {test_ticker}")
            print(f"   Dividend count: {brapi_data.get('dividend_count_3mo', 0)}")
            print(f"   Total dividends: R$ {brapi_data.get('total_dividends_3mo', 0):.2f}")
        else:
            print(f"   ⚠️ BRAPI call returned no data for {test_ticker}")
    except Exception as e:
        print(f"   ❌ BRAPI call failed: {e}")

    # Test 5: Dividend history
    print("\n5. Testing dividend history...")
    history = analyzer.get_dividend_history_summary(test_ticker, 12)
    if "error" not in history:
        print(f"   ✅ Dividend history successful")
        print(f"   Total dividends (12m): R$ {history['total_dividends']:.2f}")
        print(f"   Dividend count: {history['dividend_count']}")
    else:
        print(f"   ❌ Dividend history failed: {history['error']}")

    print("\n✅ FII Dividend Analysis tests completed!")
    return True


def test_individual_fii():
    """Test individual FII analysis with detailed output"""
    print("\n🔍 Detailed FII Analysis Test...")

    analyzer = FIIDividendAnalyzer()
    fii_portfolio = analyzer.get_fii_portfolio()

    if not fii_portfolio:
        print("❌ No FII portfolio found")
        return

    # Test each FII
    for ticker, position in fii_portfolio.items():
        print(f"\n📊 Analyzing {ticker}...")
        quantity = position.get("quantity", 0)

        # Get dividend analysis
        dividend_analysis = analyzer.analyze_fii_dividends(ticker)
        if dividend_analysis:
            print(f"   Current Price: R$ {dividend_analysis.get('current_price', 0):.2f}")
            print(f"   Annual Yield: {dividend_analysis.get('annual_dividend_yield', 0):.2f}%")
            print(f"   Monthly Dividend: R$ {dividend_analysis.get('avg_monthly_dividend', 0):.2f}")

            # Calculate position income
            income_data = analyzer.calculate_portfolio_dividend_income(quantity, ticker)
            print(f"   Your Position: {quantity} shares")
            print(f"   Monthly Income: R$ {income_data['monthly_income']:.2f}")
            print(f"   Annual Income: R$ {income_data['annual_income']:.2f}")
            print(f"   Total Investment: R$ {income_data['total_investment']:,.2f}")
        else:
            print(f"   ❌ No data available for {ticker}")


if __name__ == "__main__":
    print("🏢 FII Dividend Analysis Test Suite")
    print("=" * 50)

    # Run tests
    success = test_fii_dividend_analysis()

    if success:
        test_individual_fii()
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
