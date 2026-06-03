from langgraph.graph import END, StateGraph

from ..config.logging_config import get_logger
from ..agents.formatter_node import agent_formatter
from ..agents.modify_node import agent_modify
from ..agents.recommend_node import agent_recommend
from ..agents.router_node import agent_router
from ..agents.search_node import agent_search
from .state import AgentState

logger = get_logger("asta.graph")


def route_decision(state: AgentState) -> str:
    """
    Routing function that decides which node to go to based on the intent.

    Args:
        state: Current state with the intent classified by the router

    Returns:
        The detected intent (search, modify, recommend, conversation, unknown).
        conditional_edges maps this intent to the corresponding node.
    """
    intent = state.get("intent")

    logger.debug(f"Intent detectado: {intent}")

    # Validar que el intent existe
    if not intent:
        logger.warning("Intent es None, usando 'unknown'")
        return "unknown"

    # Devolver el intent directamente (no el nombre del nodo)
    # El conditional_edges se encarga de mapear intent → nodo
    if intent in ["search", "modify", "recommend", "conversation"]:
        return intent
    else:
        # Intent no reconocido o no implementado
        return "unknown"


# 1. Crear el grafo
graph = StateGraph(AgentState)

# 2. Agregar nodos implementados
graph.add_node("router", agent_router)
graph.add_node("search_agent", agent_search)
graph.add_node("modify_agent", agent_modify)
graph.add_node("recommend_agent", agent_recommend)
graph.add_node("formatter", agent_formatter)


# Nodo temporal para intents no implementados
def unknown_node(state: AgentState) -> AgentState:
    """Temporary node for unimplemented intents."""
    intent = state.get("intent")
    state["intermediate_result"] = (
        f"El intent '{intent}' aún no está implementado. Solo 'search' está disponible por ahora."
    )
    state["error"] = None
    return state


graph.add_node("unknown", unknown_node)

# 3. Definir punto de entrada
graph.set_entry_point("router")

# 4. Agregar edge condicional desde router
# Este diccionario mapea: intent (devuelto por route_decision) → nombre del nodo
graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "search": "search_agent",
        "modify": "modify_agent",
        "recommend": "recommend_agent",
    },
)

# 5. Todos los nodos van al formatter
graph.add_edge("search_agent", "formatter")
graph.add_edge("modify_agent", "formatter")
graph.add_edge("recommend_agent", "formatter")
graph.add_edge("unknown", "formatter")

# 6. Formatter va al final
graph.add_edge("formatter", END)

# 7. Compilar el grafo
logger.debug("Compilando el grafo multiagente...")
app = graph.compile()

# Generar visualización del grafo
try:
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    logger.debug("Grafo compilado y visualización generada (graph.png)")
except Exception as e:
    logger.warning(f"Grafo compilado pero no se pudo generar visualización: {e}")
