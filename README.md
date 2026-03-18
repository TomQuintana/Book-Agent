# ASTA API

Sistema multiagente de gestión de libros construido con LangGraph y FastAPI.

```
  /\_/\
 ( o.o )  ASTA - Book Management Agent
  > ^ <
```

## Descripción

ASTA es un sistema multiagente que permite gestionar una colección de libros a través de lenguaje natural. Usa LangGraph para orquestar agentes especializados que interpretan las consultas del usuario y ejecutan operaciones sobre una base de datos SQLite.

## Arquitectura

El sistema utiliza un grafo multiagente con el siguiente flujo:

1. **Router Node** - Clasifica la intención del usuario (search, modify, recommend, conversation)
2. **Agentes especializados** - Cada intención se enruta a un agente con tools específicas
3. **Formatter Node** - Genera una respuesta final amigable

### Agentes disponibles

| Agente | Intención | Tools |
|--------|-----------|-------|
| Search Agent | Buscar y listar libros | `list_books`, `get_book` |
| Modify Agent | Crear, actualizar, eliminar | `create_book`, `update_book`, `delete_book` |

## Stack

- **LangGraph** - Orquestación del grafo multiagente
- **LangChain + OpenAI** - LLM para procesamiento de lenguaje natural
- **FastAPI** - API REST
- **SQLModel + SQLite** - Persistencia de datos
- **Rich + Prompt Toolkit** - Interfaz CLI

## Setup

```bash
# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

### Variables de entorno requeridas

```
OPENAI_API_KEY=tu-api-key
DATABASE_URL=sqlite:///src/data/books.db
```

## Uso

### CLI (interfaz de terminal)

```bash
make run-cli
```

### API REST

```bash
make run-api
```

Endpoints disponibles:

- `POST /query` - Procesa una consulta via JSON `{"message": "..."}`
- `GET /ask?question=...` - Procesa una consulta via query param
- `GET /graph/visualize` - Visualización del grafo en formato Mermaid

### Ejemplos de consultas

```
Crea un libro llamado 1984 de George Orwell, tipo fiction, estado pending
Lista todos los libros
Busca libros de García Márquez
Elimina el libro con ID 3
```
