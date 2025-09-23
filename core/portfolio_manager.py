"""
Portfolio Management System
Handles multiple stock portfolios with persistent storage
"""

import json
import os
import streamlit as st
from datetime import datetime
from typing import Dict, List
from app.config import DEFAULT_PORTFOLIOS


class PortfolioManager:
    """Manages multiple stock portfolios with persistent storage"""

    def __init__(self):
        self.portfolios_file = "portfolios.json"
        self.load_portfolios()

    def load_portfolios(self):
        """Load portfolios from JSON file"""
        if os.path.exists(self.portfolios_file):
            with open(self.portfolios_file, "r") as f:
                self.portfolios = json.load(f)
        else:
            # Initialize with default portfolios
            self.portfolios = DEFAULT_PORTFOLIOS.copy()

    def get_market_from_portfolio_name(self, portfolio_name: str) -> str:
        """Extract market type from portfolio name"""
        name_lower = portfolio_name.lower()
        if ("brazilian" in name_lower or "b3" in name_lower or
            "acoes" in name_lower or "brasil" in name_lower or
            "brazil" in name_lower):
            return "Brazilian"
        elif ("us" in name_lower or "nyse" in name_lower or
              "nasdaq" in name_lower or "america" in name_lower):
            return "US"
        else:
            # Fallback to old logic
            return "Brazilian" if "brazil" in name_lower else "US"

    def migrate_old_portfolio_structure(self):
        """Migrate old portfolio structure to new multi-portfolio structure"""
        if "Brazilian" in self.portfolios and "US" in self.portfolios:
            # Check if we need to migrate
            if not any("Brazilian_" in key for key in self.portfolios.keys()):
                # Migrate old structure
                new_portfolios = {}

                # Migrate Brazilian portfolio
                if "Brazilian" in self.portfolios and self.portfolios["Brazilian"]:
                    new_portfolios["Brazilian_B3"] = self.portfolios["Brazilian"]

                # Migrate US portfolio
                if "US" in self.portfolios and self.portfolios["US"]:
                    new_portfolios["US_NYSE"] = self.portfolios["US"]

                # Keep any other portfolios
                for key, value in self.portfolios.items():
                    if key not in ["Brazilian", "US"]:
                        new_portfolios[key] = value

                self.portfolios = new_portfolios
                self.save_portfolios()
                st.success("✅ Migrated portfolio structure to support multiple portfolios per market!")

    def save_portfolios(self):
        """Save portfolios to JSON file"""
        with open(self.portfolios_file, "w") as f:
            json.dump(self.portfolios, f, indent=2)

    def add_stock(
        self, portfolio_name: str, ticker: str, quantity: int, avg_price: float
    ):
        """Add or update a stock in the portfolio"""
        if portfolio_name not in self.portfolios:
            self.portfolios[portfolio_name] = {}

        self.portfolios[portfolio_name][ticker] = {
            "quantity": quantity,
            "avg_price": avg_price,
            "date_added": datetime.now().isoformat(),
        }
        self.save_portfolios()

    def remove_stock(self, portfolio_name: str, ticker: str):
        """Remove a stock from the portfolio"""
        if (
            portfolio_name in self.portfolios
            and ticker in self.portfolios[portfolio_name]
        ):
            del self.portfolios[portfolio_name][ticker]
            self.save_portfolios()

    def get_portfolio_stocks(self, portfolio_name: str) -> Dict:
        """Get all stocks in a portfolio"""
        return self.portfolios.get(portfolio_name, {})

    def get_portfolio_names(self) -> List[str]:
        """Get all portfolio names"""
        return list(self.portfolios.keys())

    def create_portfolio(self, name: str, market: str, exchange: str):
        """Create a new portfolio"""
        portfolio_key = f"{market}_{exchange}"
        if portfolio_key not in self.portfolios:
            self.portfolios[portfolio_key] = {}
            self.save_portfolios()
            return True
        return False

    def delete_portfolio(self, portfolio_name: str):
        """Delete a portfolio"""
        if portfolio_name in self.portfolios:
            del self.portfolios[portfolio_name]
            self.save_portfolios()
            return True
        return False
