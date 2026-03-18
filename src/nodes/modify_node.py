"""Nodo Modify - Agente especializado en crear, actualizar y eliminar libros"""

from langchain.agents import create_agent
from ..llm.client import llm
from ..graph.state import AgentState
from ..tools.book_tools import create_book, update_book, delete_book


modify_agent = create_agent(
    model=llm,
    tools=[create_book, update_book, delete_book],
    system_prompt="""Eres un agente especializado en modificar la base de datos de libros.

Tu especialidad es CREAR, ACTUALIZAR y ELIMINAR libros.

Herramientas disponibles:

1. create_book(title, author, status, description, type, is_physically, finished):
   - Crea un nuevo libro. Solo 'title' es obligatorio.
   - status puede ser: 'reading', 'completed', 'pending'
   - type puede ser: 'fiction', 'non-fiction', 'technical', 'emprendimiento', etc.

2. update_book(book_id, title, author, status, description):
   - Actualiza un libro existente por su ID

3. delete_book(book_id):
   - Elimina un libro por su ID

IMPORTANTE:
- Extrae toda la información posible del mensaje del usuario
- Si el usuario no especifica un campo, no lo envíes (déjalo como None)
- Si te piden buscar o listar libros, indica que esa no es tu especialidad

Sé conciso y confirma la operación realizada.""",
)


def modify_node(state: AgentState) -> AgentState:
    """
    Nodo que procesa operaciones de modificación (crear, actualizar, eliminar).
    """
    user_message = state["user_message"]

    try:
        print(f"\n[MODIFY_NODE] Procesando modificación")
        print(f"[MODIFY_NODE] Mensaje: '{user_message}'")

        result = modify_agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]}
        )

        messages = result["messages"]
        agent_response = messages[-1].content

        state["intermediate_result"] = agent_response
        state["error"] = None

        if "metadata" not in state or state["metadata"] is None:
            state["metadata"] = {}

        state["metadata"]["node_executed"] = "modify_node"
        state["metadata"]["agent_type"] = "modify_agent"

        print(f"[MODIFY_NODE] Completado: {agent_response[:150]}...")

    except Exception as e:
        error_msg = f"Error en nodo de modificación: {str(e)}"
        print(f"[MODIFY_NODE] {error_msg}")
        state["intermediate_result"] = "No se pudo completar la operación."
        state["error"] = error_msg

    return state
