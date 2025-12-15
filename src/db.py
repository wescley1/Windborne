from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables early so `config` can read them
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://windborne:password@127.0.0.1:5433/windborne")

engine = create_engine(DATABASE_URL, future=True)
# set expire_on_commit=False so ORM instances keep attributes after session close
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
Base = declarative_base()

def get_session():
    return SessionLocal()