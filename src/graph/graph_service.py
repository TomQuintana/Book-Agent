"""Service for running the LangGraph multi-agent graph."""

from typing import Optional

from langfuse.langchain import CallbackHandler

from ..config.logging_config import get_logger
from ..config.settings import settings
from .agent_graph import app as agent_graph
from .state import AgentState

logger = get_logger("asta.service")

langfuse_handler = CallbackHandler()


class GraphService:
    """
    Service for processing user queries through the multi-agent graph.

    This service:
    - Initializes the graph state with the user query
    - Runs the full graph (router → specialized agent → formatter)
    - Returns the processed final response
    - Handles errors centrally
    """

    def __init__(self):
        """Initializes the service with the compiled graph."""
        self.graph = agent_graph

    def process_query(self, user_message: str, metadata: Optional[dict] = None) -> dict:
        """
        Processes a user query through the multi-agent graph.

        Flow:
        1. Router classifies the intent (search/modify/recommend/conversation)
        2. Routes to the specialized agent that handles the query
        3. Formatter generates a friendly final response

        Args:
            user_message: User message or query
            metadata: Optional additional data (user_id, session_id, etc.)

        Returns:
            Dict with the following structure:
            {
                "response": str,      # Final formatted response
                "intent": str,        # Detected intent
                "success": bool,      # Whether it completed successfully
                "error": str | None,  # Error message if it failed
                "metadata": dict      # Additional metadata
            }

        Example:
            >>> result = graph_service.process_query("List all books")
            >>> print(result["response"])
            "Here are all the available books: ..."
            >>> print(result["intent"])
            "search"
        """
        try:
            initial_state: AgentState = {
                "user_message": user_message,
                "intent": None,
                "intermediate_result": None,
                "final_response": None,
                "error": None,
                "metadata": metadata or {},
            }

            logger.info(f"Procesando: '{user_message}'")
            result = self.graph.invoke(
                initial_state, config={"callbacks": [langfuse_handler]}
            )
            logger.debug(f"Estado final: {result}")

            # Verificar si hubo errores durante la ejecución
            if result.get("error"):
                logger.warning(f"Error en ejecución: {result['error']}")
                return {
                    "response": "Lo siento, hubo un error al procesar tu consulta.",
                    "intent": result.get("intent"),
                    "success": False,
                    "error": result["error"],
                    "metadata": result.get("metadata", {}),
                }

            # Respuesta exitosa
            logger.info(f"Completado — Intención: {result.get('intent')}")

            return {
                "response": result.get("final_response") or "No se generó respuesta",
                "intent": result.get("intent"),
                "success": True,
                "error": None,
                "metadata": result.get("metadata", {}),
            }

        except Exception as e:
            # Capturar errores no manejados
            error_msg = f"Error inesperado en el grafo: {str(e)}"
            logger.error(error_msg)

            return {
                "response": "Lo siento, ocurrió un error inesperado al procesar tu consulta.",
                "intent": None,
                "success": False,
                "error": error_msg,
                "metadata": metadata or {},
            }

    def get_graph_visualization(self) -> str:
        """
        Returns a Mermaid diagram of the graph for debugging and documentation.

        Returns:
            String with the Mermaid diagram of the graph
        """
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception as e:
            return f"Error generando visualización: {str(e)}"


# Instancia global del servicio (patrón singleton)
graph_service = GraphService()
