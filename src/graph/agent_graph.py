from langgraph.graph import END, StateGraph

from ..nodes.formatter_node import formatter_node
from ..nodes.modify_node import modify_node
from ..nodes.router_node import router_node
from ..nodes.search_node import search_node
from .state import AgentState


def route_decision(state: AgentState) -> str:
    """
    Función de enrutamiento que decide a qué nodo ir según el intent.

    Args:
        state: Estado actual con el intent clasificado por el router

    Returns:
        El intent detectado (search, modify, recommend, conversation, unknown)
        El conditional_edges mapeará este intent al nodo correspondiente
    """
    intent = state.get("intent")

    print(f"[ROUTE_DECISION] Intent detectado: {intent}")

    # Validar que el intent existe
    if not intent:
        print(f"[ROUTE_DECISION] ⚠️  Intent es None, usando 'unknown'")
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
graph.add_node("router", router_node)
graph.add_node("search_agent", search_node)
graph.add_node("modify_agent", modify_node)
graph.add_node("formatter", formatter_node)


# Nodo temporal para intents no implementados
def unknown_node(state: AgentState) -> AgentState:
    """Nodo temporal para intents no implementados aún"""
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
        "search": "search_agent",          # Intent "search" → nodo "search_agent"
        "modify": "modify_agent",
        "recommend": "unknown",            # TODO: Cambiar a "recommend_agent" cuando se implemente
        "conversation": "unknown",         # TODO: Cambiar a "conversation_agent" cuando se implemente
        "unknown": "unknown",              # Intent desconocido → nodo "unknown"
    },
)

# 5. Todos los nodos van al formatter
graph.add_edge("search_agent", "formatter")
graph.add_edge("modify_agent", "formatter")
graph.add_edge("unknown", "formatter")

# 6. Formatter va al final
graph.add_edge("formatter", END)

# 7. Compilar el grafo
print("[AGENT_GRAPH] Compilando el grafo multiagente...")
app = graph.compile()

# Generar visualización del grafo
try:
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    print("[AGENT_GRAPH] ✅ Grafo compilado y visualización generada (graph.png)")
except Exception as e:
    print(
        f"[AGENT_GRAPH] ⚠️  Grafo compilado pero no se pudo generar visualización: {e}"
    )
