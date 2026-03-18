from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..graph import graph_service

router = APIRouter()


class QueryRequest(BaseModel):
    message: str


class QueryResponse(BaseModel):
    response: str
    intent: str
    success: bool


@router.get("/")
async def root():
    return {"message": "Welcome to ASTA API - Book Management System with Multi-Agent LangGraph"}


@router.get("/ask")
async def ask_agent(question: str):
    """
    GET endpoint that processes a question using the multi-agent graph system.

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
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )

    return {
        "question": question,
        "answer": result["response"],
        "intent": result["intent"],
        "metadata": result["metadata"]
    }


@router.post("/query")
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    POST endpoint that processes a query using the multi-agent graph system.

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
    result = graph_service.process_query(request.message)

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )

    return QueryResponse(
        response=result["response"],
        intent=result["intent"] or "unknown",
        success=result["success"]
    )


@router.get("/graph/visualize")
async def visualize_graph():
    """
    Endpoint to visualize the multi-agent graph structure.

    Returns a Mermaid diagram of the graph for debugging and documentation.

    Example:
        GET /graph/visualize
    """
    try:
        mermaid_diagram = graph_service.get_graph_visualization()
        return {
            "format": "mermaid",
            "diagram": mermaid_diagram,
            "info": "You can visualize this diagram at https://mermaid.live/"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualization: {str(e)}"
        )
