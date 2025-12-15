import sys
from pathlib import Path
from datetime import datetime

# ensure repo root is on sys.path so "from src ..." imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db_manager import DBManager
from src.db import engine

def parse_number(v):
    if v is None:
        return None
    try:
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().replace(",", "").replace("$", "")
        if s == "" or s.lower() in ("none","null","na","-"):
            return None
        neg = False
        if s.startswith("(") and s.endswith(")"):
            neg = True
            s = s[1:-1]
        val = float(s)
        return -val if neg else val
    except:
        return None

def year_from_fs(fs):
    if fs.fiscal_date:
        return fs.fiscal_date.year
    d = fs.data.get("fiscalDateEnding") or fs.data.get("fiscal_date")
    try:
        return datetime.fromisoformat(d).year
    except:
        try:
            return int(str(d)[:4])
        except:
            return None

def calc_and_persist():
    dbm = DBManager(engine)
    companies = dbm.get_companies()
    for comp in companies:
        reports = dbm.fetch_financials(company_id=comp.id, statement_type="income_statement", period="annual")
        rev_by_year = {}
        gross_by_year = {}
        net_by_year = {}
        years = set()
        for r in reports:
            yr = year_from_fs(r)
            if yr is None:
                continue
            years.add(yr)
            data = r.data or {}
            rev_by_year[yr] = parse_number(data.get("totalRevenue") or data.get("total_revenue") or data.get("Revenue"))
            gross_by_year[yr] = parse_number(data.get("grossProfit") or data.get("gross_profit"))
            net_by_year[yr] = parse_number(data.get("netIncome") or data.get("net_income") or data.get("netIncomeLoss"))
        years = sorted(years)
        for i, yr in enumerate(years):
            rev = rev_by_year.get(yr)
            gross = gross_by_year.get(yr)
            net = net_by_year.get(yr)
            prev_rev = rev_by_year.get(years[i-1]) if i>0 else None
            metrics = {
                "gross_margin": (gross / rev) * 100 if rev and gross is not None and rev != 0 else None,
                "net_margin": (net / rev) * 100 if rev and net is not None and rev != 0 else None,
                "revenue_yoy": ((rev - prev_rev) / prev_rev) * 100 if prev_rev and rev is not None and prev_rev != 0 else None,
            }
            for name, val in metrics.items():
                dbm.upsert_metric(company_id=comp.id, year=yr, metric_name=name, value=val)
    print("Metrics calculated and persisted")

if __name__ == "__main__":
    calc_and_persist()