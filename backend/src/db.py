import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./robust.db")
AUTO_CREATE_SCHEMA = os.getenv("ROBUST_AUTO_CREATE_SCHEMA", "true").lower() == "true"
AUTO_SEED_DEMO_DATA = os.getenv("ROBUST_AUTO_SEED_DEMO_DATA", "true").lower() == "true"
CONNECT_ARGS = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, future=True, connect_args=CONNECT_ARGS)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
