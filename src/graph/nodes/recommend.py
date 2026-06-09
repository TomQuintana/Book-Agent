"""Recommend node — wraps the recommend subagent for the graph."""

from ..state import AgentState
from ...agents.recommend_agent import recommend_agent
from ...config.logging_config import get_logger

logger = get_logger("asta.recommend")


def agent_recommend(state: AgentState) -> AgentState:
    """
    Node that generates personalized book recommendations.

    Flow:
    1. Calls get_read_books() via the subagent to retrieve the user's reading history
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

        tools_used = []
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_info = {
                        "name": tool_call.get("name", "unknown"),
                        "args": tool_call.get("args", {}),
                    }
                    tools_used.append(tool_info)
                    logger.debug(f"Tool llamada: {tool_info['name']}()")

        agent_response = messages[-1].content

        state["intermediate_result"] = agent_response
        state["error"] = None

        if "metadata" not in state or state["metadata"] is None:
            state["metadata"] = {}

        state["metadata"]["node_executed"] = "agent_recommend"
        state["metadata"]["agent_type"] = "recommend_agent"
        state["metadata"]["tools_used"] = tools_used

        logger.debug(f"Completado: {agent_response[:150]}...")

    except Exception as e:
        error_msg = f"Error en nodo de recomendación: {str(e)}"
        logger.error(error_msg)
        state["intermediate_result"] = "No se pudieron generar recomendaciones."
        state["error"] = error_msg

    return state
