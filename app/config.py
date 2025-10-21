"""
Configuration and constants for the Portfolio Management Dashboard
"""

import os
from typing import Dict, List

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Page configuration
PAGE_CONFIG = {
    "page_title": "Portfolio Management Dashboard",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# API Configuration
API_KEYS = {
    "TWELVE_DATA_API_KEY": os.getenv("TWELVE_DATA_API_KEY"),
    "ALPHA_VANTAGE_API_KEY": os.getenv("ALPHA_VANTAGE_API_KEY"),
    "BRAPI_API_KEY": os.getenv("BRAPI_API_KEY"),
    "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
}

# Telegram Configuration
TELEGRAM_CONFIG = {
    "API_ID": os.getenv("TELEGRAM_API_ID"),
    "API_HASH": os.getenv("TELEGRAM_API_HASH"),
    "PHONE": os.getenv("TELEGRAM_PHONE"),
    "SESSION_NAME": "telegram_session",
    "BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "BOT_USERNAME": os.getenv("TELEGRAM_BOT_USERNAME", "your_bot_username"),
    "BOT_URL": os.getenv("TELEGRAM_BOT_URL", "https://t.me/your_bot_username"),
    "DEFAULT_CHANNELS": [
        "@stocknews",
        "@brstocks",
        "@fiidiscussion",
        "@usstocks"
    ],
    "MONITORING_INTERVAL": 300,  # 5 minutes in seconds
    "MESSAGE_LIMIT": 100,
    "RETENTION_DAYS": 7
}

# Brazilian sector mappings (fallback when live data unavailable)
BRAZILIAN_SECTORS = {
    # Financial Services
    "ITUB4": "Financial Services", "ITUB3": "Financial Services",
    "BBDC4": "Financial Services", "BBDC3": "Financial Services",
    "SANB11": "Financial Services", "SANB3": "Financial Services",
    "BBAS3": "Financial Services", "ABCB4": "Financial Services",
    "ITSA4": "Financial Services", "ITSA3": "Financial Services",
    "FESA4": "Financial Services", "FESA3": "Financial Services",
    "ISAE4": "Financial Services",

    # Energy
    "PETR4": "Energy", "PETR3": "Energy", "PRIO3": "Energy",
    "3R11": "Energy", "RRRP3": "Energy", "VBBR3": "Energy",

    # Mining/Materials
    "VALE3": "Materials", "CSNA3": "Materials", "USIM5": "Materials",
    "GGBR4": "Materials", "GGBR3": "Materials", "CSAN3": "Materials",
    "GOAU4": "Materials",

    # Utilities
    "EGIE3": "Utilities", "CPLE6": "Utilities", "CPLE3": "Utilities",
    "ELET3": "Utilities", "ELET6": "Utilities", "ENBR3": "Utilities",
    "UNIP6": "Utilities", "UNIP3": "Utilities",

    # Real Estate
    "VAMO3": "Real Estate", "BRML3": "Real Estate", "CYRE3": "Real Estate",
    "JHSF3": "Real Estate", "MULT3": "Real Estate", "BRPR3": "Real Estate",

    # Consumer Goods
    "ABEV3": "Consumer Staples", "JBSS3": "Consumer Staples",
    "MRFG3": "Consumer Staples", "RADL3": "Consumer Staples",

    # Technology
    "TOTS3": "Technology", "LWSA3": "Technology", "POSI3": "Technology",

    # Telecommunications
    "VIVT3": "Telecommunications", "VIVT4": "Telecommunications",
    "TIMS3": "Telecommunications", "OIBR3": "Telecommunications",

    # Healthcare
    "PSSA3": "Healthcare", "RDOR3": "Healthcare", "QUAL3": "Healthcare",

    # Industrial
    "WEGE3": "Industrials", "EMBR3": "Industrials", "RENT3": "Industrials",
    "SAPR4": "Industrials", "SAPR3": "Industrials", "EZTC3": "Industrials",

    # Retail
    "MGLU3": "Consumer Discretionary", "LREN3": "Consumer Discretionary",
    "VVAR3": "Consumer Discretionary", "AMER3": "Consumer Discretionary",
}

# US sector mappings (fallback when live data unavailable)
US_SECTORS = {
    "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology",
    "AMZN": "Consumer Discretionary", "TSLA": "Consumer Discretionary",
    "META": "Technology", "NVDA": "Technology", "NFLX": "Communication Services",
    "JPM": "Financial Services", "BAC": "Financial Services",
    "WMT": "Consumer Staples", "PG": "Consumer Staples",
    "JNJ": "Healthcare", "PFE": "Healthcare", "UNH": "Healthcare",
    "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
    "KO": "Consumer Staples", "PEP": "Consumer Staples",
    "DIS": "Communication Services", "CMCSA": "Communication Services",
    # Portfolio stocks
    "WBD": "Communication Services",  # Warner Bros Discovery
    "LIT": "Technology",  # Global X Lithium & Battery Tech ETF
    "TLT": "Financial Services",  # iShares 20+ Year Treasury Bond ETF
    "QQQ": "Technology",  # Invesco QQQ Trust (NASDAQ 100)
    "SOXX": "Technology",  # iShares Semiconductor ETF
    "VNQ": "Real Estate",  # Vanguard Real Estate ETF
    "SGOV": "Financial Services",  # iShares 0-3 Month Treasury Bond ETF
    "BRK.B": "Financial Services",  # Berkshire Hathaway Class B
    "XLE": "Energy",  # Energy Select Sector SPDR Fund
    "XLV": "Healthcare",  # Health Care Select Sector SPDR Fund
    "HDV": "Consumer Staples",  # iShares Core High Dividend ETF
    "LTC": "Real Estate",  # LTC Properties (REIT)
    "CQQQ": "Technology",  # Invesco China Technology ETF
    "APPS": "Technology",  # Digital Turbine
}

# Brazilian dividend yield mappings (fallback when live data unavailable)
BRAZILIAN_DIVIDEND_YIELDS = {
    "ITUB4": 8.5, "ITUB3": 8.5,  # Itaú
    "BBDC4": 7.2, "BBDC3": 7.2,  # Bradesco
    "VALE3": 6.8,  # Vale
    "PETR4": 5.5, "PETR3": 5.5,  # Petrobras
    "ABEV3": 4.2,  # Ambev
    "WEGE3": 3.8,  # WEG
    "MGLU3": 2.1,  # Magazine Luiza
    "VIVT3": 3.5,  # Vivo
    "EGIE3": 4.8,  # Engie Brasil
    "CPLE6": 5.2, "CPLE3": 5.2,  # Copel
    "UNIP6": 4.1, "UNIP3": 4.1,  # Unipar
    "PSSA3": 2.8,  # Porto Seguro
    "SAPR4": 3.2, "SAPR3": 3.2,  # Sanepar
    "VBBR3": 6.5,  # Vale Brasil
    "CSAN3": 4.5,  # Companhia Siderúrgica Nacional
    "ISAE4": 5.8,  # Isae
    "GOAU4": 3.9,  # Gerdau
    "FESA4": 6.2, "FESA3": 6.2,  # Fesa
    "ITSA4": 7.8, "ITSA3": 7.8,  # Itaúsa
    "SANB11": 6.05,  # Santander - from your example
    "PRIO3": 0.0,  # PetroRio - might not pay dividends
    # Acoes_B3 Portfolio - Updated from spreadsheet
    "VAMO3": 0.0,  # Vamos - no dividend yield
    "EGIE3": 4.8,  # Engie Brasil
    "VBBR3": 6.5,  # Vale Brasil
    "CSAN3": 4.5,  # Companhia Siderúrgica Nacional
    "ISAE4": 5.8,  # Isae
    "SAPR4": 3.2, "SAPR3": 3.2,  # Sanepar
    "GOAU4": 3.9,  # Gerdau
    "PSSA3": 2.8,  # Porto Seguro
    "CPLE6": 5.2, "CPLE3": 5.2,  # Copel
    "UNIP6": 4.1, "UNIP3": 4.1,  # Unipar
    "VIVT3": 3.5,  # Vivo
    "FESA4": 6.2, "FESA3": 6.2,  # Fesa
    # FII Portfolio - Real Estate Investment Funds (Updated from spreadsheet)
    "VISC11": 8.84,  # Vinci Shopping Centers
    "HGLG11": 8.23,  # CSHG Logística
    "HGRU11": 9.96,  # CSHG Renda Urbana
    "BTLG11": 9.10,  # BTG Pactual Logística
    "KNCR11": 13.20,  # Kinea Renda Imobiliária
    "XPLG11": 9.72,  # XP Log
    "MXRF11": 12.03,  # Maxi Renda
    "RZTR11": 13.65,  # Riza Terrax
    "HCTR11": 17.25,  # Hectare CE
    "CPTI11": 14.61,  # Capitania Securities II
}

# Brazilian Price-to-Book ratio mappings (fallback when live data unavailable)
BRAZILIAN_PB_RATIOS = {
    # Acoes_B3 Portfolio - Updated from spreadsheet
    "VAMO3": 0.0,  # Vamos - no P/B data
    "SANB11": 0.0,  # Santander - no P/B data
    "EGIE3": 1.2,  # Engie Brasil
    "VBBR3": 0.8,  # Vale Brasil
    "CSAN3": 0.9,  # Companhia Siderúrgica Nacional
    "ISAE4": 1.1,  # Isae
    "SAPR4": 1.3, "SAPR3": 1.3,  # Sanepar
    "PRIO3": 2.1,  # PetroRio
    "GOAU4": 0.7,  # Gerdau
    "PSSA3": 1.4,  # Porto Seguro
    "CPLE6": 1.0, "CPLE3": 1.0,  # Copel
    "UNIP6": 1.5, "UNIP3": 1.5,  # Unipar
    "VIVT3": 1.8,  # Vivo
    "FESA4": 0.9, "FESA3": 0.9,  # Fesa
    "ITSA4": 0.6, "ITSA3": 0.6,  # Itaúsa
    # FII Portfolio - Real Estate Investment Funds (typically higher P/B)
    "VISC11": 1.1,  # Vinci Shopping Centers
    "HGLG11": 1.0,  # CSHG Logística
    "HGRU11": 1.2,  # CSHG Renda Urbana
    "BTLG11": 1.3,  # BTG Pactual Logística
    "KNCR11": 1.1,  # Kinea Renda Imobiliária
    "XPLG11": 1.0,  # XP Log
    "MXRF11": 1.2,  # Maxi Renda
    "RZTR11": 1.1,  # Riza Terrax
    "HCTR11": 1.0,  # Hectare CE
    "CPTI11": 1.2,  # Capitania Securities II
}

# US Price-to-Book ratio mappings (fallback when live data unavailable)
US_PB_RATIOS = {
    "AAPL": 45.2, "MSFT": 12.8, "GOOGL": 6.1,
    "AMZN": 8.5, "TSLA": 12.3, "META": 7.2,
    "NVDA": 25.4, "NFLX": 6.8, "JPM": 1.4,
    "BAC": 1.2, "WMT": 5.1, "PG": 4.8,
    "JNJ": 4.2, "PFE": 1.8, "UNH": 5.9,
    "XOM": 2.1, "CVX": 1.8, "COP": 2.3,
    "KO": 9.8, "PEP": 2.9, "DIS": 2.1,
    "CMCSA": 2.4,
    # Portfolio stocks
    "WBD": 0.8,  # Warner Bros Discovery
    "LIT": 1.2,  # Global X Lithium & Battery Tech ETF
    "TLT": 0.0,  # iShares 20+ Year Treasury Bond ETF (bond fund)
    "QQQ": 4.2,  # Invesco QQQ Trust
    "SOXX": 3.8,  # iShares Semiconductor ETF
    "VNQ": 2.1,  # Vanguard Real Estate ETF
    "SGOV": 0.0,  # iShares 0-3 Month Treasury Bond ETF (bond fund)
    "BRK.B": 1.4,  # Berkshire Hathaway Class B
    "XLE": 1.8,  # Energy Select Sector SPDR Fund
    "XLV": 4.2,  # Health Care Select Sector SPDR Fund
    "HDV": 2.8,  # iShares Core High Dividend ETF
    "LTC": 1.9,  # LTC Properties (REIT)
    "CQQQ": 1.5,  # Invesco China Technology ETF
    "APPS": 2.3,  # Digital Turbine
}

# US dividend yield mappings (fallback when live data unavailable)
US_DIVIDEND_YIELDS = {
    "AAPL": 0.5, "MSFT": 0.7, "GOOGL": 0.0,
    "AMZN": 0.0, "TSLA": 0.0, "META": 0.0,
    "NVDA": 0.1, "NFLX": 0.0, "JPM": 2.5,
    "BAC": 2.8, "WMT": 1.4, "PG": 2.5,
    "JNJ": 2.9, "PFE": 3.2, "UNH": 1.4,
    "XOM": 3.1, "CVX": 3.8, "COP": 1.2,
    "KO": 3.0, "PEP": 2.7, "DIS": 0.0,
    "CMCSA": 2.8,
    # Portfolio stocks (Updated from spreadsheet)
    "DIS": 0.65,  # Disney
    "WBD": 0.0,  # Warner Bros Discovery (no dividend)
    "LIT": 1.15,  # Global X Lithium & Battery Tech ETF
    "TLT": 3.34,  # iShares 20+ Year Treasury Bond ETF
    "QQQ": 0.57,  # Invesco QQQ Trust
    "SOXX": 0.63,  # iShares Semiconductor ETF
    "VNQ": 3.91,  # Vanguard Real Estate ETF (REIT ETF, good dividend)
    "SGOV": 4.14,  # iShares 0-3 Month Treasury Bond ETF
    "BRK.B": 3.34,  # Berkshire Hathaway Class B
    "CMCSA": 3.28,  # Comcast Corporation
    "XLE": 3.27,  # Energy Select Sector SPDR Fund (energy sector, good dividend)
    "XLV": 1.63,  # Health Care Select Sector SPDR Fund (healthcare, moderate dividend)
    "HDV": 3.67,  # iShares Core High Dividend ETF (high dividend focused)
    "JNJ": 3.45,  # Johnson & Johnson
    "LTC": 6.33,  # LTC Properties (REIT, high dividend)
    "CQQQ": 0.27,  # Invesco China Technology ETF
    "APPS": 0.0,  # Digital Turbine (growth stock, no dividend)
}

# Market configurations
MARKET_CONFIGS = {
    "Brazilian": {
        "exchanges": ["B3", "OTC"],
        "currency": "BRL",
        "ticker_suffix": ".SA"
    },
    "US": {
        "exchanges": ["NYSE", "NASDAQ"],
        "currency": "USD",
        "ticker_suffix": ""
    }
}

# Default portfolio structure
DEFAULT_PORTFOLIOS = {
    "Brazilian_B3": {},
    "US_NYSE": {}
}

# Cache TTL settings (in seconds)
CACHE_TTL = {
    "stock_data": 1800,      # 30 minutes
    "portfolio_data": 1800,  # 30 minutes
    "news_data": 1800,      # 30 minutes
    "ai_analysis": 3600,    # 1 hour
}

# API rate limiting
RATE_LIMITS = {
    "yahoo_finance": 0.5,   # 500ms between calls
    "twelve_data": 1.0,     # 1 second between calls
    "alpha_vantage": 2.0,   # 2 seconds between calls
    "brapi": 0.5,           # 500ms between calls
}

# Technical analysis settings
TECHNICAL_ANALYSIS = {
    "sma_periods": [20, 50],
    "ema_periods": [20],
    "rsi_period": 14,
    "bollinger_period": 20,
    "macd_periods": [12, 26, 9]
}
