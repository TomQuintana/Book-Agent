"""Nodo Formatter - Formatea resultados de forma amigable para el usuario"""

from ..llm.client import llm
from ..graph.state import AgentState


def formatter_node(state: AgentState) -> AgentState:
    """
    Nodo final que formatea la respuesta para el usuario de forma amigable.

    Este nodo:
    1. Toma los resultados intermedios (de search_node, modify_node, etc.)
    2. Considera el intent del usuario (search, modify, recommend, conversation)
    3. Genera una respuesta final bien formateada y amigable
    4. Maneja casos de error de forma clara

    Args:
        state: Estado actual con intermediate_result e intent

    Returns:
        Estado actualizado con final_response
    """

    intermediate_result = state.get("intermediate_result")
    intent = state.get("intent")
    user_message = state.get("user_message")
    error = state.get("error")

    try:
        print(f"\n[FORMATTER_NODE] 📝 Formateando respuesta final")
        print(f"[FORMATTER_NODE] Intent: {intent}")

        # Si hubo un error, generar respuesta de error amigable
        if error:
            print(f"[FORMATTER_NODE] ⚠️  Detectado error: {error}")

            error_prompt = f"""El usuario preguntó: "{user_message}"

Hubo un error al procesar su consulta: {error}

Genera una respuesta amigable explicando que hubo un problema y sugiere al usuario qué puede hacer.
Sé empático y profesional."""

            response = llm.invoke(error_prompt)
            state["final_response"] = response.content.strip()
            print(f"[FORMATTER_NODE] ✅ Respuesta de error formateada")
            return state

        # Si no hay resultados intermedios, respuesta genérica
        if not intermediate_result:
            state["final_response"] = "Lo siento, no pude procesar tu consulta correctamente."
            print(f"[FORMATTER_NODE] ⚠️  No hay resultados intermedios")
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

        print(f"[FORMATTER_NODE] ✅ Respuesta formateada exitosamente")
        print(f"[FORMATTER_NODE] Respuesta: {final_text[:150]}...")

    except Exception as e:
        error_msg = f"Error en nodo de formateo: {str(e)}"
        print(f"[FORMATTER_NODE] ❌ {error_msg}")

        # Fallback: retornar el resultado intermedio sin formatear
        state["final_response"] = intermediate_result or "Ocurrió un error al formatear la respuesta."
        state["error"] = error_msg

    return state
