"""Book service with CRUD operations backed by the database."""

from sqlmodel import select

from ..database.connection import get_session
from ..database.models import Book, BookCreate, BookUpdate


class BookService:
    """Service for book CRUD operations."""

    def create_book(self, book_data: BookCreate) -> Book:
        """Create and persist a new book."""
        with get_session() as session:
            book = Book.model_validate(book_data)
            session.add(book)
            session.commit()
            session.refresh(book)
            return book

    def get_by_title_author(self, title: str, author: str | None) -> Book | None:
        """Find a book by title+author. Acts as the idempotency guard on retries."""
        with get_session() as session:
            query = select(Book).where(Book.title == title, Book.author == author)
            return session.exec(query).first()

    def get_book(self, book_id: int) -> Book | None:
        """Fetch a book by id, or None if it doesn't exist."""
        with get_session() as session:
            return session.get(Book, book_id)

    def update_book(self, book_id: int, book_data: BookUpdate) -> Book | None:
        """Update the given fields of a book, or return None if it doesn't exist."""
        with get_session() as session:
            book = session.get(Book, book_id)
            if not book:
                return None
            fields = book_data.model_dump(exclude_unset=True)
            for key, value in fields.items():
                setattr(book, key, value)
            session.add(book)
            session.commit()
            session.refresh(book)
            return book

    def delete_book(self, book_id: int) -> bool:
        """Delete a book by id. Returns False if it doesn't exist."""
        with get_session() as session:
            book = session.get(Book, book_id)
            if not book:
                return False
            session.delete(book)
            session.commit()
            return True

    def list_books(self, status: str = None, author: str = None) -> list[Book]:
        """List books, optionally filtered by status and/or author."""
        with get_session() as session:
            query = select(Book)
            if status:
                query = query.where(Book.status == status)
            if author:
                query = query.where(Book.author.contains(author))
            query = query.order_by(Book.created_at.desc())
            return session.exec(query).all()
