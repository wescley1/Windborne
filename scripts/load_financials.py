import os
import sys
from pathlib import Path
import json
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# ensure repo root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db import engine
from src.db_manager import DBManager
from src.utils import parse_date, normalize_fields

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATA_PATH = Path("data/financial_data.json")

def ensure_tables(dbm: DBManager) -> None:
    """Create database tables if they don't exist."""
    dbm.create_tables()
    logger.info("Tables ensured")

def load() -> None:
    """
    Load financial data from JSON file into database.
    Handles errors gracefully and logs statistics.
    """
    dbm = DBManager(engine)
    ensure_tables(dbm)

    if not DATA_PATH.exists():
        logger.error(f"{DATA_PATH} not found")
        return

    try:
        payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        return

    inserted = 0
    failed = 0
    skipped = 0

    for company_name, company_data in payload.items():
        try:
            # Extract ticker from any statement
            ticker: Optional[str] = None
            for s in ("income_statement", "balance_sheet", "cash_flow_statement"):
                if company_data.get(s) and company_data[s].get("symbol"):
                    ticker = company_data[s]["symbol"]
                    break

            if not ticker:
                logger.warning(f"No ticker found for {company_name}, skipping")
                skipped += 1
                continue

            company = dbm.upsert_company(name=company_name, ticker=ticker, metadata={})
            logger.info(f"Processing company: {company_name} ({ticker})")

            # Process each statement type
            for stype in ("income_statement", "balance_sheet", "cash_flow_statement"):
                reports = company_data.get(stype, {}).get("annualReports", []) or []
                
                for rep in reports:
                    try:
                        fiscal = parse_date(rep.get("fiscalDateEnding") or rep.get("fiscal_date"))
                        if not fiscal:
                            logger.warning(f"No fiscal date for {company_name} {stype}, skipping report")
                            continue

                        # Normalize fields
                        normalized = normalize_fields(rep, stype)
                        
                        dbm.insert_financial_statement(
                            company_id=company.id,
                            statement_type=stype,
                            period="annual",
                            fiscal_date=fiscal,
                            data=rep,
                            **normalized  # revenue, gross_profit, net_income, etc.
                        )
                        inserted += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to insert statement for {company_name} ({stype}, {fiscal}): {e}")
                        failed += 1
                        continue

        except Exception as e:
            logger.error(f"Failed to process company {company_name}: {e}")
            failed += 1
            continue

    logger.info(f"Load complete: {inserted} inserted, {failed} failed, {skipped} skipped")
    print(f"Loaded {inserted} financial statements into DB ({failed} failed, {skipped} skipped)")

if __name__ == "__main__":
    load()