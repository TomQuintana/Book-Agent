"""Formatter Node — Formats agent results into user-friendly responses."""

from ..config.logging_config import get_logger
from ..graph.state import AgentState
from ..llm.client import llm

logger = get_logger("asta.formatter")


def agent_formatter(state: AgentState) -> AgentState:
    """
    Final node that formats the response for the user in a friendly way.

    This node:
    1. Takes intermediate results (from search_node, modify_node, etc.)
    2. Considers the user's intent (search, modify, recommend, conversation)
    3. Generates a well-structured and friendly final response
    4. Handles error cases clearly

    Args:
        state: Current state with intermediate_result and intent

    Returns:
        Updated state with final_response
    """

    intermediate_result = state.get("intermediate_result")
    intent = state.get("intent")
    user_message = state.get("user_message")
    error = state.get("error")

    try:
        logger.debug(f"Formateando respuesta final — intent: {intent}")

        # Si hubo un error, generar respuesta de error amigable
        if error:
            logger.warning(f"Detectado error: {error}")

            error_prompt = f"""El usuario preguntó: "{user_message}"

Hubo un error al procesar su consulta: {error}

Genera una respuesta amigable explicando que hubo un problema y sugiere al usuario qué puede hacer.
Sé empático y profesional."""

            response = llm.invoke(error_prompt)
            state["final_response"] = response.content.strip()
            logger.debug("Respuesta de error formateada")
            return state

        # Si no hay resultados intermedios, respuesta genérica
        if not intermediate_result:
            state["final_response"] = (
                "Lo siento, no pude procesar tu consulta correctamente."
            )
            logger.warning("No hay resultados intermedios")
            return state

        # Separar debug info del resultado si existe
        debug_info = ""
        clean_result = intermediate_result

        if "[DEBUG INFO]" in intermediate_result:
            parts = intermediate_result.split("[DEBUG INFO]")
            clean_result = parts[0].strip()
            debug_info = "[DEBUG INFO]" + parts[1] if len(parts) > 1 else ""

        # Formatear respuesta según el intent
        format_prompt = f"""Eres un asistente de gestión de libros amigable y profesional.

El usuario hizo esta consulta: "{user_message}"

El sistema detectó que su intención es: {intent}

Los resultados obtenidos son:
{clean_result}

Tu trabajo es tomar estos resultados y generar una respuesta final:
- Clara y bien estructurada
- Amigable y conversacional
- Que responda directamente a lo que el usuario preguntó
- Si hay libros listados, preséntalos de forma organizada

IMPORTANTE: NO inventes información. Solo usa los datos proporcionados en los resultados."""

        # Invocar el LLM para formatear
        response = llm.invoke(format_prompt)
        final_text = response.content.strip()

        # Agregar debug info al final si existe
        if debug_info:
            final_text += "\n\n" + debug_info

        # Actualizar el estado con la respuesta final
        state["final_response"] = final_text

        # Actualizar metadata
        if "metadata" not in state or state["metadata"] is None:
            state["metadata"] = {}

        state["metadata"]["formatted"] = True
        state["metadata"]["formatter_node"] = "executed"

        logger.debug(f"Respuesta formateada: {final_text[:150]}...")

    except Exception as e:
        error_msg = f"Error en nodo de formateo: {str(e)}"
        logger.error(error_msg)

        # Fallback: retornar el resultado intermedio sin formatear
        state["final_response"] = (
            intermediate_result or "Ocurrió un error al formatear la respuesta."
        )
        state["error"] = error_msg

    return state
