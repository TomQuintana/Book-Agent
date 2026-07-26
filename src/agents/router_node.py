"""Router Node — Classifies user intent for graph routing."""

from ..config.logging_config import get_logger
from ..graph.state import AgentState
from ..llm.client import llm
from ..llm.langfuse_client import langfuse

logger = get_logger("asta.router")


# Prompt canónico: fallback si Langfuse no responde y fuente para el seed (scripts/seed_prompts.py)
# Variable en sintaxis mustache de Langfuse: {{user_message}}
ROUTER_PROMPT = """Eres un clasificador de intenciones para un sistema de gestión de libros.

Analiza el siguiente mensaje del usuario y clasifica su intención en UNA de estas categorías:

1. "search" - Si quiere buscar, listar, ver o consultar información de libros existentes
   Ejemplos: "lista todos los libros", "busca libros de García Márquez", "dame info del libro 5"

2. "modify" - Si quiere crear, actualizar, editar o eliminar libros
   Ejemplos: "crea un libro llamado 1984", "actualiza el estado del libro 3", "elimina el libro 2"

3. "recommend" - Si pide recomendaciones, sugerencias o consejos sobre qué leer
   Ejemplos: "recomiéndame un libro", "qué debería leer ahora", "sugiéreme algo de ciencia ficción"

4. "conversation" - Si es una pregunta general, saludo o no está relacionado
   con operaciones de libros
   Ejemplos: "hola", "cómo estás", "qué puedes hacer", "explícame qué es un libro"

Mensaje del usuario: "{{user_message}}"

Responde ÚNICAMENTE con una de estas palabras: search, modify, recommend, conversation
NO agregues explicaciones, solo la categoría.
"""


def agent_router(state: AgentState) -> AgentState:
    """Classifies the user's intent to route to the correct agent.

    Possible intents:
    - search: Search, list, or retrieve book information
    - modify: Create, update, or delete books
    - recommend: Request recommendations or suggestions
    - conversation: General questions with no specific book operation
    """
    user_message = state["user_message"]

    prompt = langfuse.get_prompt("router-classifier", fallback=ROUTER_PROMPT)
    classification_prompt = prompt.compile(user_message=user_message)

    try:
        response = llm.invoke(classification_prompt)
        intent = response.content.strip().lower()

        valid_intents = ["search", "modify", "recommend", "conversation"]
        if intent not in valid_intents:
            for valid_intent in valid_intents:
                if valid_intent in intent:
                    intent = valid_intent
                    break
            else:
                intent = "conversation"

        state["intent"] = intent
        state["error"] = None

        logger.debug(f"Mensaje: '{user_message}' -> Intención: {intent}")

    except Exception as e:
        logger.error(f"Error al clasificar intención: {str(e)}")
        state["intent"] = "conversation"
        state["error"] = f"Error en clasificación: {str(e)}"

    return state
