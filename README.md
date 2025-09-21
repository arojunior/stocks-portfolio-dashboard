# Portfolio Management Dashboard

A comprehensive multi-portfolio management dashboard that replaces your Google Spreadsheet for tracking stock investments across different markets (Brazilian and US stocks).

## 🚧 Current Status (September 2025)

**✅ Fully Functional:**

- Multi-portfolio management (Brazilian & US stocks)
- Real-time stock price fetching with multiple API sources
- Portfolio analytics and performance metrics
- AI-powered analysis (Ollama + Google Gemini)
- News feed with sentiment analysis
- Technical analysis charts
- Configurable refresh intervals
- Progressive loading for large portfolios
- **NEW**: Sector analysis and dividend yield tracking
- **NEW**: Real-time sector and dividend data from Yahoo Finance

**🔄 In Development:**

- Enhanced sector diversification metrics
- Advanced dividend income projections
- Portfolio comparison features

**✅ Recently Fixed:**

- Sector and dividend data now displays correctly in portfolio table
- Fixed Streamlit deprecation warnings
- Improved data fetching with real sector and dividend information
- Cache clearing utility for better development experience

## Features

### 🚀 Core Features

- **Multi-Portfolio Support**: Manage separate portfolios for different markets (Brazilian, US, or custom portfolios)
- **Real-Time Data**: Automatic fetching of current stock prices, daily changes, and market data
- **Portfolio Analytics**: Comprehensive metrics including total returns, best/worst performers, and portfolio composition
- **Interactive Visualizations**: Pie charts for portfolio composition and bar charts for performance analysis
- **Persistent Storage**: Your portfolio data is saved locally in JSON format

### 🤖 AI-Powered Features (DeepCharts Inspired)

- **Local AI Analysis**: Ollama integration with LLaMA 3.2 for completely free portfolio insights
- **Professional Portfolio Analysis**: AI-powered performance assessment, risk analysis, and recommendations
- **Smart Trading Signals**: AI-generated BUY/SELL/HOLD recommendations based on price movements
- **News Sentiment Analysis**: Google Gemini integration for analyzing market impact of news
- **Technical Analysis**: Advanced candlestick charts with multiple technical indicators
- **No API Limits**: Local AI means unlimited analysis without cost barriers

### 📊 Dashboard Components

#### Portfolio Overview

- Total invested amount
- Current portfolio value
- Total return (absolute and percentage)
- Number of profitable vs total stocks

#### Visual Analytics

- **Portfolio Composition**: Pie chart showing weight of each stock by current value
- **Performance Overview**: Horizontal bar chart showing gain/loss percentage for each stock
- **Detailed Table**: Comprehensive view with all stock data, formatted with conditional coloring
- **Sector Analysis**: Real-time sector information for portfolio diversification tracking
- **Dividend Analysis**: Dividend yields and annual dividend amounts from Yahoo Finance

#### Stock Management

- Add new stocks with ticker, quantity, and average price
- Update existing stock positions
- Remove stocks from portfolio
- Support for both US stocks (e.g., AAPL) and Brazilian stocks (e.g., PETR4)

#### 🤖 AI-Powered Analysis

- **Portfolio Overview**: Comprehensive AI analysis of performance, risk, and diversification
- **Trading Signals**: Smart BUY/SELL/HOLD recommendations with reasoning
- **News Sentiment**: AI analysis of news impact on your specific stocks
- **Technical Charts**: Advanced candlestick charts with SMA, EMA, Bollinger Bands, RSI, MACD, VWAP

#### 📰 News Feed

- **Real-Time News**: Latest news for stocks in your portfolio
- **Multiple Sources**: NewsAPI, Alpha Vantage, web scraping fallbacks
- **Sentiment Analysis**: AI-powered sentiment scoring for each news article

## Installation

### Prerequisites

- Python 3.8 or higher
- Git
- **For AI Features**:
  - Ollama (for local AI analysis)
  - Google Gemini API key (for news sentiment analysis)

### Setup with Virtual Environment (Recommended)

**Always use a virtual environment for Python projects!**

```bash
# 1. Clone the repository
git clone <repository-url>
cd stocks-portfolio-dashboard

# 2. Create and activate virtual environment
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Set up AI features (optional but recommended)
# Install Ollama for local AI analysis
brew install ollama  # macOS
# or follow instructions at https://ollama.ai for other platforms

# Start Ollama service
brew services start ollama

# Download LLaMA model
ollama pull llama3.2

        # 5. Configure API keys (create .env file)
        echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
        echo "NEWSAPI_KEY=your_newsapi_key_here" >> .env
        echo "ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here" >> .env
        echo "BRAPI_API_KEY=your_brapi_api_key_here" >> .env
```

> 📋 **See [SETUP.md](SETUP.md) for detailed installation instructions, AI setup, and troubleshooting.**

## Usage

### Running the Dashboard

```bash
# Make sure virtual environment is activated first!
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Then run the dashboard
streamlit run portfolio_dashboard.py
```

### Getting Started

1. **Create a Portfolio**: Use the sidebar to create a new portfolio (e.g., "Brazilian", "US", "Tech Stocks")
2. **Add Stocks**: Select your portfolio and use the "Add/Update Stock" section to add your holdings
   - For US stocks: Use ticker symbols like `AAPL`, `GOOGL`, `MSFT`
   - For Brazilian stocks: Use ticker symbols like `PETR4`, `VALE3`, `ITUB4`
