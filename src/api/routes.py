"""API route definitions for the ASTA multi-agent book service."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..config.logging_config import get_logger
from ..database.connection import get_db
from ..dto.request import QueryRequest
from ..dto.response import QueryResponse
from ..graph import graph_service
from ..services.conversation_service import ConversationService

router = APIRouter()
logger = get_logger("asta.api")


@router.get("/")
async def root():
    """Welcome endpoint with basic API information."""
    return {"message": "Welcome to ASTA API - Book Management System with Multi-Agent LangGraph"}


def create_thread_id() -> str:
    """Generate a unique thread ID for a new conversation."""
    return str(uuid.uuid4())


@router.post("/query")
async def process_query(request: QueryRequest, session: Session = Depends(get_db)) -> QueryResponse:
    """POST endpoint that processes a query using the multi-agent graph system.

    The LangGraph multi-agent system:
    - Router node: Classifies user intent (search/modify/recommend/conversation)
    - Agent nodes: Execute specialized tasks based on intent
    - Formatter node: Generates user-friendly final response

    Args:
        request: QueryRequest with the user's message
        session: Database session injected by FastAPI (closed after the request)

    Returns:
        QueryResponse with the agent's response, intent, and success status

    Example:
        POST /query
        Body: {"message": "Crea un libro llamado '1984' escrito por George Orwell"}
    """
    thread_id = request.thread_id or create_thread_id()
    result = graph_service.process_query(request.message, thread_id=thread_id)
    conversation_service = ConversationService(session)

    if not result["success"]:
        logger.error(f"Turno fallido en '{thread_id}': {result['error']}")

        return QueryResponse(
            response=result["response"],
            intent=result["intent"] or "unknown",
            thread_id=thread_id,
            success=False,
        )

    conversation_service.persist_turn(thread_id, request.message, result["response"])

    return QueryResponse(
        response=result["response"],
        intent=result["intent"] or "unknown",
        thread_id=result["thread_id"],
        success=True,
    )


@router.post("/query/{thread_id}/retry")
async def retry_query(thread_id: str, session: Session = Depends(get_db)) -> QueryResponse:
    """Retries the conversation's last turn without resending the message.

    The original message comes from the LangGraph checkpoint, not the body.
    """
    result = graph_service.resume(thread_id)

    if not result["success"]:
        raise HTTPException(status_code=409, detail="No hay nada pendiente para reintentar")

    conversation_service = ConversationService(session)
    conversation_service.persist_turn(thread_id, result["user_message"], result["response"])

    return QueryResponse(
        response=result["response"],
        intent=result["intent"] or "unknown",
        thread_id=thread_id,
        success=True,
    )


@router.get("/query/{thread_id}/state")
async def query_state(thread_id: str):
    """Debug: LangGraph checkpoint flow for a thread (which node is pending and why)."""
    return graph_service.inspect(thread_id)


@router.post("/conversations")
async def create_conversation(session: Session = Depends(get_db)):
    """Creates a fresh conversation and returns its thread_id and (null) title."""
    conversation_service = ConversationService(session)
    conv = conversation_service.create(create_thread_id())
    return {"thread_id": conv.thread_id, "title": conv.title}


@router.get("/conversations")
async def get_conversations(session: Session = Depends(get_db)):
    """Lists existing conversations (title, user_id, timestamps), most recent first."""
    conversation_service = ConversationService(session)
    return {"conversations": conversation_service.list()}


@router.get("/conversations/{thread_id}")
async def get_conversation(thread_id: str, session: Session = Depends(get_db)):
    """Returns a conversation's full message history, or 404 if it doesn't exist."""
    conversation_service = ConversationService(session)
    if conversation_service.get(thread_id) is None:
        raise HTTPException(status_code=404, detail=f"Conversación '{thread_id}' no encontrada")
    return {"thread_id": thread_id, "messages": conversation_service.get_messages(thread_id)}


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
