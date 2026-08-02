"""Response DTOs for the API."""

from pydantic import BaseModel


class QueryResponse(BaseModel):
    """Response body returned by the /query endpoint."""

    response: str
    intent: str
    thread_id: str
    success: bool
