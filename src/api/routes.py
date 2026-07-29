"""API route definitions for the ASTA multi-agent book service."""

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..graph import graph_service
from ..graph.checkpointer import checkpointer, list_conversations

router = APIRouter()


# TODO: sacar las interfaces de request/response a un archivo aparte, para que puedan ser 
# importadas por el cliente y por el servidor.s
class QueryRequest(BaseModel):
    """Request body for the /query endpoint."""

    message: str
    thread_id: str | None = None


class QueryResponse(BaseModel):
    """Response body returned by the /query endpoint."""

    response: str
    intent: str
    thread_id: str
    success: bool


@router.get("/")
async def root():
    """Welcome endpoint with basic API information."""
    return {"message": "Welcome to ASTA API - Book Management System with Multi-Agent LangGraph"}


@router.get("/ask")
async def ask_agent(question: str):
    """GET endpoint that processes a question using the multi-agent graph system.

    The graph automatically:
    1. Classifies the intent (search/modify/recommend/conversation)
    2. Routes to the specialized agent
    3. Generates a formatted response

    Args:
        question: The question to ask the AI agent

    Returns:
        A JSON response with the agent's answer and detected intent

    Example:
        GET /ask?question=Lista todos los libros
    """
    result = graph_service.process_query(question)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "question": question,
        "answer": result["response"],
        "intent": result["intent"],
        "metadata": result["metadata"],
    }


@router.post("/query")
async def process_query(request: QueryRequest) -> QueryResponse:
    """POST endpoint that processes a query using the multi-agent graph system.

    The LangGraph multi-agent system:
    - Router node: Classifies user intent (search/modify/recommend/conversation)
    - Agent nodes: Execute specialized tasks based on intent
    - Formatter node: Generates user-friendly final response

    Args:
        request: QueryRequest with the user's message

    Returns:
        QueryResponse with the agent's response, intent, and success status

    Example:
        POST /query
        Body: {"message": "Crea un libro llamado '1984' escrito por George Orwell"}
    """
    # El cliente manda el thread_id para continuar una conversación;
    # si no viene, el servidor mintea uno nuevo y lo devuelve.
    thread_id = request.thread_id or str(uuid.uuid4())
    result = graph_service.process_query(request.message, thread_id=thread_id)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return QueryResponse(
        response=result["response"],
        intent=result["intent"] or "unknown",
        thread_id=result["thread_id"],
        success=result["success"],
    )


@router.post("/conversations")
async def create_conversation():
    """Mints a fresh conversation id (thread_id) for the client to use on /query."""
    return {"thread_id": str(uuid.uuid4())}


@router.get("/conversations")
async def get_conversations():
    """Lists existing conversations (one per thread_id), most recent first."""
    return {"conversations": list_conversations()}


@router.get("/conversations/{thread_id}")
async def get_conversation(thread_id: str):
    """Returns the current (last-5-turns) messages of a conversation, or 404."""
    tuple_ = checkpointer.get_tuple({"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}})
    if tuple_ is None:
        raise HTTPException(status_code=404, detail=f"Conversación '{thread_id}' no encontrada")

    messages = tuple_.checkpoint.get("channel_values", {}).get("messages", [])
    return {
        "thread_id": thread_id,
        "messages": [
            {"role": getattr(m, "type", "unknown"), "content": getattr(m, "content", str(m))}
            for m in messages
        ],
    }


@router.get("/graph/visualize")
async def visualize_graph():
    """Endpoint to visualize the multi-agent graph structure.

    Returns a Mermaid diagram of the graph for debugging and documentation.

    Example:
        GET /graph/visualize
    """
    try:
        mermaid_diagram = graph_service.get_graph_visualization()
        return {
            "format": "mermaid",
            "diagram": mermaid_diagram,
            "info": "You can visualize this diagram at https://mermaid.live/",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating visualization: {str(e)}"
        ) from e
