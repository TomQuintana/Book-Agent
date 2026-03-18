"""Nodo Router - Clasifica la intención del usuario"""

from ..graph.state import AgentState
from ..llm.client import llm


def router_node(state: AgentState) -> AgentState:
    """
    Clasifica la intención del usuario para enrutar al agente correcto.

    Intenciones posibles:
    - search: Buscar, listar, obtener información de libros
    - modify: Crear, actualizar o eliminar libros
    - recommend: Pedir recomendaciones o sugerencias
    - conversation: Preguntas generales sin operación específica
    """

    user_message = state["user_message"]

    # Prompt para clasificar la intención
    classification_prompt = f"""Eres un clasificador de intenciones para un sistema de gestión de libros.

Analiza el siguiente mensaje del usuario y clasifica su intención en UNA de estas categorías:

1. "search" - Si quiere buscar, listar, ver o consultar información de libros existentes
   Ejemplos: "lista todos los libros", "busca libros de García Márquez", "dame info del libro 5"

2. "modify" - Si quiere crear, actualizar, editar o eliminar libros
   Ejemplos: "crea un libro llamado 1984", "actualiza el estado del libro 3", "elimina el libro 2"

3. "recommend" - Si pide recomendaciones, sugerencias o consejos sobre qué leer
   Ejemplos: "recomiéndame un libro", "qué debería leer ahora", "sugiéreme algo de ciencia ficción"

4. "conversation" - Si es una pregunta general, saludo o no está relacionado con operaciones de libros
   Ejemplos: "hola", "cómo estás", "qué puedes hacer", "explícame qué es un libro"

Mensaje del usuario: "{user_message}"

Responde ÚNICAMENTE con una de estas palabras: search, modify, recommend, conversation
NO agregues explicaciones, solo la categoría.
"""

    try:
        # Invocar el LLM para clasificar
        response = llm.invoke(classification_prompt)
        intent = response.content.strip().lower()

        # Validar que la respuesta sea una de las intenciones válidas
        valid_intents = ["search", "modify", "recommend", "conversation"]
        if intent not in valid_intents:
            # Si el LLM responde algo inválido, intentamos parsear
            for valid_intent in valid_intents:
                if valid_intent in intent:
                    intent = valid_intent
                    break
            else:
                # Por defecto, lo consideramos conversación
                intent = "conversation"

        # Actualizar el estado con la intención detectada
        state["intent"] = intent
        state["error"] = None

        print(f"[ROUTER] Mensaje: '{user_message}' -> Intención: {intent}")

    except Exception as e:
        print(f"[ROUTER] Error al clasificar intención: {str(e)}")
        state["intent"] = "conversation"
        state["error"] = f"Error en clasificación: {str(e)}"

    return state
