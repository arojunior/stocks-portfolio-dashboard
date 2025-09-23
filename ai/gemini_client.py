"""
Google Gemini AI Client Module
Handles AI analysis using Google Gemini
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import os
from app.config import API_KEYS


class GeminiClient:
    """Client for Google Gemini AI analysis"""

    def __init__(self):
        self.api_key = API_KEYS.get("GEMINI_API_KEY")
        self.available = self._check_availability()

        if self.available:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def _check_availability(self) -> bool:
        """Check if Gemini is available"""
        return bool(self.api_key)

    def analyze_portfolio(self, portfolio_data: List[Dict], metrics: Dict) -> Optional[str]:
        """Generate portfolio analysis using Gemini"""
        if not self.available:
            return None

        try:
            # Prepare portfolio summary
            portfolio_summary = self._prepare_portfolio_summary(portfolio_data, metrics)

            prompt = f"""
            Analyze this stock portfolio and provide insights:

            {portfolio_summary}

            Please provide:
            1. Overall portfolio performance assessment
            2. Risk analysis and diversification insights
            3. Top performing and underperforming stocks
            4. Sector concentration analysis
            5. Dividend income analysis
            6. Recommendations for improvement

            Keep the analysis concise but informative.
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Error generating Gemini analysis: {e}")
            return None

    def analyze_stock(self, ticker: str, stock_data: Dict) -> Optional[str]:
        """Generate individual stock analysis using Gemini"""
        if not self.available:
            return None

        try:
            prompt = f"""
            Analyze this stock and provide insights:

            Ticker: {ticker}
            Current Price: ${stock_data.get('current_price', 0):.2f}
            Change: {stock_data.get('change_percent', 0):.2f}%
            Sector: {stock_data.get('sector', 'Unknown')}
            Dividend Yield: {stock_data.get('dividend_yield', 0):.2f}%

            Please provide:
            1. Stock performance assessment
            2. Sector analysis
            3. Dividend analysis
            4. Investment recommendation (BUY/HOLD/SELL)
            5. Risk assessment

            Keep the analysis concise but informative.
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Error generating Gemini stock analysis: {e}")
            return None

    def generate_trading_signals(self, portfolio_data: List[Dict]) -> List[Dict]:
        """Generate trading signals for portfolio stocks"""
        if not self.available:
            return []

        signals = []

        for stock in portfolio_data:
            try:
                ticker = stock.get('Ticker', '')
                gain_loss = stock.get('gain_loss_percent', 0)
                dividend_yield = stock.get('dividend_yield', 0)

                prompt = f"""
                Analyze this stock and provide a trading signal:

                Ticker: {ticker}
                Gain/Loss: {gain_loss:.2f}%
                Dividend Yield: {dividend_yield:.2f}%

                Provide a trading signal: BUY, HOLD, or SELL
                Provide a brief reason for the signal.
                """

                response = self.model.generate_content(prompt)
                signal_text = response.text.strip()
                signal = self._parse_trading_signal(signal_text)

                signals.append({
                    "ticker": ticker,
                    "signal": signal.get("action", "HOLD"),
                    "reason": signal.get("reason", "No analysis available"),
                    "confidence": signal.get("confidence", 0.5)
                })

            except Exception as e:
                print(f"Error generating trading signal for {ticker}: {e}")
                signals.append({
                    "ticker": ticker,
                    "signal": "HOLD",
                    "reason": "Analysis unavailable",
                    "confidence": 0.0
                })

        return signals

    def analyze_news_sentiment(self, news_data: List[Dict]) -> Optional[str]:
        """Analyze news sentiment for portfolio stocks"""
        if not self.available or not news_data:
            return None

        try:
            # Prepare news summary
            news_summary = self._prepare_news_summary(news_data)

            prompt = f"""
            Analyze the sentiment of these news articles related to the portfolio stocks:

            {news_summary}

            Please provide:
            1. Overall market sentiment
            2. Positive and negative factors
            3. Impact on portfolio performance
            4. Key themes and trends

            Keep the analysis concise but informative.
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Error generating news sentiment analysis: {e}")
            return None

    def _prepare_portfolio_summary(self, portfolio_data: List[Dict], metrics: Dict) -> str:
        """Prepare portfolio summary for AI analysis"""
        summary = f"""
        Portfolio Summary:
        - Total Value: ${metrics.get('total_value', 0):,.2f}
        - Total Gain/Loss: {metrics.get('total_gain_loss_percent', 0):.2f}%
        - Number of Stocks: {metrics.get('num_stocks', 0)}
        - Annual Dividends: ${metrics.get('total_annual_dividends', 0):,.2f}
        - Portfolio Dividend Yield: {metrics.get('portfolio_dividend_yield', 0):.2f}%

        Top Performers:
        - Best: {metrics.get('best_performer', {}).get('ticker', 'N/A')} ({metrics.get('best_performer', {}).get('return', 0):.2f}%)
        - Worst: {metrics.get('worst_performer', {}).get('ticker', 'N/A')} ({metrics.get('worst_performer', {}).get('return', 0):.2f}%)

        Stock Details:
        """

        for stock in portfolio_data[:10]:  # Limit to top 10 stocks
            summary += f"""
        - {stock.get('Ticker', '')}: {stock.get('gain_loss_percent', 0):.2f}% (Sector: {stock.get('sector', 'Unknown')}, Dividend: {stock.get('dividend_yield', 0):.2f}%)
        """

        return summary

    def _prepare_news_summary(self, news_data: List[Dict]) -> str:
        """Prepare news summary for AI analysis"""
        summary = "Recent News Articles:\n"

        for i, article in enumerate(news_data[:5], 1):  # Limit to top 5 articles
            title = article.get('title', 'No title')
            summary_text = article.get('summary', 'No summary')
            sentiment = article.get('sentiment', 'neutral')

            summary += f"""
        {i}. {title}
           Summary: {summary_text}
           Sentiment: {sentiment}
        """

        return summary

    def _parse_trading_signal(self, signal_text: str) -> Dict:
        """Parse trading signal from AI response"""
        signal_text = signal_text.upper()

        action = "HOLD"
        if "BUY" in signal_text:
            action = "BUY"
        elif "SELL" in signal_text:
            action = "SELL"

        # Extract confidence based on language strength
        confidence = 0.5
        if any(word in signal_text for word in ["STRONG", "HIGHLY", "DEFINITELY"]):
            confidence = 0.8
        elif any(word in signal_text for word in ["WEAK", "SLIGHTLY", "MAYBE"]):
            confidence = 0.3

        return {
            "action": action,
            "reason": signal_text,
            "confidence": confidence
        }
