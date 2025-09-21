# Portfolio Dashboard Setup Guide

## Prerequisites

- Python 3.8 or higher
- Git
- **For Enhanced Data Sources (Optional)**:
  - BRAPI API key (Brazilian stocks - free)
  - Twelve Data API key (premium stock data)
  - Alpha Vantage API key (premium stock data + news)
  - NewsAPI key (news feed)
- **For AI Features (Recommended)**:
  - Ollama (for local AI analysis)
  - Google Gemini API key (for news sentiment analysis)
  - Homebrew (macOS) or equivalent package manager

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd stocks-portfolio-dashboard
```

### 2. Create Virtual Environment

**Always use a virtual environment for Python projects!**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

### 4. Set Up AI Features (Recommended)

#### 4.1 Install Ollama (Local AI - Completely Free)

```bash
# macOS (using Homebrew)
brew install ollama

# Start Ollama service
brew services start ollama

# Download LLaMA 3.2 model (2GB download)
ollama pull llama3.2

# Test Ollama installation
ollama run llama3.2 "Hello! Can you help me analyze stock portfolios?"
```

**For other platforms:**

- **Linux**: `curl -fsSL https://ollama.ai/install.sh | sh`
- **Windows**: Download from https://ollama.ai/download

#### 4.2 Configure API Keys (Optional but Recommended)

Create a `.env` file in the project root:

```bash
        # Create .env file with your API keys
        echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
        echo "NEWSAPI_KEY=your_newsapi_key_here" >> .env
        echo "ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here" >> .env
        echo "TWELVE_DATA_API_KEY=your_twelve_data_key_here" >> .env
        echo "BRAPI_API_KEY=your_brapi_api_key_here" >> .env
```

**How to get API keys:**

- **Google Gemini**: https://makersuite.google.com/app/apikey (Free tier: 15 requests/minute)
- **NewsAPI**: https://newsapi.org/register (Free tier: 100 requests/day)
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key (Free tier: 25 requests/day)
- **Twelve Data**: https://twelvedata.com/pricing (Free tier: 8 requests/minute)
- **BRAPI**: https://brapi.dev/dashboard (Brazilian stocks, enhanced features with API key)

### 5. Run the Dashboard

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the dashboard
streamlit run portfolio_dashboard.py
```

The dashboard will be available at `http://localhost:8501`

### 6. Development Tools (Optional)

```bash
# Clear Streamlit cache when making code changes
python3 clear_cache.py

# This helps ensure your code updates are visible immediately
```

## 🤖 AI Features Overview

### Local AI (Ollama + LLaMA 3.2)

- ✅ **Completely free** - no API costs ever
- ✅ **No rate limits** - analyze as much as you want
- ✅ **Privacy-focused** - data stays on your machine
- ✅ **Professional-grade** analysis
- ✅ **Works offline**

### Cloud AI (Google Gemini)

- 📰 **News sentiment analysis**
- 🌐 **Real-time market insights**
- 🔄 **Free tier**: 15 requests/minute
- 💡 **Advanced reasoning** capabilities

## Virtual Environment Management

### Activating the Environment

**Always activate the virtual environment before working on the project:**

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Deactivating the Environment

```bash
deactivate
```

### Updating Dependencies

```bash
# Activate environment first
source venv/bin/activate

# Install new packages
pip install <package-name>

# Update requirements.txt
pip freeze > requirements.txt
```

## Project Structure

```
stocks-portfolio-dashboard/
├── venv/                      # Virtual environment (not committed)
├── portfolio_dashboard.py     # Main application
├── requirements.txt          # Python dependencies
├── portfolios.json           # User data (created at runtime)
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── SETUP.md                 # This setup guide
└── DEVELOPMENT_HISTORY.md   # Development timeline
```

## Troubleshooting

### Virtual Environment Issues

- **Command not found**: Ensure Python is installed and in PATH
- **Permission denied**: Use `python3 -m venv venv` instead of `python -m venv venv`
- **Module not found**: Ensure virtual environment is activated before installing packages

### Streamlit Issues

- **Port already in use**: Use `streamlit run portfolio_dashboard.py --server.port 8502`
- **Module import errors**: Verify all dependencies are installed in the active virtual environment

