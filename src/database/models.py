"""SQLModel schemas for books: the table model and its create/update payloads."""

from datetime import date, datetime

from sqlmodel import Field, SQLModel


class Book(SQLModel, table=True):  # type: ignore[call-arg]
    """Book table model."""

    __tablename__ = "books"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(..., min_length=1)
    author: str | None = None
    status: str | None = None
    type: str | None = None
    description: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.now)
    is_physically: bool | None = Field(default=False)
    finished: date | None = None


class BookCreate(SQLModel):
    """Payload for creating a new book."""

    title: str = Field(..., min_length=1)
    author: str | None = None
    status: str | None = None
    type: str | None = None
    description: str | None = None
    is_physically: bool | None = Field(default=False)
    finished: date | None = None


class BookUpdate(SQLModel):
    """Payload for partially updating an existing book."""

    title: str | None = Field(default=None, min_length=1)
    author: str | None = None
    status: str | None = None
    type: str | None = None
    description: str | None = None
    is_physically: bool | None = None
    finished: date | None = None


class Conversation(SQLModel, table=True):  # type: ignore[call-arg]
    """Conversation metadata, keyed by LangGraph thread_id."""

    __tablename__ = "conversations"

    thread_id: str = Field(primary_key=True)  # = thread_id de LangGraph
    user_id: str = Field(default="default_user", index=True)
    title: str | None = None  # None hasta el 1er mensaje
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Message(SQLModel, table=True):  # type: ignore[call-arg]
    """Single message (user or assistant) belonging to a conversation."""

    __tablename__ = "messages"
    id: int | None = Field(default=None, primary_key=True)
    thread_id: str = Field(foreign_key="conversations.thread_id", index=True)
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
