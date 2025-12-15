from contextlib import contextmanager
from typing import Iterable, Optional, List
from datetime import date

from sqlalchemy.orm import Session

from src.db import engine, Base, get_session
from src.models import Company, FinancialStatement, Metric

class DBManager:
    def __init__(self, engine_ = None):
        self.engine = engine_ or engine

    def create_tables(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session(self) -> Iterable[Session]:
        s = get_session()
        try:
            yield s
            s.commit()
        except:
            s.rollback()
            raise
        finally:
            s.close()

    # Companies
    def upsert_company(self, name: str, ticker: str, metadata: Optional[dict] = None) -> Company:
        with self.session() as s:
            c = s.query(Company).filter((Company.name == name) | (Company.ticker == ticker)).one_or_none()
            if c:
                c.ticker = ticker or c.ticker
                c.metadata_json = metadata or c.metadata_json
                return c
            c = Company(name=name, ticker=ticker, metadata_json=metadata or {})
            s.add(c)
            s.flush()
            return c

    def get_companies(self) -> List[Company]:
        with self.session() as s:
            return s.query(Company).all()

    # Financial statements
    def insert_financial_statement(self, company_id: int, statement_type: str, period: str, fiscal_date: Optional[date], data: dict) -> FinancialStatement:
        with self.session() as s:
            existing = s.query(FinancialStatement).filter_by(
                company_id=company_id,
                statement_type=statement_type,
                fiscal_date=fiscal_date,
            ).one_or_none()
            if existing:
                # Update existing record in-place (idempotent behaviour)
                existing.period = period or existing.period
                existing.data = data or existing.data
                return existing
            fs = FinancialStatement(company_id=company_id, statement_type=statement_type, period=period, fiscal_date=fiscal_date, data=data)
            s.add(fs)
            s.flush()
            return fs

    def fetch_financials(self, company_id: Optional[int]=None, statement_type: Optional[str]=None, period: Optional[str]=None):
        with self.session() as s:
            q = s.query(FinancialStatement)
            if company_id is not None:
                q = q.filter(FinancialStatement.company_id == company_id)
            if statement_type is not None:
                q = q.filter(FinancialStatement.statement_type == statement_type)
            if period is not None:
                q = q.filter(FinancialStatement.period == period)
            return q.order_by(FinancialStatement.fiscal_date.asc()).all()

    # Metrics
    def upsert_metric(self, company_id: int, year: int, metric_name: str, value: Optional[float]) -> Metric:
        with self.session() as s:
            m = s.query(Metric).filter_by(company_id=company_id, year=year, metric_name=metric_name).one_or_none()
            if m:
                m.value = value
                return m
            m = Metric(company_id=company_id, year=year, metric_name=metric_name, value=value)
            s.add(m)
            s.flush()
            return m

    def get_metrics(self, company_id: Optional[int]=None):
        with self.session() as s:
            q = s.query(Metric)
            if company_id is not None:
                q = q.filter(Metric.company_id == company_id)
            return q.order_by(Metric.company_id, Metric.year).all()