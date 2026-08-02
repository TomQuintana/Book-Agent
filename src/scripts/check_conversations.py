"""Verifica ConversationService: crea, agrega mensajes, ordena, titula y lista.

Confirma además que el FK arreglado (Message.thread_id -> conversations.thread_id)
ya no rompe create_all.

Usage:
    uv run python -m src.scripts.check_conversations
"""

from src.database.connection import get_session, init_db
from src.database.models import Conversation
from src.services.conversation_service import ConversationService

_THREAD = "_check_thread"


async def check_conversation_flow() -> None:
    """Exercise the full service flow against books.db and clean up after."""
    await init_db()  # crea tablas — falla acá si el FK sigue roto

    with get_session() as session:
        svc = ConversationService(session)

        try:
            conv = svc.create(_THREAD)
            assert svc.get(_THREAD) is not None, "la conversación debería persistir"
            assert conv.title is None, "el título arranca en None"

            svc.add_message(_THREAD, "user", "hola")
            svc.add_message(_THREAD, "assistant", "buenas")
            msgs = svc.get_messages(_THREAD)
            assert [m.role for m in msgs] == ["user", "assistant"], "orden incorrecto"

            refreshed = svc.get(_THREAD)
            assert refreshed.updated_at >= refreshed.created_at, "updated_at no se tocó"

            svc.set_title(_THREAD, "saludo")
            assert svc.get(_THREAD).title == "saludo", "el título no persistió"

            assert _THREAD in {c.thread_id for c in svc.list()}, "list() no incluye la conversación"
        finally:
            # limpieza: borrar mensajes + conversación de prueba
            for m in svc.get_messages(_THREAD):
                session.delete(m)
            conv = session.get(Conversation, _THREAD)
            if conv:
                session.delete(conv)
            session.commit()


if __name__ == "__main__":
    import asyncio

    asyncio.run(check_conversation_flow())
