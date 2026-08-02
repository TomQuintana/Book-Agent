"""Generate short conversation titles from the first user message."""

# ponytail: título con el llm global (gpt-4o, temp 0); si molesta el costo,
# cachear o usar modelo chico.
from src.llm.client import llm


def generate_title(first_message: str) -> str:
    """Build a short title (<=6 words) from the first user message via the shared llm."""
    prompt = f"Resumí en máximo 6 palabras, sin comillas, el tema de:\n{first_message}"
    return llm.invoke(prompt).content.strip().strip('"')[:60]
