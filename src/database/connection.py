"""Database engine and session management."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


async def init_db():
    """Creates database tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Returns a new database session (caller is responsible for closing it)."""
    return Session(engine)


def get_db() -> Generator[Session]:
    """FastAPI dependency: yields a session and closes it after the request."""
    with Session(engine) as session:
        yield session
