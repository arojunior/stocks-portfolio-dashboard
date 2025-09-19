# Portfolio Management Dashboard

A comprehensive multi-portfolio management dashboard that replaces your Google Spreadsheet for tracking stock investments across different markets (Brazilian and US stocks).

## Features

### 🚀 Core Features
- **Multi-Portfolio Support**: Manage separate portfolios for different markets (Brazilian, US, or custom portfolios)
- **Real-Time Data**: Automatic fetching of current stock prices, daily changes, and market data
- **Portfolio Analytics**: Comprehensive metrics including total returns, best/worst performers, and portfolio composition
- **Interactive Visualizations**: Pie charts for portfolio composition and bar charts for performance analysis
- **Persistent Storage**: Your portfolio data is saved locally in JSON format

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

#### Stock Management
- Add new stocks with ticker, quantity, and average price
- Update existing stock positions
- Remove stocks from portfolio
- Support for both US stocks (e.g., AAPL) and Brazilian stocks (e.g., PETR4)

## Installation

### Prerequisites
- Python 3.8 or higher
- Git

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
```

> 📋 **See [SETUP.md](SETUP.md) for detailed installation instructions and troubleshooting.**

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

### Stock Ticker Format
- **US Stocks**: Use the standard ticker symbol (e.g., `AAPL` for Apple)
- **Brazilian Stocks**: Use the ticker without the `.SA` suffix (e.g., `PETR4` for Petrobras) - the system will automatically add the `.SA` suffix when fetching data from Brazilian portfolios

## Data Sources

- **Stock Data**: Yahoo Finance (via `yfinance` library)
- **Real-Time Updates**: Prices are fetched in real-time when the dashboard loads
- **Market Support**: US stocks and Brazilian stocks (B3 exchange)

## File Structure

```
portfolio_dashboard.py          # Main dashboard application
portfolios.json                # Your portfolio data (auto-created)
requirements.txt               # Python dependencies
README_PORTFOLIO.md            # This documentation
```

## Portfolio Data Format

Your portfolio data is stored in `portfolios.json` with the following structure:
```json
{
  "Brazilian": {
    "PETR4": {
      "quantity": 100,
      "avg_price": 25.50,
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

| Feature | Google Spreadsheet | Portfolio Dashboard |
|---------|-------------------|-------------------|
| Real-time prices | Manual refresh needed | Automatic fetching |
| Portfolio analytics | Manual calculations | Automatic calculations |
| Visual charts | Limited/manual | Interactive charts |
| Multiple portfolios | Multiple sheets | Built-in support |
| Data persistence | Cloud-based | Local JSON file |
| Performance tracking | Manual tracking | Automatic metrics |
| Mobile-friendly | Limited | Responsive design |

## Planned Features (Future Updates)

Based on your specifications, these features will be added in future versions:
- 📈 **Interactive Charts**: Detailed price charts for individual stocks
- 📰 **News Integration**: Latest news for stocks in your portfolio
- 🤖 **AI Predictions**: Stock price predictions using machine learning
- 📊 **Advanced Analytics**: More sophisticated portfolio analysis
- 💾 **Export Features**: Export data to Excel/CSV
- 🔔 **Alerts**: Price and performance alerts

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

### Error Messages

- `"Error fetching data for [TICKER]"`: The ticker symbol might be incorrect or the stock might be delisted
- `"Portfolio already exists!"`: You're trying to create a portfolio with a name that already exists

## Support

For issues or feature requests related to this dashboard, please check the existing codebase or create an issue in the project repository.

## License

This project is based on the DeepCharts YouTube channel educational content and is intended for personal portfolio management use.

