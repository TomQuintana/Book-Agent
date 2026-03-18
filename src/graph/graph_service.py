"""Servicio para ejecutar el grafo multiagente de LangGraph"""

from typing import Optional
from .agent_graph import app as agent_graph
from .state import AgentState


class GraphService:
    """
    Servicio para procesar consultas de usuarios a través del grafo multiagente.

    Este servicio:
    - Inicializa el estado del grafo con la consulta del usuario
    - Ejecuta el grafo completo (router → agente específico → formatter)
    - Retorna la respuesta final procesada
    - Maneja errores de forma centralizada
    """

    def __init__(self):
        """Inicializa el servicio con el grafo compilado"""
        self.graph = agent_graph

    def process_query(self, user_message: str, metadata: Optional[dict] = None) -> dict:
        """
        Procesa una consulta del usuario a través del grafo multiagente.

        El flujo es:
        1. Router clasifica la intención (search/modify/recommend/conversation)
        2. Se enruta al agente específico que procesa la consulta
        3. Formatter genera una respuesta final amigable

        Args:
            user_message: Mensaje o consulta del usuario
            metadata: Información adicional opcional (user_id, session_id, etc.)

        Returns:
            Dict con la siguiente estructura:
            {
                "response": str,      # Respuesta final formateada
                "intent": str,        # Intención detectada
                "success": bool,      # Si se completó exitosamente
                "error": str | None,  # Mensaje de error si falló
                "metadata": dict      # Metadata adicional
            }

        Example:
            >>> result = graph_service.process_query("Lista todos los libros")
            >>> print(result["response"])
            "Aquí están todos los libros disponibles: ..."
            >>> print(result["intent"])
            "search"
        """
        try:
            # Construir estado inicial
            initial_state: AgentState = {
                "user_message": user_message,
                "intent": None,
                "intermediate_result": None,
                "final_response": None,
                "error": None,
                "metadata": metadata or {}
            }

            # Ejecutar el grafo completo
            print(f"\n[GRAPH_SERVICE] Procesando: '{user_message}'")
            result = self.graph.invoke(initial_state)
            print(result)

            # Verificar si hubo errores durante la ejecución
            if result.get("error"):
                print(f"[GRAPH_SERVICE] ⚠️  Error en ejecución: {result['error']}")
                return {
                    "response": "Lo siento, hubo un error al procesar tu consulta.",
                    "intent": result.get("intent"),
                    "success": False,
                    "error": result["error"],
                    "metadata": result.get("metadata", {})
                }

            # Respuesta exitosa
            print(f"[GRAPH_SERVICE] ✅ Completado - Intención: {result.get('intent')}")
            return {
                "response": result.get("final_response") or "No se generó respuesta",
                "intent": result.get("intent"),
                "success": True,
                "error": None,
                "metadata": result.get("metadata", {})
            }

        except Exception as e:
            # Capturar errores no manejados
            error_msg = f"Error inesperado en el grafo: {str(e)}"
            print(f"[GRAPH_SERVICE] ❌ {error_msg}")

            return {
                "response": "Lo siento, ocurrió un error inesperado al procesar tu consulta.",
                "intent": None,
                "success": False,
                "error": error_msg,
                "metadata": metadata or {}
            }

    def get_graph_visualization(self) -> str:
        """
        Obtiene una representación visual del grafo en formato Mermaid.

        Útil para debugging y documentación.

        Returns:
            String con el diagrama Mermaid del grafo
        """
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception as e:
            return f"Error generando visualización: {str(e)}"


# Instancia global del servicio (patrón singleton)
graph_service = GraphService()
