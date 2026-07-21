"""Sube los prompts locales a Langfuse Prompt Management (correr una sola vez).

Uso (desde la raíz del proyecto):
    uv run python -m src.scripts.seed_prompts

Idempotencia: create_prompt crea una NUEVA versión si el prompt ya existe.
Correrlo dos veces no rompe nada, solo agrega versiones duplicadas con label
'production'. Las constantes importadas de cada nodo son la fuente de verdad.
"""
import src.graph  # noqa: F401 — inicializa el paquete graph antes de importar nodos (evita import circular)
from src.llm.langfuse_client import langfuse
from src.agents.router_node import ROUTER_PROMPT
from src.agents.search_node import SEARCH_SYSTEM_PROMPT
from src.agents.modify_node import MODIFY_SYSTEM_PROMPT
from src.agents.recommend_node import RECOMMEND_SYSTEM_PROMPT
from src.agents.formatter_node import FORMATTER_PROMPT, FORMATTER_ERROR_PROMPT


PROMPTS = {
    "router-classifier": ROUTER_PROMPT,
    "search-agent": SEARCH_SYSTEM_PROMPT,
    "modify-agent": MODIFY_SYSTEM_PROMPT,
    "recommend-agent": RECOMMEND_SYSTEM_PROMPT,
    "formatter": FORMATTER_PROMPT,
    "formatter-error": FORMATTER_ERROR_PROMPT,
}


def main() -> None:
    for name, prompt in PROMPTS.items():
        langfuse.create_prompt(
            name=name,
            type="text",
            prompt=prompt,
            labels=["production"],
        )
        print(f"✓ {name}")
    print(f"\nSubidos {len(PROMPTS)} prompts a Langfuse con label 'production'.")


if __name__ == "__main__":
    main()
