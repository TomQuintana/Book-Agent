"""Recommend subagent — specialized agent for book recommendations."""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from ..llm.client import llm
from ..graph.state import InternalAgentState
from ..prompts.recommend_prompt import SYSTEM_PROMPT
from ..tools.book_tools import get_read_books

recommend_agent = create_agent(
    model=llm,
    tools=[get_read_books],
    state_schema=InternalAgentState,
    checkpointer=InMemorySaver(),
    system_prompt=SYSTEM_PROMPT,
)

print("test")
