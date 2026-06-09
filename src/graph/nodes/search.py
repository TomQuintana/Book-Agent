"""Search node — wraps the search subagent for the graph."""

from ..state import AgentState
from ...agents.search_agent import search_agent
from ...config.logging_config import get_logger

logger = get_logger("asta.search")


def agent_search(state: AgentState) -> AgentState:
    """
    Node that processes search queries using the search subagent.

    Flow:
    1. Receives the user message from the state
    2. The subagent analyzes the query and decides which tool to use
    3. Executes list_books or get_book accordingly
    4. Saves the result in intermediate_result

    Args:
        state: Current graph state containing user_message

    Returns:
        Updated state with intermediate_result
    """
    user_message = state["user_message"]

    try:
        logger.debug(f"Procesando búsqueda: '{user_message}'")

        result = search_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            {"configurable": {"thread_id": "book_agent_session"}},
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
                        "result": msg.content[:200]
                        if hasattr(msg, "content")
                        else "No content",
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
        error_msg = f"Error en nodo de búsqueda: {str(e)}"
        logger.error(error_msg)
        state["intermediate_result"] = (
            "No se pudieron obtener resultados de la búsqueda."
        )
        state["error"] = error_msg

    return state
