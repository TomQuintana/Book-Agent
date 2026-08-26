"""Abstract repository interface for book types."""

from abc import ABC, abstractmethod

from ..models.types_books import TypesBooks


class BookTypeRepository(ABC):
    """Abstract base class for book type repository."""

    @abstractmethod
    async def get_all_book_types(self) -> list[TypesBooks]:
        """Get all book types."""
        pass

    @abstractmethod
    async def get_book_type_by_id(self, book_type_id: int) -> TypesBooks | None:
        """Get a book type by its ID."""
        pass

    @abstractmethod
    async def create_book_type(self, book_type: TypesBooks) -> TypesBooks:
        """Create a new book type."""
        pass

    @abstractmethod
    async def update_book_type(self, book_type_id: int, book_type: TypesBooks) -> TypesBooks | None:
        """Update an existing book type."""
        pass

    @abstractmethod
    async def delete_book_type(self, book_type_id: int) -> bool:
        """Delete a book type by its ID."""
        pass
