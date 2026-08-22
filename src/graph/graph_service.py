"""Service for running the LangGraph multi-agent graph."""

from langchain_core.runnables import RunnableConfig
from langfuse.langchain import CallbackHandler

from src.helpers.graph_helper import snapshot

from ..config.logging_config import get_logger
from .agent_graph import app as agent_graph
from .state import AgentState

logger = get_logger("asta.service")

langfuse_handler = CallbackHandler()


class GraphService:
    """Service for processing user queries through the multi-agent graph.

    This service:
    - Initializes the graph state with the user query
    - Runs the full graph (router → specialized agent → formatter)
    - Returns the processed final response
    - Handles errors centrally
    """

    def __init__(self):
        """Initializes the service with the compiled graph."""
        self.graph = agent_graph

    def _config(self, thread_id: str) -> RunnableConfig:
        """Builds the config dict for the graph's invoke() method."""
        return {
            "configurable": {"thread_id": thread_id},
            "callbacks": [langfuse_handler],
        }

    def _format(self, result: dict, thread_id: str) -> dict:
        """Builds the response dict from the graph's final state."""
        if result.get("error"):
            logger.warning(f"Error en ejecución: {result['error']}")

            return {
                "response": "Lo siento, hubo un error al procesar tu consulta.",
                "intent": result.get("intent"),
                "thread_id": thread_id,
                "success": False,
                "error": result["error"],
                "metadata": result.get("metadata", {}),
            }

        logger.info(f"Completado — Intención: {result.get('intent')}")

        return {
            "response": result.get("final_response") or "No se generó respuesta",
            "intent": result.get("intent"),
            "thread_id": thread_id,
            "success": True,
            "error": None,
            "metadata": result.get("metadata", {}),
        }

    def process_query(
        self, user_message: str, thread_id: str | None = None, metadata: dict | None = None
    ) -> dict:
        """Processes a user query through the multi-agent graph.

        Flow:
        1. Router classifies the intent (search/modify/recommend/conversation)
        2. Routes to the specialized agent that handles the query
        3. Formatter generates a friendly final response

        Args:
            user_message: User message or query
            thread_id: Conversation/session ID for state persistence (None starts a new one)
            metadata: Optional additional data (user_id, session_id, etc.)

        Returns:
            Dict with the following structure:
            {
                "response": str,      # Final formatted response
                "intent": str,        # Detected intent
                "success": bool,      # Whether it completed successfully
                "error": str | None,  # Error message if it failed
                "metadata": dict      # Additional metadata
                "thread_id": str        # Thread/session ID for context
            }

        Example:
            >>> result = graph_service.process_query("List all books")
            >>> print(result["response"])
            "Here are all the available books: ..."
            >>> print(result["intent"])
            "search"
        """
        try:
            thread_id = thread_id or "book_agent_session"

            initial_state: AgentState = {
                "thread_id": thread_id,
                "user_message": user_message,
                "intent": None,
                "intermediate_result": None,
                "final_response": None,
                "error": None,
                "metadata": metadata or {},
            }

            logger.info(f"Procesando: '{user_message}'")

            result = self.graph.invoke(initial_state, self._config(thread_id))

            logger.debug(f"Estado final: {result}")

            return self._format(result, thread_id)

        except Exception as e:
            error_msg = f"Error inesperado en el grafo: {str(e)}"
            logger.error(error_msg)

            return {
                "response": "Lo siento, ocurrió un error inesperado al procesar tu consulta.",
                "intent": None,
                "thread_id": thread_id,
                "success": False,
                "error": error_msg,
                "metadata": metadata or {},
            }

    def resume(self, thread_id: str) -> dict:
        """Retries the half-finished turn without the user rewriting anything.

        The node that failed never consolidated its checkpoint: it stayed in state.next.
        invoke(None, config) re-runs it from the last consolidated checkpoint (the
        router's), so the intent is not recomputed.
        """
        config = self._config(thread_id)
        state = self.graph.get_state(config)

        if not state.next:
            return {
                "response": "No hay nada pendiente para reintentar.",
                "intent": None,
                "thread_id": thread_id,
                "success": False,
                "error": "No hay ninguna ejecución pendiente",
                "metadata": {},
            }

        logger.info(f"Reanudando '{thread_id}' desde {state.next}")

        try:
            result = self.graph.invoke(None, config)

        except Exception as e:
            error_msg = f"El reintento volvió a fallar: {str(e)}"

            logger.error(error_msg)

            return {
                "response": "Lo siento, el reintento volvió a fallar.",
                "intent": state.values.get("intent"),
                "thread_id": thread_id,
                "success": False,
                "error": error_msg,
                "metadata": {},
            }

        return self._format(result, thread_id) | {
            "user_message": state.values.get("user_message"),
        }

    def inspect(self, thread_id: str) -> dict:
        """Human-readable view of a thread's checkpoints, for debugging retries.

        The `checkpoints` table stores msgpack blobs, so raw SQL is unreadable — and
        `next` isn't a column at all, LangGraph derives it from the pending writes.
        """
        config = self._config(thread_id)
        state = self.graph.get_state(config)

        return {
            "thread_id": thread_id,
            "current": snapshot(state),
            "can_retry": bool(state.next),
            # más viejo primero, así se lee como el flujo del turno
            "history": [snapshot(s) for s in reversed(list(self.graph.get_state_history(config)))],
        }

    def get_graph_visualization(self) -> str:
        """Returns a Mermaid diagram of the graph for debugging and documentation.

        Returns:
            String with the Mermaid diagram of the graph
        """
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception as e:
            return f"Error generando visualización: {str(e)}"


graph_service = GraphService()
