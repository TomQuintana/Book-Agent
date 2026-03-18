from fastapi import FastAPI
from .routes import router
from contextlib import asynccontextmanager
from ..database.connection import init_db

app = FastAPI(title="ASTA API", version="0.1.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles the lifespan events of the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    print('server is starting')
    await init_db()
    print('server docc - http://localhost:3001/docs')
    yield
    print('server is shutting down')


app.include_router(router)
