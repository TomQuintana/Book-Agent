"""Modify node — wraps the modify subagent for the graph."""

from ..state import AgentState
from ...agents.modify_agent import modify_agent
from ...config.logging_config import get_logger

logger = get_logger("asta.modify")


def agent_modify(state: AgentState) -> AgentState:
    """Node that processes modification operations (create, update, delete)."""
    user_message = state["user_message"]

    try:
        logger.debug(f"Procesando modificación: '{user_message}'")

        result = modify_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            {"configurable": {"thread_id": "book_agent_session"}},
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
        error_msg = f"Error en nodo de modificación: {str(e)}"
        logger.error(error_msg)
        state["intermediate_result"] = "No se pudo completar la operación."
        state["error"] = error_msg

    return state
