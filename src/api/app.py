"""FastAPI application entrypoint for the ASTA API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..config.logging_config import get_logger
from ..database.connection import init_db
from .routes import router

logger = get_logger("asta.api")


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


app = FastAPI(title="ASTA API", version="0.1.0", lifespan=lifespan)
app.include_router(router)
