from sqlmodel import SQLModel, Session, create_engine
from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


async def init_db():
    """Crea las tablas si no existen"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Retorna una nueva sesión de base de datos"""
    return Session(engine)
