# Project Structure Documentation

## 📁 **New Organized Structure**

The project has been refactored from a single large file (`portfolio_dashboard.py`) into a clean, modular structure:

```
stocks-portfolio-dashboard/
├── app/                          # Main application
│   ├── __init__.py
│   ├── main.py                   # Main Streamlit application
│   ├── config.py                 # Configuration and constants
│   └── utils.py                  # Utility functions
├── core/                         # Core business logic
│   ├── __init__.py
│   ├── portfolio_manager.py      # Portfolio management
│   ├── data_fetcher.py           # Data fetching functions
│   └── analytics.py              # Portfolio analytics
├── ui/                           # User interface components
│   ├── __init__.py
│   ├── components.py             # Reusable UI components
│   └── charts.py                 # Chart creation functions
├── data/                         # Data layer
│   ├── __init__.py
│   ├── apis/                     # API-specific modules
│   │   ├── __init__.py
│   │   ├── yahoo_finance.py       # Yahoo Finance API
│   │   ├── twelve_data.py        # Twelve Data API
│   │   ├── alpha_vantage.py      # Alpha Vantage API
│   │   └── brapi.py              # BRAPI for Brazilian stocks
│   └── models.py                 # Data models (future)
├── ai/                           # AI integration
│   ├── __init__.py
│   ├── ollama_client.py          # Ollama AI client
│   └── gemini_client.py          # Google Gemini client
├── tests/                        # Test files
│   ├── __init__.py
│   ├── test_portfolio.py         # Portfolio tests
│   └── test_data_fetcher.py      # Data fetcher tests
├── requirements.txt
├── portfolios.json
├── README.md
├── SETUP.md
├── DEVELOPMENT_HISTORY.md
└── PROJECT_STRUCTURE.md          # This file
```

## 🎯 **Module Responsibilities**

### **App Layer (`app/`)**
- **`main.py`**: Main Streamlit application entry point
- **`config.py`**: All configuration, constants, and settings
- **`utils.py`**: Common utility functions

### **Core Layer (`core/`)**
- **`portfolio_manager.py`**: Portfolio CRUD operations, persistence
- **`data_fetcher.py`**: Stock data fetching with multiple API fallbacks
- **`analytics.py`**: Portfolio metrics, risk analysis, performance calculations

### **UI Layer (`ui/`)**
- **`components.py`**: Reusable Streamlit components (tables, metrics, forms)
- **`charts.py`**: Specialized chart creation functions

### **Data Layer (`data/`)**
- **`apis/`**: API-specific implementations
  - **`yahoo_finance.py`**: Yahoo Finance integration
  - **`twelve_data.py`**: Twelve Data API integration
  - **`alpha_vantage.py`**: Alpha Vantage API integration
  - **`brapi.py`**: BRAPI for Brazilian stocks

### **AI Layer (`ai/`)**
- **`ollama_client.py`**: Local AI analysis using Ollama
- **`gemini_client.py`**: Google Gemini AI integration

### **Tests (`tests/`)**
- **`test_portfolio.py`**: Portfolio manager tests
- **`test_data_fetcher.py`**: Data fetching tests

## 🚀 **Benefits of New Structure**

### **1. Maintainability**
- **Single Responsibility**: Each module has a clear, focused purpose
- **Easy Navigation**: Find code quickly by functionality
- **Reduced Complexity**: Smaller, manageable files

### **2. Scalability**
- **Modular Design**: Add new features without affecting existing code
- **API Extensions**: Easy to add new data sources
- **UI Components**: Reusable components for new features

### **3. Testing**
- **Unit Tests**: Test individual modules in isolation
- **Integration Tests**: Test module interactions
- **Mock Testing**: Easy to mock dependencies

### **4. Development**
- **Parallel Development**: Multiple developers can work on different modules
- **Code Reviews**: Smaller, focused changes
- **Debugging**: Easier to isolate and fix issues

## 📋 **Migration Guide**

### **From Old Structure**
The original `portfolio_dashboard.py` (2,739 lines) has been split into:

1. **Portfolio Management** → `core/portfolio_manager.py`
2. **Data Fetching** → `core/data_fetcher.py` + `data/apis/*.py`
3. **UI Components** → `ui/components.py` + `ui/charts.py`
4. **Analytics** → `core/analytics.py`
5. **AI Integration** → `ai/ollama_client.py` + `ai/gemini_client.py`
6. **Configuration** → `app/config.py`
7. **Main App** → `app/main.py`

### **Running the Application**
```bash
# Old way
streamlit run portfolio_dashboard.py

# New way
streamlit run app/main.py
```

### **Import Changes**
```python
# Old imports
from portfolio_dashboard import PortfolioManager, fetch_stock_data

# New imports
from core.portfolio_manager import PortfolioManager
from core.data_fetcher import fetch_stock_data
```

## 🔧 **Development Workflow**

### **Adding New Features**
1. **Data Sources**: Add to `data/apis/`
2. **UI Components**: Add to `ui/components.py`
3. **Analytics**: Add to `core/analytics.py`
4. **AI Features**: Add to `ai/`

### **Testing**
```bash
# Run specific tests
python tests/test_portfolio.py

# Run all tests
python -m pytest tests/
```

### **Configuration**
All configuration is centralized in `app/config.py`:
- API keys
- Market configurations
- Cache settings
- Rate limits

## 📊 **File Size Comparison**

| Module | Lines | Purpose |
|--------|-------|---------|
| **Original** | 2,739 | Everything in one file |
| **app/main.py** | ~150 | Main application |
| **core/portfolio_manager.py** | ~100 | Portfolio management |
| **core/data_fetcher.py** | ~300 | Data fetching |
| **core/analytics.py** | ~200 | Analytics |
| **ui/components.py** | ~250 | UI components |
| **ui/charts.py** | ~200 | Charts |
| **data/apis/*.py** | ~150 each | API modules |
| **ai/*.py** | ~200 each | AI modules |

**Total**: ~1,500 lines (45% reduction in main files)

## 🎯 **Next Steps**

1. **Test the refactored application**
2. **Update documentation**
3. **Add more comprehensive tests**
4. **Optimize performance**
5. **Add new features to specific modules**

---

*This structure makes the project much more maintainable and scalable for future development.*
