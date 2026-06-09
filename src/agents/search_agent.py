"""Search subagent — specialized agent for book search queries."""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from ..llm.client import llm
from ..graph.state import InternalAgentState
from ..prompts.search_prompt import SYSTEM_PROMPT
from ..tools.book_tools import list_books, get_book

search_agent = create_agent(
    model=llm,
    tools=[list_books, get_book],
    state_schema=InternalAgentState,
    checkpointer=InMemorySaver(),
    system_prompt=SYSTEM_PROMPT,
)
