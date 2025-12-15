from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, UniqueConstraint, Index, JSON as SQLA_JSON
from sqlalchemy.sql import func
from src.db import Base, engine

# prefer JSONB for postgres, fallback to SQL JSON for sqlite/dev
try:
    from sqlalchemy.dialects.postgresql import JSONB
except Exception:
    JSONB = None

if getattr(engine, "dialect", None) and getattr(engine.dialect, "name", None) == "postgresql" and JSONB is not None:
    JSON_TYPE = JSONB
else:
    JSON_TYPE = SQLA_JSON

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    ticker = Column(String(32), nullable=False, index=True)
    metadata_json = Column("metadata", JSON_TYPE, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    statement_type = Column(String(64), nullable=False, index=True)  # e.g., income_statement
    period = Column(String(32), nullable=False)  # 'annual' or 'quarterly'
    fiscal_date = Column(Date, nullable=True, index=True)
    data = Column(JSON_TYPE, nullable=False)  # raw normalized JSON for that fiscal period
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("company_id", "statement_type", "fiscal_date", name="u_company_statement_fiscal"),
        Index("ix_company_statement_period", "company_id", "statement_type", "period"),
    )

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    metric_name = Column(String(64), nullable=False, index=True)
    value = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("company_id", "year", "metric_name", name="u_company_year_metric"),
        Index("ix_company_year_metric", "company_id", "year", "metric_name"),
    )