"""Request DTOs for the API."""

from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request body for the /query endpoint."""

    message: str
    thread_id: str | None = None
