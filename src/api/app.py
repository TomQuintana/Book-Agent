from fastapi import FastAPI
from .routes import router
from contextlib import asynccontextmanager
from ..database.connection import init_db
from ..config.logging_config import get_logger

logger = get_logger("asta.api")
app = FastAPI(title="ASTA API", version="0.1.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles the lifespan events of the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    logger.info("Server is starting")
    await init_db()
    logger.info("Server docs — http://localhost:8000/docs")
    yield
    logger.info("Server is shutting down")


app.include_router(router)
