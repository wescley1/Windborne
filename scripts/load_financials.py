import os
import sys
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables early so `config` can read them
load_dotenv()

# ensure repo root is on sys.path so "from src ..." imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db import engine
from src.db_manager import DBManager

DATA_PATH = Path("data/financial_data.json")

def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d", "%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        return None

def ensure_tables(dbm: DBManager):
    dbm.create_tables()

def load():
    dbm = DBManager(engine)
    ensure_tables(dbm)

    if not DATA_PATH.exists():
        print("data/financial_data.json not found")
        return

    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    # expected payload: list of companies with keys: name, ticker, statements (list)
    inserted = 0
    for company_name, company_data in payload.items():
        # extrair ticker (se presente em qualquer statement)
        ticker = None
        for s in ("income_statement", "balance_sheet", "cash_flow_statement"):
            if company_data.get(s) and company_data[s].get("symbol"):
                ticker = company_data[s]["symbol"]
                break

        company = dbm.upsert_company(name=company_name, ticker=ticker, metadata={})

        # para cada tipo de demonstração, pegar annualReports e inserir
        for stype in ("income_statement", "balance_sheet", "cash_flow_statement"):
            reports = company_data.get(stype, {}).get("annualReports", []) or []
            for rep in reports:
                fiscal = parse_date(rep.get("fiscalDateEnding") or rep.get("fiscal_date"))
                dbm.insert_financial_statement(
                    company_id=company.id,
                    statement_type=stype,
                    period="annual",
                    fiscal_date=fiscal,
                    data=rep
                )
                inserted += 1

    print(f"Loaded {inserted} financial statements into DB")

if __name__ == "__main__":
    load()