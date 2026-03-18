# ASTA API

Multi-agent book management system built with LangGraph and FastAPI.

```
  /\_/\
 ( o.o )  ASTA - Book Management Agent
  > ^ <
```

## Description

ASTA is a multi-agent system that manages a book collection through natural language. It uses LangGraph to orchestrate specialized agents that interpret user queries and execute operations on a SQLite database.

## Architecture

The system uses a multi-agent graph with the following flow:

1. **Router Node** - Classifies user intent (search, modify, recommend, conversation)
2. **Specialized Agents** - Each intent is routed to an agent with specific tools
3. **Formatter Node** - Generates a user-friendly final response

### Available Agents

| Agent | Intent | Tools |
|-------|--------|-------|
| Search Agent | Search and list books | `list_books`, `get_book` |
| Modify Agent | Create, update, delete | `create_book`, `update_book`, `delete_book` |

## Stack

- **LangGraph** - Multi-agent graph orchestration
- **LangChain + OpenAI** - LLM for natural language processing
- **FastAPI** - REST API
- **SQLModel + SQLite** - Data persistence
- **Rich + Prompt Toolkit** - CLI interface

## Setup

```bash
# Install dependencies
uv sync

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Required environment variables

```
OPENAI_API_KEY=your-api-key
DATABASE_URL=sqlite:///src/data/books.db
```

## Usage

### CLI (terminal interface)

```bash
make run-cli
```

### REST API

```bash
make run-api
```

Available endpoints:

- `POST /query` - Process a query via JSON `{"message": "..."}`
- `GET /ask?question=...` - Process a query via query param
- `GET /graph/visualize` - Graph visualization in Mermaid format

### Query examples

```
Create a book called 1984 by George Orwell, type fiction, status pending
List all books
Search books by García Márquez
Delete book with ID 3
```
