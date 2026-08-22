"""Modify Node — Specialized agent for creating, updating and deleting books."""

from langchain.agents import create_agent

from ..config.logging_config import get_logger
from ..graph.checkpointer import checkpointer
from ..graph.state import AgentState, InternalAgentState
from ..llm.client import llm
from ..llm.langfuse_client import langfuse
from ..tools.book_tools import create_book, delete_book, update_book

logger = get_logger("asta.modify")


MODIFY_SYSTEM_PROMPT = """Eres un agente especializado en modificar la base de datos de libros.

Tu especialidad es CREAR, ACTUALIZAR y ELIMINAR libros.

Herramientas disponibles:

1. create_book(title, author, status, description, type, is_physically, finished):
   - Crea un nuevo libro. Solo 'title' es obligatorio.
   - status puede ser: 'reading', 'completed', 'pending'
   - type puede ser: 'fiction', 'non-fiction', 'technical', 'emprendimiento', etc.

2. update_book(book_id, title, author, status, description):
   - Actualiza un libro existente por su ID

3. delete_book(book_id):
   - Elimina un libro por su ID

IMPORTANTE:
- Extrae toda la información posible del mensaje del usuario
- Si el usuario no especifica un campo, no lo envíes (déjalo como None)
- Si te piden buscar o listar libros, indica que esa no es tu especialidad

Sé conciso y confirma la operación realizada."""


modify_agent = create_agent(
    model=llm,
    tools=[create_book, update_book, delete_book],
    state_schema=InternalAgentState,
    checkpointer=checkpointer,
    system_prompt=langfuse.get_prompt("modify-agent", fallback=MODIFY_SYSTEM_PROMPT).prompt,
)


def agent_modify(state: AgentState) -> AgentState:
    """Node that processes modification operations (create, update, delete)."""
    user_message = state["user_message"]

    # raise ConnectionError("boom: proveedor caido (TEMPORAL, sacar)")

    try:
        result = modify_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            {
                "configurable": {
                    "thread_id": state.get("thread_id") or "book_agent_session",
                    "checkpoint_ns": "agents",
                }
            },
        )

        messages = result["messages"]

        agent_response = messages[-1].content

        state["intermediate_result"] = agent_response

        state["error"] = None

        if "metadata" not in state or state["metadata"] is None:
            state["metadata"] = {}

        state["metadata"]["node_executed"] = "agent_modify"
        state["metadata"]["agent_type"] = "modify_agent"

        logger.debug(f"Completado: {agent_response[:150]}...")

    except Exception as e:
        logger.error(f"Error en nodo de modificación: {str(e)}")
        raise

    return state
