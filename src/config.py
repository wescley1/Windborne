import os
from dotenv import load_dotenv
from pathlib import Path

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

    def init_config(self):
        if not self.ALPHA_VANTAGE_API_KEY:
            raise ValueError("API_KEY environment variable is not set.")
        
        folder_path = Path('data')
        folder_path.mkdir(parents=True, exist_ok=True)
        

    

# Export module-level aliases expected by other module
config_instance = Config()
config_instance.init_config()
API_KEY = Config.ALPHA_VANTAGE_API_KEY
COMPANIES = Config.COMPANIES
FINANCIAL_STATEMENTS = Config.FINANCIAL_STATEMENTS
REQUEST_LIMIT = Config.REQUEST_LIMIT
CALLS_PER_MINUTE = Config.CALLS_PER_MINUTE
DEV_MODE = Config.DEV_MODE