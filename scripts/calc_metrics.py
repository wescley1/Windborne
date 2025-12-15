import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional

# ensure repo root is on sys.path so "from src ..." imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db_manager import DBManager
from src.db import engine
from src.utils import parse_number

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def year_from_fs(fs) -> int:
    """Extract year from financial statement fiscal_date or data."""
    if fs.fiscal_date:
        return fs.fiscal_date.year
    d = fs.data.get("fiscalDateEnding") or fs.data.get("fiscal_date")
    try:
        return datetime.fromisoformat(d).year
    except Exception:
        try:
            return int(str(d)[:4])
        except Exception:
            return None

def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """Safe division returning None if denominator is zero or None."""
    if denominator is None or numerator is None or denominator == 0:
        return None
    return numerator / denominator

def calc_and_persist() -> None:
    """
    Calculate financial metrics from normalized columns and persist to metrics table.
    Handles errors gracefully and logs statistics.
    """
    dbm = DBManager(engine)
    companies = dbm.get_companies()
    total_metrics = 0
    failed = 0

    for comp in companies:
        try:
            logger.info(f"Calculating metrics for {comp.name} ({comp.ticker})")
            
            # Use normalized columns instead of parsing JSON
            reports = dbm.fetch_financials(
                company_id=comp.id, 
                statement_type="income_statement", 
                period="annual"
            )
            
            # Build dicts by year using normalized columns
            rev_by_year = {}
            gross_by_year = {}
            net_by_year = {}
            years = set()
            
            for r in reports:
                yr = year_from_fs(r)
                if yr is None:
                    logger.warning(f"No year for report {r.id}, skipping")
                    continue
                years.add(yr)
                # Use normalized columns directly
                rev_by_year[yr] = r.revenue
                gross_by_year[yr] = r.gross_profit
                net_by_year[yr] = r.net_income

            years = sorted(years)
            
            for i, yr in enumerate(years):
                rev = rev_by_year.get(yr)
                gross = gross_by_year.get(yr)
                net = net_by_year.get(yr)
                prev_rev = rev_by_year.get(years[i-1]) if i > 0 else None

                # Calculate metrics with safe division
                metrics = {
                    "gross_margin": safe_divide(gross, rev) * 100 if safe_divide(gross, rev) else None,
                    "net_margin": safe_divide(net, rev) * 100 if safe_divide(net, rev) else None,
                    "revenue_yoy": safe_divide((rev - prev_rev) if prev_rev and rev else None, prev_rev) * 100 if prev_rev and safe_divide(rev - prev_rev, prev_rev) else None,
                }

                for name, val in metrics.items():
                    try:
                        dbm.upsert_metric(company_id=comp.id, year=yr, metric_name=name, value=val)
                        total_metrics += 1
                    except Exception as e:
                        logger.error(f"Failed to upsert metric {name} for {comp.name} year {yr}: {e}")
                        failed += 1

        except Exception as e:
            logger.error(f"Failed to calculate metrics for {comp.name}: {e}")
            failed += 1
            continue

    logger.info(f"Metrics calculation complete: {total_metrics} persisted, {failed} failed")
    print(f"Metrics calculated and persisted ({total_metrics} total, {failed} failed)")

if __name__ == "__main__":
    calc_and_persist()