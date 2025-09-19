# Portfolio Dashboard Setup Guide

## Prerequisites
- Python 3.8 or higher
- Git

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

### 4. Run the Dashboard
```bash
streamlit run portfolio_dashboard.py
```

The dashboard will be available at `http://localhost:8501`

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

## Environment Variables (Optional)
Create a `.env` file for API keys (not committed to git):
```bash
# .env file
ALPHA_VANTAGE_API_KEY=your_key_here
TWELVE_DATA_API_KEY=your_key_here
```

Load in Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
```

---

**Remember: Always activate your virtual environment before working on the project!** 🐍✨
