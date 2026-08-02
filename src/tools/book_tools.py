"""LangChain tools exposing book CRUD operations to the agent."""

from datetime import date

from langchain_core.tools import tool

from ..database.models import BookCreate, BookUpdate
from ..services.book_service import BookService

book_service = BookService()


# TODO: see a type by default
@tool
def create_book(
    title: str,
    author: str = None,
    status: str = None,
    type: str = None,
    description: str = None,
    is_physically: bool = False,
    finished: str = None,
) -> str:
    """Creates a new book in the database.

    Args:
        title: Book title (required)
        author: Book author (optional)
        status: Reading status — 'reading', 'completed', 'pending' (optional)
        type: Book type — 'fiction', 'non-fiction', 'technical', 'emprendimiento' (optional)
        description: Book description (optional)
        is_physically: Whether the book is a physical copy (optional, default False)
        finished: Completion date in YYYY-MM-DD format (optional)

    Returns:
        Confirmation message with the created book details
    """
    try:
        book_data = BookCreate(
            title=title,
            author=author,
            status=status,
            type=type,
            description=description,
            is_physically=is_physically,
            finished=date.fromisoformat(finished) if finished else None,
        )
        book = book_service.create_book(book_data)
        return f"Libro '{book.title}' creado exitosamente con ID {book.id}"
    except Exception as e:
        return f"Error al crear el libro: {str(e)}"


@tool
def get_book(book_id: int) -> str:
    """Retrieves detailed information about a book by its ID.

    Args:
        book_id: Unique book ID

    Returns:
        Full book details or an error message if not found
    """
    try:
        book = book_service.get_book(book_id)
        if not book:
            return f"No se encontró ningún libro con ID {book_id}"

        return f"""Libro encontrado:
        - ID: {book.id}
        - Título: {book.title}
        - Autor: {book.author or "No especificado"}
        - Estado: {book.status or "No especificado"}
        - Tipo: {book.type or "No especificado"}
        - Descripción: {book.description or "Sin descripción"}
        - Es físico: {"Sí" if book.is_physically else "No"}
        - Fecha de finalización: {book.finished or "No finalizado"}
            """
    except Exception as e:
        return f"Error al obtener el libro: {str(e)}"


@tool
def update_book(
    book_id: int,
    title: str = None,
    author: str = None,
    status: str = None,
    description: str = None,
) -> str:
    """Updates the information of an existing book.

    Args:
        book_id: ID of the book to update (required)
        title: New book title (optional)
        author: New book author (optional)
        status: New reading status (optional)
        description: New description (optional)

    Returns:
        Confirmation message with the updated data
    """
    try:
        book_data = BookUpdate(title=title, author=author, status=status, description=description)
        book = book_service.update_book(book_id, book_data)
        if not book:
            return f"No se encontró ningún libro con ID {book_id}"

        return f"Libro '{book.title}' (ID: {book_id}) actualizado correctamente"
    except Exception as e:
        return f"Error al actualizar el libro: {str(e)}"


@tool
def delete_book(book_id: int) -> str:
    """Deletes a book from the database.

    Args:
        book_id: ID of the book to delete

    Returns:
        Confirmation message or error
    """
    try:
        deleted = book_service.delete_book(book_id)
        if deleted:
            return f"Libro con ID {book_id} eliminado exitosamente"
        else:
            return f"No se encontró ningún libro con ID {book_id}"
    except Exception as e:
        return f"Error al eliminar el libro: {str(e)}"


@tool
def list_books(status: str = None, author: str = None, title: str = None) -> str:
    """Lists and searches books in the database with optional filters.

    Use this tool to:
    - List all books (no parameters)
    - Search by specific title (e.g. "1984", "One Hundred Years of Solitude")
    - Search by author (e.g. "García Márquez", "George Orwell")
    - Filter by reading status (e.g. "completed", "reading", "pending")
    - Combine filters (e.g. author + status)

    Args:
        title: Search by book title (partial, case-insensitive) (optional)
        author: Filter by author (partial, case-insensitive) (optional)
        status: Filter by reading status — 'reading', 'completed', 'pending' (optional)

    Returns:
        Formatted list of matching books with their details

    Examples:
        - list_books(title="1984") → Finds books with "1984" in the title
        - list_books(author="Orwell") → Finds books by authors containing "Orwell"
        - list_books(status="completed") → Lists completed books
        - list_books() → Lists all books
    """
    try:
        books = book_service.list_books(status=status, author=author)

        # Filtrar por título si se especifica
        if title and books:
            title_lower = title.lower()
            books = [book for book in books if book.title and title_lower in book.title.lower()]

        if not books:
            filters = []
            if title:
                filters.append(f"title='{title}'")
            if status:
                filters.append(f"status='{status}'")
            if author:
                filters.append(f"author='{author}'")
            filter_str = " con filtros: " + ", ".join(filters) if filters else ""
            return f"No se encontraron libros{filter_str}"

        result = f"Encontrados {len(books)} libro(s):\n\n"
        for book in books:
            result += f"[ID: {book.id}] {book.title}\n"
            result += f"    Autor: {book.author or 'No especificado'}\n"
            result += f"    Estado: {book.status or 'No especificado'}\n"
            if book.description:
                desc = (
                    book.description[:100] + "..."
                    if len(book.description) > 100
                    else book.description
                )
                result += f"    Descripción: {desc}\n"
            result += "\n"

        return result
    except Exception as e:
        return f"Error al listar libros: {str(e)}"


@tool
def get_read_books() -> str:
    """Retrieves the user's reading history (completed and in-progress books) from the database.

    Use this tool before making recommendations to understand what the user has already read.
    Returns books with status 'completed' and 'reading'.

    Returns:
        Formatted list of read books with title, author and type
    """
    try:
        completed = book_service.list_books(status="completed")
        reading = book_service.list_books(status="reading")
        all_read = completed + reading

        if not all_read:
            return (
                "El usuario no tiene libros registrados como leídos o en progreso en su biblioteca."
            )

        result = f"Historial de lectura del usuario ({len(all_read)} libro(s)):\n\n"

        if completed:
            result += "📚 Libros terminados:\n"
            for book in completed:
                result += f"  - {book.title}"
                if book.author:
                    result += f" (de {book.author})"
                if book.type:
                    result += f" [{book.type}]"
                result += "\n"

        if reading:
            result += "\n📖 Libros en progreso:\n"
            for book in reading:
                result += f"  - {book.title}"
                if book.author:
                    result += f" (de {book.author})"
                if book.type:
                    result += f" [{book.type}]"
                result += "\n"

        return result
    except Exception as e:
        return f"Error al obtener el historial de lectura: {str(e)}"


# Lista de todas las tools disponibles para exportar
book_tools = [create_book, get_book, update_book, delete_book, list_books, get_read_books]
