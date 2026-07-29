"""Checkpointer LangGraph persistido en la SQLite ya existente (books.db).

Reemplaza el InMemorySaver por-agente para que el estado de conversación
sobreviva reinicios del proceso.
"""

import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from sqlmodel import Field, SQLModel, func, select

from ..config.settings import settings
from ..database.connection import get_session

db_path = settings.DATABASE_URL.replace("sqlite:///", "")

_conn = sqlite3.connect(db_path, check_same_thread=False)

checkpointer = SqliteSaver(_conn)
checkpointer.setup()


class Checkpoint(SQLModel, table=True):
    """Mapeo mínimo de la tabla `checkpoints` que crea LangGraph (solo lectura).

    ponytail: la tabla real la crea checkpointer.setup(); declaramos solo las
    dos columnas que consultamos.
    """

    __tablename__ = "checkpoints"

    thread_id: str = Field(primary_key=True)
    checkpoint_id: str = Field(primary_key=True)


def list_conversations() -> list[dict]:
    """Conversaciones distintas (un thread_id = una conversación).

    MAX(checkpoint_id) sirve de recencia: los checkpoint_id de LangGraph son
    UUIDs ordenables por tiempo. ponytail: sin título; agregar tabla
    `conversations` si se quiere nombre legible.
    """
    last_id = func.max(Checkpoint.checkpoint_id)
    query = (
        select(Checkpoint.thread_id, func.count().label("n"), last_id.label("last_id"))
        .group_by(Checkpoint.thread_id)
        .order_by(last_id.desc())
    )
    with get_session() as session:
        rows = session.exec(query).all()

    return [
        {"thread_id": r.thread_id, "checkpoints": r.n, "last_checkpoint_id": r.last_id}
        for r in rows
    ]
