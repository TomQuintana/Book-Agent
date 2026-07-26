"""Upload local prompts to Langfuse Prompt Management (run once).

Usage (from the project root):
    uv run python -m src.scripts.seed_prompts

Idempotency: create_prompt creates a NEW version if the prompt already
exists. Running it twice is safe, it just adds duplicate versions with the
'production' label. The constants imported from each node are the source
of truth.
"""

import src.graph  # noqa: F401 — inicializa el paquete graph antes de importar nodos (evita import circular)
from src.agents.formatter_node import FORMATTER_ERROR_PROMPT, FORMATTER_PROMPT
from src.agents.modify_node import MODIFY_SYSTEM_PROMPT
from src.agents.recommend_node import RECOMMEND_SYSTEM_PROMPT
from src.agents.router_node import ROUTER_PROMPT
from src.agents.search_node import SEARCH_SYSTEM_PROMPT
from src.llm.langfuse_client import langfuse

PROMPTS = {
    "router-classifier": ROUTER_PROMPT,
    "search-agent": SEARCH_SYSTEM_PROMPT,
    "modify-agent": MODIFY_SYSTEM_PROMPT,
    "recommend-agent": RECOMMEND_SYSTEM_PROMPT,
    "formatter": FORMATTER_PROMPT,
    "formatter-error": FORMATTER_ERROR_PROMPT,
}


def main() -> None:
    """Create/update all PROMPTS in Langfuse with the 'production' label."""
    for name, prompt in PROMPTS.items():
        langfuse.create_prompt(
            name=name,
            type="text",
            prompt=prompt,
            labels=["production"],
        )


if __name__ == "__main__":
    main()
