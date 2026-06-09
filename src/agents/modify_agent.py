"""Modify subagent — specialized agent for creating, updating and deleting books."""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from ..llm.client import llm
from ..graph.state import InternalAgentState
from ..prompts.modify_prompt import SYSTEM_PROMPT
from ..tools.book_tools import create_book, update_book, delete_book

modify_agent = create_agent(
    model=llm,
    tools=[create_book, update_book, delete_book],
    state_schema=InternalAgentState,
    checkpointer=InMemorySaver(),
    system_prompt=SYSTEM_PROMPT,
)
