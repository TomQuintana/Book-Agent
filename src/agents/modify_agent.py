"""Modify subagent — specialized agent for creating, updating and deleting books."""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from ..llm.client import llm
from ..graph.state import InternalAgentState
from ..tools.book_tools import create_book, update_book, delete_book

modify_agent = create_agent(
    model=llm,
    tools=[create_book, update_book, delete_book],
    state_schema=InternalAgentState,
    checkpointer=InMemorySaver(),
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
