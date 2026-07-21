"""Recommend Node — Specialized agent for book recommendations."""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from ..config.logging_config import get_logger
from ..graph.state import AgentState, InternalAgentState
from ..llm.client import llm
from ..llm.langfuse_client import langfuse
from ..tools.book_tools import get_read_books

logger = get_logger("asta.recommend")


# Prompt canónico: fallback si Langfuse no responde y fuente para el seed (scripts/seed_prompts.py)
RECOMMEND_SYSTEM_PROMPT = """Eres un agente experto en literatura y recomendaciones de libros.

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
- Si no hay historial y el usuario no da pistas, pide más contexto antes de recomendar."""


recommend_agent = create_agent(
    model=llm,
    tools=[get_read_books],
    state_schema=InternalAgentState,
    checkpointer=InMemorySaver(),
    system_prompt=langfuse.get_prompt(
        "recommend-agent", fallback=RECOMMEND_SYSTEM_PROMPT
    ).prompt,
)


def agent_recommend(state: AgentState) -> AgentState:
    """
    Node that generates personalized book recommendations.

    Flow:
    1. Calls get_read_books() to retrieve the user's reading history
    2. Analyzes the user message and the history
    3. Generates up to 5 recommendations not already in the library

    Args:
        state: Current graph state containing user_message

    Returns:
        Updated state with intermediate_result
    """
    user_message = state["user_message"]

    try:
        logger.debug(f"Procesando recomendación: '{user_message}'")

        result = recommend_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            {"configurable": {"thread_id": "book_agent_session"}},
        )

        messages = result["messages"]

        # tools_used = []
        # for msg in messages:
        #     if hasattr(msg, "tool_calls") and msg.tool_calls:
        #         for tool_call in msg.tool_calls:
        #             tool_info = {
        #                 "name": tool_call.get("name", "unknown"),
        #                 "args": tool_call.get("args", {}),
        #             }
        #             tools_used.append(tool_info)
        #             logger.debug(f"Tool llamada: {tool_info['name']}()")

        agent_response = messages[-1].content

        state["intermediate_result"] = agent_response
        state["error"] = None

        if "metadata" not in state or state["metadata"] is None:
            state["metadata"] = {}

        state["metadata"]["node_executed"] = "agent_recommend"
        state["metadata"]["agent_type"] = "recommend_agent"
        # state["metadata"]["tools_used"] = tools_used

        logger.debug(f"Completado: {agent_response[:150]}...")

    except Exception as e:
        error_msg = f"Error en nodo de recomendación: {str(e)}"
        logger.error(error_msg)
        state["intermediate_result"] = "No se pudieron generar recomendaciones."
        state["error"] = error_msg

    return state
