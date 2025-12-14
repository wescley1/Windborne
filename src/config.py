import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEV_MODE = os.getenv("DEV_MODE", "true").lower()
    ALPHA_VANTAGE_API_KEY = os.getenv("API_KEY")
    BASE_URL = "https://www.alphavantage.co/query"
    COMPANIES = {
        "TE Connectivity": "TEL",
        "Sensata Technologies": "ST",
        "DuPont de Nemours": "DD"
    }
    FINANCIAL_STATEMENTS = ["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"]
    DATA_PERIOD = "annual"
    REQUEST_LIMIT = 25
    CALLS_PER_MINUTE = 5

# Export module-level aliases expected by other modules
API_KEY = Config.ALPHA_VANTAGE_API_KEY
COMPANIES = Config.COMPANIES
FINANCIAL_STATEMENTS = Config.FINANCIAL_STATEMENTS
REQUEST_LIMIT = Config.REQUEST_LIMIT
CALLS_PER_MINUTE = Config.CALLS_PER_MINUTE