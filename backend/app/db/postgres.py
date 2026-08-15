import logging
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all DB Insights internal PostgreSQL models."""


def create_postgres_engine(url: str | None = None) -> Engine:
    """Creates SQLAlchemy engine for PostgreSQL persistence."""
    db_url = url or settings.POSTGRES_URL
    connect_args = {}

    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine = create_engine(
            db_url,
            connect_args=connect_args,
        )
    else:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=5,
        )
    return engine


engine = create_postgres_engine()
SessionFactory = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for obtaining a database session."""
    session: Session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    with get_db_context() as session:
        yield session


def init_db(target_engine: Engine | None = None) -> None:
    """Creates all database tables defined on Base (useful for SQLite tests)."""
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