3. **Monitor Performance**: The dashboard will automatically fetch real-time data and display your portfolio performance
4. **Explore AI Features**: Scroll down to the "🤖 AI-Powered Portfolio Insights" section to:
   - Get comprehensive portfolio analysis with Ollama (local AI)
   - View smart trading signals and recommendations
   - Analyze news sentiment with Google Gemini
5. **Check News Feed**: View the latest news for your portfolio stocks with AI sentiment analysis

### Stock Ticker Format

- **US Stocks**: Use the standard ticker symbol (e.g., `AAPL` for Apple)
- **Brazilian Stocks**: Use the ticker without the `.SA` suffix (e.g., `PETR4` for Petrobras) - the system will automatically add the `.SA` suffix when fetching data from Brazilian portfolios

## Data Sources

### Stock Data

- **Primary**: Yahoo Finance (via `yfinance` library)
- **Fallback APIs**: Alpha Vantage, Twelve Data (with API keys)
- **Real-Time Updates**: Prices are fetched in real-time when the dashboard loads
- **Market Support**: US stocks and Brazilian stocks (B3 exchange)

### News Data

- **Primary**: NewsAPI (100 requests/day free tier)
- **Fallback**: Alpha Vantage News API, web scraping
- **AI Analysis**: Google Gemini for sentiment analysis

### AI Services

- **Local AI**: Ollama with LLaMA 3.2 (completely free, no limits)
- **Cloud AI**: Google Gemini (free tier: 15 requests/minute)
- **Technical Analysis**: TA-Lib for advanced indicators

## File Structure

```
portfolio_dashboard.py          # Main dashboard application
portfolios.json                # Your portfolio data (auto-created)
requirements.txt               # Python dependencies
README.md                      # This documentation
SETUP.md                       # Detailed setup instructions
DEVELOPMENT_HISTORY.md         # Development timeline and changes
.env                          # API keys (create this file)
.gitignore                    # Git ignore patterns
```

## Portfolio Data Format

Your portfolio data is stored in `portfolios.json` with the following structure:

```json
{
  "Brazilian": {
    "PETR4": {
      "quantity": 100,
      "avg_price": 25.5,
      "date_added": "2024-01-15T10:30:00"
    }
  },
  "US": {
    "AAPL": {
      "quantity": 50,
      "avg_price": 150.75,
      "date_added": "2024-01-20T14:20:00"
    }
  }
}
```

## Features Comparison: Spreadsheet vs Dashboard

| Feature              | Google Spreadsheet    | Portfolio Dashboard    |
| -------------------- | --------------------- | ---------------------- |
| Real-time prices     | Manual refresh needed | Automatic fetching     |
| Portfolio analytics  | Manual calculations   | Automatic calculations |
| Visual charts        | Limited/manual        | Interactive charts     |
| Multiple portfolios  | Multiple sheets       | Built-in support       |
| Data persistence     | Cloud-based           | Local JSON file        |
| Performance tracking | Manual tracking       | Automatic metrics      |
| Mobile-friendly      | Limited               | Responsive design      |

## ✅ Recently Added Features

- ✅ **AI-Powered Analysis**: Ollama + LLaMA 3.2 for local portfolio insights
- ✅ **News Integration**: Real-time news feed with sentiment analysis
- ✅ **Technical Charts**: Advanced candlestick charts with indicators
- ✅ **Smart Trading Signals**: AI-generated recommendations
- ✅ **Multi-Source Data**: Fallback APIs for reliable data fetching
- ✅ **Sector Analysis**: Real-time sector information for all stocks
- ✅ **Dividend Tracking**: Dividend yields and annual dividend amounts
- ✅ **Enhanced Data Fetching**: Improved Yahoo Finance integration for comprehensive stock data
- ✅ **Cache Management**: Utility script for clearing Streamlit cache during development

## 🚀 Planned Features (Future Updates)

- 📊 **Advanced Analytics**: More sophisticated portfolio analysis
- 💾 **Export Features**: Export data to Excel/CSV
- 🔔 **Alerts**: Price and performance alerts
- 📱 **Mobile App**: React Native companion app
- 🌐 **Web Deployment**: Cloud-hosted version

## Troubleshooting

### Common Issues

1. **Stock data not loading**:

   - Check your internet connection
   - Verify the ticker symbol is correct
   - For Brazilian stocks, ensure you're using the correct B3 ticker format

2. **Portfolio not saving**:

   - Make sure you have write permissions in the application directory
   - Check if `portfolios.json` file can be created/modified

3. **Performance issues**:

   - Disable auto-refresh if you have many stocks
   - Consider splitting large portfolios into smaller ones

4. **Code changes not showing**:
   - Run the cache clearing utility: `python3 clear_cache.py`
   - Restart the Streamlit app: `streamlit run portfolio_dashboard.py`
   - Clear browser cache if issues persist

### Error Messages

- `"Error fetching data for [TICKER]"`: The ticker symbol might be incorrect or the stock might be delisted
- `"Portfolio already exists!"`: You're trying to create a portfolio with a name that already exists

## Support

For issues or feature requests related to this dashboard, please check the existing codebase or create an issue in the project repository.

## License

This project is based on the DeepCharts YouTube channel educational content and is intended for personal portfolio management use.