### API Issues

- **No stock data**: Check internet connection and API rate limits
- **Brazilian stocks not found**: Ensure ticker format is correct (e.g., PETR4, not PETR4.SA)

### AI Setup Issues

#### Ollama Troubleshooting

- **Ollama not found**: Ensure Ollama is installed and in PATH
- **Service not running**: Run `brew services start ollama` (macOS) or `ollama serve` (other platforms)
- **Model not found**: Run `ollama pull llama3.2` to download the model
- **Connection refused**: Check if Ollama is running on `http://localhost:11434`

#### Google Gemini Issues

- **API key invalid**: Verify your Gemini API key at https://makersuite.google.com/app/apikey
- **Rate limit exceeded**: Free tier allows 15 requests/minute
- **Module not found**: Ensure `google-generativeai` is installed: `pip install google-generativeai`

#### General AI Issues

- **AI section not showing**: Check if `.env` file exists and contains valid API keys
- **Analysis taking too long**: Local AI (Ollama) may take 10-30 seconds for first analysis
- **No AI insights**: Ensure you have stocks in your portfolio before running AI analysis

### Development Issues

#### Code Changes Not Showing

- **Sector/dividend data not updating**: Run `python3 clear_cache.py` to clear Streamlit cache
- **UI not reflecting changes**: Restart the Streamlit app after clearing cache
- **Cache clearing fails**: Ensure you have write permissions in the project directory

## Best Practices

### Always Use Virtual Environments

- ✅ **Isolates project dependencies** from system Python
- ✅ **Prevents version conflicts** between projects
- ✅ **Makes deployment reproducible**
- ✅ **Easier to manage requirements**

### Development Workflow

1. Activate virtual environment
2. Make code changes
3. Test functionality
4. Update requirements if needed
5. Commit changes
6. Deactivate environment when done

### Before Committing

```bash
# Ensure virtual environment is active
source venv/bin/activate

# Update requirements.txt if you added packages
pip freeze > requirements.txt

# Test the application
streamlit run portfolio_dashboard.py
```

## 🎯 Quick Start Checklist

### Essential Setup (5 minutes)

- [ ] Clone repository
- [ ] Create virtual environment (`python -m venv venv`)
- [ ] Activate environment (`source venv/bin/activate`)
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Run dashboard (`streamlit run portfolio_dashboard.py`)

### AI Features Setup (10 minutes)

- [ ] Install Ollama (`brew install ollama`)
- [ ] Start Ollama service (`brew services start ollama`)
- [ ] Download LLaMA model (`ollama pull llama3.2`)
- [ ] Get Google Gemini API key (https://makersuite.google.com/app/apikey)
- [ ] Create `.env` file with API keys
- [ ] Test AI features in dashboard

### Optional Enhancements

- [ ] Get NewsAPI key for better news coverage
- [ ] Get Alpha Vantage key for additional stock data
- [ ] Get Twelve Data key for Brazilian stocks

## Environment Variables Reference

```bash
        # .env file - Copy this template and add your keys
        GOOGLE_API_KEY=your_gemini_api_key_here
        NEWSAPI_KEY=your_newsapi_key_here
        ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
        TWELVE_DATA_API_KEY=your_twelve_data_key_here
        BRAPI_API_KEY=your_brapi_api_key_here
```

## 🚀 What You Get

### Without AI Setup

- ✅ Multi-portfolio management
- ✅ Real-time stock prices
- ✅ Portfolio analytics and charts
- ✅ News feed (limited)
- ✅ Sector analysis and dividend tracking
- ✅ Enhanced data fetching with Yahoo Finance

### With AI Setup

- ✅ **Everything above, plus:**
- 🤖 **Professional portfolio analysis**
- 📈 **AI trading signals**
- 📰 **Smart news sentiment analysis**
- 📊 **Advanced technical charts**
- 💡 **Investment recommendations**

---

**Remember: Always activate your virtual environment before working on the project!** 🐍✨

**Pro Tip: The AI features transform this from a simple tracker into a professional-grade portfolio analysis tool!** 🚀
