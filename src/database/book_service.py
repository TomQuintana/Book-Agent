from typing import List, Optional
from sqlmodel import select
from .models import Book, BookCreate, BookUpdate
from .connection import get_session


class BookService:
    """Servicio para operaciones CRUD de libros"""

    def create_book(self, book_data: BookCreate) -> Book:
        with get_session() as session:
            book = Book.model_validate(book_data)
            session.add(book)
            session.commit()
            session.refresh(book)
            return book

    def get_book(self, book_id: int) -> Optional[Book]:
        with get_session() as session:
            return session.get(Book, book_id)

    def update_book(self, book_id: int, book_data: BookUpdate) -> Optional[Book]:
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
        with get_session() as session:
            book = session.get(Book, book_id)
            if not book:
                return False
            session.delete(book)
            session.commit()
            return True

    def list_books(self, status: str = None, author: str = None) -> List[Book]:
        with get_session() as session:
            query = select(Book)
            if status:
                query = query.where(Book.status == status)
            if author:
                query = query.where(Book.author.contains(author))
            query = query.order_by(Book.created_at.desc())
            return session.exec(query).all()


book_service = BookService()
