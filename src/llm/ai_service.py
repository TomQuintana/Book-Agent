"""Book-management agent built on top of the LLM client and tools."""

from langchain.agents import create_agent

from ..tools.book_tools import book_tools
from .client import llm

# Crear el agente (más simple y moderno)
agent = create_agent(
    model=llm,
    tools=book_tools,
    system_prompt="""Eres un asistente especializado en gestión de libros.
    Puedes ayudar a crear, buscar, actualizar, eliminar y listar libros.
    Cuando el usuario te pida realizar operaciones sobre libros, usa las herramientas disponibles.
    Siempre sé claro y conciso en tus respuestas.
    Si necesitas información adicional para completar una tarea, pregunta al usuario.""",
)


class AIService:
    """AI service for processing book-related queries."""

    def __init__(self):
        self.agent = agent

    def process_query(self, query: str) -> str:
        """Processes a user query using the agent with tools.

        Args:
            query: User query or question

        Returns:
            Agent response after executing the necessary tools
        """
        result = self.agent.invoke({"messages": [{"role": "user", "content": query}]})

        # Extract the last agent response
        return result["messages"][-1].content


# Global service instance
ai_service = AIService()
