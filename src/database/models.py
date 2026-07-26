"""SQLModel schemas for books: the table model and its create/update payloads."""

from datetime import date, datetime

from sqlmodel import Field, SQLModel


class Book(SQLModel, table=True):
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
