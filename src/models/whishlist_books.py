"""Wishlist book table model."""

from sqlmodel import Field, SQLModel


class WhishlistBooks(SQLModel, table=True):
    """Wishlist books table model."""

    id: int = Field(default=None, primary_key=True)
    title: str = Field(..., min_length=1)
    author: str | None = None
    type: str | None = None
    site: str | None = None
