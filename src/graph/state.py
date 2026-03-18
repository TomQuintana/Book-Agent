"""Estado compartido del grafo multiagente"""

from typing import TypedDict, Optional, Literal


class AgentState(TypedDict):
    """Estado que se comparte entre todos los nodos del grafo.

    Este estado se pasa de nodo en nodo, permitiendo que cada uno
    lea información y agregue sus resultados.
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
