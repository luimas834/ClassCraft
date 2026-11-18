"""The connection to PostgreSQL.
Gives the app one engine, a session maker, and the base class for the tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# pool_pre_ping asks the database whether a reused connection is still alive.
# Without it the first request after a database restart fails.
engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Every table class inherits from this one."""
