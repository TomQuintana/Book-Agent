from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(..., min_length=1)
    author: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    is_physically: Optional[bool] = Field(default=False)
    finished: Optional[date] = None


class BookCreate(SQLModel):
    title: str = Field(..., min_length=1)
    author: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    is_physically: Optional[bool] = Field(default=False)
    finished: Optional[date] = None


class BookUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1)
    author: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    is_physically: Optional[bool] = None
    finished: Optional[date] = None
