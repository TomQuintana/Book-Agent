"""Nodo Recommend - Agente especializado en recomendar libros"""

from langchain.agents import create_agent
from ..llm.client import llm
from ..graph.state import AgentState
from ..tools.book_tools import get_read_books


recommend_agent = create_agent(
    model=llm,
    tools=[get_read_books],
    system_prompt="""Eres un agente experto en literatura y recomendaciones de libros.

Tu única responsabilidad es RECOMENDAR libros que el usuario aún no ha leído.

Proceso que debes seguir:
1. Llama a get_read_books() para ver el historial de lectura del usuario en su biblioteca.
2. Analiza el mensaje del usuario: puede mencionar libros específicos que leyó, géneros que le gustan, o pedir recomendaciones abiertas.
3. Combina ambas fuentes (historial en DB + lo que dice el usuario) para entender sus gustos.
4. Genera hasta 5 recomendaciones de libros que NO estén ya en su historial.

Formato de respuesta obligatorio para cada recomendación:
- **Título** — Autor
  Género: [género]
  Por qué te lo recomiendo: [1-2 oraciones explicando por qué encaja con sus gustos]

Reglas:
- Máximo 5 recomendaciones.
- No recomiendes libros que ya aparecen en el historial del usuario.
- Si el usuario menciona libros en su mensaje, tenlos en cuenta aunque no estén en la DB.
- Prioriza libros reconocidos y de calidad dentro del género o estilo preferido.
- Si el usuario no da contexto suficiente, usa el historial de la DB para inferir gustos.
- Si no hay historial y el usuario no da pistas, pide más contexto antes de recomendar.""",
)


def recommend_node(state: AgentState) -> AgentState:
    """
    Nodo que genera recomendaciones de libros personalizadas.

    Flujo:
    1. Llama a get_read_books() para obtener el historial del usuario
    2. Analiza el mensaje del usuario y el historial
    3. Genera hasta 5 recomendaciones que no estén ya en la biblioteca

    Args:
        state: Estado actual del grafo con user_message

    Returns:
        Estado actualizado con intermediate_result
    """
    user_message = state["user_message"]

    try:
        print(f"\n[RECOMMEND_NODE] Procesando recomendación")
        print(f"[RECOMMEND_NODE] Mensaje: '{user_message}'")

        result = recommend_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]}
        )

        messages = result["messages"]

        tools_used = []
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_info = {
                        "name": tool_call.get("name", "unknown"),
                        "args": tool_call.get("args", {}),
                    }
                    tools_used.append(tool_info)
                    print(f"[RECOMMEND_NODE] Tool llamada: {tool_info['name']}()")

        agent_response = messages[-1].content

        state["intermediate_result"] = agent_response
        state["error"] = None

        if "metadata" not in state or state["metadata"] is None:
            state["metadata"] = {}

        state["metadata"]["node_executed"] = "recommend_node"
        state["metadata"]["agent_type"] = "recommend_agent"
        state["metadata"]["tools_used"] = tools_used

        print(f"[RECOMMEND_NODE] Completado: {agent_response[:150]}...")

    except Exception as e:
        error_msg = f"Error en nodo de recomendación: {str(e)}"
        print(f"[RECOMMEND_NODE] {error_msg}")
        state["intermediate_result"] = "No se pudieron generar recomendaciones."
        state["error"] = error_msg

    return state
