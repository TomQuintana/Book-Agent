import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///src/data/books.db")
    LANGSMITH_TRACING: str = os.getenv("LANGSMITH_TRACING", "true")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")


settings = Settings()
