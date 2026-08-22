"""Search Node — Specialized agent for book search queries."""

from langchain.agents import create_agent

from ..config.logging_config import get_logger
from ..graph.checkpointer import checkpointer
from ..graph.state import AgentState, InternalAgentState
from ..llm.client import llm
from ..llm.langfuse_client import langfuse
from ..tools.book_tools import get_book, list_books

logger = get_logger("asta.search")


SEARCH_SYSTEM_PROMPT = """Eres un agente especializado en búsqueda y consulta de libros.

Tu especialidad es BUSCAR información sobre libros, no modificarlos.

Tus responsabilidades:
- Buscar libros por título, autor o estado
- Listar todos los libros disponibles
- Obtener información detallada de libros específicos por ID

Herramientas disponibles:

1. list_books(title, author, status):
   - Busca libros por TÍTULO: list_books(title="1984")
   - Busca libros por AUTOR: list_books(author="Orwell")
   - Filtra por ESTADO: list_books(status="completed")
   - Lista TODOS los libros: list_books()
   - Combina filtros: list_books(title="1984", author="Orwell")

2. get_book(book_id):
   - Obtiene información detallada de un libro específico por su ID numérico
   - Usa esto SOLO cuando el usuario mencione un ID específico (ej: "libro 5", "ID 3")

IMPORTANTE:
- Para búsquedas por título o autor, USA list_books() con los parámetros correspondientes
- Para búsquedas por ID específico, USA get_book(book_id)
- Si el usuario pide crear, actualizar o eliminar libros, responde amablemente
  que esa no es tu especialidad
- Las búsquedas son case-insensitive y parciales (no necesitan ser exactas)

Ejemplos:
- "Busca 1984" → list_books(title="1984")
- "Libros de Orwell" → list_books(author="Orwell")
- "Libro con ID 5" → get_book(5)
- "Lista todos los libros" → list_books()

Sé conciso y útil en tus respuestas."""

search_agent = create_agent(
    model=llm,
    tools=[list_books, get_book],
    state_schema=InternalAgentState,
    checkpointer=checkpointer,
    system_prompt=langfuse.get_prompt("search-agent", fallback=SEARCH_SYSTEM_PROMPT).prompt,
)


def agent_search(state: AgentState) -> AgentState:
    """Node that processes search queries using a specialized internal agent.

    Flow:
    1. Receives the user message from the state
    2. The internal agent analyzes the query
    3. The agent decides which tool to use (list_books or get_book)
    4. Executes the corresponding tool
    5. Saves the result in intermediate_result

    Args:
        state: Current graph state containing user_message

    Returns:
        Updated state with intermediate_result

    Example queries handled:
        - "List all books"
        - "Find books by García Márquez"
        - "Show completed books"
        - "Get info for book with ID 5"
    """
    user_message = state["user_message"]

    try:
        logger.debug(f"Procesando búsqueda: '{user_message}'")

        result = search_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            {
                "configurable": {
                    "thread_id": state.get("thread_id") or "book_agent_session",
                    "checkpoint_ns": "agents",
                }
            },
        )

        messages = result["messages"]

        tools_used = []
        tool_results = []

        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_info = {
                        "name": tool_call.get("name", "unknown"),
                        "args": tool_call.get("args", {}),
                    }
                    tools_used.append(tool_info)
                    logger.debug(f"Tool llamada: {tool_info['name']}({tool_info['args']})")

            if hasattr(msg, "type") and msg.type == "tool":
                tool_results.append(
                    {
                        "tool": getattr(msg, "name", "unknown"),
                        "result": msg.content[:200] if hasattr(msg, "content") else "No content",
                    }
                )
                logger.debug(f"Tool resultado: {msg.content[:100]}...")

        agent_response = messages[-1].content

        debug_info = ""
        if tools_used:
            debug_info = "\n\n[DEBUG INFO]\n"
            debug_info += f"Tools ejecutadas: {len(tools_used)}\n"
            for i, tool in enumerate(tools_used, 1):
                debug_info += f"{i}. {tool['name']}({tool['args']})\n"
        else:
            debug_info = "\n\n[DEBUG INFO]\n⚠️  No se ejecutó ninguna tool\n"

        state["intermediate_result"] = agent_response + debug_info
        state["error"] = None

        if "metadata" not in state or state["metadata"] is None:
            state["metadata"] = {}

        state["metadata"]["node_executed"] = "agent_search"
        state["metadata"]["agent_type"] = "search_agent"
        state["metadata"]["tools_available"] = ["list_books", "get_book"]
        state["metadata"]["tools_used"] = tools_used
        state["metadata"]["tools_count"] = len(tools_used)

        logger.debug(f"Búsqueda completada - Tools usadas: {len(tools_used)}")
        logger.debug(f"Resultado: {agent_response[:150]}...")

    except Exception as e:
        logger.error(f"Error en nodo de búsqueda: {str(e)}")
        raise

    return state
