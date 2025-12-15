"""Utility functions for parsing and data normalization."""
from typing import Optional
from datetime import date, datetime
import logging
import requests

logger = logging.getLogger(__name__)

def parse_date(s: Optional[str]) -> Optional[date]:
    """
    Parse fiscal date from various formats (YYYY-MM-DD, YYYYMMDD, YYYY, ISO).
    
    Args:
        s: Date string to parse
        
    Returns:
        date object or None if parsing fails
    """
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d", "%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    try:
        return datetime.fromisoformat(str(s)).date()
    except Exception:
        logger.debug(f"Failed to parse date: {s}")
        return None

def parse_number(v) -> Optional[float]:
    """
    Parse numeric value handling negatives (parentheses), commas, currency symbols.
    
    Args:
        v: Value to parse (int, float, str, or None)
        
    Returns:
        float or None if parsing fails
        
    Examples:
        parse_number("1,234.56") -> 1234.56
        parse_number("(500)") -> -500.0
        parse_number("$1M") -> None (unsupported)
    """
    if v is None:
        return None
    try:
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().replace(",", "").replace("$", "")
        if s == "" or s.lower() in ("none", "null", "na", "-"):
            return None
        neg = s.startswith("(") and s.endswith(")")
        if neg:
            s = s[1:-1]
        val = float(s)
        return -val if neg else val
    except Exception as e:
        logger.debug(f"Failed to parse number '{v}': {e}")
        return None

def normalize_income_statement(data: dict) -> dict:
    """
    Normalize field names from Alpha Vantage income statement to canonical form.
    
    Args:
        data: Raw income statement dict from API
        
    Returns:
        Dict with normalized keys: revenue, gross_profit, net_income, currency
    """
    return {
        "revenue": parse_number(
            data.get("totalRevenue") or 
            data.get("revenues") or 
            data.get("Revenue")
        ),
        "gross_profit": parse_number(
            data.get("grossProfit") or 
            data.get("gross_profit")
        ),
        "net_income": parse_number(
            data.get("netIncome") or 
            data.get("net_income") or 
            data.get("netIncomeLoss")
        ),
        "currency": data.get("reportedCurrency", "USD"),
    }

def normalize_balance_sheet(data: dict) -> dict:
    """
    Normalize field names from Alpha Vantage balance sheet.
    
    Args:
        data: Raw balance sheet dict from API
        
    Returns:
        Dict with normalized keys: total_assets, total_liabilities, currency
    """
    return {
        "total_assets": parse_number(
            data.get("totalAssets") or 
            data.get("total_assets")
        ),
        "total_liabilities": parse_number(
            data.get("totalLiabilities") or 
            data.get("total_liabilities")
        ),
        "currency": data.get("reportedCurrency", "USD"),
    }

def normalize_cash_flow(data: dict) -> dict:
    """
    Normalize field names from Alpha Vantage cash flow statement.
    
    Args:
        data: Raw cash flow dict from API
        
    Returns:
        Dict with normalized keys: operating_cashflow, currency
    """
    return {
        "operating_cashflow": parse_number(
            data.get("operatingCashflow") or 
            data.get("operating_cashflow")
        ),
        "currency": data.get("reportedCurrency", "USD"),
    }

def normalize_fields(data: dict, statement_type: str) -> dict:
    """
    Dispatcher to normalize fields based on statement type.
    
    Args:
        data: Raw statement dict
        statement_type: One of 'income_statement', 'balance_sheet', 'cash_flow_statement'
        
    Returns:
        Dict with normalized field names
    """
    if statement_type == "income_statement":
        return normalize_income_statement(data)
    elif statement_type == "balance_sheet":
        return normalize_balance_sheet(data)
    elif statement_type == "cash_flow_statement":
        return normalize_cash_flow(data)
    return {}

def fetch_data_from_api(api_key, symbol, function, datatype='json'):
    base_url = "https://www.alphavantage.co/query"
    params = {
        'function': function,
        'symbol': symbol,
        'apikey': api_key,
        'datatype': datatype
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data from API: {response.status_code} - {response.text}")

def format_financial_data(data):
    # This function can be expanded to format the financial data as needed
    return data

def log_error(message):
    logging.basicConfig(level=logging.ERROR)
    logging.error(message)