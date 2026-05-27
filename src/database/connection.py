from sqlmodel import SQLModel, Session, create_engine
from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


async def init_db():
    """Creates database tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Returns a new database session."""
    return Session(engine)
