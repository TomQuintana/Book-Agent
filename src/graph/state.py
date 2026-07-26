"""Shared state for the multi-agent graph."""

from typing import Annotated, Literal, TypedDict

from langchain.agents import AgentState as LangChainAgentState


def keep_last_5_iterations(existing: list, new: list) -> list:
    """Reducer that keeps only the last 5 conversation turns (10 messages)."""
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
    intent: Literal["search", "modify", "recommend", "conversation"] | None

    # Resultados intermedios de los nodos
    intermediate_result: str | None

    # Respuesta final formateada
    final_response: str | None

    # Información de error si algo falla
    error: str | None

    # Metadata adicional
    metadata: dict | None
