"""Shared state for the multi-agent graph."""

from typing import TypedDict, Optional, Literal, Annotated
from langchain.agents import AgentState as LangChainAgentState


def keep_last_5_iterations(existing: list, new: list) -> list:
    print('Messages:', (existing + new)[-10:])
    return (existing + new)[-10:]


class InternalAgentState(LangChainAgentState):
    """Internal agent state with a sliding window of the last 5 conversation turns."""
    messages: Annotated[list, keep_last_5_iterations]


class AgentState(TypedDict):
    """State shared across all graph nodes.

    Passed from node to node, allowing each one to read data and append its results.
    """

    # Entrada del usuario
    user_message: str

    # Intención detectada por el router
    intent: Optional[Literal["search", "modify", "recommend", "conversation"]]

    # Resultados intermedios de los nodos
    intermediate_result: Optional[str]

    # Respuesta final formateada
    final_response: Optional[str]

    # Información de error si algo falla
    error: Optional[str]

    # Metadata adicional
    metadata: Optional[dict]
