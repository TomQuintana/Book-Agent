"""Nodo Search - Agente especializado en búsqueda de libros"""

from langchain.agents import create_agent
from ..llm.client import llm
from ..graph.state import AgentState
from ..tools.book_tools import list_books, get_book


# Crear agente interno especializado SOLO en búsqueda
# Este agente solo tiene acceso a tools de lectura (NO puede modificar datos)
search_agent = create_agent(
    model=llm,
    tools=[list_books, get_book],  # Solo tools de búsqueda/consulta
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
    Nodo que procesa consultas de búsqueda usando un agente interno especializado.

    Flujo:
    1. Recibe el mensaje del usuario desde el estado
    2. El agente interno analiza la consulta
    3. El agente decide qué tool usar (list_books o get_book)
    4. Ejecuta la tool correspondiente
    5. Guarda el resultado en intermediate_result

    Args:
        state: Estado actual del grafo con user_message

    Returns:
        Estado actualizado con intermediate_result

    Ejemplos de consultas que maneja:
        - "Lista todos los libros"
        - "Busca libros de García Márquez"
        - "Muéstrame libros completados"
        - "Dame información del libro con ID 5"
    """

    user_message = state["user_message"]

    try:
        print(f"\n[SEARCH_NODE] 🔍 Procesando búsqueda")
        print(f"[SEARCH_NODE] Mensaje: '{user_message}'")

        # El agente interno decide automáticamente qué tool usar
        result = search_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]}
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
                    print(
                        f"[SEARCH_NODE] 🔧 Tool llamada: {tool_info['name']}({tool_info['args']})"
                    )

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
                print(f"[SEARCH_NODE] 📊 Tool resultado: {msg.content[:100]}...")

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

        print(f"[SEARCH_NODE] ✅ Búsqueda completada - Tools usadas: {len(tools_used)}")
        print(f"[SEARCH_NODE] Resultado: {agent_response[:150]}...")

    except Exception as e:
        error_msg = f"Error en nodo de búsqueda: {str(e)}"
        print(f"[SEARCH_NODE] ❌ {error_msg}")

        state["intermediate_result"] = (
            "No se pudieron obtener resultados de la búsqueda."
        )
        state["error"] = error_msg

    return state
