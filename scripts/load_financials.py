import os
import json
from datetime import datetime
from pathlib import Path
import sys

from dotenv import load_dotenv
load_dotenv()

# ensure repo root is on sys.path so "from src ..." imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db import engine, Base, get_session
from src.models import Company, FinancialStatement

DATA_PATH = Path("data/financial_data.json")

def parse_date(s):
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        return None

def ensure_tables():
    Base.metadata.create_all(bind=engine)

def load():
    if not DATA_PATH.exists():
        raise SystemExit(f"{DATA_PATH} not found")
    
    ensure_tables()
    with open(DATA_PATH, encoding="utf-8") as fh:
        payload = json.load(fh)

    session = get_session()

    
    
    try:
        for company_name, statements in payload.items():
            ticker = statements.get("income_statement", {}).get("symbol") or statements.get("balance_sheet", {}).get("symbol")
            # upsert company (simple)
            company = session.query(Company).filter(Company.name == company_name).one_or_none()
            if not company:
                company = Company(name=company_name, ticker=ticker, metadata_json={})
                session.add(company)
                session.flush()  # populate id

            # load each statement type (annual only, last 3 entries)
            mapping = {
                "income_statement": statements.get("income_statement", {}).get("annualReports", []),
                "balance_sheet": statements.get("balance_sheet", {}).get("annualReports", []),
                "cash_flow_statement": statements.get("cash_flow_statement", {}).get("annualReports", []),
            }
            for stype, reports in mapping.items():
                # take first 3 (assumes most recent first)
                for report in reports[:3]:
                    fiscal = parse_date(report.get("fiscalDateEnding") or report.get("fiscal_date") or "")
                    # skip if duplicate exists
                    exists = session.query(FinancialStatement).filter_by(
                        company_id=company.id,
                        statement_type=stype,
                        fiscal_date=fiscal
                    ).one_or_none()
                    if exists:
                        continue
                    fs = FinancialStatement(
                        company_id=company.id,
                        statement_type=stype,
                        period="annual",
                        fiscal_date=fiscal,
                        data=report
                    )
                    session.add(fs)

        session.commit()
        print("Loaded financial statements into DB")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print(os.getenv("DATABASE_URL"))
    load()