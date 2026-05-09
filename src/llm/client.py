import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from src.config.logging_config import get_logger


load_dotenv()

# reflection_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a viral twitter influencer grading a tweet. Generate critique and recommendations for the user's tweet."
#             "Always provide detailed recommendations, including requests for length, virality, style, etc.",
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#     ]
# )
#
#
# generation_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a twitter techie influencer assistant tasked with writing excellent twitter posts."
#             " Generate the best twitter post possible for the user's request."
#             " If the user provides critique, respond with a revised version of your previous attempts.",
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#     ]
# )

llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

_logger = get_logger("asta.llm")
_logger.debug("LLM client initialized")
# generate_chain = generation_prompt | llm
# reflection_chain = reflection_prompt | llm
