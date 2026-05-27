"""Search Node — Specialized agent for book search queries."""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from ..llm.client import llm
from ..graph.state import AgentState, InternalAgentState
from ..tools.book_tools import list_books, get_book
from ..config.logging_config import get_logger

logger = get_logger("asta.search")


# Crear agente interno especializado SOLO en búsqueda
# Este agente solo tiene acceso a tools de lectura (NO puede modificar datos)
search_agent = create_agent(
    model=llm,
    tools=[list_books, get_book],  # Solo tools de búsqueda/consulta
    state_schema=InternalAgentState,
    checkpointer=InMemorySaver(),
    system_prompt="""Eres un agente especializado en búsqueda y consulta de libros.

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
- Si el usuario pide crear, actualizar o eliminar libros, responde amablemente que esa no es tu especialidad
- Las búsquedas son case-insensitive y parciales (no necesitan ser exactas)

Ejemplos:
- "Busca 1984" → list_books(title="1984")
- "Libros de Orwell" → list_books(author="Orwell")
- "Libro con ID 5" → get_book(5)
- "Lista todos los libros" → list_books()

Sé conciso y útil en tus respuestas.""",
)


def search_node(state: AgentState) -> AgentState:
    """
    Node that processes search queries using a specialized internal agent.

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

        # El agente interno decide automáticamente qué tool usar
        result = search_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            {"configurable": {"thread_id": "book_agent_session"}},
        )

        # Extraer todos los mensajes para debugging
        messages = result["messages"]

        # Extraer información de tool calls para debugging
        tools_used = []
        tool_results = []

        for msg in messages:
            # Detectar si es un mensaje con tool calls
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_info = {
                        "name": tool_call.get("name", "unknown"),
                        "args": tool_call.get("args", {}),
                    }
                    tools_used.append(tool_info)
                    logger.debug(f"Tool llamada: {tool_info['name']}({tool_info['args']})")

            # Detectar si es un resultado de tool
            if hasattr(msg, "type") and msg.type == "tool":
                tool_results.append(
                    {
                        "tool": getattr(msg, "name", "unknown"),
                        "result": msg.content[:200]
                        if hasattr(msg, "content")
                        else "No content",
                    }
                )
                logger.debug(f"Tool resultado: {msg.content[:100]}...")

        # Extraer la respuesta final del agente (último mensaje)
        agent_response = messages[-1].content

        # Construir resultado con información de debugging
        debug_info = ""
        if tools_used:
            debug_info = "\n\n[DEBUG INFO]\n"
            debug_info += f"Tools ejecutadas: {len(tools_used)}\n"
            for i, tool in enumerate(tools_used, 1):
                debug_info += f"{i}. {tool['name']}({tool['args']})\n"
        else:
            debug_info = "\n\n[DEBUG INFO]\n⚠️  No se ejecutó ninguna tool\n"

        # Actualizar el estado
        state["intermediate_result"] = agent_response + debug_info
        state["error"] = None

        # Agregar metadata para tracking
        if "metadata" not in state or state["metadata"] is None:
            state["metadata"] = {}

        state["metadata"]["node_executed"] = "search_node"
        state["metadata"]["agent_type"] = "search_agent"
        state["metadata"]["tools_available"] = ["list_books", "get_book"]
        state["metadata"]["tools_used"] = tools_used
        state["metadata"]["tools_count"] = len(tools_used)

        logger.debug(f"Búsqueda completada - Tools usadas: {len(tools_used)}")
        logger.debug(f"Resultado: {agent_response[:150]}...")

    except Exception as e:
        error_msg = f"Error en nodo de búsqueda: {str(e)}"
        logger.error(error_msg)

        state["intermediate_result"] = (
            "No se pudieron obtener resultados de la búsqueda."
        )
        state["error"] = error_msg

    return state
