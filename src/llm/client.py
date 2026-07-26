"""OpenAI chat model client used across the multi-agent graph."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.config.logging_config import get_logger

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

_logger = get_logger("asta.llm")
_logger.debug("LLM client initialized")
